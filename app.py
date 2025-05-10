import streamlit as st
import pandas as pd
from movie_graph import Movie, MovieGraph, jaccard_similarity

# Load data and build graph
@st.cache_data
def build_graph():
    df = pd.read_csv("movies.csv")
    graph = MovieGraph()
    for _, row in df.iterrows():
        title = row['Series_Title']
        genres = list(set([row['genre_1'], row['genre_2'], row['genre_3']]))
        movie = Movie(title, genres)
        graph.add_movie(movie)

    titles = list(graph.movies.keys())
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            t1, t2 = titles[i], titles[j]
            sim = jaccard_similarity(graph.movies[t1].genres, graph.movies[t2].genres)
            if sim > 0.3:
                graph.add_similarity(t1, t2, sim)
    return graph

graph = build_graph()

# UI
st.title("Movie Recommender")
st.subheader("By May Mon Thant & Thant Thaw Tun")
st.write("This app recommends movies based on genre similarity.")

movie_titles = sorted([movie.title for movie in graph.movies.values()])
selected_title = st.selectbox("Pick a movie:", movie_titles)

if selected_title:
    st.subheader(f"Recommendations for: {selected_title}")
    similar_movies = graph.get_similar_movies(selected_title)
    if similar_movies:
        for title, score in similar_movies[:10]:
            st.write(f"**{graph.get_movie(title).title}** - Similarity: {score:.2f}")
    else:
        st.write("No similar movies found.")
