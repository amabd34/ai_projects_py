"""
Comprehensive tests for MoviePreprocessor service.
Tests data loading, text processing, TF-IDF vectorization, similarity calculations, and file I/O operations.
"""

import os
import pandas as pd
import numpy as np
import pytest
import tempfile
import joblib
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.services.movie_preprocessor import MoviePreprocessor, preprocess_movies


class TestMoviePreprocessor:
    """Test suite for MoviePreprocessor class."""
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_init_success(self, mock_get_config, mock_config):
        """Test successful MoviePreprocessor initialization."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.data_file': 'test_movies.csv',
            'recommendations.processed_data_dir': 'test_data/processed',
            'recommendations.text_features': ['genres', 'keywords', 'overview'],
            'recommendations.tfidf_params': {},
            'recommendations.preprocessing': {}
        }.get(key, default)
        
        preprocessor = MoviePreprocessor()
        assert preprocessor.data_file == 'test_movies.csv'
        assert preprocessor.processed_data_dir == 'test_data/processed'
        assert preprocessor.text_features == ['genres', 'keywords', 'overview']
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_load_data_success(self, mock_get_config, mock_config, sample_movie_data):
        """Test successful data loading."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.data_file': 'test_movies.csv'
        }.get(key, default)
        
        # Create test CSV file
        df = pd.DataFrame(sample_movie_data)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_csv = f.name
        
        try:
            with patch.object(MoviePreprocessor, '__init__', lambda x: None):
                preprocessor = MoviePreprocessor()
                preprocessor.data_file = temp_csv
                
                result_df = preprocessor.load_data()
                assert len(result_df) == 3
                assert 'title' in result_df.columns
                assert 'genres' in result_df.columns
        finally:
            os.unlink(temp_csv)
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_load_data_file_not_found(self, mock_get_config, mock_config, temp_data_dir):
        """Test data loading when file doesn't exist - should create sample dataset."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.data_file': 'nonexistent.csv'
        }.get(key, default)

        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.data_file = 'nonexistent.csv'
            preprocessor.processed_data_path = Path(temp_data_dir)

            # Should create sample dataset instead of raising error
            df = preprocessor.load_data()
            assert len(df) > 0
            assert 'title' in df.columns
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_clean_text(self, mock_get_config, mock_config):
        """Test text cleaning functionality."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            # Set up required attributes
            preprocessor.preprocessing_params = {
                'lowercase': True,
                'remove_punctuation': True,
                'remove_stopwords': True,
                'lemmatize': True,
                'min_word_length': 2
            }
            preprocessor.stop_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            preprocessor.lemmatizer = Mock()
            preprocessor.lemmatizer.lemmatize = lambda x: x  # Simple identity function for testing

            # Test basic cleaning
            dirty_text = "Action|Drama|Thriller"
            clean_text = preprocessor.clean_text(dirty_text)
            assert clean_text == "action drama thriller"
            
            # Test with special characters
            dirty_text = "Sci-Fi & Fantasy (2023)!"
            clean_text = preprocessor.clean_text(dirty_text)
            assert "sci" in clean_text
            assert "fi" in clean_text
            assert "fantasy" in clean_text
            assert "2023" not in clean_text  # Numbers should be removed
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_clean_text_empty_input(self, mock_get_config, mock_config):
        """Test text cleaning with empty or None input."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            # Set up required attributes
            preprocessor.preprocessing_params = {
                'lowercase': True,
                'remove_punctuation': True,
                'remove_stopwords': True,
                'lemmatize': True,
                'min_word_length': 2
            }
            preprocessor.stop_words = set()
            preprocessor.lemmatizer = Mock()

            assert preprocessor.clean_text("") == ""
            assert preprocessor.clean_text(None) == ""
            assert preprocessor.clean_text("   ") == ""
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_create_combined_features(self, mock_get_config, mock_config, sample_movie_data):
        """Test combined features creation."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.text_features': ['genres', 'keywords', 'overview']
        }.get(key, default)
        
        df = pd.DataFrame(sample_movie_data)
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.text_features = ['genres', 'keywords', 'overview']

            # Mock clean_text to return simplified text
            def mock_clean_text(text):
                if pd.isna(text) or not text:
                    return ""
                return text.lower().replace('|', ' ').replace(',', ' ')

            preprocessor.clean_text = mock_clean_text

            result_df = preprocessor.create_combined_features(df)

            assert 'combined_features' in result_df.columns
            assert len(result_df) == len(df)

            # Check that combined features contain text from all specified columns
            combined_text = result_df['combined_features'].iloc[0]
            assert 'action' in combined_text.lower()
            assert 'drama' in combined_text.lower()
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_create_combined_features_missing_columns(self, mock_get_config, mock_config):
        """Test combined features creation with missing columns."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.text_features': ['genres', 'nonexistent_column']
        }.get(key, default)
        
        df = pd.DataFrame({
            'title': ['Movie A'],
            'genres': ['Action|Drama']
        })
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.text_features = ['genres', 'nonexistent_column']

            # Mock clean_text to return simplified text
            def mock_clean_text(text):
                if pd.isna(text) or not text:
                    return ""
                return text.lower().replace('|', ' ').replace(',', ' ')

            preprocessor.clean_text = mock_clean_text

            result_df = preprocessor.create_combined_features(df)

            assert 'combined_features' in result_df.columns
            # Should handle missing columns gracefully
            assert 'action' in result_df['combined_features'].iloc[0].lower()
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_create_tfidf_matrix(self, mock_get_config, mock_config, sample_movie_data):
        """Test TF-IDF matrix creation."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.tfidf_params': {
                'max_features': 100,
                'stop_words': 'english',
                'ngram_range': [1, 2]
            }
        }.get(key, default)
        
        df = pd.DataFrame(sample_movie_data)
        # Create meaningful combined features for TF-IDF
        df['combined_features'] = [
            'action adventure superhero movie exciting',
            'drama romance emotional story love',
            'comedy funny humor entertainment'
        ]

        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.tfidf_params = {
                'max_features': 100,
                'stop_words': None,  # Don't remove stop words for this test
                'ngram_range': (1, 2),
                'min_df': 1  # Include all terms
            }
            
            vectorizer, tfidf_matrix = preprocessor.create_tfidf_matrix(df)
            
            assert tfidf_matrix.shape[0] == len(df)
            assert tfidf_matrix.shape[1] <= 100  # max_features constraint
            assert hasattr(vectorizer, 'transform')
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_create_similarity_matrix(self, mock_get_config, mock_config):
        """Test similarity matrix creation."""
        mock_get_config.side_effect = lambda key, default: default
        
        # Create a simple TF-IDF matrix for testing
        tfidf_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            
            similarity_matrix = preprocessor.create_similarity_matrix(tfidf_matrix)
            
            assert similarity_matrix.shape == (3, 3)
            # Diagonal should be 1 (perfect similarity with itself)
            assert np.allclose(np.diag(similarity_matrix), 1.0)
            # Off-diagonal should be 0 (no similarity)
            assert np.allclose(similarity_matrix - np.diag(np.diag(similarity_matrix)), 0.0)
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_save_processed_data(self, mock_get_config, mock_config, temp_data_dir, sample_movie_data):
        """Test saving processed data."""
        mock_get_config.side_effect = lambda key, default: default
        
        df = pd.DataFrame(sample_movie_data)
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = np.array([[1, 0], [0, 1]])
        similarity_matrix = np.array([[1, 0.5], [0.5, 1]])
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.processed_data_dir = temp_data_dir
            preprocessor.processed_data_path = Path(temp_data_dir)
            
            saved_files = preprocessor.save_processed_data(
                df, vectorizer, tfidf_matrix, similarity_matrix
            )
            
            # Check that all expected files were saved
            expected_files = [
                'processed_movies',
                'tfidf_vectorizer',
                'tfidf_matrix',
                'similarity_matrix',
                'movie_indices'
            ]

            for file in expected_files:
                assert file in saved_files
                assert os.path.exists(saved_files[file])
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_check_processed_data_exists(self, mock_get_config, mock_config, temp_data_dir):
        """Test checking if processed data exists."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.processed_data_dir = temp_data_dir
            preprocessor.processed_data_path = Path(temp_data_dir)
            
            # Initially should not exist
            assert not preprocessor.check_processed_data_exists()
            
            # Create some files
            required_files = [
                'similarity_matrix.pkl',
                'movie_indices.pkl',
                'processed_movies.pkl'
            ]
            
            for file in required_files:
                file_path = os.path.join(temp_data_dir, file)
                with open(file_path, 'w') as f:
                    f.write('dummy')
            
            # Now should exist
            assert preprocessor.check_processed_data_exists()
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_process_all_success(self, mock_get_config, mock_config, sample_movie_data, temp_data_dir):
        """Test complete processing pipeline."""
        mock_get_config.side_effect = lambda key, default: {
            'recommendations.data_file': 'test_movies.csv',
            'recommendations.processed_data_dir': temp_data_dir,
            'recommendations.text_features': ['genres', 'keywords', 'overview'],
            'recommendations.tfidf_params': {'max_features': 100},
            'recommendations.preprocessing': {}
        }.get(key, default)
        
        # Create test CSV file
        df = pd.DataFrame(sample_movie_data)
        test_csv = os.path.join(temp_data_dir, 'test_movies.csv')
        df.to_csv(test_csv, index=False)
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.data_file = test_csv
            preprocessor.processed_data_dir = temp_data_dir
            preprocessor.processed_data_path = Path(temp_data_dir)
            preprocessor.text_features = ['genres', 'keywords', 'overview']
            preprocessor.tfidf_params = {'max_features': 100, 'min_df': 1, 'stop_words': None}
            preprocessor.preprocessing_params = {}

            # Mock the methods that require complex setup
            def mock_clean_text(text):
                if pd.isna(text) or not text:
                    return ""
                return text.lower().replace('|', ' ').replace(',', ' ')

            preprocessor.clean_text = mock_clean_text

            saved_files = preprocessor.process_all()

            assert len(saved_files) > 0
            assert 'similarity_matrix' in saved_files
            assert 'movie_indices' in saved_files
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_download_nltk_data(self, mock_get_config, mock_config):
        """Test NLTK data downloading."""
        mock_get_config.side_effect = lambda key, default: default
        
        with patch('nltk.download') as mock_download, \
             patch.object(MoviePreprocessor, '__init__', lambda x: None):
            
            preprocessor = MoviePreprocessor()
            preprocessor.download_nltk_data()
            
            # Should attempt to download required NLTK data
            assert mock_download.call_count > 0
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_lemmatize_text(self, mock_get_config, mock_config):
        """Test text lemmatization."""
        mock_get_config.side_effect = lambda key, default: default

        with patch('nltk.word_tokenize') as mock_tokenize, \
             patch.object(MoviePreprocessor, '__init__', lambda x: None):

            mock_tokenize.return_value = ['running', 'quickly', 'through', 'the', 'forest']

            preprocessor = MoviePreprocessor()
            # Set up required attributes
            preprocessor.stop_words = {'the', 'through'}

            # Mock the lemmatizer
            mock_lemmatizer = Mock()
            mock_lemmatizer.lemmatize.side_effect = lambda word: {
                'running': 'run',
                'quickly': 'quick'
            }.get(word, word)
            preprocessor.lemmatizer = mock_lemmatizer

            result = preprocessor.lemmatize_text("running quickly through the forest")

            # Should remove stopwords and lemmatize
            assert 'run' in result
            assert 'quick' in result
            assert 'the' not in result
            assert 'through' not in result


class TestPreprocessMoviesFunction:
    """Test suite for the convenience function."""
    
    @patch('src.services.movie_preprocessor.MoviePreprocessor')
    def test_preprocess_movies_no_force(self, mock_preprocessor_class):
        """Test preprocess_movies function without forcing reprocess."""
        mock_instance = Mock()
        mock_instance.check_processed_data_exists.return_value = True
        mock_preprocessor_class.return_value = mock_instance
        
        result = preprocess_movies(force_reprocess=False)
        
        assert result == {}
        mock_instance.check_processed_data_exists.assert_called_once()
        mock_instance.process_all.assert_not_called()
    
    @patch('src.services.movie_preprocessor.MoviePreprocessor')
    def test_preprocess_movies_force_reprocess(self, mock_preprocessor_class):
        """Test preprocess_movies function with forced reprocessing."""
        mock_instance = Mock()
        mock_instance.process_all.return_value = {'file1': 'path1'}
        mock_preprocessor_class.return_value = mock_instance
        
        result = preprocess_movies(force_reprocess=True)
        
        assert result == {'file1': 'path1'}
        mock_instance.check_processed_data_exists.assert_not_called()
        mock_instance.process_all.assert_called_once()


class TestMoviePreprocessorEdgeCases:
    """Test edge cases and error conditions."""
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_empty_dataframe(self, mock_get_config, mock_config):
        """Test processing with empty dataframe."""
        mock_get_config.side_effect = lambda key, default: default
        
        empty_df = pd.DataFrame()
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.text_features = ['genres']
            
            with pytest.raises(Exception):  # Should handle gracefully or raise appropriate error
                preprocessor.create_combined_features(empty_df)
    
    @patch('src.services.movie_preprocessor.config')
    @patch('src.services.movie_preprocessor.get_config')
    def test_invalid_tfidf_params(self, mock_get_config, mock_config, sample_movie_data):
        """Test TF-IDF creation with invalid parameters."""
        mock_get_config.side_effect = lambda key, default: default
        
        df = pd.DataFrame(sample_movie_data)
        df['combined_features'] = df['genres']
        
        with patch.object(MoviePreprocessor, '__init__', lambda x: None):
            preprocessor = MoviePreprocessor()
            preprocessor.tfidf_params = {'max_features': -1}  # Invalid parameter
            
            with pytest.raises(ValueError):
                preprocessor.create_tfidf_matrix(df)
