import pandas as pd
from tree import load_from_dataframe

if __name__ == "__main__":
    df = pd.read_csv("imdb_top_1000_cleaned.csv")  
    movie_bst = load_from_dataframe(df)
   
    #print(movie_bst.get_movies_by_genre("Drama")[3:7])
    
    movie_title = input("Enter a movie title to search: ").strip()
    
    node = movie_bst.search(movie_title)
    if node:
        print(node.movie)
    else:
        print("Movie not found")

    
   
    # testing for CREATE 
    from tree import Movie

new_movie = Movie(
    movie_id=1001,
    title="My Test Movie",
    genres=["Comedy", "Drama"],
    year="2025",
    rating=8.0,
    director="Test Director",
    stars=["Star A", "Star B"]
)

movie_bst.insert(new_movie)

print(movie_bst.search("My Test Movie").movie)


# testing for UPDATE function 
success = movie_bst.update_movie("The Green Mile", rating=9.5, year="2000")

if success:
    print("Updated successfully.")
    print(movie_bst.search("The Green Mile").movie)
else:
    print("Update failed.")
    
# need to test delete function 