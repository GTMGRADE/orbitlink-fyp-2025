# firestore_migrations.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, DuplicateKeyError
from pymongo.collection import Collection
from pymongo.database import Database
from typing import Union, List, Dict, Tuple, Any, Optional
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

logger.info("Loading environment variables...")
load_dotenv()
logger.info("Environment variables loaded")

def _normalize_index_spec(index_spec: Union[str, List[Tuple[str, int]], Any]) -> Tuple[Union[List[Tuple[str, int]], List[Any]], str]:
    """
    Normalize index specification to a standard format for comparison.
    
    Args:
        index_spec: Index specification (field name, list of tuples, or dict)
    
    Returns:
        Tuple of (normalized_spec, display_name) where normalized_spec is a list of tuples
    """
    if isinstance(index_spec, str):
        # Single field index
        return [(index_spec, 1)], f"'{index_spec}'"
    elif isinstance(index_spec, list):
        # Compound index or list format
        return index_spec, str(index_spec)
    else:
        # Other format (dict, etc.)
        return [index_spec], str(index_spec)


def _index_exists(collection: Collection, normalized_spec: Union[List[Tuple[str, int]], str, List[Any]]) -> bool:
    """
    Check if an index with the given specification already exists in the collection.
    
    Args:
        collection: MongoDB collection object
        normalized_spec: Normalized index specification (list of tuples)
    
    Returns:
        True if index exists, False otherwise
    """
    # Get list of existing indexes
    try:
        existing_indexes = collection.list_indexes()
        index_list = list(existing_indexes)
        logger.info(f"Found {len(index_list)} existing indexes")
    except Exception as e:
        logger.warning(f"Could not list existing indexes: {e}, proceeding with creation...")
        return False
    
    # Check if index already exists
    for existing_index in index_list:
        existing_key = existing_index.get('key', {})
        
        # Compare index keys
        if isinstance(normalized_spec, list) and len(normalized_spec) > 0:
            if isinstance(normalized_spec[0], tuple):
                # Compound index - check all fields match
                if len(existing_key) == len(normalized_spec):
                    match = all(
                        existing_key.get(field) == direction 
                        for field, direction in normalized_spec
                    )
                    if match:
                        return True
            else:
                # Single field in list format
                if existing_key == dict(normalized_spec):
                    return True
        elif isinstance(normalized_spec, str):
            # Single field string
            if normalized_spec in existing_key:
                return True
    
    return False


def safe_create_index(
    collection: Collection,
    index_spec: Union[str, List[Tuple[str, int]], Any],
    index_name: Optional[str] = None,
    background: bool = True,
    timeout: int = 30000,
    unique: bool = False
) -> bool:
    """
    Safely create an index with existence checking and timeout handling.
    
    Args:
        collection: MongoDB collection object
        index_spec: Index specification (field name, list, or dict)
        index_name: Optional name for the index (for logging)
        background: Create index in background (non-blocking)
        timeout: Timeout in milliseconds (default 30 seconds)
        unique: Whether the index should be unique
    
    Returns:
        True if index was created or already exists, False on error
    """
    try:
        # Normalize index specification
        normalized_spec, default_display_name = _normalize_index_spec(index_spec)
        display_name = index_name or default_display_name
        
        logger.info(f"Checking if index {display_name} already exists...")
        
        # Check if index already exists
        if _index_exists(collection, normalized_spec):
            logger.info(f"Index {display_name} already exists, skipping creation")
            return True
        
        logger.info(f"Index {display_name} does not exist, creating...")
        logger.info(f"Using background={background}, timeout={timeout}ms, unique={unique}")
        
        # Prepare index creation options
        create_options = {
            'background': background
        }
        if unique:
            create_options['unique'] = True
        
        # Create index with options
        logger.info(f"Initiating index creation for {display_name}...")
        result = collection.create_index(index_spec, **create_options)
        
        logger.info(f"Index {display_name} creation initiated, result: {result}")
        logger.info(f"Index {display_name} created successfully")
        return True
        
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        logger.warning(f"Error creating index {display_name}: {error_type}: {error_msg}")
        
        # Check if error is because index already exists (race condition)
        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower() or "E11000" in error_msg:
            logger.info(f"Index {display_name} already exists (detected via error), continuing...")
            return True
        
        return False


