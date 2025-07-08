#!/usr/bin/env python3
"""
Movie Preprocessing Module for Recommendation System
Handles data loading, text cleaning, TF-IDF vectorization, and similarity calculations.
"""

import os
import sys
import pandas as pd
import numpy as np
import pickle
import re
import string
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

# ML and NLP imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import joblib

# Add the src directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config_loader import get_config, config

class MoviePreprocessor:
    """
    Movie data preprocessing class for building recommendation system.
    Handles text cleaning, TF-IDF vectorization, and similarity matrix generation.
    """
    
    def __init__(self):
        """Initialize the preprocessor with configuration settings."""
        self.config = config
        self.data_file = get_config('recommendations.data_file', 'movies.csv')
        self.processed_data_dir = get_config('recommendations.processed_data_dir', 'data/processed')
        self.text_features = get_config('recommendations.text_features', 
                                       ['genres', 'keywords', 'overview'])
        self.tfidf_params = get_config('recommendations.tfidf_params', {})
        self.preprocessing_params = get_config('recommendations.preprocessing', {})
        
        # Initialize NLTK components
        try:
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            print("⚠️ NLTK data not found, downloading...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        
        # Create processed data directory
        self.processed_data_path = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / self.processed_data_dir
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ MoviePreprocessor initialized")
        print(f"📁 Data file: {self.data_file}")
        print(f"📂 Processed data directory: {self.processed_data_path}")
    
    def load_data(self) -> pd.DataFrame:
        """
        Load movie data from CSV file.
        
        Returns:
            pd.DataFrame: Loaded movie data
        """
        try:
            # Look for the data file in multiple locations
            possible_paths = [
                Path(os.path.dirname(os.path.abspath(__file__))) / '..' / self.data_file,
                Path(os.path.dirname(os.path.abspath(__file__))) / '..' / 'data' / 'raw' / self.data_file,
                Path(self.data_file)
            ]
            
            data_path = None
            for path in possible_paths:
                if path.exists():
                    data_path = path
                    break
            
            if data_path is None:
                # Create a sample dataset if no file is found
                print("⚠️ No movies.csv found, creating sample dataset...")
                return self._create_sample_dataset()
            
            print(f"📖 Loading data from: {data_path}")
            df = pd.read_csv(data_path)
            
            print(f"✅ Loaded {len(df)} movies")
            print(f"📊 Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print("🔄 Creating sample dataset instead...")
            return self._create_sample_dataset()
    
    def _create_sample_dataset(self) -> pd.DataFrame:
        """Create a sample movie dataset for demonstration."""
        sample_data = {
            'title': [
                'The Shawshank Redemption', 'The Godfather', 'The Dark Knight',
                'Pulp Fiction', 'Forrest Gump', 'Inception', 'The Matrix',
                'Goodfellas', 'Fight Club', 'Star Wars', 'Casablanca',
                'The Avengers', 'Titanic', 'Avatar', 'Jurassic Park',
                'Terminator 2', 'Back to the Future', 'Alien', 'Blade Runner',
                'The Silence of the Lambs'
            ],
            'genres': [
                'Drama', 'Crime Drama', 'Action Crime Drama',
                'Crime Drama', 'Drama Romance', 'Action Sci-Fi Thriller',
                'Action Sci-Fi', 'Crime Drama', 'Drama Thriller', 
                'Adventure Fantasy Sci-Fi', 'Drama Romance War',
                'Action Adventure Sci-Fi', 'Drama Romance',
                'Action Adventure Fantasy Sci-Fi', 'Adventure Sci-Fi Thriller',
                'Action Sci-Fi Thriller', 'Adventure Comedy Sci-Fi',
                'Horror Sci-Fi Thriller', 'Sci-Fi Thriller', 'Crime Horror Thriller'
            ],
            'overview': [
                'Two imprisoned men bond over years finding solace and redemption',
                'The aging patriarch of an organized crime dynasty transfers control',
                'Batman raises the stakes in his war on crime with the Joker',
                'The lives of two mob hitmen intertwine in four tales of violence',
                'The presidencies of Kennedy and Johnson through an Alabama man',
                'A thief steals corporate secrets through dream-sharing technology',
                'A computer programmer fights an underground war against machines',
                'The story of Henry Hill and his life in the mob',
                'An insomniac office worker forms an underground fight club',
                'Luke Skywalker joins forces with a Jedi Knight to rescue Princess Leia',
                'A cynical American expatriate struggles to help his former lover',
                'Earths mightiest heroes must come together to stop Loki',
                'A seventeen-year-old aristocrat falls in love with a poor artist',
                'A paraplegic Marine dispatched to the moon Pandora',
                'A paleontologist visiting a dinosaur theme park',
                'A cyborg assassin sent back in time',
                'A teenager accidentally sent back in time',
                'A space merchant vessel receives an unknown transmission',
                'A blade runner must pursue and terminate replicants',
                'A young FBI cadet must gain the trust of imprisoned cannibal'
            ],
            'keywords': [
                'prison friendship hope redemption', 'mafia family loyalty power',
                'batman joker chaos order', 'crime violence nonlinear narrative',
                'vietnam war disability friendship', 'dreams reality heist mind',
                'virtual reality artificial intelligence rebellion', 'organized crime loyalty betrayal',
                'insomnia consumerism masculinity', 'space opera rebellion empire',
                'world war ii resistance love', 'superhero team alien invasion',
                'ship disaster class love', 'alien world environmental message',
                'dinosaurs science theme park', 'time travel cyborg future',
                'time travel family comedy', 'space horror alien creature',
                'dystopia android identity', 'serial killer psychology fbi'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        
        # Save sample dataset
        sample_path = self.processed_data_path.parent / self.data_file
        df.to_csv(sample_path, index=False)
        print(f"💾 Saved sample dataset to: {sample_path}")

        return df

    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text data.

        Args:
            text (str): Raw text to clean

        Returns:
            str: Cleaned text
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""

        # Convert to lowercase
        if self.preprocessing_params.get('lowercase', True):
            text = text.lower()

        # Remove punctuation
        if self.preprocessing_params.get('remove_punctuation', True):
            text = text.translate(str.maketrans('', '', string.punctuation))

        # Remove extra whitespace and numbers
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\d+', '', text)

        # Tokenize
        tokens = word_tokenize(text)

        # Remove stopwords
        if self.preprocessing_params.get('remove_stopwords', True):
            tokens = [token for token in tokens if token not in self.stop_words]

        # Filter by minimum word length
        min_length = self.preprocessing_params.get('min_word_length', 2)
        tokens = [token for token in tokens if len(token) >= min_length]

        # Lemmatize
        if self.preprocessing_params.get('lemmatize', True):
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]

        return ' '.join(tokens)

    def create_combined_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create combined text features for each movie.

        Args:
            df (pd.DataFrame): Movie dataframe

        Returns:
            pd.DataFrame: Dataframe with combined features
        """
        print("🔄 Creating combined text features...")

        # Create a copy to avoid modifying original
        processed_df = df.copy()

        # Clean individual text features
        for feature in self.text_features:
            if feature in processed_df.columns:
                print(f"   Cleaning {feature}...")
                processed_df[f'{feature}_clean'] = processed_df[feature].apply(self.clean_text)
            else:
                print(f"   ⚠️ Feature '{feature}' not found in data, skipping...")
                processed_df[f'{feature}_clean'] = ""

        # Combine all cleaned features
        feature_columns = [f'{feature}_clean' for feature in self.text_features
                          if f'{feature}_clean' in processed_df.columns]

        processed_df['combined_features'] = processed_df[feature_columns].apply(
            lambda x: ' '.join(x.astype(str)), axis=1
        )

        print(f"✅ Combined features created for {len(processed_df)} movies")
        return processed_df

    def create_tfidf_matrix(self, df: pd.DataFrame) -> Tuple[Any, Any]:
        """
        Create TF-IDF matrix from combined features.

        Args:
            df (pd.DataFrame): Dataframe with combined features

        Returns:
            Tuple[TfidfVectorizer, sparse matrix]: Vectorizer and TF-IDF matrix
        """
        print("🔠 Creating TF-IDF matrix...")

        # Get TF-IDF parameters from config
        tfidf_params = {
            'max_features': self.tfidf_params.get('max_features', 5000),
            'stop_words': self.tfidf_params.get('stop_words', 'english'),
            'ngram_range': tuple(self.tfidf_params.get('ngram_range', [1, 2])),
            'min_df': self.tfidf_params.get('min_df', 2),
            'max_df': self.tfidf_params.get('max_df', 0.8)
        }

        print(f"   TF-IDF parameters: {tfidf_params}")

        # Create and fit TF-IDF vectorizer
        vectorizer = TfidfVectorizer(**tfidf_params)
        tfidf_matrix = vectorizer.fit_transform(df['combined_features'])

        print(f"✅ TF-IDF matrix created: {tfidf_matrix.shape}")
        return vectorizer, tfidf_matrix

    def create_similarity_matrix(self, tfidf_matrix) -> np.ndarray:
        """
        Create cosine similarity matrix from TF-IDF matrix.

        Args:
            tfidf_matrix: TF-IDF sparse matrix

        Returns:
            np.ndarray: Cosine similarity matrix
        """
        print("📐 Computing cosine similarity matrix...")

        similarity_matrix = cosine_similarity(tfidf_matrix)

        print(f"✅ Similarity matrix created: {similarity_matrix.shape}")
        return similarity_matrix

    def save_processed_data(self, df: pd.DataFrame, vectorizer, tfidf_matrix,
                           similarity_matrix: np.ndarray) -> Dict[str, str]:
        """
        Save all processed data to pickle files.

        Args:
            df (pd.DataFrame): Processed movie dataframe
            vectorizer: TF-IDF vectorizer
            tfidf_matrix: TF-IDF sparse matrix
            similarity_matrix (np.ndarray): Cosine similarity matrix

        Returns:
            Dict[str, str]: Dictionary of saved file paths
        """
        print("💾 Saving processed data...")

        # Create movie title to index mapping
        movie_indices = pd.Series(df.index, index=df['title']).to_dict()

        # File paths
        files = {
            'similarity_matrix': self.processed_data_path / get_config('recommendations.similarity_matrix_file', 'similarity_matrix.pkl'),
            'tfidf_matrix': self.processed_data_path / get_config('recommendations.tfidf_matrix_file', 'tfidf_matrix.pkl'),
            'movie_indices': self.processed_data_path / get_config('recommendations.movie_indices_file', 'movie_indices.pkl'),
            'processed_movies': self.processed_data_path / get_config('recommendations.processed_movies_file', 'processed_movies.pkl'),
            'tfidf_vectorizer': self.processed_data_path / 'tfidf_vectorizer.pkl'
        }

        # Save all files
        try:
            joblib.dump(similarity_matrix, files['similarity_matrix'])
            joblib.dump(tfidf_matrix, files['tfidf_matrix'])
            joblib.dump(movie_indices, files['movie_indices'])
            joblib.dump(df, files['processed_movies'])
            joblib.dump(vectorizer, files['tfidf_vectorizer'])

            print("✅ All processed data saved successfully:")
            for name, path in files.items():
                print(f"   📄 {name}: {path}")

            return {name: str(path) for name, path in files.items()}

        except Exception as e:
            print(f"❌ Error saving processed data: {e}")
            raise e

    def process_all(self) -> Dict[str, str]:
        """
        Run the complete preprocessing pipeline.

        Returns:
            Dict[str, str]: Dictionary of saved file paths
        """
        print("🚀 Starting complete preprocessing pipeline...")

        try:
            # Step 1: Load data
            df = self.load_data()

            # Step 2: Create combined features
            processed_df = self.create_combined_features(df)

            # Step 3: Create TF-IDF matrix
            vectorizer, tfidf_matrix = self.create_tfidf_matrix(processed_df)

            # Step 4: Create similarity matrix
            similarity_matrix = self.create_similarity_matrix(tfidf_matrix)

            # Step 5: Save all processed data
            saved_files = self.save_processed_data(processed_df, vectorizer,
                                                 tfidf_matrix, similarity_matrix)

            print("🎉 Preprocessing pipeline completed successfully!")
            return saved_files

        except Exception as e:
            print(f"❌ Preprocessing pipeline failed: {e}")
            raise e

    def check_processed_data_exists(self) -> bool:
        """
        Check if processed data files already exist.

        Returns:
            bool: True if all required files exist
        """
        required_files = [
            'similarity_matrix.pkl',
            'movie_indices.pkl',
            'processed_movies.pkl'
        ]

        for filename in required_files:
            file_path = self.processed_data_path / filename
            if not file_path.exists():
                return False

        return True

# Convenience function for standalone usage
def preprocess_movies(force_reprocess: bool = False) -> Dict[str, str]:
    """
    Convenience function to run movie preprocessing.

    Args:
        force_reprocess (bool): Force reprocessing even if files exist

    Returns:
        Dict[str, str]: Dictionary of processed file paths
    """
    preprocessor = MoviePreprocessor()

    if not force_reprocess and preprocessor.check_processed_data_exists():
        print("✅ Processed data already exists. Use force_reprocess=True to regenerate.")
        return {}

    return preprocessor.process_all()

if __name__ == "__main__":
    # Run preprocessing when script is executed directly
    import argparse

    parser = argparse.ArgumentParser(description='Movie Recommendation Preprocessing')
    parser.add_argument('--force', action='store_true',
                       help='Force reprocessing even if files exist')

    args = parser.parse_args()

    try:
        saved_files = preprocess_movies(force_reprocess=args.force)
        if saved_files:
            print("\n🎯 Preprocessing completed! Files saved:")
            for name, path in saved_files.items():
                print(f"   {name}: {path}")
    except Exception as e:
        print(f"\n❌ Preprocessing failed: {e}")
        sys.exit(1)
