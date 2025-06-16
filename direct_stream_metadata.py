#!/usr/bin/env python3

import requests
import re
import time
from mutagen.mp4 import MP4
from mutagen.id3 import ID3NoHeaderError
import io
from urllib.parse import urljoin

class HLSMetadataExtractor:
    def __init__(self, base_url="https://streams.blob.core.windows.net/rock/FLAC/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_latest_segments(self):
        """Fetch the current m3u8 playlist and extract latest segment URLs"""
        try:
            playlist_url = urljoin(self.base_url, "stream.m3u8")
            response = self.session.get(playlist_url)
            response.raise_for_status()
            
            # Parse m3u8 to get segment filenames
            segments = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    segments.append(line)
            
            # Return the last few segments (most recent)
            return segments[-3:] if segments else []
            
        except Exception as e:
            print(f"Error fetching playlist: {e}")
            return []
    
    def download_segment(self, segment_filename):
        """Download a specific segment file"""
        try:
            segment_url = urljoin(self.base_url, segment_filename)
            response = self.session.get(segment_url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading segment {segment_filename}: {e}")
            return None
    
    def extract_metadata_from_segment(self, segment_data):
        """Extract ID3/metadata from fMP4 segment"""
        try:
            # Create file-like object from segment data
            segment_io = io.BytesIO(segment_data)
            
            # Try to parse as MP4 (fMP4 format)
            try:
                mp4_file = MP4(segment_io)
                
                # Extract metadata from MP4 tags
                metadata = {}
                if mp4_file.tags:
                    # Common MP4 metadata atoms
                    metadata['artist'] = mp4_file.tags.get('\xa9ART', [''])[0]
                    metadata['title'] = mp4_file.tags.get('\xa9nam', [''])[0] 
                    metadata['album'] = mp4_file.tags.get('\xa9alb', [''])[0]
                    
                    # Also check for ID3 tags embedded in MP4
                    if any(metadata.values()):
                        return metadata
                        
            except Exception as mp4_error:
                print(f"MP4 parsing failed: {mp4_error}")
            
            # If MP4 parsing fails, look for ID3 tags in the raw data
            segment_io.seek(0)
            data = segment_io.read()
            
            # Search for ID3v2 header (starts with "ID3")
            id3_start = data.find(b'ID3')
            if id3_start != -1:
                try:
                    id3_data = io.BytesIO(data[id3_start:])
                    from mutagen.id3 import ID3
                    id3 = ID3(id3_data)
                    
                    return {
                        'artist': str(id3.get('TPE1', '')),
                        'title': str(id3.get('TIT2', '')),
                        'album': str(id3.get('TALB', ''))
                    }
                except Exception as id3_error:
                    print(f"ID3 parsing failed: {id3_error}")
            
            return {'artist': '', 'title': '', 'album': ''}
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {'artist': '', 'title': '', 'album': ''}
    
    def get_current_metadata(self):
        """Get the current playing metadata"""
        segments = self.get_latest_segments()
        
        if not segments:
            print("No segments found")
            return {'artist': '', 'title': '', 'album': ''}
        
        # Try the most recent segments first
        for segment in reversed(segments):
            print(f"Trying segment: {segment}")
            segment_data = self.download_segment(segment)
            
            if segment_data:
                metadata = self.extract_metadata_from_segment(segment_data)
                if any(metadata.values()):  # If we found any metadata
                    return metadata
        
        print("No metadata found in any segments")
        return {'artist': '', 'title': '', 'album': ''}

def extract_stream_metadata():
    """Main function to extract current stream metadata"""
    extractor = HLSMetadataExtractor()
    return extractor.get_current_metadata()

if __name__ == "__main__":
    print("Extracting metadata from Savvy Beast Radio HLS stream...")
    metadata = extract_stream_metadata()
    
    print("\nCurrent Track:")
    print(f"Artist: {metadata['artist']}")
    print(f"Title: {metadata['title']}")
    print(f"Album: {metadata['album']}")