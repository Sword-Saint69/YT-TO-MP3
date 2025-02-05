import requests
import re

# WARNING: Hardcoding API keys is not secure. Use environment variables instead.
RAPIDAPI_KEY = '703cbef966mshe75a704d906e8c2p13829djsn0a2a4330afaa'

# API endpoint for YouTube to MP3 conversion
API_URL = "https://youtube-mp36.p.rapidapi.com/dl"

def extract_video_id(url_or_id):
    """
    Extracts the video ID from a YouTube URL or returns the ID if it's already provided.
    Supports both full URLs and direct video IDs.
    """
    # Regex to match YouTube video IDs from different URL formats
    youtube_regex = (
        r'(?:https?:\/\/)?(?:www\.)?'
        r'(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)'
        r'([a-zA-Z0-9_-]{11})'
    )

    match = re.search(youtube_regex, url_or_id)
    if match:
        return match.group(1)  # Return the extracted video ID
    elif len(url_or_id) == 11:
        # If the input is exactly 11 characters, assume it's a video ID
        return url_or_id
    else:
        raise ValueError("Invalid YouTube URL or ID")

def download_youtube_mp3(video_url_or_id):
    try:
        # Extract the video ID from the input (URL or direct ID)
        video_id = extract_video_id(video_url_or_id)

        # Query parameters: YouTube video ID
        querystring = {"id": video_id}

        # Headers for the API request
        headers = {
            "x-rapidapi-host": "youtube-mp36.p.rapidapi.com",
            "x-rapidapi-key": RAPIDAPI_KEY
        }

        # Send a GET request to the API
        response = requests.get(API_URL, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse the JSON response
        data = response.json()

        if data.get('status') == 'ok':
            # Extract the download link for the MP3 file
            mp3_url = data['link']
            title = data['title']

            # Download the MP3 file
            print(f"Downloading: {title}.mp3")
            mp3_response = requests.get(mp3_url)

            # Save the MP3 file locally
            with open(f"{title}.mp3", 'wb') as f:
                f.write(mp3_response.content)

            print(f"Download completed: {title}.mp3")
        else:
            print("Error: Unable to fetch MP3 link.")
            print(data.get('msg', 'Unknown error'))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except ValueError as ve:
        print(f"Invalid input: {ve}")

if __name__ == "__main__":
    # Input the YouTube video URL or ID
    youtube_input = input("Enter the YouTube video URL or ID: ")
    download_youtube_mp3(youtube_input)
