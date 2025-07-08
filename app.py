#!/usr/bin/env python3
"""
Flask Movie Search Web Application
Uses OMDb API to search and display movie information
"""

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Your OMDb API key
OMDB_API_KEY = "ecb12403"

def get_movie_details(title, api_key):
    """Get movie details from OMDb API - using your existing function"""
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    res = requests.get(url).json()
    if res.get("Response") == "True":
        result = res.get("Plot", "N/A"), res.get("Poster", "N/A")
        plot = result[0]
        poster = result[1]
        return plot, poster
    else:
        return "N/A", "N/A"

def get_movie_full_details(title, api_key):
    """Enhanced version that gets more movie details for the website"""
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}&plot=full"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("Response") == "True":
            return {
                "found": True,
                "title": data.get("Title", "N/A"),
                "year": data.get("Year", "N/A"),
                "plot": data.get("Plot", "N/A"),
                "poster": data.get("Poster", "N/A"),
                "director": data.get("Director", "N/A"),
                "actors": data.get("Actors", "N/A"),
                "genre": data.get("Genre", "N/A"),
                "runtime": data.get("Runtime", "N/A"),
                "imdb_rating": data.get("imdbRating", "N/A"),
                "released": data.get("Released", "N/A"),
                "rated": data.get("Rated", "N/A"),
                "language": data.get("Language", "N/A"),
                "country": data.get("Country", "N/A"),
                "awards": data.get("Awards", "N/A"),
                "box_office": data.get("BoxOffice", "N/A"),
                "imdb_id": data.get("imdbID", "N/A")
            }
        else:
            return {
                "found": False,
                "error": data.get("Error", "Movie not found")
            }
    except Exception as e:
        return {
            "found": False,
            "error": f"API Error: {str(e)}"
        }

@app.route('/')
def home():
    """Home page with search form"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_movie():
    """Handle movie search"""
    movie_title = request.form.get('movie_title', '').strip()
    
    if not movie_title:
        return render_template('index.html', error="Please enter a movie title")
    
    # Get movie details
    movie_data = get_movie_full_details(movie_title, OMDB_API_KEY)
    
    if movie_data["found"]:
        return render_template('movie_details.html', movie=movie_data)
    else:
        return render_template('index.html', 
                             error=f"Movie '{movie_title}' not found. {movie_data.get('error', '')}")

@app.route('/api/search/<movie_title>')
def api_search(movie_title):
    """API endpoint for movie search (JSON response)"""
    movie_data = get_movie_full_details(movie_title, OMDB_API_KEY)
    return jsonify(movie_data)

@app.route('/popular')
def popular_movies():
    """Show some popular movies"""
    popular_titles = [
        "The Shawshank Redemption",
        "The Godfather", 
        "The Dark Knight",
        "Pulp Fiction",
        "Forrest Gump",
        "Inception",
        "The Matrix",
        "Goodfellas",
        "The Lord of the Rings: The Return of the King",
        "Fight Club"
    ]
    
    movies = []
    for title in popular_titles:
        movie_data = get_movie_full_details(title, OMDB_API_KEY)
        if movie_data["found"]:
            movies.append(movie_data)
    
    return render_template('popular.html', movies=movies)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
