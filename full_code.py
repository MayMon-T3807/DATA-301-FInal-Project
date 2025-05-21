import csv
from collections import defaultdict

# Unified Movie object definition combining fields from both codes.
class Movie:
    def __init__(self, movie_id, title, genres, director, actors, year=None, rating=None, runtime=None, description=None):
        self.movie_id = movie_id
        self.title = title
        self.genres = set(genres)
        self.director = director.strip().lower() if director else ""
        self.actors = set(actor.strip().lower() for actor in actors if actor)
        self.year = year
        self.rating = rating
        self.runtime = runtime
        self.description = description

    def __repr__(self):
        return f"Movie(ID={self.movie_id}, Title='{self.title}', Rating={self.rating})"

# Trie support for efficient prefix search (used for titles and genres).
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.movies = []  # Store Movie objects

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word, movie):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.movies.append(movie)
    
    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        movies = []
        self._collect_movies(node, prefix, movies)
        return movies
    
    def _collect_movies(self, node, prefix, movies):
        if node.is_end:
            movies.extend(node.movies)
        for child in node.children.values():
            self._collect_movies(child, prefix, movies)

# Binary Search Tree (BST) that organizes movies based on title.
class CatalogueBST:
    def __init__(self, movie, depth=1):
        self.movie = movie
        self.title = movie.title.lower()
        self.depth = depth
        self.left = None
        self.right = None
    
    def insert(self, movie):
        if movie.title.lower() < self.title:
            if self.left is None:
                self.left = CatalogueBST(movie, self.depth+1)
            else:
                self.left.insert(movie)
        else:
            if self.right is None:
                self.right = CatalogueBST(movie, self.depth+1)
            else:
                self.right.insert(movie)
    
    def retrieve(self, movie_name: str):
        if self.title == movie_name.lower():
            return self.movie
        elif movie_name.lower() > self.title and self.right is not None:
            return self.right.retrieve(movie_name)
        elif movie_name.lower() < self.title and self.left is not None:
            return self.left.retrieve(movie_name)
        else:
            return None

# Graph structure to capture similarity links between movies.
class MovieGraph:
    def __init__(self):
        self.movies = {}   # Maps movie_id to Movie
        self.adj_list = {}  # Maps movie_id to dict of neighbor movie_id -> similarity score
	
    def add_movie(self, movie):
        self.movies[movie.movie_id] = movie
        self.adj_list[movie.movie_id] = {}
    
    def add_similarity(self, id1, id2, score):
        if id1 not in self.movies or id2 not in self.movies:
            print("Both movies must exist to add similarity.")
            return
        self.adj_list[id1][id2] = score
        self.adj_list[id2][id1] = score  # Create an undirected link

    def get_movie(self, title):
        normalized_title = title.strip().lower()
        for movie in self.movies.values():
            if movie.title.lower() == normalized_title:
                return movie
        return None

    def get_similar_movies(self, movie_id):
        neighbors = self.adj_list.get(movie_id, {})
        return sorted(neighbors.items(), key=lambda x: x[1], reverse=True)

# Functions for computing the similarity between two movies.
def jaccard_similarity(set1, set2):
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union) if union else 0

def combined_similarity(movie1, movie2, weights=None):
    if weights is None:
        weights = {"genre": 0.5, "actors": 0.3, "director": 0.2}
    genre_sim = jaccard_similarity(movie1.genres, movie2.genres)
    actor_sim = jaccard_similarity(movie1.actors, movie2.actors)
    director_sim = 1.0 if movie1.director == movie2.director else 0.0
    combined = weights["genre"] * genre_sim + weights["actors"] * actor_sim + weights["director"] * director_sim
    return combined

