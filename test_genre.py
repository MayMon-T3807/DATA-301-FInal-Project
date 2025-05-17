import csv
from collections import defaultdict

class Movie:
    def __init__(self, movie_id, title, genres, year=None, rating=None, director=None, stars=None, runtime=None, description=None):
        self.movie_id = movie_id
        self.title = title
        self.genres = set(genres) if genres else set()
        self.year = year
        self.rating = rating
        self.director = director
        self.stars = stars if stars else []

        
    def __repr__(self):
        return f"Movie(ID={self.movie_id}, Title='{self.title}', Genres={self.genres}, Rating={self.rating})"

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.movies = []

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
        for char, child_node in node.children.items():
            self._collect_movies(child_node, prefix + char, movies)

class MovieDatabase:
    def __init__(self):
        self.bst = None
        self.genre_tries = defaultdict(Trie)
        self.title_trie = Trie()
        self.all_genres = set()
    
    def load_from_csv(self, filename):
        with open(filename, encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            movies = list(reader)
        
        # Initialize BST with first movie
        first_movie = self._create_movie_object(movies[0], 0)
        self.bst = catalogue_BST(first_movie)
        self._add_to_tries(first_movie)
        
        # Process remaining movies
        for idx in range(1, len(movies)):
            movie = self._create_movie_object(movies[idx], idx)
            self.bst.insert(movie)
            self._add_to_tries(movie)
    
    def _create_movie_object(self, movie_data, movie_id):
        genres = []
        for i in range(1, 4):
            genre_col = f'genre_{i}'
            if genre_col in movie_data and movie_data[genre_col].lower() != 'none':
                genres.append(movie_data[genre_col].strip())
    
        stars = []
        for i in range(1, 5):
            star_col = f'Star{i}'
            if star_col in movie_data:
                stars.append(movie_data[star_col].strip())
        
        self.all_genres.update(genres)
        
        return Movie(
            movie_id=movie_id,
            title=movie_data['Series_Title'].strip(),
            genres=genres,
            year=movie_data.get('Released_Year', '').strip(),
            rating=float(movie_data.get('IMDB_Rating', 0)),
            director=movie_data.get('Director', '').strip(),
            stars=stars,
            runtime=movie_data.get('Runtime', '').strip(),  
        )
    
    def _add_to_tries(self, movie):
        self.title_trie.insert(movie.title.lower(), movie)
        
        for genre in movie.genres:
            self.genre_tries[genre].insert(movie.title.lower(), movie)
    
    def genre_search(self):
        if not self.all_genres:
            print("No genres found in database.")
            return
        
        print("\nAvailable genres:")
        sorted_genres = sorted(self.all_genres)
        for i, genre in enumerate(sorted_genres, 1):
            print(f"{i}. {genre}")
        
        try:
            choice = int(input("\nEnter the number of the genre you want to search: ")) - 1
            selected_genre = sorted_genres[choice]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return
        
        genre_movies = self.genre_tries[selected_genre].search_prefix("")
        print(f"\nMovies in '{selected_genre}':")
        for i, movie in enumerate(genre_movies, 1):
            print(f"{i}. {movie.title} ({movie.year}) - Rating: {movie.rating}")
        
        self._handle_movie_selection(genre_movies)
    
    def general_search(self):
        prefix = input("\nEnter the beginning of a movie title: ").lower()
        matching_movies = self.title_trie.search_prefix(prefix)
        
        if not matching_movies:
            print("No movies found with that prefix.")
            return
        
        print("\nMatching movies:")
        for i, movie in enumerate(matching_movies, 1):
            print(f"{i}. {movie.title} ({movie.year}) - Rating: {movie.rating}")
        
        self._handle_movie_selection(matching_movies)
    
    def _handle_movie_selection(self, movies):
        if not movies:
            return
        
        try:
            choice = input("\nEnter the number of a movie to see details (or press Enter to skip): ")
            if not choice:
                return
            
            movie = movies[int(choice)-1]
            print(f"\nTitle: {movie.title}")
            print(f"Year: {movie.year}")
            print(f"Rating: {movie.rating}")
            print(f"Director: {movie.director}")
            print(f"Stars: {', '.join(movie.stars)}")
            print(f"Genres: {', '.join(movie.genres)}")
            print(f"Runtime: {movie.runtime}")
            print(f"Description: {movie.description}")
        except (ValueError, IndexError):
            print("Invalid selection.")

class catalogue_BST:
    def __init__(self, movie, depth=1):
        self.movie = movie
        self.title = movie.title.lower()
        self.depth = depth
        self.left = None
        self.right = None
    
    def insert(self, movie):
        if movie.title.lower() < self.title:
            if self.left is None:
                self.left = catalogue_BST(movie, self.depth+1)
            else:
                self.left.insert(movie)
        else:
            if self.right is None:
                self.right = catalogue_BST(movie, self.depth+1)
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

def main():
    db = MovieDatabase()
    db.load_from_csv("imdb_top_1000_cleaned.csv")
    
    while True:
        print("\n===== Movie Search =====")
        print("1. Search by Genre")
        print("2. General Search")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            db.genre_search()
        elif choice == "2":
            db.general_search()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()