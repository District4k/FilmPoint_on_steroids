import os
import json
import random
import requests
from flask import Blueprint, jsonify, request
from .models import Movie, Watchlist

API_KEY = 'your_api_key_here'
API_URL = 'https://api.themoviedb.org/3'

regions = {
    "us": "US",
    "india": "IN",
    "europe": "FR",
    "asia": "JP",
    "latam": "BR"
}

genres = {
    "action": 28,
    "comedy": 35,
    "drama": 18,
    "horror": 27,
    "romance": 10749,
    "scifi": 878
}

# Load genres data from the static folder (adjust the path if needed)
genres_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/film_point/genres.json')
with open(genres_file_path, 'r') as f:
    genres_data = json.load(f)

GENRE_MAP = {genre['id']: genre['name'] for genre in genres_data['genres']}

api = Blueprint('api', __name__)


# API endpoint to get movie recommendations
@api.route('/recommendations', methods=['GET'])
def get_movie_recommendations():
    movie_filter = request.args.getlist('filter')  # ['action', '2020-2021', 'us'] passed as query parameters
    if len(movie_filter) < 3:
        return jsonify({"error": "Invalid filter parameters"}), 400

    genre, date_total, region = movie_filter
    recommended_movies = get_film_list_by_filter([genre, date_total, region])
    return jsonify([movie.to_dict() for movie in recommended_movies])


# Function to fetch and transform movie data
def get_film_list_by_filter(movie_filter):
    genre = movie_filter[0]
    date_total = movie_filter[1]
    date_gte = date_total.split('-')[0] + '-01-01'
    date_lte = date_total.split('-')[1] + '-12-31'
    region = movie_filter[2]

    base_url = f"{API_URL}/discover/movie?release_date.gte={date_gte}&release_date.lte={date_lte}&with_genres={genres.get(genre)}"
    if region != "none":
        base_url += f"&region={regions.get(region)}"

    response = requests.get(base_url, headers={'Authorization': f'Bearer {API_KEY}'})

    if response.status_code == 200:
        recommended_movies_json = response.json().get('results', [])
        objects_array = transform_movie_data(recommended_movies_json)
        recommended_movies = random.sample(objects_array, 10)  # Get 10 random movies
    else:
        recommended_movies = []
    return recommended_movies


# Function to transform raw movie data into Movie objects
def transform_movie_data(movie_data):
    movies = []
    for data in movie_data:
        name = data.get("title", "")
        movie_id = data.get("id", "")
        image = data.get("poster_path", "")
        genre_ids = data.get("genre_ids", [])
        genre_names = [GENRE_MAP.get(genre_id, "Unknown") for genre_id in genre_ids]
        genre = ", ".join(map(str, genre_names))
        year = data.get("release_date", "").split("-")[0]
        description = data.get("overview", "")
        rating = data.get("vote_average", 0.0)

        # Create Movie object
        movie = Movie(movie_id=movie_id, name=name, image=image, genre=genre, year=year, description=description,
                      rating=rating)

        # Check if the movie is already in the user's watchlist
        movie.isWatchListed = Watchlist.query.filter_by(user_id=request.user.id, movie_id=movie_id).first() is not None
        movies.append(movie)

    return movies
