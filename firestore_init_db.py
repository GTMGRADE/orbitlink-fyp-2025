# init_db.py
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


def create_index(
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

def _initialize_collection(
    db: Database,
    collection_name: str,
    fields: Dict[str, str],
    index_configs: List[Dict[str, Any]]
) -> bool:
    """
    Initialize a MongoDB collection with structure document and indexes.
    
    Args:
        db: MongoDB database object
        collection_name: Name of the collection to initialize
        fields: Dictionary describing the collection's fields
        index_configs: List of index configurations, each containing:
            - 'spec': Index specification (string or list of tuples)
            - 'name': Display name for the index
            - 'unique': Whether the index should be unique (default: False)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing '{collection_name}' collection...")
        collection = db[collection_name]
        logger.info(f"{collection_name.capitalize()} collection object obtained")
        
        # Create structure document
        structure_doc = {
            '_id': '_structure',
            '_type': 'collection_structure',
            'fields': fields,
            'indexes': [
                {
                    'fields': config['spec'] if isinstance(config['spec'], list) else [config['spec']],
                    'unique': config.get('unique', False)
                }
                for config in index_configs
            ],
            'created_at': datetime.utcnow()
        }
        logger.info(f"Structure document prepared for {collection_name} collection")
        
        # Upsert structure document to ensure collection exists
        logger.info(f"Performing upsert operation on {collection_name} collection...")
        result = collection.update_one(
            {'_id': '_structure'},
            {'$set': structure_doc},
            upsert=True
        )
        logger.info(f"Upsert result - matched: {result.matched_count}, modified: {result.modified_count}, upserted_id: {result.upserted_id}")
        
        # Create indexes
        logger.info(f"Creating indexes for {collection_name} collection...")
        for index_config in index_configs:
            create_index(
                collection,
                index_config['spec'],
                index_name=index_config['name'],
                background=True,
                unique=index_config.get('unique', False)
            )
        logger.info(f"{collection_name.capitalize()} collection indexes processed")
        print(f"✓ {collection_name} collection initialized")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing {collection_name} collection: {type(e).__name__}: {e}", exc_info=True)
        print(f"❌ Error initializing {collection_name} collection: {e}")
        return False


def init_db() -> None:
    """Initialize MongoDB collections with sample structure"""
    logger.info("=" * 60)
    logger.info("Starting init_db() function")
    logger.info("=" * 60)
    
    try:
        logger.info("Getting database connection...")
        db = get_db()
        logger.info("Database connection obtained")
        
        # MongoDB collections are created automatically when you write to them
        # But we can create reference documents to ensure collections exist
        # and set up any initial indexes/structure
        
        print("Initializing MongoDB collections...")
        logger.info("Starting collection initialization...")
        
        # Collection configurations
        collection_configs = {
            'users': {
                'fields': {
                    'email': 'string (unique)',
                    'username': 'string (unique)',
                    'password': 'string (hashed)',
                    'created_at': 'timestamp',
                    'status': 'string (default: active)'
                },
                'indexes': [
                    {'spec': 'email', 'name': "'email' (unique)", 'unique': True},
                    {'spec': 'username', 'name': "'username' (unique)", 'unique': True},
                    {'spec': 'status', 'name': "'status'", 'unique': False}
                ]
            },
            'projects': {
                'fields': {
                    'user_id': 'ObjectId (reference to users)',
                    'name': 'string',
                    'description': 'string',
                    'last_opened': 'date',
                    'archived': 'boolean (default: false)',
                    'created_at': 'timestamp'
                },
                'indexes': [
                    {'spec': 'user_id', 'name': "'user_id'", 'unique': False},
                    {'spec': [('user_id', 1), ('archived', 1)], 'name': "'user_id' + 'archived' (compound)", 'unique': False},
                    {'spec': 'created_at', 'name': "'created_at'", 'unique': False}
                ]
            },
            'youtube_analysis': {
                'fields': {
                    'user_id': 'ObjectId (reference to users)',
                    'project_id': 'ObjectId (reference to projects)',
                    'channel_url': 'string',
                    'channel_title': 'string',
                    'analysis_data': 'object',
                    'created_at': 'timestamp'
                },
                'indexes': [
                    {'spec': [('user_id', 1), ('project_id', 1)], 'name': "'user_id' + 'project_id' (compound)", 'unique': False},
                    {'spec': 'created_at', 'name': "'created_at'", 'unique': False},
                    {'spec': [('user_id', 1), ('created_at', -1)], 'name': "'user_id' + 'created_at' (compound, descending)", 'unique': False}
                ]
            }
        }
        
        # Initialize all collections
        for collection_name, config in collection_configs.items():
            _initialize_collection(
                db,
                collection_name,
                config['fields'],
                config['indexes']
            )
        
        logger.info("All collections initialized successfully")
        print("\n✅ MongoDB collections initialized successfully")
        print("\n📝 Note: Indexes have been created automatically.")
        print("   You can verify them in Firebase Console > Firestore Database > Indexes")
        logger.info("=" * 60)
        logger.info("init_db() completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in init_db(): {type(e).__name__}: {e}", exc_info=True)
        print(f"❌ Error initializing MongoDB: {e}")
        raise

def check_database_status() -> None:
    """Check if MongoDB collections are accessible"""
    logger.info("=" * 60)
    logger.info("Starting check_database_status() function")
    logger.info("=" * 60)
    
    try:
        logger.info("Getting database connection...")
        db = get_db()
        logger.info("Database connection obtained")
        
        collections = ['users', 'projects', 'youtube_analysis']
        
        print("🔍 Checking MongoDB collections...")
        logger.info(f"Checking {len(collections)} collections: {', '.join(collections)}")
        
        for collection_name in collections:
            try:
                logger.info(f"Checking collection: {collection_name}")
                # Try to read from the collection
                collection = db[collection_name]
                logger.info(f"Collection object obtained for: {collection_name}")
                
                # Get one document to test access
                logger.info(f"Attempting to find one document in {collection_name}...")
                doc = collection.find_one()
                logger.info(f"find_one() completed for {collection_name}")
                
                logger.info(f"Counting documents in {collection_name}...")
                count = collection.count_documents({})
                logger.info(f"Document count for {collection_name}: {count}")
                
                print(f"✓ {collection_name} collection is accessible ({count} documents)")
                logger.info(f"Successfully checked {collection_name} collection")
            except Exception as e:
                logger.error(f"Error checking {collection_name} collection: {type(e).__name__}: {e}", exc_info=True)
                print(f"⚠️ {collection_name} collection check failed: {e}")
        
        logger.info("All collections checked")
        print("\n✅ MongoDB connection is working")
        logger.info("=" * 60)
        logger.info("check_database_status() completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error in check_database_status(): {type(e).__name__}: {e}", exc_info=True)
        print(f"❌ Error checking MongoDB status: {e}")

if __name__ == "__main__":
    import argparse
    
    logger.info("Script started")
    logger.info("Parsing command line arguments...")
    
    parser = argparse.ArgumentParser(description='MongoDB database management utilities')
    parser.add_argument('--init', action='store_true', help='Initialize MongoDB collections')
    parser.add_argument('--check', action='store_true', help='Check MongoDB status')
    
    args = parser.parse_args()
    logger.info(f"Arguments parsed - init: {args.init}, check: {args.check}")
    
    if args.init:
        print("🚀 Initializing MongoDB...")
        logger.info("Running initialization (--init flag)")
        init_db()
    elif args.check:
        print("🔍 Checking MongoDB status...")
        logger.info("Running status check (--check flag)")
        check_database_status()
    else:
        # Default: just initialize
        logger.info("Running default initialization (no flags)")
        print("🚀 Initializing MongoDB...")
        init_db()
    
    logger.info("Script completed")