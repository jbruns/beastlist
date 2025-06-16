// Playlist History JavaScript
class PlaylistHistory {
    constructor() {
        this.playlistData = [];
        this.filteredData = [];
        this.filters = {
            artist: '',
            title: '',
            album: '',
            year: ''
        };
        
        this.init();
    }
    
    init() {
        // Initialize filter event listeners
        this.setupFilterListeners();
        
        // Load initial data
        this.loadPlaylistData();
        
        // Set up auto-refresh (every 30 seconds)
        setInterval(() => {
            this.loadPlaylistData();
        }, 30000);
    }
    
    setupFilterListeners() {
        const artistFilter = document.getElementById('artistFilter');
        const titleFilter = document.getElementById('titleFilter');
        const albumFilter = document.getElementById('albumFilter');
        const yearFilter = document.getElementById('yearFilter');
        const clearButton = document.getElementById('clearFilters');
        
        // Add event listeners for real-time filtering
        artistFilter.addEventListener('input', (e) => {
            this.filters.artist = e.target.value.toLowerCase();
            this.applyFilters();
        });
        
        titleFilter.addEventListener('input', (e) => {
            this.filters.title = e.target.value.toLowerCase();
            this.applyFilters();
        });
        
        albumFilter.addEventListener('input', (e) => {
            this.filters.album = e.target.value.toLowerCase();
            this.applyFilters();
        });
        
        yearFilter.addEventListener('input', (e) => {
            this.filters.year = e.target.value.toLowerCase();
            this.applyFilters();
        });
        
        // Clear filters button
        clearButton.addEventListener('click', () => {
            this.clearAllFilters();
        });
    }
    
    async loadPlaylistData() {
        const playlistContainer = document.getElementById('playlistHistory');
        
        try {
            // Show loading state
            playlistContainer.innerHTML = '<div class="loading">Loading playlist history...</div>';
            
            // In a real implementation, this would fetch from your Azure Function API
            // For now, we'll use mock data
            const response = await this.fetchPlaylistFromAPI();
            
            if (response.success) {
                this.playlistData = response.data;
                this.applyFilters();
            } else {
                throw new Error('Failed to load playlist data');
            }
            
        } catch (error) {
            console.error('Error loading playlist:', error);
            playlistContainer.innerHTML = '<div class="error">Error loading playlist history. Please try again later.</div>';
        }
    }
    
    async fetchPlaylistFromAPI() {
        try {
            const response = await fetch('/api/playlist');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching from API, falling back to mock data:', error);
            // Fallback to mock data if API fails
            const mockData = this.generateMockData();
            return {
                success: true,
                data: mockData
            };
        }
    }
    
    generateMockData() {
        // Generate mock playlist data for demonstration
        const artists = ['The Beatles', 'Pink Floyd', 'Led Zeppelin', 'Queen', 'The Rolling Stones', 'AC/DC', 'Metallica', 'Nirvana'];
        const albums = ['Abbey Road', 'The Dark Side of the Moon', 'Led Zeppelin IV', 'A Night at the Opera', 'Sticky Fingers', 'Back in Black', 'Master of Puppets', 'Nevermind'];
        const titles = ['Come Together', 'Money', 'Stairway to Heaven', 'Bohemian Rhapsody', 'Paint It Black', 'Thunderstruck', 'Enter Sandman', 'Smells Like Teen Spirit'];
        const years = [1969, 1973, 1971, 1975, 1971, 1980, 1986, 1991];
        
        const mockData = [];
        for (let i = 0; i < 50; i++) {
            const randomIndex = Math.floor(Math.random() * artists.length);
            const timestamp = new Date(Date.now() - (i * 2 * 60 * 1000)); // Every 2 minutes going back
            
            mockData.push({
                timestamp: timestamp.toISOString(),
                artist: artists[randomIndex],
                title: titles[randomIndex],
                album: albums[randomIndex],
                year: years[randomIndex]
            });
        }
        
        return mockData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }
    
    applyFilters() {
        // Filter the data based on current filter values
        this.filteredData = this.playlistData.filter(item => {
            const artistMatch = !this.filters.artist || 
                (item.artist && item.artist.toLowerCase().includes(this.filters.artist));
            const titleMatch = !this.filters.title || 
                (item.title && item.title.toLowerCase().includes(this.filters.title));
            const albumMatch = !this.filters.album || 
                (item.album && item.album.toLowerCase().includes(this.filters.album));
            const yearMatch = !this.filters.year || 
                (item.year && item.year.toString().includes(this.filters.year));
            
            return artistMatch && titleMatch && albumMatch && yearMatch;
        });
        
        this.renderPlaylist();
    }
    
    renderPlaylist() {
        const playlistContainer = document.getElementById('playlistHistory');
        
        if (this.filteredData.length === 0) {
            playlistContainer.innerHTML = '<div class="no-results">No playlist entries match your current filters.</div>';
            return;
        }
        
        let html = '';
        this.filteredData.forEach(item => {
            const formattedTimestamp = this.formatTimestamp(item.timestamp);
            
            html += `
                <div class="playlist-item">
                    <div class="playlist-cell timestamp">${formattedTimestamp}</div>
                    <div class="playlist-cell artist">${this.escapeHtml(item.artist || '')}</div>
                    <div class="playlist-cell title">${this.escapeHtml(item.title || '')}</div>
                    <div class="playlist-cell album">${this.escapeHtml(item.album || '')}</div>
                    <div class="playlist-cell year">${item.year || ''}</div>
                </div>
            `;
        });
        
        playlistContainer.innerHTML = html;
    }
    
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 60) {
            return `${diffMins} min${diffMins !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    clearAllFilters() {
        // Clear all filter inputs
        document.getElementById('artistFilter').value = '';
        document.getElementById('titleFilter').value = '';
        document.getElementById('albumFilter').value = '';
        document.getElementById('yearFilter').value = '';
        
        // Reset filter values
        this.filters = {
            artist: '',
            title: '',
            album: '',
            year: ''
        };
        
        // Reapply filters (which will show all data)
        this.applyFilters();
    }
}

// Initialize the playlist when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const playlist = new PlaylistHistory();
});

// Add some additional functionality for a better user experience
document.addEventListener('DOMContentLoaded', () => {
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + / to focus on artist filter
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            document.getElementById('artistFilter').focus();
        }
        
        // Escape to clear all filters
        if (e.key === 'Escape') {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.type === 'text') {
                activeElement.blur();
            }
        }
    });
    
    // Add focus/blur effects for better UX
    const filterInputs = document.querySelectorAll('.filter-row input');
    filterInputs.forEach(input => {
        input.addEventListener('focus', (e) => {
            e.target.parentElement.style.backgroundColor = 'rgba(0, 192, 255, 0.1)';
        });
        
        input.addEventListener('blur', (e) => {
            e.target.parentElement.style.backgroundColor = '';
        });
    });
});