$(document).ready(function() {
    let searchTimeout;
    const searchInput = $('#search-input');
    const suggestionsContainer = $('#search-suggestions');

    function debounce(func, wait) {
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(searchTimeout);
                func(...args);
            };
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(later, wait);
        };
    }

    function performSearch(query) {
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        $.ajax({
            url: '/ajax/search/',
            type: 'GET',
            data: { q: query },
            success: function(response) {
                displaySuggestions(response.results);
            },
            error: function(xhr, status, error) {
                console.error('Search error:', error);
                hideSuggestions();
            }
        });
    }

    function displaySuggestions(results) {
        if (results.length === 0) {
            hideSuggestions();
            return;
        }
        
        let html = '';
        results.forEach(function(question) {
            html += `
                <div class="suggestion-item p-2 border-bottom border-secondary" style="cursor: pointer;" 
                     onclick="window.location.href='${question.url}'" 
                     onmouseover="this.style.backgroundColor='#495057'" 
                     onmouseout="this.style.backgroundColor='transparent'">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1 text-light">${escapeHtml(question.title)}</h6>
                            <p class="mb-1 text-muted small">${escapeHtml(question.content)}</p>
                            <small class="text-info">by ${escapeHtml(question.author)} • ${question.created_at}</small>
                        </div>
                        <span class="badge bg-primary ms-2">${question.rating}</span>
                    </div>
                </div>
            `;
        });
        
        suggestionsContainer.html(html);
        showSuggestions();
    }

    function showSuggestions() {
        suggestionsContainer.removeClass('d-none');
    }

    function hideSuggestions() {
        suggestionsContainer.addClass('d-none');
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }

    const debouncedSearch = debounce(performSearch, 300);

    searchInput.on('input', function() {
        const query = $(this).val().trim();
        debouncedSearch(query);
    });

    $(document).on('click', function(e) {
        if (!$(e.target).closest('#search-form').length) {
            hideSuggestions();
        }
    });

    searchInput.on('focus', function() {
        const query = $(this).val().trim();
        if (query.length >= 2) {
            debouncedSearch(query);
        }
    });

    let currentSuggestionIndex = -1;
    
    searchInput.on('keydown', function(e) {
        const suggestions = $('.suggestion-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentSuggestionIndex = Math.min(currentSuggestionIndex + 1, suggestions.length - 1);
            highlightSuggestion(suggestions, currentSuggestionIndex);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentSuggestionIndex = Math.max(currentSuggestionIndex - 1, -1);
            highlightSuggestion(suggestions, currentSuggestionIndex);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentSuggestionIndex >= 0 && suggestions.length > 0) {
                suggestions.eq(currentSuggestionIndex).click();
            }
        } else if (e.key === 'Escape') {
            hideSuggestions();
            currentSuggestionIndex = -1;
        }
    });

    function highlightSuggestion(suggestions, index) {
        suggestions.css('background-color', 'transparent');
        if (index >= 0 && index < suggestions.length) {
            suggestions.eq(index).css('background-color', '#495057');
        }
    }

    searchInput.on('input', function() {
        currentSuggestionIndex = -1;
    });
}); 