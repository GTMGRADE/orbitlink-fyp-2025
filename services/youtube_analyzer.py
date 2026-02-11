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
import networkx as nx
import community as community_louvain

# Set matplotlib backend BEFORE importing matplotlib
os.environ['MPLBACKEND'] = 'Agg'

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server environments
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] Matplotlib import failed: {e}")
    import traceback
    traceback.print_exc()
    MATPLOTLIB_AVAILABLE = False
    matplotlib = None
    plt = None
import base64
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

# Import sentiment analysis service with safe fallback
try:
    from services.sentiment_analysis import run_sentiment_analysis
    SENTIMENT_ANALYSIS_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] Sentiment analysis import failed, using fallback: {e}")

    def run_sentiment_analysis(comments):
        # Fallback returns empty charts and zeroed scores to keep UI alive
        return {
            "overall_score": 0,
            "label_counts": {"positive": 0, "neutral": 0, "negative": 0},
            "word_cloud": None,
            "pie_chart": None,
            "top_like_comments": sorted(
                [
                    {
                        "text": (c.get("text") or ""),
                        "author_name": c.get("author_name", "Unknown"),
                        "like_count": c.get("like_count", 0),
                        "published_at": c.get("published_at"),
                        "label": "neutral",
                        "score": 0,
                    }
                    for c in comments if c.get("text")
                ],
                key=lambda x: x.get("like_count", 0),
                reverse=True,
            )[:5],
        }

    SENTIMENT_ANALYSIS_AVAILABLE = False

