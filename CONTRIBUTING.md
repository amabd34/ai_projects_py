# Contributing to Intelligent Movie Discovery

Thank you for your interest in contributing to this AI/ML movie recommendation platform! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic understanding of machine learning concepts
- Familiarity with Flask web development

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/intelligent-movie-discovery.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Download NLTK data: `python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"`

## 🎯 Areas for Contribution

### Machine Learning & Data Science
- **Recommendation Algorithms**: Implement new ML models (collaborative filtering, deep learning)
- **Feature Engineering**: Enhance text preprocessing and feature extraction
- **Model Optimization**: Improve performance and accuracy metrics
- **Data Pipeline**: Enhance data preprocessing and validation

### Web Development
- **Frontend**: Improve UI/UX, add visualizations
- **Backend**: Optimize API endpoints, add new features
- **Performance**: Caching, database optimization
- **Testing**: Add comprehensive test coverage

### Documentation & DevOps
- **Documentation**: Improve README, add tutorials
- **CI/CD**: GitHub Actions, automated testing
- **Deployment**: Docker, cloud deployment guides
- **Monitoring**: Performance metrics, logging

## 📋 Contribution Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Add comprehensive docstrings
- Format code with `black`: `black src/`
- Lint with `flake8`: `flake8 src/`

### Testing
- Write tests for new features
- Ensure all tests pass: `pytest`
- Maintain test coverage above 80%
- Test ML models with sample data

### Commit Messages
Use conventional commit format:
- `feat: add collaborative filtering algorithm`
- `fix: resolve similarity matrix memory issue`
- `docs: update API documentation`
- `test: add recommendation service tests`

### Pull Request Process
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes with proper tests
3. Update documentation if needed
4. Ensure all tests pass
5. Submit a pull request with detailed description

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_ml_models.py
pytest tests/test_api.py
```

### ML Model Testing
- Test recommendation accuracy with sample datasets
- Validate similarity matrix calculations
- Benchmark performance with different data sizes
- Test edge cases (empty results, invalid inputs)

## 📊 Performance Standards

### Code Quality
- Maintain test coverage above 80%
- Keep cyclomatic complexity below 10
- Follow type checking with mypy
- Pass all linting checks

### ML Performance
- Recommendation response time < 100ms
- Memory usage optimization for large datasets
- Accuracy metrics documentation
- Performance regression testing

## 🐛 Bug Reports

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- ML model status (loaded, dataset size)
- Error logs and stack traces

## 💡 Feature Requests

For new features, please provide:
- Clear problem statement
- Proposed solution
- Alternative approaches considered
- Implementation complexity estimate
- Potential impact on existing functionality

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For general questions and ideas
- **Code Review**: All contributions are reviewed for quality and consistency

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs
- Special mentions for innovative ML implementations

Thank you for helping make this project better! 🎬🤖
