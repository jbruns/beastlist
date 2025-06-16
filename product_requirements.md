# Product Requirements Document: Web-Based Application for m3u8 Audio Stream Metadata

## 1. Introduction

This document outlines the requirements for a web-based application that interfaces with an m3u8 audio stream endpoint, containing a series of fMP4 audio chunks. The application will extract metadata from the audio stream, store it in a database, and provide a user-facing component to view playlist history with real-time filtering.

## 2. Goals

*   Extract artist, title, album, and year metadata information from the audio stream.
*   Store the metadata in a database, along with a timestamp.
*   Provide users with the ability to view playlist history.
*   Implement real-time filtering of the playlist fields without additional requests to the service.
*   Mirror the style of an existing website (https://www.savvybeastradio.com).

## 3. Detailed Plan

```mermaid
graph LR
    A[HLS Stream] --> B(Backend: Metadata Extractor - Azure Function);
    B --> C{Azure Table Storage};
    C --> D(Frontend: Playlist History);
    D --> E{User Filters};
    E --> D;
```

### 3.1. Backend (Metadata Extractor)

*   **Language:** Python
*   **Functionality:**
    *   Fetch the m3u8 playlist from the specified URL.
    *   Download the latest audio segments (fMP4).
    *   Extract metadata (artist, title, album, year) from the audio segments using ID3 tags.
    *   Store the extracted metadata in Azure Table Storage, along with a timestamp.
*   **Implementation:**
    *   Implement the metadata extractor as an Azure Function.
    *   Configure the Azure Function to run on a timer trigger with a 2-minute interval.
    *   Modify [`direct_stream_metadata.py`](direct_stream_metadata.py) to:
        *   Accept the m3u8 playlist URL as a configuration setting.
        *   Connect to Azure Table Storage.
        *   Extract the "year" metadata from the audio segments.
        *   Store the extracted metadata in Azure Table Storage.

*   **Database:** Azure Table Storage
    *   **Schema:**
        *   `PartitionKey`: (e.g., "artist")
        *   `RowKey`: (unique identifier, e.g., timestamp)
        *   `artist`: STRING
        *   `title`: STRING
        *   `album`: STRING
        *   `year`: INT
        *   `timestamp`: DATETIME

### 3.2. Frontend (Playlist History)

*   **Language:** HTML, CSS, JavaScript
*   **Framework/Library:** None (to match the style of the provided website)
*   **Functionality:**
    *   Display the playlist history from Azure Table Storage.
    *   Implement real-time filtering by artist, title, album, and year.
    *   Mirror the style of [https://www.savvybeastradio.com](https://www.savvybeastradio.com).
*   **Implementation:**
    *   Create an HTML page to display the playlist history.
    *   Use CSS to style the page to match the Savvy Beast Radio website.
    *   Use JavaScript to:
        *   Fetch the playlist history from the backend.
        *   Display the playlist history in a table or list.
        *   Implement real-time filtering using JavaScript.
*   **API Endpoint:**
    *   Create a simple API endpoint on the backend (e.g., using Flask or FastAPI) to serve the playlist history from Azure Table Storage.

### 3.3. Filtering Implementation

*   The frontend will use JavaScript to filter the playlist history in real-time.
*   The user will be able to enter text in the artist, title, album, and year fields.
*   As the user types, the JavaScript code will filter the playlist history to show only the songs that match the entered text.
*   The filtering will be case-insensitive.

### 3.4. Deployment

*   The backend will be deployed as an Azure Function.
*   The frontend can be hosted on a web server or CDN.

## 4. Technologies

*   Python
*   Azure Table Storage
*   Azure Functions
*   HTML
*   CSS
*   JavaScript