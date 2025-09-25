import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv("metadata.csv", low_memory=False)
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    df["year"] = df["publish_time"].dt.year
    df["abstract_word_count"] = df["abstract"].fillna("").apply(lambda x: len(x.split()))
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔧 Filters")
year_range = st.sidebar.slider("Select publication year range", 2019, 2023, (2020, 2021))
selected_journal = st.sidebar.selectbox("Filter by journal", options=["All"] + sorted(df["journal"].dropna().unique().tolist()))
show_wordcloud = st.sidebar.checkbox("Show Word Cloud", value=True)
show_sources = st.sidebar.checkbox("Show Source Distribution", value=True)

# Filter data
filtered_df = df[df["year"].between(year_range[0], year_range[1])]
if selected_journal != "All":
    filtered_df = filtered_df[filtered_df["journal"] == selected_journal]

# App layout
st.title("📊 CORD-19 Data Explorer")
st.write("Explore COVID-19 research papers by year, journal, and title keywords.")

# Sample data
st.subheader("📄 Sample of Filtered Data")
st.dataframe(filtered_df[["title", "journal", "publish_time", "abstract_word_count"]].head(10))

# Download button
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_metadata.csv",
    mime="text/csv"
)

# Publications over time
st.subheader("📅 Publications Over Time")
year_counts = filtered_df["year"].value_counts().sort_index()
fig1, ax1 = plt.subplots()
sns.barplot(x=year_counts.index, y=year_counts.values, ax=ax1, palette="crest")
ax1.set_xlabel("Year")
ax1.set_ylabel("Number of Papers")
st.pyplot(fig1)

# Top journals
st.subheader("🏛️ Top Journals")
top_journals = filtered_df["journal"].value_counts().head(10)
fig2, ax2 = plt.subplots()
sns.barplot(y=top_journals.index, x=top_journals.values, ax=ax2, palette="flare")
ax2.set_xlabel("Number of Papers")
ax2.set_ylabel("Journal")
st.pyplot(fig2)

# Word cloud
if show_wordcloud:
    st.subheader("☁️ Word Cloud of Paper Titles")
    titles = " ".join(filtered_df["title"].dropna().tolist()).lower()
    wordcloud = WordCloud(width=800, height=400, background_color="white", max_words=100).generate(titles)
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    ax3.imshow(wordcloud, interpolation="bilinear")
    ax3.axis("off")
    st.pyplot(fig3)

# Source distribution
if show_sources:
    st.subheader("🗂️ Source Distribution")
    sources = filtered_df["source_x"].fillna("").str.split(";").explode()
    source_counts = sources.value_counts().head(10)
    fig4, ax4 = plt.subplots()
    sns.barplot(y=source_counts.index, x=source_counts.values, ax=ax4, palette="rocket")
    ax4.set_xlabel("Number of Papers")
    ax4.set_ylabel("Source")
    st.pyplot(fig4)
