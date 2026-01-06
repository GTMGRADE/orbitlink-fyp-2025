# services/youtube_analyzer.py
import re
import math
import pandas as pd
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import os
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

class YouTubeAnalyzer:
    def __init__(self, api_key):
        """Initialize YouTube API with provided API key"""
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def resolve_channel_id(self, channel_url):
        """Resolve any YouTube URL to channel ID - EXACT SAME AS COLAB"""
        patterns = [
            (r"youtube\.com/channel/(UC[\w-]+)", "channel"),
            (r"youtube\.com/user/([\w-]+)", "user"),
            (r"youtube\.com/@([\w\.\-]+)", "handle")
        ]
        
        for pattern, kind in patterns:
            match = re.search(pattern, channel_url)
            if match:
                if kind == "channel":
                    return match.group(1)
                elif kind == "user":
                    try:
                        response = self.youtube.channels().list(
                            part="id", 
                            forUsername=match.group(1)
                        ).execute()
                        return response['items'][0]['id'] if response.get('items') else None
                    except:
                        continue
                elif kind == "handle":
                    try:
                        response = self.youtube.search().list(
                            part="snippet",
                            q=match.group(1),
                            type="channel",
                            maxResults=1
                        ).execute()
                        return response['items'][0]['snippet']['channelId'] if response.get('items') else None
                    except:
                        continue
        
        raise ValueError("Could not resolve channel URL")
    
    def get_channel_metadata(self, channel_id):
        """Get comprehensive channel information - EXACT SAME AS COLAB"""
        try:
            response = self.youtube.channels().list(
                part="snippet,statistics,brandingSettings,topicDetails",
                id=channel_id
            ).execute()
            
            if not response.get('items'):
                return None
                
            item = response['items'][0]
            
            metadata = {
                'title': item['snippet'].get('title', 'Unknown'),
                'description': item['snippet'].get('description', ''),
                'published_at': item['snippet'].get('publishedAt', ''),
                'subscriber_count': int(item['statistics'].get('subscriberCount', 0)),
                'video_count': int(item['statistics'].get('videoCount', 0)),
                'view_count': int(item['statistics'].get('viewCount', 0)),
                'country': item.get('brandingSettings', {}).get('channel', {}).get('country', ''),
                'keywords': item.get('brandingSettings', {}).get('channel', {}).get('keywords', ''),
                'topics': item.get('topicDetails', {}).get('topicCategories', []),
                'profile_image': item['snippet'].get('thumbnails', {}).get('high', {}).get('url', '')
            }
            
            # Calculate engagement rate (EXACT SAME AS COLAB)
            if metadata['subscriber_count'] > 0 and metadata['video_count'] > 0:
                metadata['engagement_rate'] = (metadata['view_count'] / metadata['subscriber_count']) / metadata['video_count'] * 100
            else:
                metadata['engagement_rate'] = 0
                
            return metadata
            
        except Exception as e:
            print(f"Error fetching channel metadata: {e}")
            return None
    
    def get_channel_videos(self, channel_id, max_videos=30, timeframe_days=180):
        """Get recent videos with metadata - MATCH COLAB EXACTLY"""
        videos = []
        next_page_token = None
        
        # Calculate the publishedAfter date string in ISO 8601 format (SAME AS COLAB)
        published_after = (datetime.utcnow() - timedelta(days=timeframe_days)).isoformat() + "Z"
        
        try:
            while len(videos) < max_videos:
                request = self.youtube.search().list(
                    part="id,snippet",
                    channelId=channel_id,
                    type="video",
                    order="date",
                    publishedAfter=published_after,  # ADD THIS LINE - SAME AS COLAB
                    maxResults=min(50, max_videos - len(videos)),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    
                    # Get detailed video statistics
                    video_response = self.youtube.videos().list(
                        part="statistics,snippet,contentDetails",
                        id=video_id
                    ).execute()
                    
                    if video_response.get('items'):
                        video_data = video_response['items'][0]
                        
                        video_info = {
                            'video_id': video_id,
                            'title': video_data['snippet']['title'],
                            'published_at': video_data['snippet']['publishedAt'],
                            'views': int(video_data['statistics'].get('viewCount', 0)),
                            'likes': int(video_data['statistics'].get('likeCount', 0)),
                            'comments': int(video_data['statistics'].get('commentCount', 0)),
                            'duration': video_data['contentDetails'].get('duration', 'PT0S'),
                            'description': video_data['snippet'].get('description', '')
                        }
                        
                        # Calculate engagement metrics (EXACT SAME AS COLAB)
                        if video_info['views'] > 0:
                            video_info['like_rate'] = (video_info['likes'] / video_info['views']) * 100
                            video_info['comment_rate'] = (video_info['comments'] / video_info['views']) * 100
                        else:
                            video_info['like_rate'] = 0
                            video_info['comment_rate'] = 0
                        
                        videos.append(video_info)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
        except HttpError as e:
            print(f"API Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        
        return videos
    
    def analyze_comments(self, video_id, channel_owner_id, max_comments=2000):
        """Collect and analyze comments - MATCH COLAB EXACTLY"""
        all_comments = []
        reply_edges = []
        
        try:
            # Get all comment threads - NO HARD LIMIT LIKE COLAB
            next_page_token = None
            comment_count = 0
            
            while True:
                response = self.youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=next_page_token,
                    order="relevance"
                ).execute()
                
                for thread in response.get('items', []):
                    # Top-level comment - EXACT SAME AS COLAB
                    top_comment = thread['snippet']['topLevelComment']
                    thread_snippet = thread['snippet']  # This contains totalReplyCount!
                    
                    # Get the total reply count from THREAD level
                    thread_total_reply_count = thread_snippet.get('totalReplyCount', 0)
                    
                    top_data = self._extract_comment_metrics(top_comment, channel_owner_id, is_reply=False)
                    # IMPORTANT: Add thread-level reply count to top comment (SAME AS COLAB)
                    top_data['total_reply_count'] = thread_total_reply_count
                    all_comments.append(top_data)
                    comment_count += 1
                    
                    # Get replies - NO LIMIT, GET ALL LIKE COLAB
                    if 'replies' in thread:
                        for reply in thread['replies']['comments']:
                            reply_data = self._extract_comment_metrics(reply, channel_owner_id, is_reply=True)
                            all_comments.append(reply_data)
                            comment_count += 1
                            
                            # Add reply edge (replier -> original author)
                            reply_edges.append({
                                'from': reply_data['author_id'],
                                'to': top_data['author_id'],
                                'video_id': video_id,
                                'timestamp': reply_data['published_at']
                            })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
        except Exception as e:
            print(f"Error analyzing comments for video {video_id}: {e}")
        
        return all_comments, reply_edges
    
    def _extract_comment_metrics(self, comment, channel_owner_id, is_reply=False):
        """Extract comprehensive metrics from a single comment - EXACT SAME AS COLAB"""
        snippet = comment['snippet']
        text = snippet.get('textDisplay', '')
        
        # Basic metrics
        metrics = {
            'comment_id': comment['id'],
            'author_id': snippet.get('authorChannelId', {}).get('value', 'unknown'),
            'author_name': snippet.get('authorDisplayName', 'Unknown'),
            'text': text,
            'published_at': snippet['publishedAt'],
            'updated_at': snippet.get('updatedAt', snippet['publishedAt']),
            'like_count': snippet.get('likeCount', 0),
            'is_reply': is_reply,
            'is_channel_owner': snippet.get('authorChannelId', {}).get('value') == channel_owner_id,
            'is_pinned': snippet.get('isPublic', False),
            'total_reply_count': 0,
            'parent_id': snippet.get('parentId', None) if is_reply else None
        }
        
        # Text analysis metrics
        metrics.update(self._analyze_comment_text(text))
        
        # Time analysis
        published_time = datetime.fromisoformat(metrics['published_at'].replace('Z', '+00:00'))
        metrics['hour_of_day'] = published_time.hour
        metrics['day_of_week'] = published_time.strftime('%A')
        
        return metrics
    
    def _analyze_comment_text(self, text):
        """Analyze comment text for various metrics - EXACT SAME AS COLAB"""
        analysis = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'has_questions': int('?' in text),
            'has_exclamations': int('!' in text),
            'has_links': int('http://' in text.lower() or 'https://' in text.lower()),
            'has_mentions': int('@' in text),
            'has_hashtags': int('#' in text),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0
        }
        
        # Sentiment analysis
        try:
            blob = TextBlob(text)
            analysis['sentiment_polarity'] = blob.sentiment.polarity
            analysis['sentiment_subjectivity'] = blob.sentiment.subjectivity
        except:
            analysis['sentiment_polarity'] = 0
            analysis['sentiment_subjectivity'] = 0
        
        # Emoji detection
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", flags=re.UNICODE)
        analysis['has_emojis'] = int(bool(emoji_pattern.search(text)))
        
        return analysis
    
    def calculate_influencer_scores(self, all_comments, reply_edges, videos_data):
        """Calculate comprehensive influencer scores - EXACT SAME FORMULA AS COLAB"""
        user_metrics = defaultdict(lambda: {
            'total_comments': 0,
            'total_likes': 0,
            'total_replies_received': 0,  # Changed from avg_replies_received
            'avg_sentiment': 0,
            'unique_videos': set(),
            'comment_lengths': [],
            'thread_starts': 0,
            'channel_owner_replies_to': 0,
            'indegree': 0,
            'outdegree': 0,
            'author_name': ''
        })
        
        # Process all comments (EXACT SAME LOGIC AS COLAB)
        for comment in all_comments:
            author_id = comment['author_id']
            metrics = user_metrics[author_id]
            
            metrics['author_name'] = comment['author_name']
            metrics['total_comments'] += 1
            metrics['total_likes'] += comment['like_count']
            metrics['total_replies_received'] += comment['total_reply_count']  # TOTAL, not avg
            metrics['comment_lengths'].append(comment['text_length'])
            metrics['unique_videos'].add(comment.get('video_id', 'unknown'))
            
            # Thread starter
            if not comment['is_reply']:
                metrics['thread_starts'] += 1
            
            # Channel owner interaction (EXACT SAME LOGIC)
            if comment['is_channel_owner'] and comment['is_reply']:
                parent_author = next((c['author_id'] for c in all_comments 
                                    if c['comment_id'] == comment['parent_id']), None)
                if parent_author:
                    user_metrics[parent_author]['channel_owner_replies_to'] += 1
            
            # Sentiment accumulation (EXACT SAME LOGIC)
            metrics['avg_sentiment'] = (metrics['avg_sentiment'] * (metrics['total_comments'] - 1) + 
                                       comment['sentiment_polarity']) / metrics['total_comments']
        
        # Process reply edges for network metrics (EXACT SAME LOGIC)
        for edge in reply_edges:
            user_metrics[edge['to']]['indegree'] += 1
            user_metrics[edge['from']]['outdegree'] += 1
        
        # Calculate final scores - USING YOUR EXACT COLAB FORMULA
        influencers = []
        for author_id, metrics in user_metrics.items():
            if metrics['total_comments'] < 3:  # Minimum threshold (SAME AS COLAB)
                continue
                
            # Calculate raw metrics
            avg_comment_length = np.mean(metrics['comment_lengths']) if metrics['comment_lengths'] else 0
            video_participation = len(metrics['unique_videos'])
            
            # Calculate individual component scores (0-10 scale) - EXACT SAME AS COLAB
            scores = {
                'engagement_score': min(10, (metrics['total_likes'] + metrics['total_replies_received'] * 2) / 100),
                'consistency_score': min(10, video_participation * 2),  # 5+ videos gets max score
                'network_score': min(10, (metrics['indegree'] + metrics['channel_owner_replies_to'] * 2) / 5),
                'quality_score': min(10, (avg_comment_length / 50) + abs(metrics['avg_sentiment']) * 5),
                'activity_score': min(10, (metrics['total_comments'] + metrics['thread_starts']) / 5),
                'responsiveness_score': min(10, metrics['outdegree'] / 3)
            }
            
            # Weighted total score (0-10 scale) - EXACT SAME WEIGHTS AS COLAB
            weights = {
                'engagement_score': 0.25,
                'consistency_score': 0.20,
                'network_score': 0.20,
                'quality_score': 0.15,
                'activity_score': 0.10,
                'responsiveness_score': 0.10
            }
            
            # YOUR EXACT FORMULA FROM COLAB
            total_score = sum(scores[key] * weights[key] for key in scores)
            
            influencers.append({
                'author_id': author_id,
                'author_name': metrics['author_name'],
                'total_score': round(total_score, 2),  # Rounded to 2 decimal places (SAME AS COLAB)
                **scores,
                'total_comments': metrics['total_comments'],
                'total_likes': metrics['total_likes'],
                'total_replies_received': metrics['total_replies_received'],  # ACTUAL REPLIES, NOT AVG
                'unique_videos': video_participation,
                'indegree': metrics['indegree'],
                'outdegree': metrics['outdegree'],
                'avg_sentiment': round(metrics['avg_sentiment'], 3),
                'channel_owner_replies': metrics['channel_owner_replies_to'],
                'thread_starts': metrics['thread_starts']
            })
        
        return sorted(influencers, key=lambda x: x['total_score'], reverse=True)
    
    def analyze_channel(self, channel_url):
        """Main analysis method - MATCHING COLAB EXACTLY"""
        try:
            # Resolve channel
            channel_id = self.resolve_channel_id(channel_url)
            
            # Get channel metadata
            channel_metadata = self.get_channel_metadata(channel_id)
            if not channel_metadata:
                return {'error': 'Could not fetch channel metadata'}
            
            # Get recent videos - ANALYZE 30 VIDEOS LIKE COLAB
            videos_data = self.get_channel_videos(channel_id, max_videos=30)
            
            if len(videos_data) == 0:
                return {'error': 'No videos found for analysis'}
            
            # Analyze comments from each video - ANALYZE ALL VIDEOS LIKE COLAB
            all_comments = []
            all_edges = []
            
            print(f"Analyzing {len(videos_data)} videos...")
            for i, video in enumerate(videos_data):
                print(f"  Video {i+1}/{len(videos_data)}: Collecting comments...")
                comments, edges = self.analyze_comments(video['video_id'], channel_id)
                all_comments.extend(comments)
                all_edges.extend(edges)
                
                # Add video ID to comments for tracking
                for comment in comments[-len(comments):]:
                    comment['video_id'] = video['video_id']
                
                # Progress update
                print(f"    Collected {len(comments)} comments (Total: {len(all_comments)})")
            
            print(f"\nTotal comments analyzed: {len(all_comments):,}")
            
            # Calculate influencer scores
            print("Calculating influencer scores...")
            influencers = self.calculate_influencer_scores(all_comments, all_edges, videos_data)
            
            return {
                'success': True,
                'channel_metadata': channel_metadata,
                'videos_analyzed': len(videos_data),
                'total_comments': len(all_comments),
                'influencers': influencers[:20],  # Top 20 influencers
                'analysis_time': datetime.now().isoformat(),
                'video_details': videos_data[:5]  # Include first 5 video details
            }
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}