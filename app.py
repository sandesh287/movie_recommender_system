import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os


# ------------------ Functions ------------------
TMDB_API_KEY = "0a74517ffa4d47aca8220baa2960e2f9"

# Function to fetch API
def fetch_movie_details(movie_id):
  url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US'
  
  response = requests.get(url)
  data = response.json()
  
  # Return poster, overview, rating
  poster = "https://via.placeholder.com/300x450?text=No+Image"
  overview = "No overview available."
  rating = "N/A"
  genres = "N/A"
  year = "N/A"
  
  if data.get('poster_path'):
    poster = "https://image.tmdb.org/t/p/original/" + data['poster_path']
  if data.get('overview'):
    overview = data['overview']
  if data.get('vote_average'):
    rating = data['vote_average']
  if data.get('genres'):
    genres = ", ".join([g['name'] for g in data['genres']])
  if data.get('release_date'):
    year = data['release_date'][:4]
  
  return poster, overview, rating, genres, year


# Function to recommend movies
def recommend(movie):
  movie_index = movies[movies['title'] == movie].index[0]
  distances = similarity[movie_index]
  movies_list = sorted(list(enumerate(distances)),reverse=True, key=lambda x:x[1])[1:6]

  results = []
  
  for i in movies_list:
    movie_data = movies.iloc[i[0]]
    
    movie_id = movie_data.movie_id
    
    poster, overview, rating, genres, year = fetch_movie_details(movie_id)
    
    results.append({
      "title": movie_data.title,
      "poster": poster,
      "overview": overview,
      "rating": rating,
      "genres": genres,
      "year": year
    })
  
  return results


# ------------------ Load Data ------------------

# Google Drive file ID
file_id = "10XwJrs0qGCHQB4_UGlm7g5oATdwc5EtS"
file_name = "similarity.pkl"

# Download only if not exists
if not os.path.exists(file_name):
  print("Downloading similarity.pkl...")
  url = f"https://drive.google.com/uc?id={file_id}"
  gdown.download(url, file_name, quiet=False)
else:
  print("similarity.pkl already exists, using local file.")

# Load the pickle
with open(file_name, "rb") as f:
    similarity = pickle.load(f)


# Load Data from local device
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
# similarity = pickle.load(open('similarity.pkl', 'rb'))


# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title('🎬 Movie Recommender System')
st.write("Discover movies like your favorites 🍿")


movie_list = movies['title'].values.tolist()

selected_movie = st.selectbox(
  "🎬 Choose a movie:",
  movies['title'].values,
  index=None,
  placeholder="Start typing to search..."
)


# ------------------ Custom CSS for cards ------------------
st.markdown("""
<style>
.movie-card {
  background: linear-gradient(to bottom, transparent, rgba(123, 31, 162, 0.8));
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-align: center;
  height: 500px;
}
.movie-card:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}

.image-container{
  display: flex;
  justify-content: center;
}

.image-container img{
  border-radius: 8px;
}

.movie-title {
  font-size: 16px;
  font-weight: 600;
  color: #f1e9ff;
  margin-top: 8px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.4);
  
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.movie-meta {
  font-size: 13px;
  color: #d1c4e9;
  text-shadow: 0 1px 3px rgba(0,0,0,0.4);
  
  display: -webkit-box;
  -webkit-line-clamp: 1;   /* 🔥 prevent overflow */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.movie-overview {
  font-size: 12px;
  color: #cbbde2;
  margin-top: 8px;
  padding-top: 8px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.4);
  
  background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);

  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


# ------------------ Recommendation Display ------------------
if st.button("🎯 Recommend"):
  results = recommend(selected_movie)
  
  st.subheader("✨ Recommended Movies for you")
  
  # Dynamic columns: mobile-friendly
  cols_per_row = 5  # desktop
  rows = [results[i:i + cols_per_row] for i in range(0, len(results), cols_per_row)]

  for row in rows:
    cols = st.columns(len(row))

    for idx, movie in enumerate(row):
      with cols[idx]:
        st.markdown(
          f"""
          <div class="movie-card">
            <div class="image-container">
              <img src="{movie['poster']}" width="180">
            </div>
            
            <div class="movie-title">{movie['title']}</div>
            
            <div class="movie-meta">
                ⭐ {movie['rating']} | {movie['year']}
            </div>
            
            <div class="movie-meta">
                {movie['genres']}
            </div>

            <div class="movie-overview">
                {movie['overview']}
            </div>
          </div>
          """,
          unsafe_allow_html=True
        )