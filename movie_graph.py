class Movie:
    def __init__(self, movie_id, title, genres):
        self.movie_id = movie_id
        self.title = title
        self.genres = set(genres)

    def __repr__(self):
        return f"Movie(ID={self.movie_id}, Title='{self.title}')"
    
class MovieGraph:
    def __init__(self):
        self.movies = {}  # movie_id -> Movie
        self.adj_list = {}  # movie_id -> {neighbor_id: similarity_score}

    # Normalization titles
    def _normalize(self, title):
        return title.strip().lower()

    # Create
    def add_movie(self, movie):
        key = self._normalize(movie.title)
        self.movies[key] = movie
        self.adj_list[key] = {}

    def add_similarity(self, id1, id2, score):
        if id1 not in self.movies or id2 not in self.movies:
            print("Both movies must exist to add similarity.")
            return
        self.adj_list[id1][id2] = score
        self.adj_list[id2][id1] = score  # Undirected graph

    # Read
    def get_movie(self, title):
        return self.movies.get(self._normalize(title))

    def get_similar_movies(self, movie_id):
        neighbors = self.adj_list.get(movie_id, {})
        return sorted(neighbors.items(), key=lambda x: x[1], reverse=True)

    # Update
    def update_movie(self, movie_id, title=None, genres=None):
        if movie_id not in self.movies:
            print(f"No movie found with ID {movie_id}")
            return
        movie = self.movies[movie_id]
        if title:
            movie.title = title
        if genres:
            movie.genres = set(genres)

    def update_similarity(self, id1, id2, new_score):
        if id1 in self.adj_list and id2 in self.adj_list[id1]:
            self.adj_list[id1][id2] = new_score
            self.adj_list[id2][id1] = new_score
        else:
            print("Similarity link doesn't exist.")

    # Delete
    def delete_movie(self, movie_id):
        if movie_id in self.movies:
            del self.movies[movie_id]
            del self.adj_list[movie_id]
            for neighbors in self.adj_list.values():
                neighbors.pop(movie_id, None)
        else:
            print(f"No movie found with ID {movie_id}")

    def delete_similarity(self, id1, id2):
        self.adj_list.get(id1, {}).pop(id2, None)
        self.adj_list.get(id2, {}).pop(id1, None)
   
import pandas as pd

df = pd.read_csv("imdb_top_1000_cleaned.csv")

def get_genres(row):
    return list(set([row['genre_1'], row['genre_2'], row['genre_3']]))

# Create Movie objects from DataFrame
graph = MovieGraph()

for idx, row in df.iterrows():
    movie_id = idx
    title = row['Series_Title']
    genres = get_genres(row)
    movie = Movie(movie_id, title, genres)
    graph.add_movie(movie)

def jaccard_similarity(set1, set2):
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union) if union else 0

movie_ids = list(graph.movies.keys())

for i in range(len(movie_ids)):
    for j in range(i + 1, len(movie_ids)):
        id1 = movie_ids[i]
        id2 = movie_ids[j]

        genres1 = graph.movies[id1].genres
        genres2 = graph.movies[id2].genres

        sim = jaccard_similarity(genres1, genres2)

        if sim > 0.3:
            graph.add_similarity(id1, id2, sim)

title = (input("Enter the name of the movie you like: "))
movie = graph.get_movie(title)

if movie:
    print(f"Recommendations for: {movie}")
    for similar_title, score in graph.get_similar_movies(title)[:5]:
        print(f"  {graph.get_movie(similar_title)} with similarity {score:.2f}")
else:
    print(f"Movie '{title}' not found in the graph.")
