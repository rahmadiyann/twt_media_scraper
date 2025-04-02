# Twitter Media Scraper

A robust Python-based tool for downloading media content (photos and videos) from Twitter user profiles. This tool efficiently retrieves and organizes media content while maintaining proper error handling and logging.

## Features

- Download photos and videos from any public Twitter profile
- Automatic organization of media into separate folders for photos and videos
- JSON metadata storage for downloaded content
- Comprehensive error handling and logging
- Support for high-quality video downloads
- Environment-based configuration for API credentials

## Prerequisites

- Python 3.6 or higher
- Twitter API credentials (API Key and API Host)
- Internet connection

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/twt_media_scrapper.git
cd twt_media_scrapper
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API credentials:

```
API_KEY=your_api_key_here
API_HOST=your_api_host_here
```

## Usage

Run the script with a Twitter username as an argument:

```bash
python main.py username
```

The script will:

1. Create a directory structure under `medias/username/`
2. Download photos to `medias/username/photos/`
3. Download videos to `medias/username/videos/`
4. Save metadata to `medias/username/data.json`

## Project Structure

```
twitter_scrapper/
├── main.py              # Main script file
├── requirements.txt     # Project dependencies
├── .env                # Environment variables (not tracked in git)
└── medias/             # Downloaded media storage
    └── username/       # User-specific media folder
        ├── photos/     # Downloaded photos
        ├── videos/     # Downloaded videos
        └── data.json   # Media metadata
```

## Configuration

The script uses environment variables for configuration:

- `API_KEY`: Your Twitter API key
- `API_HOST`: Your Twitter API host

## Error Handling

The script includes comprehensive error handling for:

- API request failures
- Media download issues
- Invalid user profiles
- File system operations
- Network connectivity problems

## Logging

All operations are logged with timestamps and appropriate log levels:

- INFO: Successful operations
- ERROR: Failed operations and exceptions

## Dependencies

- requests: For HTTP requests
- python-dotenv: For environment variable management
- yt-dlp: For video downloads

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
