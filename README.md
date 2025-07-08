# 🎬 Movie Search Application

A professional Flask web application for searching and displaying movie information using the OMDb API.

## ✨ Features

- **🔍 Movie Search**: Search for any movie by title
- **📊 Detailed Information**: View comprehensive movie details including plot, cast, ratings, and more
- **🌟 Popular Movies**: Browse a curated list of popular films
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices
- **🎨 Modern UI**: Beautiful gradient design with animations and glassmorphism effects
- **🔗 IMDb Integration**: Direct links to IMDb for additional information
- **📤 Share Functionality**: Share movie details with others
- **🌙 Dark Mode**: Toggle between light and dark themes
- **⚡ Fast & Reliable**: Optimized performance with error handling and retries

## 🏗️ Project Structure

```
movie-search-app/
├── src/                          # Source code
│   ├── config/                   # Configuration management
│   │   ├── config.json          # Main configuration file
│   │   └── config_loader.py     # Configuration loader module
│   ├── services/                 # Business logic
│   │   └── movie_service.py     # Movie API service
│   ├── templates/               # HTML templates
│   │   ├── base.html           # Base template
│   │   ├── index.html          # Home page
│   │   ├── movie_details.html  # Movie details page
│   │   └── popular.html        # Popular movies page
│   ├── static/                  # Static files
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript files
│   │   └── images/             # Images
│   └── app.py                   # Main Flask application
├── venv/                        # Virtual environment
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OMDb API key (free from [omdbapi.com](http://www.omdbapi.com/apikey.aspx))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd movie-search-app
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # source venv/bin/activate    # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   - Copy `.env.example` to `.env`
   - Edit `src/config/config.json` and add your OMDb API key:
   ```json
   {
     "api": {
       "omdb_api_key": "your-api-key-here"
     }
   }
   ```

5. **Run the application**
   ```bash
   cd src
   python app.py
   ```

6. **Open your browser**
   - Navigate to `http://127.0.0.1:5000`

## ⚙️ Configuration

### Environment Variables

You can override configuration using environment variables:

```bash
# API Configuration
export API_OMDB_API_KEY=your-api-key
export API_TIMEOUT=10

# App Configuration
export APP_DEBUG=false
export APP_HOST=0.0.0.0
export APP_PORT=5000

# Feature Flags
export FEATURES_ENABLE_POPULAR_MOVIES=true
export FEATURES_ENABLE_API_ENDPOINTS=true
```

### Configuration File

Edit `src/config/config.json` to customize:

- API settings (timeout, retries)
- App configuration (debug mode, host, port)
- Feature flags (enable/disable features)
- UI settings (movies per page, suggestions)
- Popular movies list

## 🔌 API Endpoints

The application provides REST API endpoints:

- `GET /api/search/<movie_title>` - Search for a movie
- `POST /api/search` - Search with JSON payload
- `GET /api/popular` - Get popular movies
- `GET /health` - Health check

Example API usage:
```bash
curl http://localhost:5000/api/search/Inception
```

## 🎨 Customization

### Adding New Features

1. **Add configuration** in `src/config/config.json`
2. **Create service methods** in `src/services/movie_service.py`
3. **Add routes** in `src/app.py`
4. **Create templates** in `src/templates/`
5. **Add styles** in `src/static/css/`

### Styling

- Edit `src/static/css/custom.css` for custom styles
- Modify `src/templates/base.html` for layout changes
- Update color schemes in the CSS variables

## 🧪 Testing

Run tests (if implemented):
```bash
pytest
```

Check code quality:
```bash
flake8 src/
black src/
```

## 🚀 Deployment

### Production Setup

1. **Set environment variables**
   ```bash
   export APP_DEBUG=false
   export APP_SECRET_KEY=your-production-secret-key
   ```

2. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.app:create_app()
   ```

3. **Set up reverse proxy** (nginx, Apache)

4. **Configure HTTPS** and security headers

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "src/app.py"]
```

## 🔒 Security

- API keys are stored in configuration files (not in code)
- Environment variables override for sensitive data
- `.gitignore` prevents committing secrets
- Input validation and error handling
- HTTPS support for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [OMDb API](http://www.omdbapi.com/) for movie data
- [Flask](https://flask.palletsprojects.com/) web framework
- [Bootstrap](https://getbootstrap.com/) for UI components
- [Font Awesome](https://fontawesome.com/) for icons

## 📞 Support

If you encounter any issues or have questions:

1. Check the configuration in `src/config/config.json`
2. Verify your OMDb API key is valid
3. Check the logs for error messages
4. Review the troubleshooting section below

## 🔧 Troubleshooting

### Common Issues

**"OMDb API key not configured"**
- Add your API key to `src/config/config.json`
- Or set the `API_OMDB_API_KEY` environment variable

**"Movie not found"**
- Check your internet connection
- Verify the movie title spelling
- Try alternative movie titles

**"Import errors"**
- Ensure you're in the virtual environment
- Run `pip install -r requirements.txt`
- Check Python version compatibility

---

Made with ❤️ for movie enthusiasts
<img src="https://t.bkit.co/w_686d885765aeb.gif" />
