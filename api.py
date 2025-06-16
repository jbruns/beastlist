#!/usr/bin/env python3

import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from azure.cosmosdb.table.tableservice import TableService

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Azure Table Storage configuration
AZURE_STORAGE_ACCOUNT = os.environ.get('AZURE_STORAGE_ACCOUNT', '')
AZURE_STORAGE_KEY = os.environ.get('AZURE_STORAGE_KEY', '')
AZURE_TABLE_NAME = os.environ.get('AZURE_TABLE_NAME', 'playlisthistory')

class PlaylistAPI:
    def __init__(self):
        if AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY:
            self.table_service = TableService(
                account_name=AZURE_STORAGE_ACCOUNT, 
                account_key=AZURE_STORAGE_KEY
            )
        else:
            self.table_service = None
            print("Warning: Azure Storage credentials not configured. Using mock data.")
    
    def get_playlist_history(self, limit=100):
        """Retrieve playlist history from Azure Table Storage"""
        try:
            if not self.table_service:
                return self.get_mock_data()
            
            # Query the table for recent entries
            entities = self.table_service.query_entities(
                AZURE_TABLE_NAME,
                num_results=limit
            )
            
            playlist_data = []
            for entity in entities:
                item = {
                    'timestamp': entity.get('timestamp', ''),
                    'artist': entity.get('artist', ''),
                    'title': entity.get('title', ''),
                    'album': entity.get('album', ''),
                    'year': entity.get('year', None)
                }
                playlist_data.append(item)
            
            # Sort by timestamp descending (most recent first)
            playlist_data.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return playlist_data
            
        except Exception as e:
            print(f"Error retrieving playlist data: {e}")
            return self.get_mock_data()
    
    def get_mock_data(self):
        """Generate mock data for testing when Azure Storage is not available"""
        artists = [
            'The Beatles', 'Pink Floyd', 'Led Zeppelin', 'Queen', 
            'The Rolling Stones', 'AC/DC', 'Metallica', 'Nirvana',
            'David Bowie', 'The Who', 'Black Sabbath', 'Deep Purple'
        ]
        albums = [
            'Abbey Road', 'The Dark Side of the Moon', 'Led Zeppelin IV', 
            'A Night at the Opera', 'Sticky Fingers', 'Back in Black',
            'Master of Puppets', 'Nevermind', 'The Rise and Fall of Ziggy Stardust',
            'Who\'s Next', 'Paranoid', 'Machine Head'
        ]
        titles = [
            'Come Together', 'Money', 'Stairway to Heaven', 'Bohemian Rhapsody',
            'Paint It Black', 'Thunderstruck', 'Enter Sandman', 'Smells Like Teen Spirit',
            'Heroes', 'Baba O\'Riley', 'Iron Man', 'Smoke on the Water'
        ]
        years = [1969, 1973, 1971, 1975, 1971, 1980, 1986, 1991, 1977, 1971, 1970, 1972]
        
        mock_data = []
        current_time = datetime.now()
        
        for i in range(50):
            random_index = i % len(artists)
            # Generate timestamps going back in time (every 2-5 minutes)
            minutes_ago = i * (2 + (i % 3))  # Vary the interval
            timestamp = current_time.replace(
                minute=current_time.minute - minutes_ago % 60,
                hour=current_time.hour - (minutes_ago // 60)
            )
            
            mock_data.append({
                'timestamp': timestamp.isoformat(),
                'artist': artists[random_index],
                'title': titles[random_index],
                'album': albums[random_index],
                'year': years[random_index]
            })
        
        return mock_data

# Initialize the API
playlist_api = PlaylistAPI()

@app.route('/api/playlist', methods=['GET'])
def get_playlist():
    """API endpoint to get playlist history"""
    try:
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 1000)  # Cap at 1000 entries
        
        playlist_data = playlist_api.get_playlist_history(limit)
        
        return jsonify({
            'success': True,
            'data': playlist_data,
            'count': len(playlist_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/playlist/search', methods=['GET'])
def search_playlist():
    """API endpoint to search playlist history"""
    try:
        # Get search parameters
        artist = request.args.get('artist', '').lower()
        title = request.args.get('title', '').lower()
        album = request.args.get('album', '').lower()
        year = request.args.get('year', '')
        limit = request.args.get('limit', 100, type=int)
        
        # Get all playlist data
        playlist_data = playlist_api.get_playlist_history(1000)  # Get more for filtering
        
        # Apply filters
        filtered_data = []
        for item in playlist_data:
            artist_match = not artist or (item.get('artist', '').lower().find(artist) != -1)
            title_match = not title or (item.get('title', '').lower().find(title) != -1)
            album_match = not album or (item.get('album', '').lower().find(album) != -1)
            year_match = not year or (str(item.get('year', '')).find(year) != -1)
            
            if artist_match and title_match and album_match and year_match:
                filtered_data.append(item)
        
        # Limit results
        filtered_data = filtered_data[:limit]
        
        return jsonify({
            'success': True,
            'data': filtered_data,
            'count': len(filtered_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'azure_configured': bool(AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY)
    })

@app.route('/')
def index():
    """Serve the main HTML page"""
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # For development
    app.run(debug=True, host='0.0.0.0', port=5000)