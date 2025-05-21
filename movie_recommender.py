import csv
from collections import defaultdict

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
        self._collect_movies(node, movies)
        return movies
    
    def _collect_movies(self, node, movies):
        if node.is_end:
            movies.extend(node.movies)
        for child in node.children.values():
            self._collect_movies(child, movies)

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
                self.left = CatalogueBST(movie, self.depth + 1)
            else:
                self.left.insert(movie)
        else:
            if self.right is None:
                self.right = CatalogueBST(movie, self.depth + 1)
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

class MovieGraph:
    def __init__(self):
        self.movies = {}    # movie_id -> Movie
        self.adj_list = {}  # movie_id -> {neighbor_id: similarity_score}
    
    def add_movie(self, movie):
        self.movies[movie.movie_id] = movie
        self.adj_list[movie.movie_id] = {}
    
    def add_similarity(self, id1, id2, score):
        if id1 not in self.movies or id2 not in self.movies:
            print("Both movies must exist to add similarity.")
            return
        self.adj_list[id1][id2] = score
        self.adj_list[id2][id1] = score  # undirected relationship

    def get_movie(self, title):
        normalized_title = title.strip().lower()
        for movie in self.movies.values():
            if movie.title.lower() == normalized_title:
                return movie
        return None

    def get_similar_movies(self, movie_id):
        neighbors = self.adj_list.get(movie_id, {})
        return sorted(neighbors.items(), key=lambda x: x[1], reverse=True)

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
    return weights["genre"] * genre_sim + weights["actors"] * actor_sim + weights["director"] * director_sim

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
        for key in ['genre_1', 'genre_2', 'genre_3']:
            val = movie_data.get(key, '').strip()
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

class MovieRecommendationSystem:
    def __init__(self, csv_file):
        self.db = MovieDatabase()
        self.db.load_from_csv(csv_file)
        self.graph = MovieGraph()
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
                if sim > 0.1:  # threshold to decide if two movies are similar
                    self.graph.add_similarity(movie1.movie_id, movie2.movie_id, sim)