# MovieDatabase builds search structures and loads movie data from CSV.
class MovieDatabase:
    def __init__(self):
        self.bst = None
        self.title_trie = Trie()
        self.genre_tries = defaultdict(Trie)
        self.all_genres = set()
        self.movies = {}  # movie_id -> Movie

    def load_from_csv(self, filename):
        with open(filename, encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            for idx, row in enumerate(reader):
                movie = self._create_movie_object(row, idx)
                self.movies[idx] = movie
                if self.bst is None:
                    self.bst = CatalogueBST(movie)
                else:
                    self.bst.insert(movie)
                self.title_trie.insert(movie.title.lower(), movie)
                for genre in movie.genres:
                    self.genre_tries[genre].insert(movie.title.lower(), movie)
                self.all_genres.update(movie.genres)

    def _create_movie_object(self, movie_data, movie_id):
        title = movie_data['Series_Title'].strip()
        genres = []
        for col in ['genre_1', 'genre_2', 'genre_3']:
            val = movie_data.get(col, '').strip()
            if val and val.lower() != 'none':
                genres.append(val)
        director = movie_data.get('Director', '').strip()
        actors = []
        for col in ['Star1', 'Star2', 'Star3', 'Star4']:
            actor = movie_data.get(col, '').strip()
            if actor:
                actors.append(actor)
        year = movie_data.get('Released_Year', '').strip()
        try:
            rating = float(movie_data.get('IMDB_Rating', 0))
        except:
            rating = 0.0
        runtime = movie_data.get('Runtime', '').strip() if 'Runtime' in movie_data else ""
        return Movie(movie_id, title, genres, director, actors, year, rating, runtime)

    def general_search(self):
        prefix = input("\nEnter the beginning of a movie title: ").lower()
        matching_movies = self.title_trie.search_prefix(prefix)
        if not matching_movies:
            print("No movies found with that prefix.")
            return None
        print("\nMatching movies:")
        for i, movie in enumerate(matching_movies, 1):
            print(f"{i}. {movie.title} ({movie.year}) - Rating: {movie.rating}")
        try:
            choice = input("\nEnter the number of a movie to see details (or press Enter to cancel): ")
            if not choice:
                return None
            selected = matching_movies[int(choice) - 1]
            self.display_movie_details(selected)
            return selected
        except (ValueError, IndexError):
            print("Invalid selection.")
            return None

    def genre_search(self):
        if not self.all_genres:
            print("No genres found in database.")
            return None
        print("\nAvailable genres:")
        sorted_genres = sorted(self.all_genres)
        for i, genre in enumerate(sorted_genres, 1):
            print(f"{i}. {genre}")
        try:
            choice = int(input("\nEnter the number of the genre you want to search: ")) - 1
            selected_genre = sorted_genres[choice]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return None
        genre_movies = self.genre_tries[selected_genre].search_prefix("")
        if not genre_movies:
            print(f"No movies found for genre {selected_genre}.")
            return None
        print(f"\nMovies in '{selected_genre}':")
        for i, movie in enumerate(genre_movies, 1):
            print(f"{i}. {movie.title} ({movie.year}) - Rating: {movie.rating}")
        try:
            choice = input("\nEnter the number of a movie to see details (or press Enter to cancel): ")
            if not choice:
                return None
            selected = genre_movies[int(choice) - 1]
            self.display_movie_details(selected)
            return selected
        except (ValueError, IndexError):
            print("Invalid selection.")
            return None
        
    def search_by_preference(self):
        preferred_director = input("Enter a director's name (or press Enter to skip): ").strip().lower()
        preferred_actor = input("Enter an actor's name (or press Enter to skip): ").strip().lower()
        
        movie_scores = []  # Store tuples (score, movie)

        for movie in self.movies.values():
            score = 0
            if preferred_director and movie.director == preferred_director:
                score += 2
            if preferred_actor and preferred_actor in movie.actors:
                score += 1
            
            if score > 0:
                movie_scores.append((score, movie))

        # Sort the list by score in descending order
        movie_scores.sort(reverse=True, key=lambda x: x[0])

        if movie_scores:
            print("\nTop matching movies:")
            for score, movie in movie_scores:
                print(f"{movie.title} ({movie.year}) - Rating: {movie.rating}")
        else:
            print("No matching movies found.")

    def display_movie_details(self, movie):
        print(f"\nTitle: {movie.title}")
        print(f"Year: {movie.year}")
        print(f"Rating: {movie.rating}")
        print(f"Director: {movie.director}")
        print(f"Actors: {', '.join(movie.actors)}")
        print(f"Genres: {', '.join(movie.genres)}")
        print(f"Runtime: {movie.runtime}")

# The integrated system that brings together the search database and recommendation graph.
class MovieRecommendationSystem:
    def __init__(self, csv_file):
        self.db = MovieDatabase()
        self.db.load_from_csv(csv_file)
        self.graph = MovieGraph()
        # Add every movie from the database to the graph.
        for movie in self.db.movies.values():
            self.graph.add_movie(movie)
        self.build_similarity_graph()

    def build_similarity_graph(self):
        movie_ids = list(self.db.movies.keys())
        n = len(movie_ids)
        for i in range(n):
            for j in range(i + 1, n):
                movie1 = self.db.movies[movie_ids[i]]
                movie2 = self.db.movies[movie_ids[j]]
                sim = combined_similarity(movie1, movie2)
                if sim > 0.1:
                    self.graph.add_similarity(movie1.movie_id, movie2.movie_id, sim)

    def get_recommendations(self):
        title = input("\nEnter the name of the movie for recommendations: ").strip().lower()
        movie = self.graph.get_movie(title)
        if movie:
            print(f"\nRecommendations for: {movie.title}")
            recommendations = self.graph.get_similar_movies(movie.movie_id)
            if not recommendations:
                print("No similar movies found.")
            else:
                for similar_id, score in recommendations[:10]:
                    similar_movie = self.graph.movies[similar_id]
                    print(f"  {similar_movie.title} --> Score: {score:.2f}")
        else:
            print(f"Movie '{title}' not found in the graph.")

    def show_recommendations_for_movie(self, movie):
        print(f"\nRecommendations for: {movie.title}")
        recommendations = self.graph.get_similar_movies(movie.movie_id)
        if recommendations:
            for sim_id, score in recommendations[:10]:
                sim_movie = self.graph.movies[sim_id]
                print(f"  {sim_movie.title} --> Score: {score:.2f}")
        else:
            print("No similar movies found.")

    def main_menu(self):
        while True:
            print("\n===== Movie Recommendation System =====")
            print("1. Search movie by title")
            print("2. Search movie by genre")
            print("3. Get movie recommendations")
            print("4. Search movies by director/actors preference")  # New Option
            print("5. Exit")
            
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                movie = self.db.general_search()
                if movie:
                    rec = input("Would you like to get recommendations for this movie? (y/n): ").strip().lower()
                    if rec == "y":
                        self.show_recommendations_for_movie(movie)
            elif choice == "2":
                movie = self.db.genre_search()
                if movie:
                    rec = input("Would you like to get recommendations for this movie? (y/n): ").strip().lower()
                    if rec == "y":
                        self.show_recommendations_for_movie(movie)
            elif choice == "3":
                self.get_recommendations()
            elif choice == "4":  # Trigger the new preference-based search
                self.db.search_by_preference()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice, please try again.")

def main():
    csv_file = "imdb_top_1000_cleaned.csv"  # Ensure the CSV data file is in the same directory.
    system = MovieRecommendationSystem(csv_file)
    system.main_menu()

if __name__ == "__main__":
    main()