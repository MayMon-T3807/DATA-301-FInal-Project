import streamlit as st
import pandas as pd
from movie_graph import MovieGraph, Movie  # Import your existing recommendation system

if __name__ == "__main__":
    # Load dataset
    df = pd.read_csv("imdb_top_1000_cleaned.csv")

    # Initialize movie graph
    graph = MovieGraph()
    for idx, row in df.iterrows():
        title = row['Series_Title']
        genres = list(set([row['genre_1'], row['genre_2'], row['genre_3']]))
        director = row["Director"]
        actors = [row["Star1"], row["Star2"], row["Star3"], row["Star4"]]
        movie = Movie(idx, title, genres, director, actors)
        graph.add_movie(movie)

    # Run recommendation example
    title = input("Enter the name of the movie you like: ").strip().lower()
    movie = graph.get_movie(title)

    if movie:
        print(f"Recommendations for: {movie.title}")
        for similar_key, score in graph.get_similar_movies(movie.movie_id)[:5]:
            print(f"- {graph.movies[similar_key].title} with similarity {score:.2f}")
    else:
        print(f"Movie '{title}' not found in the database.")