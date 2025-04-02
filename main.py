import requests
import json
import sys
import os
import logging
from typing import Optional, Tuple, List, Dict
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv('.env')

API_KEY = os.environ.get('API_KEY')
API_HOST = os.environ.get('API_HOST')

def make_request(endpoint: str, params: dict = None) -> Tuple[Optional[dict], int, Optional[str]]:
    """
    Makes a GET request to the specified API endpoint with the given parameters.

    Args:
        endpoint (str): The API endpoint to request.
        params (dict, optional): The query parameters for the request.

    Returns:
        Tuple[Optional[dict], int, Optional[str]]: A tuple containing the JSON response (if any),
        the HTTP status code, and an error message (if any).
    """
    url = f"https://{API_HOST}/{endpoint}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json(), response.status_code, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None, response.status_code if response else 500, str(e)

def download_media(url: str, file_name: str, media_type: str):
    """
    Downloads media from a given URL and saves it to a specified file.

    Args:
        url (str): The URL of the media to download.
        file_name (str): The file path where the media should be saved.
        media_type (str): The type of media to download ('photo' or 'video').
    """
    if media_type == 'photo':
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file_name, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download media from {url}: {e}")
    elif media_type == 'video':
        try:
            import yt_dlp
            ydl_opts = {
                'format': 'mp4',
                'outtmpl': file_name,
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            logging.info(f"Successfully downloaded video to {file_name}")
        except Exception as e:
            logging.error(f"Error downloading video: {e}")

def get_user_media(user_id: int, count: int = 100) -> Optional[List[Dict]]:
    """
    Retrieves media associated with a specific user ID.

    Args:
        user_id (int): The ID of the user whose media is to be retrieved.
        count (int, optional): The number of media items to retrieve. Defaults to 100.

    Returns:
        Optional[List[Dict]]: A list of dictionaries containing media information, or None if an error occurs.
    """
    querystring = {"user": str(user_id), "count": str(count)}
    data, status_code, response_text = make_request("user-media", querystring)
    
    if status_code != 200:
        logging.error(f"Error getting user media: {response_text}")
        return None
    
    final_data = []
    full_counter = 1
    
    try:
        entries = data['result']['timeline']['instructions'][1]['entries']
    except (KeyError, IndexError) as e:
        logging.error(f"Unexpected data format: {e}")
        return None
    
    for entry in entries:
        content = entry.get('content', {})
        if content.get('entryType') != 'TimelineTimelineItem':
            continue
        
        result = content.get('itemContent', {}).get('tweet_results', {}).get('result', {})
        media_entities = result.get('legacy', {}).get('extended_entities', {}).get('media', [])
        
        if not media_entities:
            continue
        
        media_type = media_entities[0].get('type')
        media_url = None
        
        if media_type == 'video':
            variants = media_entities[0].get('video_info', {}).get('variants', [])
            mp4_variants = [v for v in variants if v['content_type'] == 'video/mp4']
            if mp4_variants:
                media_url = max(mp4_variants, key=lambda x: x.get('bitrate', 0))['url']
        
        created_at = result.get('legacy', {}).get('created_at')
        full_text = result.get('legacy', {}).get('full_text')
        
        final_data.append({
            "id": full_counter,
            "created_at": created_at,
            "text": full_text,
            "media_type": media_type,
            "media_url": media_url
        })
        full_counter += 1
            
    return final_data

def get_user_id(username: str) -> Optional[int]:
    """
    Retrieves the user ID for a given username.

    Args:
        username (str): The username of the user.

    Returns:
        Optional[int]: The user ID if found, or None if an error occurs.
    """
    param = {"username": username}
    data, status_code, response_text = make_request("user", param)
    if status_code != 200:
        logging.error(f"Error getting user id: {response_text}")
        return None
    try:
        return data['result']['data']['user']['result']['rest_id']
    except KeyError as e:
        logging.error(f"Unexpected data format: {e}")
        return None

def main():
    """
    Main function to execute the script. It retrieves user media and saves it locally.
    """
    if len(sys.argv) < 3 or (sys.argv[1] not in ['--username', '-u']):
        print("Usage: python main.py --username <username> [--count <count>]")
        print("       python main.py -u <username> [-c <count>]")
        print("Options:")
        print("  --username, -u <username>  Specify the Twitter username to scrape media from.")
        print("  --count, -c <count>        Specify the number of media items to download (default is 5).")
        sys.exit(1)
    
    username = sys.argv[2]
    count = 5  # Default count
    if len(sys.argv) > 3 and sys.argv[3] in ['--count', '-c']:
        try:
            count = int(sys.argv[4])
        except (ValueError, IndexError):
            logging.error("Count must be an integer.")
            sys.exit(1)
    
    user_id = get_user_id(username)
    if user_id is None:
        sys.exit(1)
    
    datas = get_user_media(user_id, count)
    if datas is None:
        sys.exit(1)
        
    media_folder = f"medias/{username}"
    os.makedirs(media_folder, exist_ok=True)
    
    photo_folder = f"{media_folder}/photos"
    video_folder = f"{media_folder}/videos"
    os.makedirs(photo_folder, exist_ok=True)
    os.makedirs(video_folder, exist_ok=True)
    
    for data in datas:
        if data['media_type'] == 'photo':
            download_media(data['media_url'], f"{photo_folder}/{data['id']}.jpg", 'photo')
        elif data['media_type'] == 'video':
            download_media(data['media_url'], f"{video_folder}/video_{data['id']}.mp4", 'video')
    
    with open(f"{media_folder}/data.json", 'w') as f:
        json.dump(datas, f, indent=4)

if __name__ == '__main__':
    main()