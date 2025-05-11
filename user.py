# movie_app.py
from tree import Movie, MovieBST, load_from_dataframe
import pandas as pd
from collections import defaultdict

def greetings():
    welcome = "Hello!\nWelcome to our movie repository. Search through our movies to find information about your favorite film!\n"
    print(welcome)
    
    
    df = pd.read_csv("imdb_top_1000_cleaned.csv")
    movie_bst = load_from_dataframe(df)
    
    
    genres_list = sorted(list(movie_bst.genre_index.keys()))
    
    return movie_bst, genres_list

def restart(movie_bst, genres_list):
    again = input("\nDo you wish to search for another movie? (y/n)\n ").lower()
    if again not in ["y", "n"]:
        print("Please enter y for yes, n for no")
        return restart(movie_bst, genres_list)
    if again == "y":
        select_mode(movie_bst, genres_list)
    if again == "n":
        print("Thank you for using our service!")

def select_mode(movie_bst: MovieBST, genres_list: list):
    print("\nDo you want to choose from a specific genre or do you want to perform a general search?")
    print("[1] - Genre filtered")
    print("[2] - General search")
    
    while True:
        choose = input("Enter your choice (1 or 2): ")
        if choose in ["1", "2"]:
            break
        print("Please enter a valid choice (1 or 2)")
    
    if choose == "1":
        chosen_genre = genre_search(genres_list, movie_bst)
        matches = suggest_genre(chosen_genre, movie_bst)
        movie = get_more_information(matches, movie_bst)
        if movie: # Only print card if a movie is selected
            print_movie_card(movie)
        else:
            print("No movie selected or found.")
    else:
        matches = general_search(movie_bst)
        movie = get_more_information(matches, movie_bst)
        if movie: 
            print_movie_card(movie)
        else:
            print("No movie selected or found.")
    
    restart(movie_bst, genres_list)

def genre_search(genres_list: list, movie_bst: MovieBST):
    print("\nThese are our movie genres:")
    for idx, genre in enumerate(genres_list):
        print(f"{idx+1}. {genre.title()}")
    
    while True:
        user_choice = input("\nWhat category would you want to search? Please enter the number associated to the genre.\n")
        try:
            choice_num = int(user_choice)
            if 1 <= choice_num <= len(genres_list):
                break
            print(f"Please enter a number between 1 and {len(genres_list)}")
        except ValueError:
            print("Please enter a valid number.")
    
    chosen_genre = genres_list[choice_num-1]
    print(f"\nThese are the films we have under {chosen_genre.title()}:")
    movies = movie_bst.get_movies_by_genre(chosen_genre)
    movies.sort(key=lambda m: m.title) 
    for idx, movie in enumerate(movies):
        print(f"{idx+1}. {movie.title}")
    
    return chosen_genre

def suggest_genre(genre: str, movie_bst: MovieBST):
    movies_in_genre = movie_bst.get_movies_by_genre(genre)
    titles = [movie.title for movie in movies_in_genre]
    
    while True:
        print("\nType the beginning of the title from a movie you want information about:")
        user_input = input().strip().lower()
        matches = [title for title in titles if title.lower().startswith(user_input)]
        
        if matches:
            print(f"\nFound {len(matches)} matches!")
            matches.sort() 
            for idx, title in enumerate(matches):
                print(f"{idx+1}. {title}")
            return matches
        
        print(f"Could not find any films starting with '{user_input}'. Please try again.")

def general_search(movie_bst: MovieBST):
    all_movies = movie_bst.get_all_movies()
    titles = [movie.title for movie in all_movies]
    
    while True:
        print("\nType the beginning of the title from a movie you want information about:")
        user_input = input().strip().lower()
        matches = [title for title in titles if title.lower().startswith(user_input)]
        
        if matches:
            print(f"\nFound {len(matches)} matches!")
            matches.sort() 
            for idx, title in enumerate(matches):
                print(f"{idx+1}. {title}")
            return matches
        
        print(f"Could not find any films starting with '{user_input}'. Please try again.")

def get_more_information(matches_lst: list[str], movie_bst: MovieBST):
    if not matches_lst:
        print("No movies to choose from.")
        return None
        
    while True:
        user_choice = input("\nWhich movie do you want to find more about? Enter the number: ")
        try:
            choice_num = int(user_choice)
            if 1 <= choice_num <= len(matches_lst):
                chosen_title = matches_lst[choice_num-1]
                movie = movie_bst.search(chosen_title)
                if movie:
                    return movie
                print("Movie not found in the database. This shouldn't happen if chosen from matches.")
            else:
                print(f"Please enter a number between 1 and {len(matches_lst)}")
        except ValueError:
            print("Please enter a valid number.")

def print_movie_card(movie: Movie):
    lines = [
        f"Title: {movie.title}",
        f"Year: {movie.year}",
        f"Runtime: {movie.runtime if movie.runtime else 'N/A'}",
        f"Genre: {', '.join(g for g in movie.genres if g).title()}",
        f"Director: {movie.director}",
        f"Stars: {', '.join(s for s in movie.stars if s)}",
        f"Rating: {movie.rating}"
    ]
    
    width = max(len(line) for line in lines)
    print("┌─" + '─'*width + "─┐")
    for line in lines:
        print("│ " + line + " "*(width-len(line)) + " │")
    print('└─' + '─'*width + '─┘')


if __name__ == "__main__":
    movie_bst, genres_list = greetings()
    select_mode(movie_bst, genres_list)