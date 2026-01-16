# entities/website_content_entity.py

class WebsiteContentEntity:
    """
    TEMPORARY entity for website content (no DB).
    Stores content in-memory so updates persist during runtime.
    """

    _PAGES = {
        1: {
            "page_id": 1,
            "title": "Home",
            "content": "Welcome to OrbitLink!"
        },
        2: {
            "page_id": 2,
            "title": "About",
            "content": "About OrbitLink..."
        },
    }

    @classmethod
    def get_content(cls, page_id: int) -> dict | None:
        """
        Get content for a page. Returns dict or None if not found.
        """
        page = cls._PAGES.get(page_id)
        return page.copy() if page else None

    @classmethod
    def update_content(cls, page_id: int, updated_content: str) -> dict | None:
        """
        Update page content.
        Returns updated page dict, or None if page not found / invalid.
        """
        if page_id not in cls._PAGES:
            return None

        updated_content = (updated_content or "").strip()
        if not updated_content:
            return None

        cls._PAGES[page_id]["content"] = updated_content
        return cls._PAGES[page_id].copy()
