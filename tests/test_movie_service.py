"""
Comprehensive tests for MovieService.
Tests OMDb API interactions, error handling, rate limiting, and data formatting.
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import time

from src.services.movie_service import MovieService


class TestMovieService:
    """Test suite for MovieService class."""
    
    def test_init_success(self):
        """Test successful MovieService initialization."""
        with patch('src.services.movie_service.get_api_key', return_value='test-key'), \
             patch('src.services.movie_service.get_api_url', return_value='http://test.com'), \
             patch('src.services.movie_service.get_config') as mock_config:
            
            mock_config.side_effect = lambda key, default: {
                'api.timeout': 10,
                'api.max_retries': 3
            }.get(key, default)
            
            service = MovieService()
            assert service.api_key == 'test-key'
            assert service.base_url == 'http://test.com'
            assert service.timeout == 10
            assert service.max_retries == 3
    
    def test_init_missing_api_key(self):
        """Test MovieService initialization with missing API key."""
        with patch('src.services.movie_service.get_api_key', return_value=None):
            with pytest.raises(ValueError, match="OMDb API key not configured"):
                MovieService()
    
    def test_init_placeholder_api_key(self):
        """Test MovieService initialization with placeholder API key."""
        with patch('src.services.movie_service.get_api_key', return_value='your-api-key-here'):
            with pytest.raises(ValueError, match="OMDb API key not configured"):
                MovieService()
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_get_movie_details_success(self, mock_config, mock_url, mock_key, sample_omdb_response):
        """Test successful movie details retrieval."""
        mock_config.side_effect = lambda key, default: default
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_omdb_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            service = MovieService()
            plot, poster = service.get_movie_details("Test Movie")
            
            assert plot == "A comprehensive test movie plot that describes the story."
            assert poster == "http://example.com/poster.jpg"
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_get_movie_details_not_found(self, mock_config, mock_url, mock_key, sample_omdb_error_response):
        """Test movie details retrieval when movie not found."""
        mock_config.side_effect = lambda key, default: default
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_omdb_error_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            service = MovieService()
            plot, poster = service.get_movie_details("Nonexistent Movie")
            
            assert plot == "N/A"
            assert poster == "N/A"
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_get_movie_full_details_success(self, mock_config, mock_url, mock_key, sample_omdb_response):
        """Test successful full movie details retrieval."""
        mock_config.side_effect = lambda key, default: default
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_omdb_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            service = MovieService()
            result = service.get_movie_full_details("Test Movie")
            
            assert result["found"] is True
            assert result["title"] == "Test Movie"
            assert result["year"] == "2023"
            assert result["plot"] == "A comprehensive test movie plot that describes the story."
            assert result["poster"] == "http://example.com/poster.jpg"
            assert result["imdb_rating"] == "8.5"
            assert result["genre"] == "Action, Drama"
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_get_movie_full_details_api_error(self, mock_config, mock_url, mock_key):
        """Test movie details retrieval with API error."""
        mock_config.side_effect = lambda key, default: default
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("API Error")
            
            service = MovieService()
            result = service.get_movie_full_details("Test Movie")
            
            assert result["found"] is False
            assert "API Error" in result["error"]
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_search_movies_by_title_success(self, mock_config, mock_url, mock_key):
        """Test successful movie search by title."""
        mock_config.side_effect = lambda key, default: default
        
        search_response = {
            "Search": [
                {
                    "Title": "Test Movie",
                    "Year": "2023",
                    "imdbID": "tt1234567",
                    "Type": "movie",
                    "Poster": "http://example.com/poster.jpg"
                }
            ],
            "totalResults": "1",
            "Response": "True"
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = search_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            service = MovieService()
            result = service.search_movies_by_title("Test")
            
            assert result["found"] is True
            assert len(result["results"]) == 1
            assert result["results"][0]["Title"] == "Test Movie"
            assert result["total_results"] == "1"
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_search_movies_by_title_no_results(self, mock_config, mock_url, mock_key):
        """Test movie search with no results."""
        mock_config.side_effect = lambda key, default: default
        
        search_response = {
            "Response": "False",
            "Error": "Movie not found!"
        }
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = search_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            service = MovieService()
            result = service.search_movies_by_title("Nonexistent")
            
            assert result["found"] is False
            assert result["error"] == "Movie not found!"
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_get_movie_by_imdb_id_success(self, mock_config, mock_url, mock_key, sample_omdb_response):
        """Test successful movie retrieval by IMDb ID."""
        mock_config.side_effect = lambda key, default: default
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = sample_omdb_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            service = MovieService()
            result = service.get_movie_by_imdb_id("tt1234567")
            
            assert result["found"] is True
            assert result["title"] == "Test Movie"
            assert result["imdb_id"] == "tt1234567"
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_get_popular_movies_success(self, mock_config, mock_url, mock_key, sample_omdb_response):
        """Test successful popular movies retrieval."""
        mock_config.side_effect = lambda key, default: default
        
        with patch('requests.get') as mock_get, \
             patch('time.sleep') as mock_sleep:
            
            mock_response = Mock()
            mock_response.json.return_value = sample_omdb_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            service = MovieService()
            movie_titles = ["Test Movie 1", "Test Movie 2"]
            result = service.get_popular_movies(movie_titles)
            
            assert len(result) == 2
            assert all(movie["found"] for movie in result)
            # Verify rate limiting sleep was called
            assert mock_sleep.call_count == 2
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_retry_mechanism(self, mock_config, mock_url, mock_key, sample_omdb_response):
        """Test retry mechanism for failed requests."""
        mock_config.side_effect = lambda key, default: {
            'api.timeout': 5,
            'api.max_retries': 3
        }.get(key, default)

        with patch('requests.get') as mock_get, \
             patch('time.sleep') as mock_sleep:

            # First two calls fail, third succeeds
            mock_get.side_effect = [
                requests.exceptions.RequestException("Network error"),
                requests.exceptions.RequestException("Network error"),
                Mock(json=lambda: sample_omdb_response, raise_for_status=lambda: None)
            ]

            service = MovieService()
            result = service.get_movie_full_details("Test Movie")

            assert result["found"] is True
            assert mock_get.call_count == 3
            assert mock_sleep.call_count == 2  # Sleep between retries
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_retry_exhausted(self, mock_config, mock_url, mock_key):
        """Test behavior when all retries are exhausted."""
        mock_config.side_effect = lambda key, default: {
            'api.timeout': 5,
            'api.max_retries': 2
        }.get(key, default)
        
        with patch('requests.get') as mock_get, \
             patch('time.sleep') as mock_sleep:
            
            # All calls fail
            mock_get.side_effect = requests.exceptions.RequestException("Network error")
            
            service = MovieService()
            result = service.get_movie_full_details("Test Movie")
            
            assert result["found"] is False
            assert "Network error" in result["error"]
            assert mock_get.call_count == 2  # max_retries attempts
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_format_movie_data(self, mock_config, mock_url, mock_key, sample_omdb_response):
        """Test movie data formatting."""
        mock_config.side_effect = lambda key, default: default
        
        service = MovieService()
        formatted_data = service._format_movie_data(sample_omdb_response)
        
        assert formatted_data["found"] is True
        assert formatted_data["title"] == "Test Movie"
        assert formatted_data["year"] == "2023"
        assert formatted_data["runtime"] == "120 min"
        assert formatted_data["imdb_rating"] == "8.5"
        assert formatted_data["director"] == "Test Director"
        assert formatted_data["actors"] == "Test Actor 1, Test Actor 2"
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_format_movie_data_missing_fields(self, mock_config, mock_url, mock_key):
        """Test movie data formatting with missing fields."""
        mock_config.side_effect = lambda key, default: default
        
        incomplete_response = {
            "Title": "Test Movie",
            "Response": "True"
            # Missing many fields
        }
        
        service = MovieService()
        formatted_data = service._format_movie_data(incomplete_response)
        
        assert formatted_data["found"] is True
        assert formatted_data["title"] == "Test Movie"
        assert formatted_data["year"] == "N/A"
        assert formatted_data["plot"] == "N/A"
        assert formatted_data["poster"] == "N/A"
    
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_timeout_handling(self, mock_config, mock_url, mock_key):
        """Test timeout handling in API requests."""
        mock_config.side_effect = lambda key, default: {
            'api.timeout': 1,
            'api.max_retries': 1
        }.get(key, default)
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            
            service = MovieService()
            result = service.get_movie_full_details("Test Movie")
            
            assert result["found"] is False
            assert "timeout" in result["error"].lower()


class TestMovieServiceIntegration:
    """Integration tests for MovieService (require actual API or mocked responses)."""
    
    @pytest.mark.integration
    @patch('src.services.movie_service.get_api_key', return_value='test-key')
    @patch('src.services.movie_service.get_api_url', return_value='http://test.com')
    @patch('src.services.movie_service.get_config')
    def test_full_workflow(self, mock_config, mock_url, mock_key, sample_omdb_response):
        """Test complete workflow from search to details."""
        mock_config.side_effect = lambda key, default: default
        
        search_response = {
            "Search": [{"Title": "Test Movie", "imdbID": "tt1234567"}],
            "Response": "True"
        }
        
        with patch('requests.get') as mock_get:
            # First call for search, second for details
            mock_get.side_effect = [
                Mock(json=lambda: search_response, raise_for_status=lambda: None),
                Mock(json=lambda: sample_omdb_response, raise_for_status=lambda: None)
            ]
            
            service = MovieService()
            
            # Search for movie
            search_result = service.search_movies_by_title("Test")
            assert search_result["found"] is True
            
            # Get details for first result
            imdb_id = search_result["results"][0]["imdbID"]
            details = service.get_movie_by_imdb_id(imdb_id)
            assert details["found"] is True
            assert details["title"] == "Test Movie"
