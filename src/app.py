#!/usr/bin/env python3
"""
Flask Movie Search Web Application - Professional Structure
Uses OMDb API to search and display movie information with proper configuration management.
"""

import os
import sys
from flask import Flask, render_template, request, jsonify

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_loader import config, get_config, is_feature_enabled
from services.movie_service import movie_service
from services.recommendation_service import recommendation_service

def create_app():
    """Application factory pattern for Flask app creation."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app_config = config.get_app_config()
    app.config.update(app_config)
    
    # Register routes
    register_routes(app)
    
    return app

def register_routes(app):
    """Register all application routes."""
    
    @app.route('/')
    def home():
        """Home page with search form."""
        search_suggestions = config.get_search_suggestions()
        return render_template('index.html', suggestions=search_suggestions)

    @app.route('/search', methods=['POST'])
    def search_movie():
        """Handle movie search."""
        movie_title = request.form.get('movie_title', '').strip()
        
        if not movie_title:
            return render_template('index.html', 
                                 error="Please enter a movie title",
                                 suggestions=config.get_search_suggestions())
        
        # Get movie details
        movie_data = movie_service.get_movie_full_details(movie_title)
        
        if movie_data["found"]:
            return render_template('movie_details.html', movie=movie_data)
        else:
            return render_template('index.html', 
                                 error=f"Movie '{movie_title}' not found. {movie_data.get('error', '')}",
                                 suggestions=config.get_search_suggestions())

    @app.route('/popular')
    def popular_movies():
        """Show popular movies if feature is enabled."""
        if not is_feature_enabled('enable_popular_movies'):
            return render_template('index.html', 
                                 error="Popular movies feature is disabled",
                                 suggestions=config.get_search_suggestions())
        
        popular_titles = config.get_popular_movies()
        movies = movie_service.get_popular_movies(popular_titles)
        
        return render_template('popular.html', movies=movies)

    @app.route('/api/search/<movie_title>')
    def api_search(movie_title):
        """API endpoint for movie search (JSON response)."""
        if not is_feature_enabled('enable_api_endpoints'):
            return jsonify({"error": "API endpoints are disabled"}), 403
        
        movie_data = movie_service.get_movie_full_details(movie_title)
        return jsonify(movie_data)

    @app.route('/api/search', methods=['POST'])
    def api_search_post():
        """API endpoint for movie search via POST."""
        if not is_feature_enabled('enable_api_endpoints'):
            return jsonify({"error": "API endpoints are disabled"}), 403
        
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({"error": "Missing 'title' in request body"}), 400
        
        movie_data = movie_service.get_movie_full_details(data['title'])
        return jsonify(movie_data)

    @app.route('/api/popular')
    def api_popular():
        """API endpoint for popular movies."""
        if not is_feature_enabled('enable_api_endpoints'):
            return jsonify({"error": "API endpoints are disabled"}), 403
        
        if not is_feature_enabled('enable_popular_movies'):
            return jsonify({"error": "Popular movies feature is disabled"}), 403
        
        popular_titles = config.get_popular_movies()
        movies = movie_service.get_popular_movies(popular_titles)
        
        return jsonify({
            "movies": movies,
            "count": len(movies)
        })

    @app.route('/recommendations')
    def recommendations_page():
        """Recommendations page."""
        if not is_feature_enabled('enable_recommendations'):
            return render_template('index.html',
                                 error="Recommendations feature is disabled",
                                 suggestions=config.get_search_suggestions())

        # Get available genres for the dropdown
        genres = recommendation_service.get_available_genres()
        return render_template('recommendations.html', genres=genres)

    @app.route('/recommendations/<movie_title>')
    def movie_recommendations(movie_title):
        """Get recommendations for a specific movie."""
        if not is_feature_enabled('enable_recommendations'):
            return render_template('index.html',
                                 error="Recommendations feature is disabled",
                                 suggestions=config.get_search_suggestions())

        # Get enhanced recommendations
        recommendations = recommendation_service.get_enhanced_recommendations(movie_title)

        if not recommendations:
            return render_template('recommendations.html',
                                 error=f"No recommendations found for '{movie_title}'",
                                 genres=recommendation_service.get_available_genres())

        return render_template('recommendation_results.html',
                             recommendations=recommendations,
                             source_movie=movie_title)

    @app.route('/recommendations/genre/<genre>')
    def genre_recommendations(genre):
        """Get recommendations by genre."""
        if not is_feature_enabled('enable_recommendations'):
            return render_template('index.html',
                                 error="Recommendations feature is disabled",
                                 suggestions=config.get_search_suggestions())

        # Get movies by genre
        recommendations = recommendation_service.get_recommendations_by_genre(genre)

        if not recommendations:
            return render_template('recommendations.html',
                                 error=f"No movies found for genre '{genre}'",
                                 genres=recommendation_service.get_available_genres())

        return render_template('recommendation_results.html',
                             recommendations=recommendations,
                             source_genre=genre)

    @app.route('/api/recommendations/<movie_title>')
    def api_movie_recommendations(movie_title):
        """API endpoint for movie recommendations."""
        if not is_feature_enabled('enable_api_endpoints') or not is_feature_enabled('enable_recommendations'):
            return jsonify({"error": "Recommendations API is disabled"}), 403

        num_recommendations = request.args.get('limit', 10, type=int)
        enhanced = request.args.get('enhanced', 'true').lower() == 'true'

        if enhanced:
            recommendations = recommendation_service.get_enhanced_recommendations(movie_title, num_recommendations)
        else:
            recommendations = recommendation_service.get_movie_recommendations(movie_title, num_recommendations)

        return jsonify({
            "source_movie": movie_title,
            "recommendations": recommendations,
            "count": len(recommendations)
        })

    @app.route('/api/recommendations/genre/<genre>')
    def api_genre_recommendations(genre):
        """API endpoint for genre-based recommendations."""
        if not is_feature_enabled('enable_api_endpoints') or not is_feature_enabled('enable_recommendations'):
            return jsonify({"error": "Recommendations API is disabled"}), 403

        num_recommendations = request.args.get('limit', 10, type=int)
        recommendations = recommendation_service.get_recommendations_by_genre(genre, num_recommendations)

        return jsonify({
            "genre": genre,
            "recommendations": recommendations,
            "count": len(recommendations)
        })

    @app.route('/api/recommendations/genres')
    def api_available_genres():
        """API endpoint for available genres."""
        if not is_feature_enabled('enable_api_endpoints') or not is_feature_enabled('enable_recommendations'):
            return jsonify({"error": "Recommendations API is disabled"}), 403

        genres = recommendation_service.get_available_genres()
        return jsonify({
            "genres": genres,
            "count": len(genres)
        })

    @app.route('/api/recommendations/stats')
    def api_recommendation_stats():
        """API endpoint for recommendation dataset statistics."""
        if not is_feature_enabled('enable_api_endpoints') or not is_feature_enabled('enable_recommendations'):
            return jsonify({"error": "Recommendations API is disabled"}), 403

        stats = recommendation_service.get_dataset_stats()
        return jsonify(stats)

    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "app": get_config('app.name'),
            "version": get_config('app.version'),
            "features": {
                "popular_movies": is_feature_enabled('enable_popular_movies'),
                "api_endpoints": is_feature_enabled('enable_api_endpoints'),
                "sharing": is_feature_enabled('enable_sharing'),
                "recommendations": is_feature_enabled('enable_recommendations')
            }
        })

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return render_template('index.html', 
                             error="Page not found",
                             suggestions=config.get_search_suggestions()), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return render_template('index.html', 
                             error="Internal server error. Please try again later.",
                             suggestions=config.get_search_suggestions()), 500

def main():
    """Main entry point for the application."""
    try:
        app = create_app()
        
        # Get configuration
        host = get_config('app.host', '127.0.0.1')
        port = get_config('app.port', 5000)
        debug = get_config('app.debug', False)
        
        print(f"🎬 Starting {get_config('app.name')} v{get_config('app.version')}")
        print(f"🌐 Server running on http://{host}:{port}")
        print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
        print(f"🎯 Features enabled:")
        print(f"   - Popular Movies: {'✅' if is_feature_enabled('enable_popular_movies') else '❌'}")
        print(f"   - API Endpoints: {'✅' if is_feature_enabled('enable_api_endpoints') else '❌'}")
        print(f"   - Sharing: {'✅' if is_feature_enabled('enable_sharing') else '❌'}")
        
        app.run(host=host, port=port, debug=debug)
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Please check your config.json file and ensure the OMDb API key is set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
