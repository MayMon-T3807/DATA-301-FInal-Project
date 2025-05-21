import streamlit as st
from movie_recommender import MovieRecommendationSystem

# Cache the system instance to avoid reloading on every refresh
@st.cache_resource
def load_system():
    csv_file = "imdb_top_1000_cleaned.csv"  # Ensure the CSV file is in the same directory
    system = MovieRecommendationSystem(csv_file)
    return system

# Load the system
system = load_system()

st.title("IMDB's Movie Recommendation System")
st.write("*By May Mon Thant & Thant Thaw Tun*")
st.video("film_loop.mp4")  

# Sidebar: choose an action
action = st.sidebar.radio("Choose an action", ["Search by Title", "Search by Genre", "Get Recommendations", "Search by Preferences"])

if action == "Search by Title":
    st.header("Search Movie by Title")
    title_prefix = st.text_input("Enter the beginning of a movie title")
    if title_prefix:
        matching_movies = system.db.title_trie.search_prefix(title_prefix.lower())
        if matching_movies:
            movie_options = [f"{movie.title} ({movie.year})" for movie in matching_movies]
            chosen = st.selectbox("Select a movie", movie_options)
            selected_movie = next((m for m in matching_movies if f"{m.title} ({m.year})" == chosen), None)
            if selected_movie:
                st.subheader("Movie Details")
                st.write(f"**Title:** {selected_movie.title}")
                st.write(f"**Year:** {selected_movie.year}")
                st.write(f"**Rating:** {selected_movie.rating}")
                st.write(f"**Director:** {selected_movie.director}")
                st.write(f"**Actors:** {', '.join(selected_movie.actors)}")
                st.write(f"**Genres:** {', '.join(selected_movie.genres)}")
                if st.button("Get Recommendations for this movie"):
                    recs = system.graph.get_similar_movies(selected_movie.movie_id)
                    if recs:
                        st.subheader("Recommendations")
                        for sim_id, score in recs[:10]:
                            sim_movie = system.graph.movies[sim_id]
                            st.markdown(f"""
                            **Title:** {sim_movie.title}  
                            **Year:** {sim_movie.year}  
                            **Rating:** {sim_movie.rating}  
                            **Director:** {sim_movie.director.capitalize()}  
                            **Actors:** {', '.join(actor.capitalize() for actor in sim_movie.actors)}  
                            **Genres:** {', '.join(sim_movie.genres)}  
                            **Similarity Score:** {score:.2f}
                            """)
                            st.markdown("---")  # This adds a horizontal line separator
                    else:
                        st.write("No recommendations found.")
        else:
            st.write("No movies found with that title prefix.")

elif action == "Search by Genre":
    st.header("Search Movies by Genre")
    genres = sorted(system.db.all_genres)
    selected_genre = st.selectbox("Select a genre", genres)
    if selected_genre:
        movies_in_genre = system.db.genre_tries[selected_genre].search_prefix("")
        if movies_in_genre:
            movie_options = [f"{movie.title} ({movie.year})" for movie in movies_in_genre]
            chosen = st.selectbox("Select a movie", movie_options)
            selected_movie = next((m for m in movies_in_genre if f"{m.title} ({m.year})" == chosen), None)
            if selected_movie:
                st.subheader("Movie Details")
                st.write(f"**Title:** {selected_movie.title}")
                st.write(f"**Year:** {selected_movie.year}")
                st.write(f"**Rating:** {selected_movie.rating}")
                st.write(f"**Director:** {selected_movie.director}")
                st.write(f"**Actors:** {', '.join(selected_movie.actors)}")
                st.write(f"**Genres:** {', '.join(selected_movie.genres)}")
                if st.button("Get Recommendations for this movie"):
                    recs = system.graph.get_similar_movies(selected_movie.movie_id)
                    if recs:
                        st.subheader("Recommendations")
                        for sim_id, score in recs[:10]:
                            sim_movie = system.graph.movies[sim_id]
                            st.markdown(f"""
                            **Title:** {sim_movie.title}  
                            **Year:** {sim_movie.year}  
                            **Rating:** {sim_movie.rating}  
                            **Director:** {sim_movie.director.capitalize()}  
                            **Actors:** {', '.join(actor.capitalize() for actor in sim_movie.actors)}  
                            **Genres:** {', '.join(sim_movie.genres)}  
                            **Similarity Score:** {score:.2f}
                            """)
                            st.markdown("---") 
                    else:
                        st.write("No recommendations found.")
        else:
            st.write("No movies found in this genre.")

elif action == "Get Recommendations":
    st.header("Get Recommendations by Movie Title")
    movie_title = st.text_input("Enter the full movie title for recommendations").strip().lower()
    if movie_title:
        movie = system.graph.get_movie(movie_title)
        if movie:
            st.subheader(f"Recommendations for {movie.title}:")
            recs = system.graph.get_similar_movies(movie.movie_id)
            if recs:
                st.subheader("Recommendations")
                for sim_id, score in recs[:10]:
                    sim_movie = system.graph.movies[sim_id]
                    st.markdown(f"""
                    **Title:** {sim_movie.title}  
                    **Year:** {sim_movie.year}  
                    **Rating:** {sim_movie.rating}  
                    **Director:** {sim_movie.director.capitalize()}  
                    **Actors:** {', '.join(actor.capitalize() for actor in sim_movie.actors)}  
                    **Genres:** {', '.join(sim_movie.genres)}  
                    **Similarity Score:** {score:.2f}
                    """)
                    st.markdown("---") 
            else:
                st.write("No recommendations found.")
        else:
            st.write("Movie not found in the system.")

elif action == "Search by Preferences":
    preferred_director = st.text_input("Enter your favorite director (optional):").strip().lower()
    preferred_actor = st.text_input("Enter your favorite actor (optional):").strip().lower()

    if preferred_director or preferred_actor:
        movie_scores = []  # Store (score, movie) tuples
        for movie in system.db.movies.values():
            score = 0
            if preferred_director and movie.director == preferred_director:
                score += 2
            if preferred_actor and preferred_actor in movie.actors:
                score += 1
            
            if score > 0:
                movie_scores.append((score, movie))
        
        movie_scores.sort(reverse=True, key=lambda x: x[0])  # Sort by priority
        st.subheader("Top Matches Based on Preferences")
        for score, movie in movie_scores[:10]:  # Show top 10
            st.write(f"{movie.title} ({movie.year}) - {movie.rating}")

