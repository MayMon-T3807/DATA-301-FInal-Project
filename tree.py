import csv
import pandas as pd
from collections import defaultdict

class Movie:
    def __init__(self, movie_id, title, genres, year=None, runtime=None, description=None, 
                 director=None, stars=None, rating=None):
        self.movie_id = movie_id
        self.title = title
        self.genres = set(genres) if genres else set()
        self.year = year
        self.runtime = runtime
        self.description = description
        self.director = director
        self.stars = stars if stars else []
        self.rating = rating
        
    def __repr__(self):
        return f"Movie(ID={self.movie_id}, Title='{self.title}', Genres={self.genres})"

class MovieNode:
    """Node in the MovieBST representing a single movie"""
    def __init__(self, movie, depth=1):
        self.movie = movie
        self.title = self._normalize(movie.title)
        self.depth = depth
        
        self.left = None
        self.right = None
        self.similar_movies = {}  
    
    def _normalize(self, title):
        
        return title.strip().lower()
    
    def add_similarity(self, movie_title, score):
       
        self.similar_movies[movie_title] = score
    
    def get_similar_movies(self):
        """Return similar movies sorted by similarity score"""
        return sorted(self.similar_movies.items(), key=lambda x: x[1], reverse=True)

class MovieBST:
    """Binary Search Tree for storing and retrieving movies"""
    def __init__(self):
        self.root = None
        self.size = 0
        self.title_index = {}  
        self.genre_index = defaultdict(list)  
        
    def _normalize(self, title):
        """Normalize movie titles for consistent comparison"""
        return title.strip().lower()
        
    # CREATE 
    def insert(self, movie):
        """Insert a movie into the BST"""
        if not self.root:
            self.root = MovieNode(movie)
            self.title_index[self._normalize(movie.title)] = self.root
            self._add_to_genre_index(movie)
            self.size += 1
            return
            
        self._insert_recursive(self.root, movie)
        
    def _insert_recursive(self, node, movie, depth=1):
        
        movie_title = self._normalize(movie.title)
        
        if movie_title == node.title:
            node.movie = movie
            return
            
        if movie_title < node.title:
            if node.left is None:
                node.left = MovieNode(movie, depth + 1)
                self.title_index[movie_title] = node.left
                self._add_to_genre_index(movie)
                self.size += 1
            else:
                self._insert_recursive(node.left, movie, depth + 1)
        else:
            if node.right is None:
                node.right = MovieNode(movie, depth + 1)
                self.title_index[movie_title] = node.right
                self._add_to_genre_index(movie)
                self.size += 1
            else:
                self._insert_recursive(node.right, movie, depth + 1)
    
    def _add_to_genre_index(self, movie):
        """Add movie to genre index"""
        for genre in movie.genres:
            self.genre_index[genre].append(movie)
    
    def add_similarity(self, title1, title2, score):
        """Add a similarity relationship between two movies"""
        norm_title1 = self._normalize(title1)
        norm_title2 = self._normalize(title2)
        
        if norm_title1 not in self.title_index or norm_title2 not in self.title_index:
            print("Both movies must exist to add similarity.")
            return False
            
        self.title_index[norm_title1].add_similarity(norm_title2, score)
        self.title_index[norm_title2].add_similarity(norm_title1, score)
        return True
    
    # READ 
    def search(self, title):
        """Search for a movie by title"""
        norm_title = self._normalize(title)
        if norm_title in self.title_index:
            return self.title_index[norm_title].movie
        return None
        
    def get_node(self, title):
        """Get the node containing a movie by title"""
        norm_title = self._normalize(title)
        return self.title_index.get(norm_title)
    
    def get_similar_movies(self, title):
        """Get similar movies to the given title"""
        node = self.get_node(title)
        if not node:
            return []
        
        similar_titles = node.get_similar_movies()
        result = []
        for similar_title, score in similar_titles:
            similar_node = self.get_node(similar_title)
            if similar_node:
                result.append((similar_node.movie, score))
        return result
    
    def get_movies_by_genre(self, genre):
        """Get all movies in a specific genre"""
        return self.genre_index.get(genre, [])
    
    # UPDATE 
    def update_movie(self, title, **kwargs):
        """Update a movie's properties"""
        node = self.get_node(title)
        if not node:
            print(f"Movie '{title}' not found.")
            return False
            
        movie = node.movie
        
        if 'title' in kwargs:
            old_title = self._normalize(movie.title)
            new_title = self._normalize(kwargs['title'])
            
            if old_title != new_title:
                del self.title_index[old_title]
                movie.title = kwargs['title']
                node.title = new_title
                self.title_index[new_title] = node
                
                for similar_title, score in list(node.similar_movies.items()):
                    similar_node = self.get_node(similar_title)
                    if similar_node:
                        del similar_node.similar_movies[old_title]
                        similar_node.similar_movies[new_title] = score
            else:
                movie.title = kwargs['title']  
    
        if 'genres' in kwargs:
            for genre in movie.genres:
                if movie in self.genre_index[genre]:
                    self.genre_index[genre].remove(movie)
            
            movie.genres = set(kwargs['genres'])
            
            for genre in movie.genres:
                self.genre_index[genre].append(movie)
                
        if 'year' in kwargs:
            movie.year = kwargs['year']
        if 'runtime' in kwargs:
            movie.runtime = kwargs['runtime']
        if 'description' in kwargs:
            movie.description = kwargs['description']
        if 'director' in kwargs:
            movie.director = kwargs['director']
        if 'stars' in kwargs:
            movie.stars = kwargs['stars']
        if 'rating' in kwargs:
            movie.rating = kwargs['rating']
            
        return True
    
    # DELETE 
    def delete(self, title):
        """Delete a movie from the BST"""
        norm_title = self._normalize(title)
        
        if norm_title not in self.title_index:
            print(f"Movie '{title}' not found.")
            return False
            
        node_to_delete = self.title_index[norm_title]
        del self.title_index[norm_title]
        
        for genre in node_to_delete.movie.genres:
            if node_to_delete.movie in self.genre_index[genre]:
                self.genre_index[genre].remove(node_to_delete.movie)
        
        for similar_title in node_to_delete.similar_movies:
            similar_node = self.get_node(similar_title)
            if similar_node:
                if norm_title in similar_node.similar_movies:
                    del similar_node.similar_movies[norm_title]
        
        self.root = self._delete_recursive(self.root, norm_title)
        self.size -= 1
        
        return True
        
    def _delete_recursive(self, node, title):
        """Helper method for recursive deletion"""
        if not node: 
            return None
            
        if title < node.title:
            node.left = self._delete_recursive(node.left, title)
        elif title > node.title:
            node.right = self._delete_recursive(node.right, title)
        else:
            if not node.left and not node.right:
                return None
            elif not node.left:
                return node.right
            elif not node.right:
                return node.left
            else:
                successor = self._find_min(node.right)
                node.movie = successor.movie
                node.title = successor.title
                self.title_index[node.title] = node
                node.right = self._delete_recursive(node.right, successor.title)
                
        return node
        
    def _find_min(self, node):
        """Find the leftmost node (minimum value)"""
        current = node
        while current.left:
            current = current.left
        return current
    
    
    def get_all_movies(self):
        """Return a list of all movies in-order"""
        result = []
        self._inorder_traversal(self.root, result)
        return result
        
    def _inorder_traversal(self, node, result):
        """Helper method for inorder traversal"""
        if node:
            self._inorder_traversal(node.left, result)
            result.append(node.movie)
            self._inorder_traversal(node.right, result)
    
    def calculate_jaccard_similarity(self, title1, title2):
        """Calculate Jaccard similarity between two movies based on genres"""
        movie1 = self.search(title1)
        movie2 = self.search(title2)
        
        if not movie1 or not movie2:
            return 0
            
        intersection = movie1.genres.intersection(movie2.genres)
        union = movie1.genres.union(movie2.genres)
        
        return len(intersection) / len(union) if union else 0
    
    def build_similarity_network(self, threshold=0.3):
        """Build similarity relationships between all movies"""
        movies = self.get_all_movies()
        
        for i in range(len(movies)):
            for j in range(i + 1, len(movies)):
                movie1 = movies[i]
                movie2 = movies[j]
                
                sim = self.calculate_jaccard_similarity(movie1.title, movie2.title)
                if sim >= threshold:
                    self.add_similarity(movie1.title, movie2.title, sim)

def load_from_dataframe(df):
    
    bst = MovieBST()
    
    def get_genres(row):
        """Helper function to extract genres from a row"""
        genres = []
        for i in range(1, 4):
            genre_col = f'genre_{i}'
            if genre_col in row and pd.notna(row[genre_col]):
                genres.append(row[genre_col].strip())
        return list(set(genres))  
    
    for idx, row in df.iterrows():
        movie_id = idx
        title = row.get('Series_Title', '').strip()
        genres = get_genres(row)
        year = str(row.get('Released_Year', '')).strip()
        runtime = str(row.get('Runtime', '')).strip()
        description = row.get('Overview', '').strip()
        director = row.get('Director', '').strip()
        
        stars = []
        for i in range(1, 5):
            star_col = f'Star{i}'
            if star_col in row and pd.notna(row[star_col]):
                stars.append(row[star_col].strip())
        
        rating = row.get('IMDB_Rating', None)
        if pd.notna(rating):
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                rating = None
        
        movie = Movie(
            movie_id=movie_id,
            title=title,
            genres=genres,
            year=year,
            runtime=runtime,
            description=description,
            director=director,
            stars=stars,
            rating=rating
        )
        
        bst.insert(movie)
    
    return bst