/**
 * Professional Dropdown Search Component for Movie Search
 * Provides real-time search suggestions with poster thumbnails
 */

class DropdownSearch {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            apiEndpoint: '/api/search/suggestions/',
            debounceDelay: 300,
            minQueryLength: 2,
            maxResults: 8,
            placeholder: 'Search for movies...',
            onSelect: null,
            ...options
        };
        
        this.searchTimeout = null;
        this.currentQuery = '';
        this.selectedIndex = -1;
        this.isLoading = false;
        this.results = [];
        
        this.init();
    }
    
    init() {
        this.createElements();
        this.bindEvents();
    }
    
    createElements() {
        // Create the main container
        this.container.innerHTML = `
            <div class="dropdown-search-container">
                <input type="text" 
                       class="dropdown-search-input" 
                       placeholder="${this.options.placeholder}"
                       autocomplete="off"
                       spellcheck="false">
                <i class="fas fa-search dropdown-search-icon"></i>
                <div class="dropdown-search-results"></div>
            </div>
        `;
        
        // Get references to elements
        this.input = this.container.querySelector('.dropdown-search-input');
        this.icon = this.container.querySelector('.dropdown-search-icon');
        this.resultsContainer = this.container.querySelector('.dropdown-search-results');
        this.dropdownContainer = this.container.querySelector('.dropdown-search-container');
    }
    
    bindEvents() {
        // Input events
        this.input.addEventListener('input', this.handleInput.bind(this));
        this.input.addEventListener('keydown', this.handleKeydown.bind(this));
        this.input.addEventListener('focus', this.handleFocus.bind(this));
        
        // Click outside to close
        document.addEventListener('click', this.handleClickOutside.bind(this));
        
        // Prevent form submission on enter if dropdown is open
        this.input.addEventListener('keypress', this.handleKeypress.bind(this));
    }
    
    handleInput(event) {
        const query = event.target.value.trim();
        this.currentQuery = query;
        this.selectedIndex = -1;
        
        // Clear previous timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // Hide results if query is too short
        if (query.length < this.options.minQueryLength) {
            this.hideResults();
            return;
        }
        
        // Debounce the search
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, this.options.debounceDelay);
    }
    
    handleKeydown(event) {
        if (!this.isResultsVisible()) return;
        
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                this.navigateDown();
                break;
            case 'ArrowUp':
                event.preventDefault();
                this.navigateUp();
                break;
            case 'Enter':
                event.preventDefault();
                this.selectCurrent();
                break;
            case 'Escape':
                this.hideResults();
                this.input.blur();
                break;
        }
    }
    
    handleKeypress(event) {
        // Prevent form submission if dropdown is open and Enter is pressed
        if (event.key === 'Enter' && this.isResultsVisible()) {
            event.preventDefault();
        }
    }
    
    handleFocus() {
        // Show results if we have a current query and results
        if (this.currentQuery.length >= this.options.minQueryLength && this.results.length > 0) {
            this.showResults();
        }
    }
    
    handleClickOutside(event) {
        if (!this.container.contains(event.target)) {
            this.hideResults();
        }
    }
    
    async performSearch(query) {
        if (query !== this.currentQuery) return; // Query changed while waiting
        
        this.setLoading(true);
        
        try {
            const response = await fetch(`${this.options.apiEndpoint}${encodeURIComponent(query)}`);
            const data = await response.json();
            
            // Check if query is still current
            if (query !== this.currentQuery) return;
            
            this.results = data.suggestions || [];
            this.renderResults();
            this.showResults();
            
        } catch (error) {
            console.error('Search failed:', error);
            this.showError('Search failed. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }
    
    renderResults() {
        if (this.results.length === 0) {
            this.resultsContainer.innerHTML = `
                <div class="dropdown-search-no-results">
                    <i class="fas fa-search me-2"></i>No movies found for "${this.currentQuery}"
                </div>
            `;
            return;
        }
        
        const resultsHtml = this.results.map((movie, index) => {
            const posterElement = movie.poster && movie.poster !== 'N/A' 
                ? `<img src="${movie.poster}" alt="${movie.title}" class="dropdown-search-poster" loading="lazy">`
                : `<div class="dropdown-search-poster-placeholder">
                     <i class="fas fa-film"></i>
                   </div>`;
            
            return `
                <div class="dropdown-search-item" data-index="${index}">
                    ${posterElement}
                    <div class="dropdown-search-info">
                        <div class="dropdown-search-title">${this.escapeHtml(movie.title)}</div>
                        <div class="dropdown-search-year">${movie.year}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        this.resultsContainer.innerHTML = resultsHtml;
        
        // Add click handlers to items
        this.resultsContainer.querySelectorAll('.dropdown-search-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.selectItem(index);
            });
        });
    }
    
    showError(message) {
        this.resultsContainer.innerHTML = `
            <div class="dropdown-search-no-results">
                <i class="fas fa-exclamation-triangle me-2"></i>${message}
            </div>
        `;
        this.showResults();
    }
    
    navigateDown() {
        this.selectedIndex = Math.min(this.selectedIndex + 1, this.results.length - 1);
        this.updateSelection();
    }
    
    navigateUp() {
        this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
        this.updateSelection();
    }
    
    updateSelection() {
        // Remove previous selection
        this.resultsContainer.querySelectorAll('.dropdown-search-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Add selection to current item
        if (this.selectedIndex >= 0) {
            const selectedItem = this.resultsContainer.querySelector(`[data-index="${this.selectedIndex}"]`);
            if (selectedItem) {
                selectedItem.classList.add('selected');
                selectedItem.scrollIntoView({ block: 'nearest' });
            }
        }
    }
    
    selectCurrent() {
        if (this.selectedIndex >= 0 && this.selectedIndex < this.results.length) {
            this.selectItem(this.selectedIndex);
        }
    }
    
    selectItem(index) {
        const movie = this.results[index];
        if (!movie) return;
        
        // Update input value
        this.input.value = movie.title;
        this.hideResults();
        
        // Call callback if provided
        if (this.options.onSelect) {
            this.options.onSelect(movie);
        } else {
            // Default behavior: redirect to movie details
            this.redirectToMovie(movie.title);
        }
    }
    
    redirectToMovie(title) {
        // Create a form and submit it to search for the movie
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/search';
        form.style.display = 'none';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'movie_title';
        input.value = title;
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        
        if (loading) {
            this.dropdownContainer.classList.add('loading');
            this.icon.className = 'fas fa-spinner dropdown-search-icon';
            this.resultsContainer.innerHTML = `
                <div class="dropdown-search-loading">
                    <span class="loading-spinner"></span>Searching...
                </div>
            `;
            this.showResults();
        } else {
            this.dropdownContainer.classList.remove('loading');
            this.icon.className = 'fas fa-search dropdown-search-icon';
        }
    }
    
    showResults() {
        this.resultsContainer.classList.add('show');
    }
    
    hideResults() {
        this.resultsContainer.classList.remove('show');
        this.selectedIndex = -1;
    }
    
    isResultsVisible() {
        return this.resultsContainer.classList.contains('show');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Public methods
    setValue(value) {
        this.input.value = value;
        this.currentQuery = value;
    }
    
    getValue() {
        return this.input.value;
    }
    
    focus() {
        this.input.focus();
    }
    
    clear() {
        this.input.value = '';
        this.currentQuery = '';
        this.hideResults();
    }
    
    destroy() {
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        document.removeEventListener('click', this.handleClickOutside.bind(this));
    }
}

// Auto-initialize dropdown search components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all elements with data-dropdown-search attribute
    document.querySelectorAll('[data-dropdown-search]').forEach(element => {
        const options = {};
        
        // Parse options from data attributes
        if (element.dataset.placeholder) {
            options.placeholder = element.dataset.placeholder;
        }
        if (element.dataset.minLength) {
            options.minQueryLength = parseInt(element.dataset.minLength);
        }
        
        new DropdownSearch(element, options);
    });
});

// Export for manual initialization
window.DropdownSearch = DropdownSearch;
