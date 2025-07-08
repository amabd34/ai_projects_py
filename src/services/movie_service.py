#!/usr/bin/env python3
"""
Movie service module for handling OMDb API interactions.
Provides clean interface for movie data retrieval and processing.
"""

import requests
import time
import sys
import os
from typing import Dict, Any, Tuple, Optional

# Add the src directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_loader import get_api_key, get_api_url, get_config

class MovieService:
    """Service class for movie data operations."""
    
    def __init__(self):
        """Initialize the movie service."""
        self.api_key = get_api_key()
        self.base_url = get_api_url()
        self.timeout = get_config('api.timeout', 10)
        self.max_retries = get_config('api.max_retries', 3)
        
        if not self.api_key or self.api_key == 'your-api-key-here':
            raise ValueError("❌ OMDb API key not configured. Please set it in config.json")
    
    def get_movie_details(self, title: str) -> Tuple[str, str]:
        """
        Get movie details (plot and poster) - compatible with original function.
        
        Args:
            title (str): Movie title to search for
            
        Returns:
            Tuple[str, str]: (plot, poster_url) or ("N/A", "N/A") if not found
        """
        movie_data = self.get_movie_full_details(title)
        if movie_data["found"]:
            return movie_data["plot"], movie_data["poster"]
        return "N/A", "N/A"
    
    def get_movie_full_details(self, title: str) -> Dict[str, Any]:
        """
        Get comprehensive movie details from OMDb API.
        
        Args:
            title (str): Movie title to search for
            
        Returns:
            Dict[str, Any]: Movie data dictionary with 'found' key indicating success
        """
        params = {
            "t": title,
            "apikey": self.api_key,
            "plot": "full"
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    self.base_url, 
                    params=params, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("Response") == "True":
                    return self._format_movie_data(data)
                else:
                    return {
                        "found": False,
                        "error": data.get("Error", "Movie not found")
                    }
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(1)  # Wait before retry
                    continue
                return {
                    "found": False,
                    "error": "Request timeout - please try again"
                }
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)  # Wait before retry
                    continue
                return {
                    "found": False,
                    "error": f"API Error: {str(e)}"
                }
        
        return {
            "found": False,
            "error": "Failed to fetch movie data after multiple attempts"
        }
    
    def _format_movie_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw OMDb API response into standardized movie data.
        
        Args:
            data (Dict[str, Any]): Raw OMDb API response
            
        Returns:
            Dict[str, Any]: Formatted movie data
        """
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
            "imdb_id": data.get("imdbID", "N/A"),
            "metascore": data.get("Metascore", "N/A"),
            "writer": data.get("Writer", "N/A"),
            "production": data.get("Production", "N/A"),
            "website": data.get("Website", "N/A")
        }
    
    def search_movies_by_title(self, title: str, year: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for movies by title with optional year filter.
        
        Args:
            title (str): Movie title to search for
            year (str, optional): Release year to filter by
            
        Returns:
            Dict[str, Any]: Search results
        """
        params = {
            "s": title,  # 's' parameter for search
            "apikey": self.api_key,
            "type": "movie"
        }
        
        if year:
            params["y"] = year
        
        try:
            response = requests.get(
                self.base_url, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("Response") == "True":
                return {
                    "found": True,
                    "results": data.get("Search", []),
                    "total_results": data.get("totalResults", "0")
                }
            else:
                return {
                    "found": False,
                    "error": data.get("Error", "No movies found")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "found": False,
                "error": f"Search failed: {str(e)}"
            }
    
    def get_movie_by_imdb_id(self, imdb_id: str) -> Dict[str, Any]:
        """
        Get movie details by IMDb ID.
        
        Args:
            imdb_id (str): IMDb ID (e.g., 'tt1375666')
            
        Returns:
            Dict[str, Any]: Movie data
        """
        params = {
            "i": imdb_id,  # 'i' parameter for IMDb ID
            "apikey": self.api_key,
            "plot": "full"
        }
        
        try:
            response = requests.get(
                self.base_url, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("Response") == "True":
                return self._format_movie_data(data)
            else:
                return {
                    "found": False,
                    "error": data.get("Error", "Movie not found")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "found": False,
                "error": f"API Error: {str(e)}"
            }
    
    def get_popular_movies(self, movie_titles: list) -> list:
        """
        Get details for a list of popular movies.
        
        Args:
            movie_titles (list): List of movie titles
            
        Returns:
            list: List of movie data dictionaries
        """
        movies = []
        for title in movie_titles:
            movie_data = self.get_movie_full_details(title)
            if movie_data["found"]:
                movies.append(movie_data)
            # Add small delay to avoid rate limiting
            time.sleep(0.1)
        return movies

# Global movie service instance
movie_service = MovieService()
