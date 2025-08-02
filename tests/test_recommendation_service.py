"""
Comprehensive tests for RecommendationService.
Tests movie recommendations, genre-based recommendations, data loading, and enhanced recommendations.
"""

import os
import pandas as pd
import numpy as np
import pytest
import tempfile
import joblib
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.services.recommendation_service import RecommendationService


class TestRecommendationService:
    """Test suite for RecommendationService class."""
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_init_success(self, mock_get_config, mock_config):
        """Test successful RecommendationService initialization."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.processed_data_dir': 'test_data/processed',
            'recommendations.max_recommendations': 10,
            'recommendations.min_similarity_score': 0.1
        }.get(key, default)
        
        service = RecommendationService()
        assert service.processed_data_dir == 'test_data/processed'
        assert service.max_recommendations == 10
        assert service.min_similarity_score == 0.1
        assert not service.is_loaded
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_load_processed_data_success(self, mock_get_config, mock_config, temp_data_dir):
        """Test successful loading of processed data."""
        mock_get_config.side_effect = lambda key, default: default
        
        # Create test data files
        similarity_matrix = np.array([[1.0, 0.8, 0.3], [0.8, 1.0, 0.5], [0.3, 0.5, 1.0]])
        movie_indices = {'Movie A': 0, 'Movie B': 1, 'Movie C': 2}
        processed_movies = pd.DataFrame({
            'title': ['Movie A', 'Movie B', 'Movie C'],
            'genres': ['Action', 'Comedy', 'Drama']
        })
        
        # Save test files
        joblib.dump(similarity_matrix, os.path.join(temp_data_dir, 'similarity_matrix.pkl'))
        joblib.dump(movie_indices, os.path.join(temp_data_dir, 'movie_indices.pkl'))
        joblib.dump(processed_movies, os.path.join(temp_data_dir, 'processed_movies.pkl'))
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.processed_data_dir = temp_data_dir
            service.processed_data_path = Path(temp_data_dir)
            service.is_loaded = False
            
            result = service.load_processed_data()
            
            assert result is True
            assert service.is_loaded is True
            assert service.similarity_matrix.shape == (3, 3)
            assert len(service.movie_indices) == 3
            assert len(service.processed_movies) == 3
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_load_processed_data_missing_files(self, mock_get_config, mock_config, temp_data_dir):
        """Test loading processed data when files are missing."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.processed_data_dir = temp_data_dir
            service.processed_data_path = Path(temp_data_dir)
            service.is_loaded = False
            
            result = service.load_processed_data()
            
            assert result is False
            assert service.is_loaded is False
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_movie_recommendations_success(self, mock_get_config, mock_config):
        """Test successful movie recommendations."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.max_recommendations': 5,
            'recommendations.min_similarity_score': 0.1
        }.get(key, default)

        # Mock data
        similarity_matrix = np.array([[1.0, 0.8, 0.3], [0.8, 1.0, 0.5], [0.3, 0.5, 1.0]])
        movie_indices = {'Movie A': 0, 'Movie B': 1, 'Movie C': 2}
        processed_movies = pd.DataFrame({
            'title': ['Movie A', 'Movie B', 'Movie C'],
            'genres': ['Action', 'Comedy', 'Drama'],
            'overview': ['Action movie', 'Funny movie', 'Dramatic movie']
        })

        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.similarity_matrix = similarity_matrix
            service.movie_indices = movie_indices
            service.processed_movies = processed_movies
            service.is_loaded = True
            service.max_recommendations = 5
            service.min_similarity_score = 0.1

            recommendations = service.get_movie_recommendations('Movie A', 2)

            assert len(recommendations) == 2
            assert recommendations[0]['title'] == 'Movie B'  # Highest similarity
            assert recommendations[0]['similarity_score'] == 0.8
            assert recommendations[1]['title'] == 'Movie C'
            assert recommendations[1]['similarity_score'] == 0.3
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_movie_recommendations_movie_not_found(self, mock_get_config, mock_config):
        """Test movie recommendations when movie is not found."""
        mock_get_config.side_effect = lambda key, default: default

        movie_indices = {'Movie A': 0, 'Movie B': 1}

        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.movie_indices = movie_indices
            service.is_loaded = True
            service.max_recommendations = 10

            recommendations = service.get_movie_recommendations('Nonexistent Movie')

            assert recommendations == []
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_movie_recommendations_not_loaded(self, mock_get_config, mock_config):
        """Test movie recommendations when data is not loaded."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.is_loaded = False
            
            with patch.object(service, 'load_processed_data', return_value=False):
                recommendations = service.get_movie_recommendations('Movie A')
                
                assert recommendations == []
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_available_genres(self, mock_get_config, mock_config):
        """Test getting available genres."""
        mock_get_config.side_effect = lambda key, default: default

        processed_movies = pd.DataFrame({
            'title': ['Movie A', 'Movie B', 'Movie C'],
            'genres': ['Action Drama', 'Comedy', 'Drama Thriller']  # Space separated as expected by implementation
        })

        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.processed_movies = processed_movies
            service.is_loaded = True

            genres = service.get_available_genres()

            expected_genres = ['Action', 'Comedy', 'Drama', 'Thriller']
            assert set(genres) == set(expected_genres)
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_available_genres_not_loaded(self, mock_get_config, mock_config):
        """Test getting available genres when data is not loaded."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.is_loaded = False
            
            with patch.object(service, 'load_processed_data', return_value=False):
                genres = service.get_available_genres()
                
                assert genres == []
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_recommendations_by_genre(self, mock_get_config, mock_config):
        """Test getting recommendations by genre."""
        mock_get_config.side_effect = lambda key, default: default
        
        processed_movies = pd.DataFrame({
            'title': ['Movie A', 'Movie B', 'Movie C', 'Movie D'],
            'genres': ['Action|Drama', 'Comedy', 'Action|Thriller', 'Drama'],
            'overview': ['Action drama', 'Funny', 'Action thriller', 'Drama'],
            'keywords': ['action', 'comedy', 'action', 'drama'],
            'cast': ['Actor A', 'Actor B', 'Actor C', 'Actor D'],
            'director': ['Dir A', 'Dir B', 'Dir C', 'Dir D']
        })
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.processed_movies = processed_movies
            service.is_loaded = True
            
            recommendations = service.get_recommendations_by_genre('Action', 2)
            
            assert len(recommendations) <= 2
            # Should only return movies with Action genre
            for rec in recommendations:
                assert 'Action' in processed_movies[processed_movies['title'] == rec['title']]['genres'].iloc[0]
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_recommendations_by_genre_not_found(self, mock_get_config, mock_config):
        """Test getting recommendations by genre when genre is not found."""
        mock_get_config.side_effect = lambda key, default: default
        
        processed_movies = pd.DataFrame({
            'title': ['Movie A'],
            'genres': ['Action']
        })
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.processed_movies = processed_movies
            service.is_loaded = True
            service.max_recommendations = 10

            recommendations = service.get_recommendations_by_genre('Horror')
            
            assert recommendations == []
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    @patch('src.services.recommendation_service.movie_service')
    def test_get_enhanced_recommendations(self, mock_movie_service, mock_get_config, mock_config):
        """Test getting enhanced recommendations with API data."""
        mock_get_config.side_effect = lambda key, default: default
        
        # Mock basic recommendations
        basic_recommendations = [
            {'title': 'Movie B', 'similarity_score': 0.8},
            {'title': 'Movie C', 'similarity_score': 0.6}
        ]
        
        # Mock API responses
        mock_movie_service.get_movie_full_details.side_effect = [
            {
                'found': True,
                'title': 'Movie B',
                'poster': 'http://example.com/poster_b.jpg',
                'imdb_rating': '8.5',
                'year': '2023'
            },
            {
                'found': False,
                'error': 'Movie not found'
            }
        ]
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            
            with patch.object(service, 'get_movie_recommendations', return_value=basic_recommendations):
                enhanced_recommendations = service.get_enhanced_recommendations('Movie A')

                assert len(enhanced_recommendations) == 2  # Both recommendations returned
                # First one should be enhanced with API data
                assert enhanced_recommendations[0]['title'] == 'Movie B'
                assert enhanced_recommendations[0]['poster'] == 'http://example.com/poster_b.jpg'
                assert enhanced_recommendations[0]['imdb_rating'] == '8.5'
                # Second one should be the original recommendation (API failed)
                assert enhanced_recommendations[1]['title'] == 'Movie C'
                assert enhanced_recommendations[1]['similarity_score'] == 0.6
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    @patch('src.services.recommendation_service.is_feature_enabled')
    def test_get_enhanced_recommendations_feature_disabled(self, mock_feature_enabled, mock_get_config, mock_config):
        """Test enhanced recommendations when feature is disabled."""
        mock_get_config.side_effect = lambda key, default: default
        mock_feature_enabled.return_value = False
        
        basic_recommendations = [{'title': 'Movie B', 'similarity_score': 0.8}]
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            
            with patch.object(service, 'get_movie_recommendations', return_value=basic_recommendations):
                enhanced_recommendations = service.get_enhanced_recommendations('Movie A')
                
                # Should return basic recommendations without enhancement
                assert enhanced_recommendations == basic_recommendations
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_dataset_stats(self, mock_get_config, mock_config):
        """Test getting dataset statistics."""
        mock_get_config.side_effect = lambda key, default: default
        
        processed_movies = pd.DataFrame({
            'title': ['Movie A', 'Movie B', 'Movie C'],
            'genres': ['Action|Drama', 'Comedy', 'Drama|Thriller']
        })
        
        similarity_matrix = np.array([[1.0, 0.8, 0.3], [0.8, 1.0, 0.5], [0.3, 0.5, 1.0]])
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.processed_movies = processed_movies
            service.similarity_matrix = similarity_matrix
            service.is_loaded = True
            
            stats = service.get_dataset_stats()
            
            assert stats['total_movies'] == 3
            assert stats['total_genres'] == 4  # Action, Drama, Comedy, Thriller
            assert 'avg_similarity' in stats
            assert 'matrix_shape' in stats
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_get_dataset_stats_not_loaded(self, mock_get_config, mock_config):
        """Test getting dataset statistics when data is not loaded."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.is_loaded = False
            
            with patch.object(service, 'load_processed_data', return_value=False):
                stats = service.get_dataset_stats()
                
                assert stats == {}


