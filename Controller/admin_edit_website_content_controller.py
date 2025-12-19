# controllers/admin_edit_website_content_controller.py
from Entity.website_content_entity import WebsiteContentEntity

class AdminEditWebsiteContentController:
    def handle(self, page_id: int, updated_content: str) -> dict:
        """
        Edit website content.
        Returns:
        - {"ok": True, "page": {...}}
        - {"ok": False, "error": "...", "code": 400/404}
        """
        updated_page = WebsiteContentEntity.update_content(page_id, updated_content)

        if updated_page is None:
            # could be page not found OR empty content
            # keep it simple: decide based on page existence
            if WebsiteContentEntity.get_content(page_id) is None:
                return {"ok": False, "error": "Page not found", "code": 404}
            return {"ok": False, "error": "Content cannot be empty", "code": 400}

        return {"ok": True, "page": updated_page}