def get_db() -> Database:
    """Get MongoDB database client for the orbitlinkfyp database"""
    logger.info("Starting get_db() function")
    
    # Get MongoDB connection string from environment
    # Format: mongodb+srv://username:password@host/database?retryWrites=true&w=majority
    logger.info("Reading MONGODB_CONNECTION_STRING from environment...")
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    database_name = os.getenv("MONGODB_DATABASE_NAME", "orbitlinkfyp")
    
    if not connection_string:
        logger.error("MONGODB_CONNECTION_STRING not found in environment variables")
        raise ValueError(
            "MONGODB_CONNECTION_STRING not found in environment variables."
        )
    
    logger.info(f"Connection string found (length: {len(connection_string)} chars)")
    logger.info(f"Database name: {database_name}")
    
    try:
        logger.info("Creating MongoDB client...")
        # Create MongoDB client
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        logger.info("MongoDB client created, testing connection...")
        
        # Test connection
        server_info = client.server_info()  # Will raise exception if connection fails
        logger.info(f"Server info retrieved: MongoDB version {server_info.get('version', 'unknown')}")
        print("✓ MongoDB connection successful")
        
        # Get database
        logger.info(f"Accessing database: {database_name}")
        db = client[database_name]
        logger.info("Database object retrieved successfully")
        return db
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Connection failure: {type(e).__name__}: {e}")
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_db(): {type(e).__name__}: {e}")
        raise


