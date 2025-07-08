/**
 * Movie Search Application - Enhanced JavaScript Functionality
 */

class MovieSearchApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAnimations();
        this.setupSearchEnhancements();
        this.setupThemeToggle();
    }

    setupEventListeners() {
        // Search form enhancements
        const searchForms = document.querySelectorAll('form[action*="search"]');
        searchForms.forEach(form => {
            form.addEventListener('submit', this.handleSearchSubmit.bind(this));
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));

        // Image lazy loading
        this.setupLazyLoading();
    }

    handleSearchSubmit(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const input = form.querySelector('input[name="movie_title"]');

        if (submitBtn && input && input.value.trim()) {
            // Show loading state
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Searching...';
            submitBtn.disabled = true;

            // Store original state for potential restoration
            setTimeout(() => {
                if (submitBtn.disabled) {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            }, 10000); // Timeout after 10 seconds
        }
    }

    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + K to focus search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('input[name="movie_title"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }

        // Escape to clear search
        if (event.key === 'Escape') {
            const searchInput = document.querySelector('input[name="movie_title"]');
            if (searchInput && document.activeElement === searchInput) {
                searchInput.value = '';
            }
        }
    }

    setupAnimations() {
        // Animate cards on page load
        const cards = document.querySelectorAll('.card, .movie-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Parallax effect for background
        window.addEventListener('scroll', this.handleParallax.bind(this));
    }

    handleParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    }

    setupSearchEnhancements() {
        const searchInputs = document.querySelectorAll('input[name="movie_title"]');
        
        searchInputs.forEach(input => {
            // Add search suggestions
            this.setupSearchSuggestions(input);
            
            // Add input validation
            input.addEventListener('input', this.validateSearchInput.bind(this));
        });
    }

    setupSearchSuggestions(input) {
        const suggestions = [
            'Inception', 'The Matrix', 'Pulp Fiction', 'The Godfather',
            'Titanic', 'Avatar', 'Forrest Gump', 'The Dark Knight',
            'Star Wars', 'Jurassic Park', 'The Shawshank Redemption'
        ];

        // Create datalist for suggestions
        const datalist = document.createElement('datalist');
        datalist.id = 'movie-suggestions';
        
        suggestions.forEach(suggestion => {
            const option = document.createElement('option');
            option.value = suggestion;
            datalist.appendChild(option);
        });

        input.setAttribute('list', 'movie-suggestions');
        input.parentNode.appendChild(datalist);
    }

    validateSearchInput(event) {
        const input = event.target;
        const value = input.value.trim();
        
        // Remove any existing validation classes
        input.classList.remove('is-valid', 'is-invalid');
        
        if (value.length > 0) {
            if (value.length < 2) {
                input.classList.add('is-invalid');
            } else {
                input.classList.add('is-valid');
            }
        }
    }

    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        } else {
            // Fallback for older browsers
            images.forEach(img => {
                img.src = img.dataset.src;
            });
        }
    }

    setupThemeToggle() {
        // Create theme toggle button
        const themeToggle = document.createElement('button');
        themeToggle.className = 'btn btn-outline-light btn-sm position-fixed';
        themeToggle.style.cssText = 'top: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px;';
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        themeToggle.title = 'Toggle Dark Mode';
        
        themeToggle.addEventListener('click', this.toggleTheme.bind(this));
        document.body.appendChild(themeToggle);

        // Check for saved theme preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            this.enableDarkMode();
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    toggleTheme() {
        const body = document.body;
        const themeToggle = document.querySelector('.position-fixed');
        
        if (body.classList.contains('dark-mode')) {
            this.disableDarkMode();
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
            localStorage.setItem('theme', 'light');
        } else {
            this.enableDarkMode();
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            localStorage.setItem('theme', 'dark');
        }
    }

    enableDarkMode() {
        document.body.classList.add('dark-mode');
        // Add dark mode styles dynamically
        const darkModeStyles = `
            .dark-mode {
                filter: invert(1) hue-rotate(180deg);
            }
            .dark-mode img {
                filter: invert(1) hue-rotate(180deg);
            }
        `;
        
        let styleSheet = document.getElementById('dark-mode-styles');
        if (!styleSheet) {
            styleSheet = document.createElement('style');
            styleSheet.id = 'dark-mode-styles';
            document.head.appendChild(styleSheet);
        }
        styleSheet.textContent = darkModeStyles;
    }

    disableDarkMode() {
        document.body.classList.remove('dark-mode');
        const styleSheet = document.getElementById('dark-mode-styles');
        if (styleSheet) {
            styleSheet.remove();
        }
    }
}

// Utility functions
const MovieUtils = {
    shareMovie: function(title, year, url) {
        if (navigator.share) {
            navigator.share({
                title: `${title} (${year}) - Movie Details`,
                text: `Check out this movie: ${title} (${year})`,
                url: url || window.location.href
            }).catch(console.error);
        } else {
            // Fallback: copy to clipboard
            const textToCopy = `${title} (${year}) - ${url || window.location.href}`;
            navigator.clipboard.writeText(textToCopy).then(() => {
                this.showNotification('Movie link copied to clipboard!', 'success');
            }).catch(() => {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = textToCopy;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                this.showNotification('Movie link copied to clipboard!', 'success');
            });
        }
    },

    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = 'top: 20px; left: 50%; transform: translateX(-50%); z-index: 1050; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : 'info'}-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    },

    formatRuntime: function(runtime) {
        if (!runtime || runtime === 'N/A') return 'N/A';
        const minutes = parseInt(runtime);
        if (isNaN(minutes)) return runtime;
        
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        
        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins}m`;
    }
};

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MovieSearchApp();
});

// Make utilities globally available
window.MovieUtils = MovieUtils;
