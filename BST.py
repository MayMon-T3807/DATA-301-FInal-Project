import pandas as pd

class Movie:
    def __init__(self, movie_id, title, genres, year=None, rating=None, 
                 director=None, stars=None, runtime=None, description=None):
        self.movie_id = movie_id
        self.title = title
        self.genres = set(genres) if genres else set()
        self.year = year
        self.rating = rating
        self.director = director
        self.stars = stars if stars else []
        self.runtime = runtime
        self.description = description
        
    def __repr__(self):
        return f"Movie(ID={self.movie_id}, Title='{self.title}', Genres={self.genres}, Rating={self.rating})"

class MovieNode:
    def __init__(self, movie, depth=1):
        self.movie = movie
        self.title = self._normalize(movie.title)
        self.depth = depth
        self.left = None
        self.right = None
    
    def _normalize(self, title):
        return title.strip().lower()

class MovieBST:
    def __init__(self):
        self.root = None
        self.size = 0
        self.title_index = {}  
        self.genre_index = {}  # Changed from defaultdict to regular dict
        
    def _normalize(self, title):
        return title.strip().lower()
        
    def _add_to_genre_index(self, movie):
        """Manually handle genre indexing without defaultdict"""
        for genre in movie.genres:
            if genre not in self.genre_index:
                self.genre_index[genre] = []
            self.genre_index[genre].append(movie)
        
    def insert(self, movie):
        if not self.root:
            self.root = MovieNode(movie)
            self.title_index[self._normalize(movie.title)] = self.root
            self._add_to_genre_index(movie)  # Use manual genre indexing
            self.size += 1
            return
        self._insert_recursive(self.root, movie)
    
    def _insert_recursive(self, node, movie, depth=1):
        norm_title = self._normalize(movie.title)
        
        if norm_title == node.title:
            node.movie = movie
            return
            
        if norm_title < node.title:
            if node.left is None:
                node.left = MovieNode(movie, depth + 1)
                self.title_index[norm_title] = node.left
                self._add_to_genre_index(movie)
                self.size += 1
            else:
                self._insert_recursive(node.left, movie, depth + 1)
        else:
            if node.right is None:
                node.right = MovieNode(movie, depth + 1)
                self.title_index[norm_title] = node.right
                self._add_to_genre_index(movie)
                self.size += 1
            else:
                self._insert_recursive(node.right, movie, depth + 1)
    
    def search(self, title):
        return self.title_index.get(self._normalize(title))
    
    def get_movies_by_genre(self, genre):
        return self.genre_index.get(genre, [])  # Returns empty list if genre doesn't exist
    
    def update_movie(self, title, **kwargs):
        movie = self.search(title)
        if not movie:
            print(f"Movie '{title}' not found.")
            return False
            
        if 'title' in kwargs:
            old_title = self._normalize(movie.title)
            new_title = self._normalize(kwargs['title'])
            if old_title != new_title:
                del self.title_index[old_title]
                movie.title = kwargs['title']
                self.title_index[new_title] = movie
    
        if 'genres' in kwargs:
            for genre in movie.genres:
                if genre in self.genre_index and movie in self.genre_index[genre]:
                    self.genre_index[genre].remove(movie)
            
            
            movie.genres = set(kwargs['genres'])
            
           
            for genre in movie.genres:
                if genre not in self.genre_index:
                    self.genre_index[genre] = []
                self.genre_index[genre].append(movie)
                
        for attr in ['year', 'rating', 'director', 'stars', 'runtime', 'description']:
            if attr in kwargs:
                setattr(movie, attr, kwargs[attr])
                
        return True
    
    def delete(self, title):
        norm_title = self._normalize(title)
        if norm_title not in self.title_index:
            print(f"Movie '{title}' not found.")
            return False
            
        movie = self.title_index[norm_title]
        del self.title_index[norm_title]
        
        # Remove from genre index
        for genre in movie.genres:
            if genre in self.genre_index and movie in self.genre_index[genre]:
                self.genre_index[genre].remove(movie)
        
        # Update BST structure
        self.root = self._delete_recursive(self.root, norm_title)
        self.size -= 1
        return True
        
    def _delete_recursive(self, node, title):
        if not node: 
            return None
            
        if title < node.title:
            node.left = self._delete_recursive(node.left, title)
        elif title > node.title:
            node.right = self._delete_recursive(node.right, title)
        else:
            if not node.left: 
                return node.right
            if not node.right: 
                return node.left
                
            successor = self._find_min(node.right)
            node.movie = successor.movie
            node.title = successor.title
            self.title_index[node.title] = node.movie
            node.right = self._delete_recursive(node.right, successor.title)
                
        return node
        
    def _find_min(self, node):
        current = node
        while current.left:
            current = current.left
        return current

def load_from_dataframe(df):
    """Load movies from DataFrame with exact column matching"""
    bst = MovieBST()
    
    for idx, row in df.iterrows():
        movie = Movie(
            movie_id=idx,
            title=row['Series_Title'].strip(),
            genres=[row[f'genre_{i}'].strip() for i in range(1,4) 
                   if f'genre_{i}' in row and pd.notna(row[f'genre_{i}'])],
            year=str(row['Released_Year']).strip(),
            rating=float(row['IMDB_Rating']) if pd.notna(row['IMDB_Rating']) else None,
            director=row['Director'].strip(),
            stars=[row[f'Star{i}'].strip() for i in range(1,5) 
                 if f'Star{i}' in row and pd.notna(row[f'Star{i}'])]
        )
        bst.insert(movie)
    
    return bst