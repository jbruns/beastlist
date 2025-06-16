# Savvy Beast Radio - Playlist History Application

A web-based application that interfaces with an m3u8 audio stream endpoint, extracts metadata from fMP4 audio chunks, and provides a user-facing component to view playlist history with real-time filtering.

## Features

- **Backend Metadata Extraction**: Extracts artist, title, album, and year metadata from HLS audio streams
- **Azure Table Storage**: Stores metadata with timestamps in Azure Table Storage
- **Azure Functions**: Runs as a timer-triggered Azure Function (every 2 minutes)
- **Web Frontend**: Displays playlist history with real-time filtering capabilities
- **Savvy Beast Radio Styling**: Mimics the design and style of the original Savvy Beast Radio website

## Architecture

```
HLS Stream → Azure Function (Metadata Extractor) → Azure Table Storage → Frontend (Playlist History)
```

## Prerequisites

- Azure subscription
- Python 3.8+
- Node.js (for development)
- Azure CLI (for deployment)

## Deployment

### 1. Deploy Azure Infrastructure

#### Deploy Azure Table Storage:
```bash
az deployment group create \
  --resource-group <your-resource-group> \
  --template-file azure_table_storage_template.json \
  --parameters storageAccountName=<unique-storage-name>
```

#### Deploy Azure Function:
```bash
az deployment group create \
  --resource-group <your-resource-group> \
  --template-file azure_function_template.json \
  --parameters functionAppName=<unique-function-name> \
              storageAccountName=<storage-account-name> \
              hlsBaseUrl=<your-hls-stream-url> \
              azureTableName=playlisthistory
```

### 2. Deploy Function Code

1. Create a function app package:
```bash
# Create function directory structure
mkdir -p MetadataExtractor
cp direct_stream_metadata.py MetadataExtractor/__init__.py
cp function.json MetadataExtractor/
cp requirements.txt .
```

2. Deploy to Azure Functions:
```bash
func azure functionapp publish <your-function-app-name> --python
```

### 3. Deploy Frontend

#### Option A: Static Web App
Deploy the frontend files (`index.html`, `css/`, `js/`, `Savvy Beast Radio_files/`) to Azure Static Web Apps or any web server.

#### Option B: Flask API (for development)
```bash
pip install -r requirements.txt
python api.py
```

## Configuration

### Environment Variables

Set the following environment variables in your Azure Function and API:

- `HLS_BASE_URL`: The base URL of your HLS stream
- `AZURE_TABLE_NAME`: Name of the Azure Table (default: "playlisthistory")
- `AZURE_STORAGE_ACCOUNT`: Azure Storage Account name
- `AZURE_STORAGE_KEY`: Azure Storage Account key

### Frontend Configuration

Update the API endpoint in `js/playlist.js` if deploying to a different domain:

```javascript
const response = await fetch('/api/playlist'); // Update this URL
```

## File Structure

```
├── README.md
├── product_requirements.md
├── requirements.txt
├── direct_stream_metadata.py          # Azure Function metadata extractor
├── function.json                      # Azure Function configuration
├── api.py                            # Flask API for serving playlist data
├── azure_table_storage_template.json # ARM template for Table Storage
├── azure_function_template.json      # ARM template for Azure Function
├── index.html                        # Main frontend page
├── css/
│   └── playlist.css                  # Custom styles for playlist
├── js/
│   └── playlist.js                   # Frontend JavaScript
└── Savvy Beast Radio_files/          # Original assets from Savvy Beast Radio
    ├── Logo_StreamS.svg
    ├── Image_Default.jpg
    ├── player_x-cyn-cyn.css
    ├── mm-fontsize.js
    ├── pad_min.js
    └── player_min.js
```

## Usage

### Frontend Features

1. **Real-time Filtering**: Filter playlist history by artist, title, album, or year
2. **Auto-refresh**: Automatically refreshes every 30 seconds
3. **Responsive Design**: Works on desktop and mobile devices
4. **Keyboard Shortcuts**: 
   - `Ctrl/Cmd + /`: Focus on artist filter
   - `Escape`: Clear focus from filter inputs

### API Endpoints

- `GET /api/playlist`: Get playlist history
- `GET /api/playlist/search`: Search playlist with filters
- `GET /api/health`: Health check endpoint

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export AZURE_STORAGE_ACCOUNT=your_account
export AZURE_STORAGE_KEY=your_key
export AZURE_TABLE_NAME=playlisthistory
```

3. Run the API server:
```bash
python api.py
```

4. Open `index.html` in a web browser or serve it with a local web server.

### Testing the Metadata Extractor

```bash
# Test the metadata extraction locally
python direct_stream_metadata.py
```

## Monitoring

- Monitor Azure Function execution in the Azure Portal
- Check function logs for metadata extraction status
- Use the `/api/health` endpoint to verify API connectivity

## Troubleshooting

### Common Issues

1. **No metadata extracted**: Check that the HLS stream URL is correct and accessible
2. **API connection failed**: Verify Azure Storage credentials and table name
3. **Frontend not loading**: Check CORS settings and API endpoint URLs

### Debug Mode

Enable debug logging by setting the Azure Function logging level to "Information" in the Azure Portal.

## License

This project uses assets and styling from Savvy Beast Radio. Please respect their copyright and usage terms.