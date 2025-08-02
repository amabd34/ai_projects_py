"""
Comprehensive tests for Flask application routes.
Tests all routes, error handling, feature toggles, API endpoints, and template rendering.
"""

import pytest
import json
from unittest.mock import Mock, patch

from src.app import create_app


class TestFlaskApp:
    """Test suite for Flask application."""
    
    def test_create_app(self, config_loader):
        """Test Flask app creation."""
        with patch('src.app.config', config_loader):
            app = create_app()
            assert app is not None
            assert app.config['TESTING'] is False
    
    def test_home_route(self, client, config_loader):
        """Test home page route."""
        with patch('src.app.config', config_loader):
            response = client.get('/')
            assert response.status_code == 200
            assert b'Movie' in response.data  # Should contain movie-related content
    
    def test_search_movie_success(self, client, mock_movie_service):
        """Test successful movie search."""
        with patch('src.app.movie_service', mock_movie_service):
            response = client.post('/search', data={'movie_title': 'Test Movie'})
            assert response.status_code == 200
            mock_movie_service.get_movie_full_details.assert_called_once_with('Test Movie')
    
    def test_search_movie_empty_title(self, client, config_loader):
        """Test movie search with empty title."""
        with patch('src.app.config', config_loader):
            response = client.post('/search', data={'movie_title': ''})
            assert response.status_code == 200
            assert b'Please enter a movie title' in response.data
    
    def test_search_movie_not_found(self, client, config_loader):
        """Test movie search when movie is not found."""
        mock_service = Mock()
        mock_service.get_movie_full_details.return_value = {
            "found": False,
            "error": "Movie not found"
        }
        
        with patch('src.app.movie_service', mock_service), \
             patch('src.app.config', config_loader):
            response = client.post('/search', data={'movie_title': 'Nonexistent Movie'})
            assert response.status_code == 200
            assert b'not found' in response.data
    
    def test_popular_movies_enabled(self, client, mock_movie_service, config_loader):
        """Test popular movies route when feature is enabled."""
        with patch('src.app.movie_service', mock_movie_service), \
             patch('src.app.config', config_loader), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/popular')
            assert response.status_code == 200
            mock_movie_service.get_popular_movies.assert_called_once()
    
    def test_popular_movies_disabled(self, client, config_loader):
        """Test popular movies route when feature is disabled."""
        with patch('src.app.config', config_loader), \
             patch('src.app.is_feature_enabled', return_value=False):
            
            response = client.get('/popular')
            assert response.status_code == 200
            assert b'disabled' in response.data
    
    def test_api_search_get_enabled(self, client, mock_movie_service):
        """Test API search GET endpoint when enabled."""
        with patch('src.app.movie_service', mock_movie_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/api/search/Test Movie')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['found'] is True
            assert data['title'] == 'Test Movie'
    
    def test_api_search_get_disabled(self, client):
        """Test API search GET endpoint when disabled."""
        with patch('src.app.is_feature_enabled', return_value=False):
            response = client.get('/api/search/Test Movie')
            assert response.status_code == 403
            
            data = json.loads(response.data)
            assert 'disabled' in data['error']
    
    def test_api_search_post_enabled(self, client, mock_movie_service):
        """Test API search POST endpoint when enabled."""
        with patch('src.app.movie_service', mock_movie_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.post('/api/search', 
                                 json={'title': 'Test Movie'},
                                 content_type='application/json')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['found'] is True
    
    def test_api_search_post_missing_title(self, client):
        """Test API search POST endpoint with missing title."""
        with patch('src.app.is_feature_enabled', return_value=True):
            response = client.post('/api/search', 
                                 json={},
                                 content_type='application/json')
            assert response.status_code == 400
            
            data = json.loads(response.data)
            assert 'Missing' in data['error']
    
    def test_api_search_suggestions(self, client, mock_movie_service):
        """Test API search suggestions endpoint."""
        mock_movie_service.search_movies_by_title.return_value = {
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
        
        with patch('src.app.movie_service', mock_movie_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/api/search/suggestions/test')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert len(data['suggestions']) == 1
            assert data['suggestions'][0]['title'] == 'Test Movie'
    
    def test_api_search_suggestions_short_query(self, client):
        """Test API search suggestions with short query."""
        with patch('src.app.is_feature_enabled', return_value=True):
            response = client.get('/api/search/suggestions/a')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['suggestions'] == []
    
    def test_api_popular(self, client, mock_movie_service):
        """Test API popular movies endpoint."""
        with patch('src.app.movie_service', mock_movie_service), \
             patch('src.app.is_feature_enabled', return_value=True), \
             patch('src.app.config') as mock_config:
            
            mock_config.get_popular_movies.return_value = ['Movie 1', 'Movie 2']
            
            response = client.get('/api/popular')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'movies' in data
            assert 'count' in data
    
    def test_recommendations_page_enabled(self, client, mock_recommendation_service):
        """Test recommendations page when feature is enabled."""
        with patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/recommendations')
            assert response.status_code == 200
            mock_recommendation_service.get_available_genres.assert_called_once()
    
    def test_recommendations_page_disabled(self, client, config_loader):
        """Test recommendations page when feature is disabled."""
        with patch('src.app.config', config_loader), \
             patch('src.app.is_feature_enabled', return_value=False):
            
            response = client.get('/recommendations')
            assert response.status_code == 200
            assert b'disabled' in response.data
    
    def test_movie_recommendations(self, client, mock_recommendation_service):
        """Test movie recommendations route."""
        with patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/recommendations/Test Movie')
            assert response.status_code == 200
            mock_recommendation_service.get_enhanced_recommendations.assert_called_once_with('Test Movie')
    
    def test_movie_recommendations_no_results(self, client, config_loader):
        """Test movie recommendations when no results found."""
        mock_service = Mock()
        mock_service.get_enhanced_recommendations.return_value = []
        mock_service.get_available_genres.return_value = ['Action', 'Comedy']
        
        with patch('src.app.recommendation_service', mock_service), \
             patch('src.app.is_feature_enabled', return_value=True), \
             patch('src.app.config', config_loader):
            
            response = client.get('/recommendations/Unknown Movie')
            assert response.status_code == 200
            assert b'No recommendations found' in response.data
    
    def test_genre_recommendations(self, client, mock_recommendation_service):
        """Test genre-based recommendations route."""
        with patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/recommendations/genre/Action')
            assert response.status_code == 200
            mock_recommendation_service.get_recommendations_by_genre.assert_called_once_with('Action')
    
    def test_api_movie_recommendations(self, client, mock_recommendation_service):
        """Test API movie recommendations endpoint."""
        with patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/api/recommendations/Test Movie?limit=5&enhanced=true')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'source_movie' in data
            assert 'recommendations' in data
            assert 'count' in data
            
            mock_recommendation_service.get_enhanced_recommendations.assert_called_once_with('Test Movie', 5)
    
    def test_api_movie_recommendations_basic(self, client, mock_recommendation_service):
        """Test API movie recommendations endpoint with basic recommendations."""
        with patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/api/recommendations/Test Movie?enhanced=false')
            assert response.status_code == 200
            
            mock_recommendation_service.get_movie_recommendations.assert_called_once()
    
    def test_api_genre_recommendations(self, client, mock_recommendation_service):
        """Test API genre recommendations endpoint."""
        with patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/api/recommendations/genre/Action?limit=3')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['genre'] == 'Action'
            
            mock_recommendation_service.get_recommendations_by_genre.assert_called_once_with('Action', 3)
    
    def test_api_available_genres(self, client, mock_recommendation_service):
        """Test API available genres endpoint."""
        with patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/api/recommendations/genres')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'genres' in data
            assert 'count' in data
    
    def test_api_recommendation_stats(self, client, mock_recommendation_service):
        """Test API recommendation stats endpoint."""
        with patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            response = client.get('/api/recommendations/stats')
            assert response.status_code == 200
            
            mock_recommendation_service.get_dataset_stats.assert_called_once()
    
    def test_health_check(self, client, config_loader):
        """Test health check endpoint."""
        with patch('src.app.config', config_loader), \
             patch('src.app.get_config') as mock_get_config, \
             patch('src.app.is_feature_enabled', return_value=True):
            
            mock_get_config.side_effect = lambda key: {
                'app.name': 'Test App',
                'app.version': '1.0.0'
            }.get(key)
            
            response = client.get('/health')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert 'features' in data
    
    def test_404_error_handler(self, client, config_loader):
        """Test 404 error handler."""
        with patch('src.app.config', config_loader):
            response = client.get('/nonexistent-route')
            assert response.status_code == 404
            assert b'not found' in response.data
    
    def test_500_error_handler(self, config_loader):
        """Test 500 error handler is registered."""
        with patch('src.app.config', config_loader):
            app = create_app()

            # Test that the error handler is registered
            assert 500 in app.error_handler_spec[None]

            # Test that we can handle a 500 error by checking the handler exists
            error_handlers = app.error_handler_spec[None][500]
            assert len(error_handlers) > 0


class TestFlaskAppIntegration:
    """Integration tests for Flask application."""
    
    @pytest.mark.integration
    def test_full_search_workflow(self, client, mock_movie_service, config_loader):
        """Test complete search workflow."""
        with patch('src.app.movie_service', mock_movie_service), \
             patch('src.app.config', config_loader):
            
            # Test home page
            response = client.get('/')
            assert response.status_code == 200
            
            # Test search
            response = client.post('/search', data={'movie_title': 'Test Movie'})
            assert response.status_code == 200
            
            # Verify service was called
            mock_movie_service.get_movie_full_details.assert_called_with('Test Movie')
    
    @pytest.mark.integration
    def test_api_workflow(self, client, mock_movie_service, mock_recommendation_service):
        """Test complete API workflow."""
        with patch('src.app.movie_service', mock_movie_service), \
             patch('src.app.recommendation_service', mock_recommendation_service), \
             patch('src.app.is_feature_enabled', return_value=True):
            
            # Test movie search API
            response = client.get('/api/search/Test Movie')
            assert response.status_code == 200
            
            # Test recommendations API
            response = client.get('/api/recommendations/Test Movie')
            assert response.status_code == 200
            
            # Test health check
            response = client.get('/health')
            assert response.status_code == 200


class TestFeatureToggles:
    """Test feature toggle functionality."""
    
    def test_all_features_disabled(self, client, config_loader):
        """Test behavior when all features are disabled."""
        with patch('src.app.config', config_loader), \
             patch('src.app.is_feature_enabled', return_value=False):
            
            # Popular movies should be disabled
            response = client.get('/popular')
            assert response.status_code == 200
            assert b'disabled' in response.data
            
            # API endpoints should be disabled
            response = client.get('/api/search/Test Movie')
            assert response.status_code == 403
            
            # Recommendations should be disabled
            response = client.get('/recommendations')
            assert response.status_code == 200
            assert b'disabled' in response.data
    
    def test_selective_feature_enabling(self, client, config_loader):
        """Test selective feature enabling."""
        def mock_feature_enabled(feature):
            return feature == 'enable_popular_movies'
        
        with patch('src.app.config', config_loader), \
             patch('src.app.is_feature_enabled', side_effect=mock_feature_enabled), \
             patch('src.app.movie_service') as mock_service:
            
            mock_service.get_popular_movies.return_value = []
            
            # Popular movies should be enabled
            response = client.get('/popular')
            assert response.status_code == 200
            mock_service.get_popular_movies.assert_called_once()
            
            # API endpoints should be disabled
            response = client.get('/api/search/Test Movie')
            assert response.status_code == 403
