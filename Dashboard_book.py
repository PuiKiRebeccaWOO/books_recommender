#Data Display
import streamlit as st
import pandas as pd

import time

#Data Visualization
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
from sklearn import datasets

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/combined_data.csv")
    return df

df = load_data()

# Map cluster numbers to readable names
cluster_labels = {
    0: "💡 Hidden Gems",
    1: "📈 Trending",
    2: "🌟 Moderately Popular",
    3: "🔥 Top Picks"
}
df["cluster_label"] = df["cluster"].map(cluster_labels)

# ---- UI ----
st.image("data/book_header.jpg")
st.title("📚 Book Recommender")

# --- Sidebar Filters for Tab 3 ---
def filter_books(df, author, category, rating, name_contains, cluster, number):
    result = df.copy()

    if author != "All":
        result = result[result["authors"] == author]

    if category != "All":
        result = result[result["category"] == category]

    if cluster != "All":
        result = result[result["cluster_label"] == cluster]

    result = result[result["averageRating"] >= rating]

    if name_contains:
        result = result[result["title"].str.contains(name_contains, case=False, na=False)]

    return result.head(number)

# Tabs
tab1, tab2, tab3 = st.tabs(["📌 Summary", "📊 Charts", "🔎 Find Books"])
with tab1:
    st.subheader("📌 Dataset Overview")
    st.write("### Data Preview")
    st.dataframe(df.head(10))
    st.metric("📘 Total Books", df.shape[0])
    st.metric("📂 Total Features", df.shape[1]-1)
    st.subheader("🔢 Unique Value Summary")
    col1, col2, col3 = st.columns(3)

    col1.metric("📚 Unique Categories", df["category"].nunique())
    col2.metric("✍️ Unique Authors", df["authors"].nunique())
    col3.metric("🎯 Clusters", df["cluster"].nunique())

with tab2:
    st.subheader("📊 Top 10 Book Categories by Count")
    filtered_df = df[df["category"] != "Unknown"]
    top_categories = filtered_df["category"].value_counts().head(10).reset_index()
    top_categories.columns = ["Category", "Count"]
    fig = px.bar(top_categories, x="Category", y="Count", title="Top 10 Categories")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔥 Top 10 Most Popular Books by Ratings Count")
    popular_books = df[df["ratingsCount"] > 0]
    top_books = popular_books.sort_values(by="ratingsCount", ascending=False).head(10)
    fig2 = px.bar(top_books, 
                  x="title", 
                  y="ratingsCount", 
                  title="Top 10 Books by Popularity (Ratings Count)",
                  labels={"ratingsCount": "Number of Ratings", "title": "Book Title"},
                  text="ratingsCount")
    
    fig2.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🎯 All Books: Cluster Visualization (Rating vs. Popularity)")
    
    # Scatter plot of all books, color by cluster label
    fig = px.scatter(
        df,
        x="averageRating",
        y="ratingsCount",
        color="cluster_label",
        hover_data=["title", "authors", "category"],
        title="All Books Clustered by Rating & Popularity",
        labels={
            "averageRating": "Average Rating",
            "ratingsCount": "Number of Ratings",
            "cluster_label": "Cluster"
        }
    )
    
    fig.update_traces(marker=dict(size=7, opacity=0.7), selector=dict(mode='markers'))
    fig.update_layout(legend_title="Cluster")
    
    st.plotly_chart(fig, use_container_width=True)
    

with tab3:
    st.subheader("🔎 Find Books by Filter")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        selected_author = st.selectbox("Author", ["All"] + sorted(df["authors"].dropna().unique().tolist()))
        selected_category = st.selectbox("Category", ["All"] + sorted(df["category"].dropna().unique().tolist()))
    with col2:
        cluster_options = ["All"] + sorted(df["cluster_label"].dropna().unique().tolist())
        selected_cluster = st.selectbox("Cluster", cluster_options)
        min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.0, step=0.5)

    name_filter = st.text_input("Book title contains (optional):")
    number_of_books = st.number_input("Number of books to display", 1, 50, 5)

    filtered_books = filter_books(df, selected_author, selected_category, min_rating, name_filter, selected_cluster, number_of_books)

    if filtered_books.empty:
        st.warning("No books found with the selected filters.")
    else:
        for i, row in filtered_books.iterrows():
            with st.container():
                st.markdown(f"### {row['title']}")
                cols = st.columns([1, 3])
                with cols[0]:
                    st.image(row["thumbnail"], width=120)
                with cols[1]:
                    st.markdown(f"**Author:** {row['authors']}")
                    st.markdown(f"**Category:** {row['category']}")
                    st.markdown(f"**Rating:** {row['averageRating']}")
                    st.markdown(f"**Description:** {row['description']}")
                st.markdown("---")
