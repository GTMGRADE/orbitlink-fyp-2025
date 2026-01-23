import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")

if api_key:
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Test 1: Search for handle
        print("\n=== Test 1: Searching for @xNaya ===")
        response = youtube.search().list(
            part="snippet",
            q="@xNaya",
            type="channel",
            maxResults=1
        ).execute()
        
        if response.get('items'):
            channel_id = response['items'][0]['snippet']['channelId']
            channel_title = response['items'][0]['snippet']['title']
            print(f"Found: {channel_title} (ID: {channel_id})")
        else:
            print("No channel found for @xNaya")
        
        # Test 2: Try without @
        print("\n=== Test 2: Searching for xNaya ===")
        response2 = youtube.search().list(
            part="snippet",
            q="xNaya",
            type="channel",
            maxResults=1
        ).execute()
        
        if response2.get('items'):
            channel_id = response2['items'][0]['snippet']['channelId']
            channel_title = response2['items'][0]['snippet']['title']
            print(f"Found: {channel_title} (ID: {channel_id})")
        else:
            print("No channel found")
            
    except Exception as e:
        print(f"Error: {e}")
