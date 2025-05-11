import pandas as pd.
from tree import load_from_dataframe

def main():
    df = pd.read_csv("imdb_top_1000_cleaned.csv")

    movie_bst = load_from_dataframe(df)

    movie_bst.build_similarity_network(threshold=0.3)


    print(f"Total movies loaded: {movie_bst.size}")

    movie_title = "Star Wars"
    movie = movie_bst.search(movie_title)

    if movie:
        print(f"\nFound movie: {movie.title}")
        print(f"Year: {movie.year}")
        print(f"Director: {movie.director}")
        print(f"Rating: {movie.rating}")
        print(f"Genres: {', '.join(movie.genres)}")

        similar_movies = movie_bst.get_similar_movies(movie_title)
        print("\nTop 5 similar movies:")
        for similar, score in similar_movies[:5]:
            print(f"- {similar.title} (similarity: {score:.2f})")
    else:
        print(f"\nMovie '{movie_title}' not found.")


    genre = "Sci-Fi"
    genre_movies = movie_bst.get_movies_by_genre(genre)
    print(f"\nFound {len(genre_movies)} movies in genre '{genre}':")
    for m in genre_movies[:3]:
        print(f"- {m.title} ({m.year})")

if __name__ == "__main__": 
    main()
