# entities/website_content_entity.py
from db_config import get_connection


class WebsiteContentEntity:
    """
    Entity for managing website content stored in MongoDB.
    """

    @classmethod
    def get_content(cls, page_id: int) -> dict | None:
        """
        Get content for a page from database. Returns dict or None if not found.
        """
        db = get_connection()
        if db is None:
            return None
        
        try:
            page = db['website_content'].find_one({"page_id": page_id})
            return page if page else None
        except Exception as e:
            print(f"Error fetching content: {e}")
            return None

    @classmethod
    def update_content(cls, page_id: int, updated_content: str) -> dict | None:
        """
        Update page content in database.
        Returns updated page dict, or None if page not found / invalid.
        """
        db = get_connection()
        if db is None:
            return None

        updated_content = (updated_content or "").strip()
        if not updated_content:
            return None

        try:
            result = db['website_content'].update_one(
                {"page_id": page_id},
                {"$set": {"content": updated_content}}
            )
            if result.matched_count > 0:
                return db['website_content'].find_one({"page_id": page_id})
            return None
        except Exception as e:
            print(f"Error updating content: {e}")
            return None