def create_analysis_tables():
    """Create collections for storing YouTube analysis results and analysis sessions"""
    logger.info("=" * 60)
    logger.info("Starting create_analysis_tables() function")
    logger.info("=" * 60)
    
    try:
        logger.info("Getting database connection...")
        db = get_db()
        logger.info("Database connection obtained")
        
        print("Creating analysis collections...")
        logger.info("Starting collection initialization...")
        
        # Collection for storing analysis sessions (NEW)
        logger.info("Processing 'analysis_sessions' collection...")
        analysis_sessions_collection = db['analysis_sessions']
        logger.info("Analysis_sessions collection object obtained")
        
        structure_doc = {
            '_id': '_structure',
            '_type': 'collection_structure',
            'fields': {
                'user_id': 'ObjectId (reference to users)',
                'project_id': 'ObjectId (reference to projects)',
                'channel_url': 'string',
                'channel_title': 'string',
                'analysis_data': 'object (JSON)',
                'analysis_job_id': 'ObjectId (reference to youtube_analysis_jobs, optional)',
                'last_accessed': 'timestamp',
                'created_at': 'timestamp'
            },
            'indexes': [
                {'fields': ['user_id', 'project_id'], 'unique': True},
                {'fields': ['user_id']},
                {'fields': ['project_id']},
                {'fields': ['analysis_job_id']},
                {'fields': ['created_at']},
                {'fields': ['last_accessed']}
            ],
            'created_at': datetime.utcnow()
        }
        logger.info("Structure document prepared for analysis_sessions collection")
        
        # Use upsert to avoid duplicate key errors
        logger.info("Performing upsert operation on analysis_sessions collection...")
        result = analysis_sessions_collection.update_one(
            {'_id': '_structure'},
            {'$set': structure_doc},
            upsert=True
        )
        logger.info(f"Upsert result - matched: {result.matched_count}, modified: {result.modified_count}, upserted_id: {result.upserted_id}")
        
        # Create indexes for analysis_sessions collection
        logger.info("Creating indexes for analysis_sessions collection...")
        safe_create_index(analysis_sessions_collection, [('user_id', 1), ('project_id', 1)], 
                         index_name="'user_id' + 'project_id' (compound, unique)", background=True, unique=True)
        safe_create_index(analysis_sessions_collection, 'user_id', index_name="'user_id'", background=True)
        safe_create_index(analysis_sessions_collection, 'project_id', index_name="'project_id'", background=True)
        safe_create_index(analysis_sessions_collection, 'analysis_job_id', index_name="'analysis_job_id'", background=True)
        safe_create_index(analysis_sessions_collection, 'created_at', index_name="'created_at'", background=True)
        safe_create_index(analysis_sessions_collection, 'last_accessed', index_name="'last_accessed'", background=True)
        logger.info("Analysis_sessions collection indexes processed")
        print("✅ analysis_sessions collection created successfully")
        
        # Collection for storing analysis jobs (EXISTING)
        logger.info("Processing 'youtube_analysis_jobs' collection...")
        youtube_analysis_jobs_collection = db['youtube_analysis_jobs']
        logger.info("Youtube_analysis_jobs collection object obtained")
        
        structure_doc = {
            '_id': '_structure',
            '_type': 'collection_structure',
            'fields': {
                'user_id': 'ObjectId (reference to users)',
                'channel_url': 'string',
                'channel_id': 'string',
                'channel_name': 'string',
                'status': 'string (enum: pending, processing, completed, failed)',
                'progress': 'integer (0-100)',
                'created_at': 'timestamp',
                'started_at': 'timestamp (optional)',
                'completed_at': 'timestamp (optional)',
                'result_data': 'object (JSON)'
            },
            'indexes': [
                {'fields': ['user_id']},
                {'fields': ['status']},
                {'fields': ['channel_id']},
                {'fields': ['created_at']},
                {'fields': ['user_id', 'status']},
                {'fields': ['user_id', 'created_at']}
            ],
            'created_at': datetime.utcnow()
        }
        logger.info("Structure document prepared for youtube_analysis_jobs collection")
        
        # Use upsert to avoid duplicate key errors
        logger.info("Performing upsert operation on youtube_analysis_jobs collection...")
        result = youtube_analysis_jobs_collection.update_one(
            {'_id': '_structure'},
            {'$set': structure_doc},
            upsert=True
        )
        logger.info(f"Upsert result - matched: {result.matched_count}, modified: {result.modified_count}, upserted_id: {result.upserted_id}")
        
        # Create indexes for youtube_analysis_jobs collection
        logger.info("Creating indexes for youtube_analysis_jobs collection...")
        safe_create_index(youtube_analysis_jobs_collection, 'user_id', index_name="'user_id'", background=True)
        safe_create_index(youtube_analysis_jobs_collection, 'status', index_name="'status'", background=True)
        safe_create_index(youtube_analysis_jobs_collection, 'channel_id', index_name="'channel_id'", background=True)
        safe_create_index(youtube_analysis_jobs_collection, 'created_at', index_name="'created_at'", background=True)
        safe_create_index(youtube_analysis_jobs_collection, [('user_id', 1), ('status', 1)], 
                         index_name="'user_id' + 'status' (compound)", background=True)
        safe_create_index(youtube_analysis_jobs_collection, [('user_id', 1), ('created_at', -1)], 
                         index_name="'user_id' + 'created_at' (compound, descending)", background=True)
        logger.info("Youtube_analysis_jobs collection indexes processed")
        print("✅ youtube_analysis_jobs collection created successfully")
        
        # Collection for storing influencers data (EXISTING)
        logger.info("Processing 'youtube_influencers' collection...")
        youtube_influencers_collection = db['youtube_influencers']
        logger.info("Youtube_influencers collection object obtained")
        
        structure_doc = {
            '_id': '_structure',
            '_type': 'collection_structure',
            'fields': {
                'analysis_job_id': 'ObjectId (reference to youtube_analysis_jobs)',
                'rank': 'integer',
                'author_id': 'string',
                'author_name': 'string',
                'total_score': 'decimal',
                'engagement_score': 'decimal',
                'network_score': 'decimal',
                'quality_score': 'decimal',
                'consistency_score': 'decimal',
                'activity_score': 'decimal',
                'responsiveness_score': 'decimal',
                'total_comments': 'integer',
                'total_likes': 'integer',
                'replies_received': 'integer',
                'unique_videos': 'integer',
                'indegree': 'integer',
                'outdegree': 'integer',
                'channel_owner_replies': 'integer',
                'thread_starts': 'integer',
                'avg_sentiment': 'decimal',
                'created_at': 'timestamp'
            },
            'indexes': [
                {'fields': ['analysis_job_id']},
                {'fields': ['analysis_job_id', 'rank']},
                {'fields': ['author_id']},
                {'fields': ['rank']},
                {'fields': ['created_at']}
            ],
            'created_at': datetime.utcnow()
        }
        logger.info("Structure document prepared for youtube_influencers collection")
        
        # Use upsert to avoid duplicate key errors
        logger.info("Performing upsert operation on youtube_influencers collection...")
        result = youtube_influencers_collection.update_one(
            {'_id': '_structure'},
            {'$set': structure_doc},
            upsert=True
        )
        logger.info(f"Upsert result - matched: {result.matched_count}, modified: {result.modified_count}, upserted_id: {result.upserted_id}")
        
        # Create indexes for youtube_influencers collection
        logger.info("Creating indexes for youtube_influencers collection...")
        safe_create_index(youtube_influencers_collection, 'analysis_job_id', index_name="'analysis_job_id'", background=True)
        safe_create_index(youtube_influencers_collection, [('analysis_job_id', 1), ('rank', 1)], 
                         index_name="'analysis_job_id' + 'rank' (compound)", background=True)
        safe_create_index(youtube_influencers_collection, 'author_id', index_name="'author_id'", background=True)
        safe_create_index(youtube_influencers_collection, 'rank', index_name="'rank'", background=True)
        safe_create_index(youtube_influencers_collection, 'created_at', index_name="'created_at'", background=True)
        logger.info("Youtube_influencers collection indexes processed")
        print("✅ youtube_influencers collection created successfully")
        
        # Collection for storing channel metadata (EXISTING)
        logger.info("Processing 'youtube_channel_metadata' collection...")
        youtube_channel_metadata_collection = db['youtube_channel_metadata']
        logger.info("Youtube_channel_metadata collection object obtained")
        
        structure_doc = {
            '_id': '_structure',
            '_type': 'collection_structure',
            'fields': {
                'analysis_job_id': 'ObjectId (reference to youtube_analysis_jobs, primary key)',
                'channel_title': 'string',
                'description': 'string',
                'subscriber_count': 'integer',
                'video_count': 'integer',
                'view_count': 'long',
                'country': 'string',
                'engagement_rate': 'decimal',
                'profile_image_url': 'string',
                'topics': 'array (JSON)',
                'created_at': 'timestamp'
            },
            'indexes': [
                {'fields': ['analysis_job_id'], 'unique': True},
                {'fields': ['channel_title']},
                {'fields': ['created_at']}
            ],
            'created_at': datetime.utcnow()
        }
        logger.info("Structure document prepared for youtube_channel_metadata collection")
        
        # Use upsert to avoid duplicate key errors
        logger.info("Performing upsert operation on youtube_channel_metadata collection...")
        result = youtube_channel_metadata_collection.update_one(
            {'_id': '_structure'},
            {'$set': structure_doc},
            upsert=True
        )
        logger.info(f"Upsert result - matched: {result.matched_count}, modified: {result.modified_count}, upserted_id: {result.upserted_id}")
        
        # Create indexes for youtube_channel_metadata collection
        logger.info("Creating indexes for youtube_channel_metadata collection...")
        safe_create_index(youtube_channel_metadata_collection, 'analysis_job_id', 
                         index_name="'analysis_job_id' (unique)", background=True, unique=True)
        safe_create_index(youtube_channel_metadata_collection, 'channel_title', index_name="'channel_title'", background=True)
        safe_create_index(youtube_channel_metadata_collection, 'created_at', index_name="'created_at'", background=True)
        logger.info("Youtube_channel_metadata collection indexes processed")
        print("✅ youtube_channel_metadata collection created successfully")
        
        # Collection for storing video data (EXISTING)
        logger.info("Processing 'youtube_videos_analysis' collection...")
        youtube_videos_analysis_collection = db['youtube_videos_analysis']
        logger.info("Youtube_videos_analysis collection object obtained")
        
        structure_doc = {
            '_id': '_structure',
            '_type': 'collection_structure',
            'fields': {
                'analysis_job_id': 'ObjectId (reference to youtube_analysis_jobs)',
                'video_id': 'string',
                'title': 'string',
                'views': 'integer',
                'likes': 'integer',
                'comments': 'integer',
                'like_rate': 'decimal',
                'comment_rate': 'decimal',
                'published_at': 'datetime',
                'created_at': 'timestamp'
            },
            'indexes': [
                {'fields': ['analysis_job_id']},
                {'fields': ['video_id']},
                {'fields': ['analysis_job_id', 'video_id']},
                {'fields': ['published_at']},
                {'fields': ['created_at']}
            ],
            'created_at': datetime.utcnow()
        }
        logger.info("Structure document prepared for youtube_videos_analysis collection")
        
        # Use upsert to avoid duplicate key errors
        logger.info("Performing upsert operation on youtube_videos_analysis collection...")
        result = youtube_videos_analysis_collection.update_one(
            {'_id': '_structure'},
            {'$set': structure_doc},
            upsert=True
        )
        logger.info(f"Upsert result - matched: {result.matched_count}, modified: {result.modified_count}, upserted_id: {result.upserted_id}")
        
        # Create indexes for youtube_videos_analysis collection
        logger.info("Creating indexes for youtube_videos_analysis collection...")
        safe_create_index(youtube_videos_analysis_collection, 'analysis_job_id', index_name="'analysis_job_id'", background=True)
        safe_create_index(youtube_videos_analysis_collection, 'video_id', index_name="'video_id'", background=True)
        safe_create_index(youtube_videos_analysis_collection, [('analysis_job_id', 1), ('video_id', 1)], 
                         index_name="'analysis_job_id' + 'video_id' (compound)", background=True)
        safe_create_index(youtube_videos_analysis_collection, 'published_at', index_name="'published_at'", background=True)
        safe_create_index(youtube_videos_analysis_collection, 'created_at', index_name="'created_at'", background=True)
        logger.info("Youtube_videos_analysis collection indexes processed")
        print("✅ youtube_videos_analysis collection created successfully")
        
        logger.info("All analysis collections initialized successfully")
        print("\n🎉 All analysis collections created/updated successfully!")
        logger.info("=" * 60)
        logger.info("create_analysis_tables() completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in create_analysis_tables(): {type(e).__name__}: {e}", exc_info=True)
        print(f"❌ Error creating collections: {e}")
        raise


if __name__ == "__main__":
    logger.info("Script started")
    logger.info("Running create_analysis_tables()...")
    print("🚀 Creating analysis collections...")
    create_analysis_tables()
    logger.info("Script completed")

