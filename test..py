import pandas as pd
from tree import load_from_dataframe

if __name__ == "__main__":
    df = pd.read_csv("imdb_top_1000_cleaned.csv")  
    movie_bst = load_from_dataframe(df)
   
    print(movie_bst.get_movies_by_genre("Drama")[3:7])
    
    movie_title = input("Enter a movie title to search: ").strip()
    
    node = movie_bst.search(movie_title)
    if node:
        print(node.movie)
    else:
        print("Movie not found")
    print(movie_bst.get_movies_by_genre("Drama")[3:7])