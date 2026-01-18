import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")
print(f"API Key loaded: {'Yes' if api_key and api_key != 'I have uploaded actually' else 'No'}")

if api_key and api_key != "I have uploaded actually":
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Test the API with a simple search
        request = youtube.search().list(
            part="snippet",
            q="test",
            maxResults=1,
            type="video"
        )
        response = request.execute()
        print("✅ YouTube API connection successful!")
        print(f"Found {len(response.get('items', []))} items")
        
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
else:
    print("❌ Invalid API key. Please update your .env file with a valid YouTube API key")