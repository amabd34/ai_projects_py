#!/usr/bin/env python3
"""
Movie Recommendation Service
Provides intelligent movie recommendations using preprocessed similarity data.
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# Add the src directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_loader import get_config, config, is_feature_enabled
from services.movie_service import movie_service

class RecommendationService:
    """
    Movie recommendation service that provides intelligent movie suggestions
    based on content similarity and user preferences.
    """
    
    def __init__(self):
        """Initialize the recommendation service."""
        self.config = config
        self.processed_data_dir = get_config('recommendations.processed_data_dir', 'data/processed')
        self.max_recommendations = get_config('recommendations.max_recommendations', 10)
        self.min_similarity_score = get_config('recommendations.min_similarity_score', 0.1)
        
        # Data storage
        self.similarity_matrix = None
        self.movie_indices = None
        self.processed_movies = None
        self.is_loaded = False
        
        # Create processed data path
        self.processed_data_path = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / self.processed_data_dir
        
        print(f"✅ RecommendationService initialized")
        print(f"📂 Processed data directory: {self.processed_data_path}")
    
    def load_processed_data(self) -> bool:
        """
        Load preprocessed similarity data from pickle files.
        
        Returns:
            bool: True if data loaded successfully
        """
        try:
            print("📖 Loading preprocessed recommendation data...")
            
            # File paths
            similarity_file = self.processed_data_path / get_config('recommendations.similarity_matrix_file', 'similarity_matrix.pkl')
            indices_file = self.processed_data_path / get_config('recommendations.movie_indices_file', 'movie_indices.pkl')
            movies_file = self.processed_data_path / get_config('recommendations.processed_movies_file', 'processed_movies.pkl')
            
            # Check if files exist
            missing_files = []
            for name, file_path in [('similarity_matrix', similarity_file), 
                                  ('movie_indices', indices_file), 
                                  ('processed_movies', movies_file)]:
                if not file_path.exists():
                    missing_files.append(name)
            
            if missing_files:
                print(f"❌ Missing processed data files: {missing_files}")
                print("💡 Run preprocessing first: python -m services.movie_preprocessor")
                return False
            
            # Load data
            self.similarity_matrix = joblib.load(similarity_file)
            self.movie_indices = joblib.load(indices_file)
            self.processed_movies = joblib.load(movies_file)
            
            self.is_loaded = True
            
            print(f"✅ Loaded recommendation data:")
            print(f"   📊 Similarity matrix: {self.similarity_matrix.shape}")
            print(f"   🎬 Movies: {len(self.movie_indices)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading processed data: {e}")
            return False
    
    def get_movie_recommendations(self, movie_title: str, num_recommendations: int = None) -> List[Dict[str, Any]]:
        """
        Get movie recommendations based on a given movie title.
        
        Args:
            movie_title (str): Title of the movie to base recommendations on
            num_recommendations (int, optional): Number of recommendations to return
            
        Returns:
            List[Dict[str, Any]]: List of recommended movies with similarity scores
        """
        if not self.is_loaded and not self.load_processed_data():
            return []
        
        if num_recommendations is None:
            num_recommendations = self.max_recommendations
        
        try:
            # Find the movie in our dataset
            movie_title_clean = movie_title.strip()
            
            # Try exact match first
            if movie_title_clean in self.movie_indices:
                movie_idx = self.movie_indices[movie_title_clean]
            else:
                # Try case-insensitive match
                title_lower = movie_title_clean.lower()
                matching_titles = [title for title in self.movie_indices.keys() 
                                 if title.lower() == title_lower]
                
                if matching_titles:
                    movie_idx = self.movie_indices[matching_titles[0]]
                    movie_title_clean = matching_titles[0]
                else:
                    # Try partial match
                    matching_titles = [title for title in self.movie_indices.keys() 
                                     if title_lower in title.lower() or title.lower() in title_lower]
                    
                    if matching_titles:
                        movie_idx = self.movie_indices[matching_titles[0]]
                        movie_title_clean = matching_titles[0]
                        print(f"🔍 Using partial match: '{movie_title}' -> '{matching_titles[0]}'")
                    else:
                        print(f"❌ Movie '{movie_title}' not found in dataset")
                        return []
            
            # Get similarity scores for this movie
            similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
            
            # Sort by similarity score (descending) and exclude the movie itself
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            similarity_scores = [score for score in similarity_scores if score[0] != movie_idx]
            
            # Filter by minimum similarity score
            similarity_scores = [score for score in similarity_scores 
                               if score[1] >= self.min_similarity_score]
            
            # Get top recommendations
            top_recommendations = similarity_scores[:num_recommendations]
            
            # Build recommendation list
            recommendations = []
            for idx, similarity_score in top_recommendations:
                movie_data = self.processed_movies.iloc[idx]
                
                recommendation = {
                    'title': movie_data['title'],
                    'similarity_score': float(similarity_score),
                    'genres': movie_data.get('genres', 'N/A'),
                    'overview': movie_data.get('overview', 'N/A')
                }
                
                # Add additional fields if available
                for field in ['keywords', 'cast', 'director']:
                    if field in movie_data:
                        recommendation[field] = movie_data[field]
                
                recommendations.append(recommendation)
            
            print(f"✅ Found {len(recommendations)} recommendations for '{movie_title_clean}'")
            return recommendations
            
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
            return []
    
    def get_recommendations_by_genre(self, genre: str, num_recommendations: int = None) -> List[Dict[str, Any]]:
        """
        Get movie recommendations based on genre.
        
        Args:
            genre (str): Genre to filter by
            num_recommendations (int, optional): Number of recommendations to return
            
        Returns:
            List[Dict[str, Any]]: List of movies in the specified genre
        """
        if not self.is_loaded and not self.load_processed_data():
            return []
        
        if num_recommendations is None:
            num_recommendations = self.max_recommendations
        
        try:
            # Filter movies by genre (case-insensitive)
            genre_lower = genre.lower()
            matching_movies = self.processed_movies[
                self.processed_movies['genres'].str.lower().str.contains(genre_lower, na=False)
            ]
            
            if matching_movies.empty:
                print(f"❌ No movies found for genre '{genre}'")
                return []
            
            # Sample random movies from the genre
            sample_size = min(num_recommendations, len(matching_movies))
            sampled_movies = matching_movies.sample(n=sample_size)
            
            # Build recommendation list
            recommendations = []
            for _, movie_data in sampled_movies.iterrows():
                recommendation = {
                    'title': movie_data['title'],
                    'genres': movie_data.get('genres', 'N/A'),
                    'overview': movie_data.get('overview', 'N/A'),
                    'similarity_score': 1.0  # Perfect match for genre
                }
                
                # Add additional fields if available
                for field in ['keywords', 'cast', 'director']:
                    if field in movie_data:
                        recommendation[field] = movie_data[field]
                
                recommendations.append(recommendation)
            
            print(f"✅ Found {len(recommendations)} movies for genre '{genre}'")
            return recommendations
            
        except Exception as e:
            print(f"❌ Error getting genre recommendations: {e}")
            return []
    
    def get_enhanced_recommendations(self, movie_title: str, num_recommendations: int = None) -> List[Dict[str, Any]]:
        """
        Get enhanced recommendations with OMDb API data.
        
        Args:
            movie_title (str): Title of the movie to base recommendations on
            num_recommendations (int, optional): Number of recommendations to return
            
        Returns:
            List[Dict[str, Any]]: List of enhanced recommended movies
        """
        # Get basic recommendations
        recommendations = self.get_movie_recommendations(movie_title, num_recommendations)
        
        if not recommendations:
            return []
        
        # Enhance with OMDb data
        enhanced_recommendations = []
        for rec in recommendations:
            try:
                # Get detailed movie data from OMDb
                movie_details = movie_service.get_movie_full_details(rec['title'])
                
                if movie_details['found']:
                    # Merge recommendation data with OMDb data
                    enhanced_rec = {
                        **rec,  # Original recommendation data
                        **movie_details,  # OMDb data
                        'recommendation_score': rec['similarity_score']  # Preserve similarity score
                    }
                    enhanced_recommendations.append(enhanced_rec)
                else:
                    # Keep original recommendation if OMDb lookup fails
                    enhanced_recommendations.append(rec)
                    
            except Exception as e:
                print(f"⚠️ Failed to enhance recommendation for '{rec['title']}': {e}")
                enhanced_recommendations.append(rec)
        
        print(f"✅ Enhanced {len(enhanced_recommendations)} recommendations")
        return enhanced_recommendations
    
    def get_available_genres(self) -> List[str]:
        """
        Get list of available genres in the dataset with enhanced parsing.

        Returns:
            List[str]: List of unique genres
        """
        if not self.is_loaded and not self.load_processed_data():
            return []

        try:
            # Extract all genres from the dataset
            all_genres = []
            for genres_str in self.processed_movies['genres'].dropna():
                # Handle multiple separators: pipe, comma, space
                genres_str = str(genres_str).replace('|', ' ').replace(',', ' ')
                genres = [g.strip() for g in genres_str.split() if g.strip()]
                all_genres.extend(genres)

            # Get unique genres and sort
            unique_genres = sorted(list(set(all_genres)))

            print(f"✅ Found {len(unique_genres)} unique genres")
            return unique_genres

        except Exception as e:
            print(f"❌ Error getting genres: {e}")
            return []
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the recommendation dataset.

        Returns:
            Dict[str, Any]: Dataset statistics
        """
        if not self.is_loaded and not self.load_processed_data():
            return {}

        try:
            # Calculate average similarity (excluding diagonal)
            similarity_values = self.similarity_matrix[self.similarity_matrix != 1.0]
            avg_similarity = float(np.mean(similarity_values)) if len(similarity_values) > 0 else 0.0

            stats = {
                'total_movies': len(self.processed_movies),
                'total_genres': len(self.get_available_genres()),
                'avg_similarity': avg_similarity,
                'matrix_shape': self.similarity_matrix.shape,
                'data_columns': list(self.processed_movies.columns),
                'sample_movies': self.processed_movies['title'].head(5).tolist(),
                'memory_usage_mb': self.similarity_matrix.nbytes / (1024 * 1024)
            }

            return stats

        except Exception as e:
            print(f"❌ Error getting dataset stats: {e}")
            return {}

# Global recommendation service instance
recommendation_service = RecommendationService()