class TestRecommendationServiceEdgeCases:
    """Test edge cases and error conditions."""
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_similarity_threshold_filtering(self, mock_get_config, mock_config):
        """Test that recommendations below similarity threshold are filtered out."""
        mock_get_config.side_effect = lambda key, default: default
        
        similarity_matrix = np.array([[1.0, 0.05, 0.8], [0.05, 1.0, 0.03], [0.8, 0.03, 1.0]])
        movie_indices = {'Movie A': 0, 'Movie B': 1, 'Movie C': 2}
        processed_movies = pd.DataFrame({
            'title': ['Movie A', 'Movie B', 'Movie C'],
            'genres': ['Action', 'Comedy', 'Drama']
        })
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.similarity_matrix = similarity_matrix
            service.movie_indices = movie_indices
            service.processed_movies = processed_movies
            service.is_loaded = True
            service.min_similarity_score = 0.1  # Threshold
            service.max_recommendations = 10
            
            recommendations = service.get_movie_recommendations('Movie A')
            
            # Should only return Movie C (0.8 similarity), not Movie B (0.05 similarity)
            assert len(recommendations) == 1
            assert recommendations[0]['title'] == 'Movie C'
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_case_insensitive_movie_search(self, mock_get_config, mock_config):
        """Test that movie search is case insensitive."""
        mock_get_config.side_effect = lambda key, default: default
        
        similarity_matrix = np.array([[1.0, 0.8], [0.8, 1.0]])
        movie_indices = {'Movie A': 0, 'Movie B': 1}
        processed_movies = pd.DataFrame({
            'title': ['Movie A', 'Movie B'],
            'genres': ['Action', 'Comedy']
        })
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.similarity_matrix = similarity_matrix
            service.movie_indices = movie_indices
            service.processed_movies = processed_movies
            service.is_loaded = True
            service.max_recommendations = 10
            service.min_similarity_score = 0.1
            
            # Test different cases
            recommendations1 = service.get_movie_recommendations('movie a')
            recommendations2 = service.get_movie_recommendations('MOVIE A')
            recommendations3 = service.get_movie_recommendations('Movie A')
            
            # All should return the same results
            assert len(recommendations1) == len(recommendations2) == len(recommendations3) == 1
            assert recommendations1[0]['title'] == recommendations2[0]['title'] == recommendations3[0]['title']
    
    @patch('src.services.recommendation_service.config')
    @patch('src.services.recommendation_service.get_config')
    def test_empty_similarity_matrix(self, mock_get_config, mock_config):
        """Test behavior with empty similarity matrix."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch.object(RecommendationService, '__init__', lambda x: None):
            service = RecommendationService()
            service.similarity_matrix = np.array([])
            service.movie_indices = {}
            service.processed_movies = pd.DataFrame()
            service.is_loaded = True
            service.max_recommendations = 10
            
            recommendations = service.get_movie_recommendations('Any Movie')
            
            assert recommendations == []
