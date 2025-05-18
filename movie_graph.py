class Movie:
    def __init__(self, movie_id, title, genres, director, actors):
        self.movie_id = movie_id
        self.title = title
        self.genres = set(genres)
        self.director = director.strip().lower()
        self.actors = set(actor.strip().lower() for actor in actors)

    def __repr__(self):
        return f"Movie(Title='{self.title}')"
    
class MovieGraph:
    def __init__(self):
        self.movies = {}  # movie_id -> Movie
        self.adj_list = {}  # movie_id -> {neighbor_id: similarity_score}

    def add_movie(self, movie):
        self.movies[movie.movie_id] = movie
        self.adj_list[movie.movie_id] = {}  # Store IDs, not titles

    def add_similarity(self, id1, id2, score):
        if id1 not in self.movies or id2 not in self.movies:
            print("Both movies must exist to add similarity.")
            return
        self.adj_list[id1][id2] = score
        self.adj_list[id2][id1] = score  # Undirected graph

    def get_movie(self, title):
        normalized_title = title.strip().lower()
        for movie in self.movies.values():
            if movie.title.lower() == normalized_title:
                return movie
        return None  # If not found

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

# Import Movie Dataset from CSV with Pandas   
import pandas as pd

df = pd.read_csv("imdb_top_1000_cleaned.csv")

def get_genres(row):
    return list(set([row['genre_1'], row['genre_2'], row['genre_3']]))

# Create Movie objects from DataFrame
graph = MovieGraph()

for idx, row in df.iterrows():
    title = row['Series_Title']
    genres = get_genres(row)
    director = row["Director"]
    actors = [row["Star1"], row["Star2"], row["Star3"], row["Star4"]]
    movie = Movie(idx, title, genres, director, actors)
    graph.add_movie(movie)

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

    combined = (
        weights["genre"] * genre_sim +
        weights["actors"] * actor_sim +
        weights["director"] * director_sim
    )
    return combined

titles = list(graph.movies.keys())

for i in range(len(titles)):
    for j in range(i + 1, len(titles)):
        id1 = titles[i]
        id2 = titles[j]

        movie1 = graph.movies[id1]
        movie2 = graph.movies[id2]
        sim = combined_similarity(movie1, movie2)

        if sim > 0.1:
            graph.add_similarity(id1, id2, sim)

title = input("Enter the name of the movie you like: ").strip().lower()
movie = graph.get_movie(title)

if movie:
    print(f"Recommendations for:{movie}")
    for similar_key, score in graph.get_similar_movies(movie.movie_id)[:10]:
        print(f"  {graph.movies[similar_key].title} --> {score:.2f}")
else:
    print(f"Movie '{title}' not found in the graph.")