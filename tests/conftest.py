"""
Pytest configuration and shared fixtures for the AI Movie Discovery Platform tests.
"""

import os
import sys
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config.config_loader import ConfigLoader
from src.services.movie_service import MovieService
from src.services.recommendation_service import RecommendationService
from src.services.movie_preprocessor import MoviePreprocessor
from src.app import create_app


@pytest.fixture
def test_config():
    """Create a test configuration dictionary."""
    return {
        "api": {
            "omdb_api_key": "test-api-key",
            "omdb_base_url": "http://www.omdbapi.com/",
            "timeout": 5,
            "max_retries": 2
        },
        "app": {
            "name": "Test Movie App",
            "version": "1.0.0",
            "debug": True,
            "host": "127.0.0.1",
            "port": 5000,
            "secret_key": "test-secret-key"
        },
        "features": {
            "enable_popular_movies": True,
            "enable_api_endpoints": True,
            "enable_sharing": True,
            "enable_recommendations": True,
            "cache_duration": 3600
        },
        "recommendations": {
            "data_file": "test_movies.csv",
            "max_recommendations": 5,
            "min_similarity_score": 0.1,
            "text_features": ["genres", "keywords", "overview"],
            "tfidf_params": {
                "max_features": 1000,
                "stop_words": "english",
                "ngram_range": [1, 2]
            },
            "processed_data_dir": "test_data/processed"
        },
        "popular_movies": [
            "The Shawshank Redemption",
            "The Godfather",
            "The Dark Knight"
        ],
        "ui": {
            "search_suggestions": [
                "The Shawshank Redemption",
                "Inception",
                "The Dark Knight"
            ]
        }
    }


@pytest.fixture
def temp_config_file(test_config):
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f, indent=2)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def config_loader(temp_config_file):
    """Create a ConfigLoader instance with test configuration."""
    return ConfigLoader(temp_config_file)


@pytest.fixture
def mock_movie_service():
    """Create a mock MovieService for testing."""
    service = Mock(spec=MovieService)
    
    # Mock successful movie response
    service.get_movie_full_details.return_value = {
        "found": True,
        "title": "Test Movie",
        "year": "2023",
        "plot": "A test movie plot",
        "poster": "http://example.com/poster.jpg",
        "imdb_rating": "8.5",
        "genre": "Action, Drama",
        "director": "Test Director",
        "actors": "Test Actor 1, Test Actor 2",
        "runtime": "120 min",
        "imdb_id": "tt1234567"
    }
    
    service.get_movie_details.return_value = ("A test movie plot", "http://example.com/poster.jpg")
    
    service.search_movies_by_title.return_value = {
        "found": True,
        "results": [
            {
                "Title": "Test Movie",
                "Year": "2023",
                "Poster": "http://example.com/poster.jpg",
                "imdbID": "tt1234567",
                "Type": "movie"
            }
        ]
    }
    
    service.get_popular_movies.return_value = [
        {
            "found": True,
            "title": "Test Movie 1",
            "year": "2023",
            "plot": "Test plot 1",
            "poster": "http://example.com/poster1.jpg",
            "genre": "Action, Drama",
            "imdb_rating": "8.5",
            "director": "Test Director",
            "actors": "Test Actor 1, Test Actor 2",
            "runtime": "120 min",
            "imdb_id": "tt1234567"
        },
        {
            "found": True,
            "title": "Test Movie 2",
            "year": "2022",
            "plot": "Test plot 2",
            "poster": "http://example.com/poster2.jpg",
            "genre": "Comedy, Romance",
            "imdb_rating": "7.8",
            "director": "Test Director 2",
            "actors": "Test Actor 3, Test Actor 4",
            "runtime": "110 min",
            "imdb_id": "tt2345678"
        }
    ]
    
    return service


@pytest.fixture
def sample_movie_data():
    """Sample movie data for testing."""
    return {
        "title": ["Movie A", "Movie B", "Movie C"],
        "genres": ["Action|Drama", "Comedy", "Horror|Thriller"],
        "keywords": ["action hero", "funny comedy", "scary monster"],
        "overview": ["An action-packed drama", "A hilarious comedy", "A terrifying horror"],
        "cast": ["Actor A", "Actor B", "Actor C"],
        "director": ["Director A", "Director B", "Director C"]
    }


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def flask_app(config_loader):
    """Create a Flask app instance for testing."""
    with patch('src.config.config_loader.config', config_loader):
        app = create_app()
        app.config['TESTING'] = True
        return app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask app."""
    return flask_app.test_client()


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for API testing."""
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def sample_omdb_response():
    """Sample OMDb API response for testing."""
    return {
        "Title": "Test Movie",
        "Year": "2023",
        "Rated": "PG-13",
        "Released": "01 Jan 2023",
        "Runtime": "120 min",
        "Genre": "Action, Drama",
        "Director": "Test Director",
        "Writer": "Test Writer",
        "Actors": "Test Actor 1, Test Actor 2",
        "Plot": "A comprehensive test movie plot that describes the story.",
        "Language": "English",
        "Country": "USA",
        "Awards": "Test Awards",
        "Poster": "http://example.com/poster.jpg",
        "Ratings": [
            {"Source": "Internet Movie Database", "Value": "8.5/10"},
            {"Source": "Rotten Tomatoes", "Value": "85%"}
        ],
        "Metascore": "75",
        "imdbRating": "8.5",
        "imdbVotes": "100,000",
        "imdbID": "tt1234567",
        "Type": "movie",
        "DVD": "01 Mar 2023",
        "BoxOffice": "$100,000,000",
        "Production": "Test Production",
        "Website": "http://testmovie.com",
        "Response": "True"
    }


@pytest.fixture
def sample_omdb_error_response():
    """Sample OMDb API error response for testing."""
    return {
        "Response": "False",
        "Error": "Movie not found!"
    }


@pytest.fixture
def mock_recommendation_service():
    """Create a mock RecommendationService for testing."""
    service = Mock(spec=RecommendationService)
    
    recommendations_data = [
        {
            "title": "Similar Movie 1",
            "similarity_score": 0.85,
            "genres": "Action, Drama",
            "overview": "A similar action drama"
        },
        {
            "title": "Similar Movie 2",
            "similarity_score": 0.75,
            "genres": "Action",
            "overview": "Another action movie"
        }
    ]

    service.get_movie_recommendations.return_value = recommendations_data
    service.get_enhanced_recommendations.return_value = recommendations_data
    
    service.get_recommendations_by_genre.return_value = [
        {
            "title": "Genre Movie 1",
            "genres": "Action",
            "overview": "An action movie",
            "similarity_score": 1.0
        }
    ]
    
    service.get_available_genres.return_value = ["Action", "Comedy", "Drama", "Horror"]
    
    service.get_dataset_stats.return_value = {
        "total_movies": 100,
        "total_genres": 20,
        "avg_similarity": 0.45
    }
    
    return service


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    
    # Clean up any test files that might have been created
    test_files = [
        "test_movies.csv",
        "test_similarity_matrix.pkl",
        "test_movie_indices.pkl"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.unlink(file)
            except:
                pass
