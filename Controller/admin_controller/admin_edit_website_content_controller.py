# controllers/admin_edit_website_content_controller.py
from entity.website_content_entity import WebsiteContentEntity
from entity.landing_content import LandingContent
import json

class AdminEditWebsiteContentController:
    def handle(self, page_id: int, updated_content: str) -> dict:
        """
        Edit website content.
        All pages now use separate database fields (no JSON stored).
        """
        updated_content = (updated_content or "").strip()
        
        if not updated_content:
            return {"ok": False, "error": "Content cannot be empty", "code": 400}
        
        print(f"[DEBUG] About to update page {page_id}")
        print(f"[DEBUG] Content length: {len(updated_content)}")
        
        try:
            # Parse JSON from form submission
            data = json.loads(updated_content)
        except json.JSONDecodeError:
            return {"ok": False, "error": "Invalid format", "code": 400}
        
        # Update based on page_id
        if page_id == 1:
            result = WebsiteContentEntity.update_content_page1(page_id, data)
        elif page_id == 2:
            result = WebsiteContentEntity.update_content_page2(page_id, data)
        elif page_id == 3:
            result = WebsiteContentEntity.update_content_page3(page_id, data)
        elif page_id == 4:
            result = WebsiteContentEntity.update_content_page4(page_id, data)
        else:
            return {"ok": False, "error": "Unknown page", "code": 404}
        
        print(f"[DEBUG] Update result: {result is not None}")

        if result is None:
            print(f"[DEBUG] Update failed or page not found")
            if WebsiteContentEntity.get_content(page_id) is None:
                return {"ok": False, "error": "Page not found", "code": 404}
            return {"ok": False, "error": "Content update failed", "code": 400}

        # Clear the landing content cache so changes are visible immediately
        LandingContent.clear_cache()
        print(f"[DEBUG] Cache cleared successfully")

        return {"ok": True, "page": result}