class YouTubeAnalyzer:
    def __init__(self, api_key):
        """Initialize YouTube API with provided API key"""
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def resolve_channel_id(self, channel_url):
        """Resolve any YouTube URL to channel ID"""
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
    
    def extract_video_id(self, video_input: str) -> str:
        """Extract video ID from various YouTube URL formats"""
        video_input = video_input.strip()

        # If it looks like just a video ID
        if re.fullmatch(r"[A-Za-z0-9_-]{8,}", video_input) and "youtube" not in video_input and "youtu.be" not in video_input:
            return video_input

        # Full YouTube URLs
        m = re.search(r"v=([A-Za-z0-9_-]{8,})", video_input)
        if m: 
            return m.group(1)

        m = re.search(r"youtu\.be/([A-Za-z0-9_-]{8,})", video_input)
        if m: 
            return m.group(1)

        m = re.search(r"youtube\.com/shorts/([A-Za-z0-9_-]{8,})", video_input)
        if m: 
            return m.group(1)

        raise ValueError("Could not extract video ID from input.")
    
    def looks_like_video_input(self, text: str) -> bool:
        """Return True if input is a video URL or likely a video ID."""
        t = text.strip()

        # video URLs
        if "watch?v=" in t or "youtu.be/" in t or "/shorts/" in t:
            return True

        # likely video id (usually 11 chars, but we allow 8+ to be safe)
        if re.fullmatch(r"[A-Za-z0-9_-]{8,}", t) and "youtube" not in t:
            return True

        return False
    
    def get_channel_metadata(self, channel_id):
        """Get comprehensive channel information"""
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
            
            # Calculate engagement rate
            if metadata['subscriber_count'] > 0 and metadata['video_count'] > 0:
                metadata['engagement_rate'] = (metadata['view_count'] / metadata['subscriber_count']) / metadata['video_count'] * 100
            else:
                metadata['engagement_rate'] = 0
                
            return metadata
            
        except Exception as e:
            print(f"Error fetching channel metadata: {e}")
            return None
    
    def get_channel_videos(self, channel_id, max_videos=30, timeframe_days=180):
        """Get recent videos with metadata"""
        videos = []
        next_page_token = None
        
        # Calculate the publishedAfter date string in ISO 8601 format
        published_after = (datetime.utcnow() - timedelta(days=timeframe_days)).isoformat() + "Z"
        
        try:
            while len(videos) < max_videos:
                request = self.youtube.search().list(
                    part="id,snippet",
                    channelId=channel_id,
                    type="video",
                    order="date",
                    publishedAfter=published_after,
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
                        
                        # Calculate engagement metrics
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
    
    def get_video_metadata(self, video_id):
        """Get metadata for a single video"""
        try:
            response = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            ).execute()
            
            if not response.get('items'):
                return None
                
            item = response['items'][0]
            snippet = item['snippet']
            stats = item.get('statistics', {})
            
            video_info = {
                'video_id': video_id,
                'title': snippet.get('title', 'Unknown Title'),
                'published_at': snippet.get('publishedAt', ''),
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)) if 'likeCount' in stats else 0,
                'comments': int(stats.get('commentCount', 0)) if 'commentCount' in stats else 0,
                'description': snippet.get('description', ''),
                'channel_id': snippet.get('channelId', ''),
                'channel_title': snippet.get('channelTitle', 'Unknown Channel')
            }
            
            # Calculate engagement rate
            if video_info['views'] > 0:
                video_info['like_rate'] = (video_info['likes'] / video_info['views']) * 100
                video_info['comment_rate'] = (video_info['comments'] / video_info['views']) * 100
            else:
                video_info['like_rate'] = 0
                video_info['comment_rate'] = 0
                
            return video_info
            
        except Exception as e:
            print(f"Error fetching video metadata: {e}")
            return None
    
    def analyze_comments(self, video_id, channel_owner_id, max_comments=2000):
        """Collect and analyze comments"""
        all_comments = []
        reply_edges = []
        
        try:
            # Get all comment threads
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
                    # Top-level comment
                    top_comment = thread['snippet']['topLevelComment']
                    thread_snippet = thread['snippet']
                    
                    # Get the total reply count from THREAD level
                    thread_total_reply_count = thread_snippet.get('totalReplyCount', 0)
                    
                    top_data = self._extract_comment_metrics(top_comment, channel_owner_id, is_reply=False)
                    top_data['total_reply_count'] = thread_total_reply_count
                    all_comments.append(top_data)
                    comment_count += 1
                    
                    # Get replies
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
                            
                            if comment_count >= max_comments:
                                break
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token or comment_count >= max_comments:
                    break
                    
        except Exception as e:
            print(f"Error analyzing comments for video {video_id}: {e}")
        
        return all_comments, reply_edges
    
    def _extract_comment_metrics(self, comment, channel_owner_id, is_reply=False):
        """Extract comprehensive metrics from a single comment"""
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
        """Analyze comment text for various metrics"""
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
    
    def calculate_influencer_scores(self, all_comments, reply_edges, videos_data, min_comments=3):
        """Calculate comprehensive influencer scores normalized to 0-10 scale"""
        user_metrics = defaultdict(lambda: {
            'total_comments': 0,
            'total_likes': 0,
            'total_replies_received': 0,
            'avg_sentiment': 0,
            'unique_videos': set(),
            'comment_lengths': [],
            'thread_starts': 0,
            'channel_owner_replies_to': 0,
            'indegree': 0,
            'outdegree': 0,
            'author_name': ''
        })
        
        # Process all comments
        for comment in all_comments:
            author_id = comment['author_id']
            metrics = user_metrics[author_id]
            
            metrics['author_name'] = comment['author_name']
            metrics['total_comments'] += 1
            metrics['total_likes'] += comment['like_count']
            metrics['total_replies_received'] += comment['total_reply_count']
            metrics['comment_lengths'].append(comment['text_length'])
            metrics['unique_videos'].add(comment.get('video_id', 'unknown'))
            
            # Thread starter
            if not comment['is_reply']:
                metrics['thread_starts'] += 1
            
            # Channel owner interaction
            if comment['is_channel_owner'] and comment['is_reply']:
                parent_author = next((c['author_id'] for c in all_comments 
                                    if c['comment_id'] == comment['parent_id']), None)
                if parent_author:
                    user_metrics[parent_author]['channel_owner_replies_to'] += 1
            
            # Sentiment accumulation
            metrics['avg_sentiment'] = (metrics['avg_sentiment'] * (metrics['total_comments'] - 1) + 
                                       comment['sentiment_polarity']) / metrics['total_comments']
        
        # Process reply edges for network metrics
        for edge in reply_edges:
            user_metrics[edge['to']]['indegree'] += 1
            user_metrics[edge['from']]['outdegree'] += 1
        
        # Calculate final scores
        influencers = []
        for author_id, metrics in user_metrics.items():
            if metrics['total_comments'] < min_comments:
                continue
                
            # Calculate raw metrics
            avg_comment_length = np.mean(metrics['comment_lengths']) if metrics['comment_lengths'] else 0
            video_participation = len(metrics['unique_videos'])
            
            # Calculate individual component scores (0-10 scale)
            scores = {
                'engagement_score': min(10, (metrics['total_likes'] + metrics['total_replies_received'] * 2) / 100),
                'consistency_score': min(10, video_participation * 2),
                'network_score': min(10, (metrics['indegree'] + metrics['channel_owner_replies_to'] * 2) / 5),
                'quality_score': min(10, (avg_comment_length / 50) + abs(metrics['avg_sentiment']) * 5),
                'activity_score': min(10, (metrics['total_comments'] + metrics['thread_starts']) / 5),
                'responsiveness_score': min(10, metrics['outdegree'] / 3)
            }
            
            # Weighted total score (0-10 scale)
            weights = {
                'engagement_score': 0.25,
                'consistency_score': 0.20,
                'network_score': 0.20,
                'quality_score': 0.15,
                'activity_score': 0.10,
                'responsiveness_score': 0.10
            }
            
            total_score = sum(scores[key] * weights[key] for key in scores)
            
            influencers.append({
                'author_id': author_id,
                'author_name': metrics['author_name'],
                'total_score': round(total_score, 2),
                **scores,
                'total_comments': metrics['total_comments'],
                'total_likes': metrics['total_likes'],
                'total_replies_received': metrics['total_replies_received'],
                'unique_videos': video_participation,
                'indegree': metrics['indegree'],
                'outdegree': metrics['outdegree'],
                'avg_sentiment': round(metrics['avg_sentiment'], 3),
                'channel_owner_replies': metrics['channel_owner_replies_to'],
                'thread_starts': metrics['thread_starts']
            })
        
        return sorted(influencers, key=lambda x: x['total_score'], reverse=True)
    
    def detect_communities(self, all_comments, reply_edges):
        """Detect communities using enhanced Louvain method with multi-resolution optimization"""
        try:
            # Build interaction graph
            G = nx.Graph()
            
            # Add nodes (all commenters)
            unique_users = set(comment['author_id'] for comment in all_comments)
            for user_id in unique_users:
                user_name = next((c['author_name'] for c in all_comments if c['author_id'] == user_id), 'Unknown')
                G.add_node(user_id, name=user_name)
            
            # Add edges (reply interactions)
            for edge in reply_edges:
                if G.has_node(edge['from']) and G.has_node(edge['to']):
                    if G.has_edge(edge['from'], edge['to']):
                        G[edge['from']][edge['to']]['weight'] += 1
                    else:
                        G.add_edge(edge['from'], edge['to'], weight=1)
            
            # If graph is too small or disconnected, return empty result
            if G.number_of_nodes() < 3 or G.number_of_edges() < 2:
                return {
                    'communities': [],
                    'modularity': 0,
                    'num_communities': 0,
                    'user_to_community': {},
                    'resolution_used': 1.0
                }
            
            # Multi-resolution community detection - find optimal resolution
            print("[COMMUNITIES] Testing multiple resolutions for optimal community structure...")
            best_partition = None
            best_modularity = -1
            best_resolution = 1.0
            
            for resolution in [0.5, 1.0, 1.5, 2.0]:
                try:
                    partition = community_louvain.best_partition(G, resolution=resolution)
                    modularity = community_louvain.modularity(partition, G)
                    
                    print(f"[COMMUNITIES] Resolution {resolution}: Modularity={modularity:.4f}, Communities={len(set(partition.values()))}")
                    
                    if modularity > best_modularity:
                        best_modularity = modularity
                        best_partition = partition
                        best_resolution = resolution
                except Exception as e:
                    print(f"[COMMUNITIES] Warning: Resolution {resolution} failed: {e}")
                    continue
            
            # Use best partition found, or fallback to default
            if best_partition is None:
                print("[COMMUNITIES] Using default resolution")
                best_partition = community_louvain.best_partition(G)
                best_modularity = community_louvain.modularity(best_partition, G)
                best_resolution = 1.0
            
            user_to_community = best_partition
            modularity = best_modularity
            
            print(f"[COMMUNITIES] Optimal resolution: {best_resolution}, Modularity: {modularity:.4f}")
            
            # Calculate advanced network metrics
            print("[COMMUNITIES] Calculating network metrics...")
            pagerank_scores = nx.pagerank(G, weight='weight')
            betweenness_scores = nx.betweenness_centrality(G, weight='weight')
            clustering_coeffs = nx.clustering(G, weight='weight')
            
            # Calculate community statistics with enhanced metrics
            community_stats = defaultdict(lambda: {
                'members': [],
                'member_names': [],
                'total_comments': 0,
                'total_likes': 0,
                'avg_sentiment': 0,
                'sentiment_count': 0,
                'pagerank_scores': {},
                'betweenness_scores': {},
                'clustering_scores': {}
            })
            
            for comment in all_comments:
                author_id = comment['author_id']
                if author_id in user_to_community:
                    comm_id = user_to_community[author_id]
                    stats = community_stats[comm_id]
                    
                    if author_id not in stats['members']:
                        stats['members'].append(author_id)
                        stats['member_names'].append(comment['author_name'])
                        stats['pagerank_scores'][author_id] = pagerank_scores.get(author_id, 0)
                        stats['betweenness_scores'][author_id] = betweenness_scores.get(author_id, 0)
                        stats['clustering_scores'][author_id] = clustering_coeffs.get(author_id, 0)
                    
                    stats['total_comments'] += 1
                    stats['total_likes'] += comment['like_count']
                    stats['avg_sentiment'] = (stats['avg_sentiment'] * stats['sentiment_count'] + 
                                             comment['sentiment_polarity']) / (stats['sentiment_count'] + 1)
                    stats['sentiment_count'] += 1
            
            # Format communities list with enhanced metrics
            communities = []
            for comm_id, stats in sorted(community_stats.items(), key=lambda x: len(x[1]['members']), reverse=True):
                # Find top influencer by PageRank
                top_influencer_id = max(stats['pagerank_scores'], key=stats['pagerank_scores'].get) if stats['pagerank_scores'] else None
                top_influencer_name = next((name for uid, name in zip(stats['members'], stats['member_names']) if uid == top_influencer_id), 'Unknown')
                
                # Find bridge users (high betweenness centrality)
                if stats['betweenness_scores']:
                    sorted_betweenness = sorted(stats['betweenness_scores'].items(), key=lambda x: x[1], reverse=True)
                    bridge_users = [uid for uid, score in sorted_betweenness[:3] if score > 0]
                else:
                    bridge_users = []
                
                # Calculate average clustering coefficient
                avg_clustering = np.mean(list(stats['clustering_scores'].values())) if stats['clustering_scores'] else 0
                
                # Build community subgraph for density
                subgraph = G.subgraph(stats['members'])
                density = nx.density(subgraph) if len(stats['members']) > 1 else 0
                
                communities.append({
                    'community_id': comm_id,
                    'size': len(stats['members']),
                    'total_comments': stats['total_comments'],
                    'total_likes': stats['total_likes'],
                    'avg_sentiment': round(stats['avg_sentiment'], 3),
                    'top_members': stats['member_names'][:5],
                    'top_influencer': top_influencer_name,
                    'top_influencer_id': top_influencer_id,
                    'top_influencer_score': round(stats['pagerank_scores'].get(top_influencer_id, 0), 4) if top_influencer_id else 0,
                    'bridge_users': [next((name for uid, name in zip(stats['members'], stats['member_names']) if uid == b_uid), 'Unknown') for b_uid in bridge_users[:2]],
                    'clustering_coefficient': round(avg_clustering, 3),
                    'density': round(density, 3)
                })
            
            print(f"[COMMUNITIES] Detected {len(communities)} communities with enhanced metrics")
            
            return {
                'communities': communities,
                'modularity': round(modularity, 3),
                'num_communities': len(communities),
                'user_to_community': user_to_community,
                'resolution_used': best_resolution
            }
            
        except Exception as e:
            print(f"Error detecting communities: {e}")
            import traceback
            traceback.print_exc()
            return {
                'communities': [],
                'modularity': 0,
                'num_communities': 0,
                'user_to_community': {},
                'resolution_used': 1.0
            }
    
    def generate_community_network_visualization(self, all_comments, reply_edges, user_to_community):
        """Generate network visualization with communities colored"""
        try:
            if not MATPLOTLIB_AVAILABLE or plt is None:
                print("[WARNING] Matplotlib not available for community visualization")
                return None
            
            if not user_to_community or len(user_to_community) == 0:
                return None
            
            # Build interaction graph
            G = nx.Graph()
            
            # Add nodes with community assignments
            unique_users = set(comment['author_id'] for comment in all_comments)
            for user_id in unique_users:
                if user_id in user_to_community:
                    user_name = next((c['author_name'] for c in all_comments if c['author_id'] == user_id), 'Unknown')
                    G.add_node(user_id, name=user_name, community=user_to_community[user_id])
            
            # Add edges
            for edge in reply_edges:
                if G.has_node(edge['from']) and G.has_node(edge['to']):
                    if G.has_edge(edge['from'], edge['to']):
                        G[edge['from']][edge['to']]['weight'] += 1
                    else:
                        G.add_edge(edge['from'], edge['to'], weight=1)
            
            if G.number_of_nodes() < 2:
                return None
            
            # Create figure
            fig, ax = plt.subplots(figsize=(14, 10))
            
            # Use spring layout for better visualization
            pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
            
            # Get unique communities and assign colors
            communities = set(user_to_community.values())
            colors = plt.cm.tab20(np.linspace(0, 1, len(communities)))
            community_colors = {comm: colors[i] for i, comm in enumerate(sorted(communities))}
            
            # Assign colors to nodes based on community
            node_colors = [community_colors[user_to_community.get(node, 0)] for node in G.nodes()]
            
            # Calculate node sizes based on degree
            degrees = dict(G.degree())
            node_sizes = [100 + degrees.get(node, 0) * 20 for node in G.nodes()]
            
            # Draw network
            nx.draw_networkx_edges(G, pos, alpha=0.2, width=0.5, ax=ax)
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, 
                                  alpha=0.7, linewidths=0.5, edgecolors='white', ax=ax)
            
            # Add title
            ax.set_title(f'Community Network Structure\n{G.number_of_nodes()} users in {len(communities)} communities',
                        fontsize=16, fontweight='bold', pad=20)
            ax.axis('off')
            
            # Add legend for communities            <!-- ...existing code... -->
            
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                         markerfacecolor=community_colors[comm], 
                                         markersize=10, label=f'Community {comm}')
                             for comm in sorted(list(communities)[:10])]  # Show top 10 communities
            ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
            
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return image_base64
            
        except Exception as e:
            print(f"Error generating community visualization: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_channel(self, channel_url, progress_callback=None):
        """Analyze a YouTube channel"""
        try:
            if progress_callback:
                progress_callback('Starting channel analysis...', 5)
            
            # Resolve channel
            if progress_callback:
                progress_callback('Resolving channel URL...', 10)
            
            channel_id = self.resolve_channel_id(channel_url)
            
            # Get channel metadata
            if progress_callback:
                progress_callback('Fetching channel information...', 20)
            
            channel_metadata = self.get_channel_metadata(channel_id)
            if not channel_metadata:
                return {'success': False, 'error': 'Could not fetch channel metadata'}
            
            # Get recent videos
            if progress_callback:
                progress_callback('Collecting recent videos...', 30)
            
            videos_data = self.get_channel_videos(channel_id, max_videos=30)
            
            if len(videos_data) == 0:
                return {'success': False, 'error': 'No videos found for analysis'}
            
            # Analyze comments from each video
            all_comments = []
            all_edges = []
            
            for i, video in enumerate(videos_data):
                if progress_callback:
                    progress = 30 + (i / len(videos_data)) * 50
                    progress_callback(f'Analyzing video {i+1}/{len(videos_data)}...', progress)
                
                comments, edges = self.analyze_comments(video['video_id'], channel_id, max_comments=2000)
                all_comments.extend(comments)
                all_edges.extend(edges)
                
                # Add video ID to comments for tracking
                for comment in comments[-len(comments):]:
                    comment['video_id'] = video['video_id']
            
            # Calculate influencer scores
            if progress_callback:
                progress_callback('Calculating influencer scores...', 85)
            
            influencers = self.calculate_influencer_scores(all_comments, all_edges, videos_data)
            
            # Run sentiment analysis
            if progress_callback:
                progress_callback('Running sentiment analysis...', 94)
            
            sentiment_analysis_result = None
            if all_comments:
                try:
                    print(f"[YOUTUBE_ANALYZER] Channel: Running sentiment analysis on {len(all_comments)} comments...")
                    sentiment_analysis_result = run_sentiment_analysis(all_comments)
                    print(f"[YOUTUBE_ANALYZER] Channel: Sentiment complete. Score: {sentiment_analysis_result.get('overall_score')}")
                    print(f"[YOUTUBE_ANALYZER] Channel: Word cloud exists: {bool(sentiment_analysis_result.get('word_cloud'))}")
                    print(f"[YOUTUBE_ANALYZER] Channel: Top comments: {len(sentiment_analysis_result.get('top_like_comments', []))}")
                except Exception as e:
                    print(f"[YOUTUBE_ANALYZER] Channel: Sentiment analysis error: {e}")
                    import traceback
                    traceback.print_exc()
                    sentiment_analysis_result = {
                        "overall_score": 0,
                        "label_counts": {"positive": 0, "neutral": 0, "negative": 0},
                        "word_cloud": None,
                        "pie_chart": None,
                        "top_like_comments": [],
                    }
            
            # Detect communities
            if progress_callback:
                progress_callback('Detecting communities...', 96)
            
            community_data = self.detect_communities(all_comments, all_edges)
            
            # Generate network visualization
            if progress_callback:
                progress_callback('Generating network visualization...', 98)
            
            network_viz = None
            if community_data.get('user_to_community'):
                network_viz = self.generate_community_network_visualization(
                    all_comments, all_edges, community_data['user_to_community']
                )
            
            # Add visualization to community data
            if network_viz:
                community_data['network_visualization'] = network_viz
            
            # Prepare result data
            result_data = {
                'success': True,
                'channel_metadata': channel_metadata,
                'videos_analyzed': len(videos_data),
                'total_comments': len(all_comments),
                'influencers': influencers[:20],
                'sentiment_analysis': sentiment_analysis_result,
                'community_detection': community_data,
                'analysis_time': datetime.now().isoformat(),
                'analysis_type': 'channel'
            }
            
            if progress_callback:
                progress_callback('Analysis complete!', 100)
            
            return {
                'success': True,
                'data': result_data
            }
            
        except Exception as e:
            print(f"Error during channel analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def analyze_video(self, video_url, progress_callback=None):
        """Analyze a single YouTube video"""
        try:
            if progress_callback:
                progress_callback('Starting video analysis...', 5)
            
            # Extract video ID
            if progress_callback:
                progress_callback('Extracting video ID...', 10)
            
            video_id = self.extract_video_id(video_url)
            
            # Get video metadata
            if progress_callback:
                progress_callback('Fetching video information...', 20)
            
            video_metadata = self.get_video_metadata(video_id)
            if not video_metadata:
                return {'success': False, 'error': 'Could not fetch video metadata'}
            
            # Get channel ID from video metadata
            channel_id = video_metadata['channel_id']
            
            # Get channel metadata for context
            channel_metadata = self.get_channel_metadata(channel_id)
            
            # Create videos_data with just this video
            videos_data = [video_metadata]
            
            # Analyze comments
            if progress_callback:
                progress_callback('Analyzing comments...', 40)
            
            all_comments, all_edges = self.analyze_comments(video_id, channel_id, max_comments=5000)
            
            # Add video ID to comments for tracking
            for comment in all_comments:
                comment['video_id'] = video_id
            
            # Calculate influencer scores (lower min_comments for single video)
            if progress_callback:
                progress_callback('Calculating influencer scores...', 75)
            
            influencers = self.calculate_influencer_scores(all_comments, all_edges, videos_data, min_comments=1)
            
            # Run sentiment analysis
            if progress_callback:
                progress_callback('Running sentiment analysis...', 82)
            
            sentiment_analysis_result = None
            if all_comments:
                try:
                    print(f"[YOUTUBE_ANALYZER] Video: Running sentiment analysis on {len(all_comments)} comments...")
                    sentiment_analysis_result = run_sentiment_analysis(all_comments)
                    print(f"[YOUTUBE_ANALYZER] Video: Sentiment complete. Score: {sentiment_analysis_result.get('overall_score')}")
                    print(f"[YOUTUBE_ANALYZER] Video: Word cloud exists: {bool(sentiment_analysis_result.get('word_cloud'))}")
                    print(f"[YOUTUBE_ANALYZER] Video: Top comments: {len(sentiment_analysis_result.get('top_like_comments', []))}")
                except Exception as e:
                    print(f"[YOUTUBE_ANALYZER] Video: Sentiment analysis error: {e}")
                    import traceback
                    traceback.print_exc()
                    sentiment_analysis_result = {
                        "overall_score": 0,
                        "label_counts": {"positive": 0, "neutral": 0, "negative": 0},
                        "word_cloud": None,
                        "pie_chart": None,
                        "top_like_comments": [],
                    }
            
            # Detect communities
            if progress_callback:
                progress_callback('Detecting communities...', 88)
            
            community_data = self.detect_communities(all_comments, all_edges)
            
            # Generate network visualization
            if progress_callback:
                progress_callback('Generating network visualization...', 95)
            
            network_viz = None
            if community_data.get('user_to_community'):
                network_viz = self.generate_community_network_visualization(
                    all_comments, all_edges, community_data['user_to_community']
                )
            
            # Add visualization to community data
            if network_viz:
                community_data['network_visualization'] = network_viz
            
            # Prepare result data
            result_data = {
                'success': True,
                'video_metadata': video_metadata,
                'channel_metadata': channel_metadata,
                'videos_analyzed': 1,
                'total_comments': len(all_comments),
                'influencers': influencers[:20],
                'sentiment_analysis': sentiment_analysis_result,
                'community_detection': community_data,
                'analysis_time': datetime.now().isoformat(),
                'analysis_type': 'video'
            }
            
            if progress_callback:
                progress_callback('Analysis complete!', 100)
            
            return {
                'success': True,
                'data': result_data
            }
            
        except Exception as e:
            print(f"Error during video analysis: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def analyze(self, input_url, progress_callback=None):
        """Analyze YouTube input (auto-detects channel or video)"""
        try:
            # Auto-detect if it's a video or channel
            if self.looks_like_video_input(input_url):
                print(f"Detected video input: {input_url}")
                return self.analyze_video(input_url, progress_callback)
            else:
                print(f"Detected channel input: {input_url}")
                return self.analyze_channel(input_url, progress_callback)
                
        except Exception as e:
            return {'success': False, 'error': f'Analysis error: {str(e)}'}