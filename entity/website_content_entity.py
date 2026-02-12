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
        Update page content in database using separate fields approach.
        Parses JSON content and routes to page-specific methods.
        Returns updated page dict, or None if page not found / invalid.
        """
        import json
        
        updated_content = (updated_content or "").strip()
        if not updated_content:
            return None

        try:
            # Parse the JSON content from the form
            content_data = json.loads(updated_content)
            print(f"[DB] Parsed JSON for page {page_id}: {list(content_data.keys()) if isinstance(content_data, dict) else type(content_data)}")
            
            # Route to page-specific update methods
            if page_id == 1:
                return cls.update_content_page1(page_id, content_data)
            elif page_id == 2:
                return cls.update_content_page2(page_id, content_data)
            elif page_id == 3:
                return cls.update_content_page3(page_id, content_data)
            elif page_id == 4:
                return cls.update_content_page4(page_id, content_data)
            else:
                print(f"[DB] Unknown page_id: {page_id}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"[DB] JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"[DB] Error: {e}")
            return None
    
    @classmethod
    def update_content_page1(cls, page_id: int, data: dict) -> dict | None:
        """Update page 1 (Hero) with separate fields: headline, description"""
        db = get_connection()
        if db is None:
            return None

        try:
            # Get exactly what the user typed
            headline = data.get('headline', '').strip()
            description = data.get('description', '').strip()
            
            print(f"[DB] PAGE 1 UPDATE - headline: {repr(headline)}, description: {repr(description[:50])}...")
            
            # Save exactly what user entered - no modifications
            result = db['website_content'].update_one(
                {"page_id": page_id},
                {"$set": {
                    "headline": headline,
                    "description": description,
                    "content_type": "separate_fields"
                }}
            )
            print(f"[DB] Update result: matched={result.matched_count}, modified={result.modified_count}")
            
            if result.matched_count > 0:
                updated = db['website_content'].find_one({"page_id": page_id})
                return updated
            return None
        except Exception as e:
            print(f"[DB] Error: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    @classmethod
    def update_content_page3(cls, page_id: int, pricing_data: dict) -> dict | None:
        """
        Update page 3 (pricing) content using separate database fields.
        Saves: plan_name, plan_price, plan_period, features (as list)
        """
        db = get_connection()
        if db is None:
            print(f"[DB] Connection failed")
            return None

        if page_id != 3:
            return None

        try:
            plans = pricing_data.get('plans', {})
            free_plan = plans.get('free', {}) if isinstance(plans, dict) else {}
            
            # Save exactly what user entered - no defaults
            plan_name = free_plan.get('name', '')
            plan_price = free_plan.get('price', '')
            plan_period = free_plan.get('period', '')
            features = pricing_data.get('included', [])
            
            print(f"[DB] Updating page 3: name='{plan_name}', price='{plan_price}', period='{plan_period}', features={len(features)}")
            
            result = db['website_content'].update_one(
                {"page_id": page_id},
                {
                    "$set": {
                        "plan_name": plan_name,
                        "plan_price": plan_price,
                        "plan_period": plan_period,
                        "features": features,
                        "content_type": "separate_fields"
                    }
                }
            )
            print(f"[DB] Update result: matched={result.matched_count}, modified={result.modified_count}")
            
            if result.matched_count > 0:
                updated = db['website_content'].find_one({"page_id": page_id})
                return updated
            
            print(f"[DB] No documents matched")
            return None
            
        except Exception as e:
            print(f"[DB] Error updating page 3: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # NOTE: update_content_page1 is defined earlier in this file (around line 65)
    # with proper validation - DO NOT duplicate it here!
    
    @classmethod
    def update_content_page2(cls, page_id: int, data: dict) -> dict | None:
        """Update page 2 (Features) with separate field: features (list)"""
        db = get_connection()
        if db is None:
            return None

        try:
            features = data.get('features', [])
            print(f"[DB] Updating page 2 with {len(features)} features")
            result = db['website_content'].update_one(
                {"page_id": page_id},
                {"$set": {
                    "features": features,
                    "content_type": "separate_fields"
                }}
            )
            print(f"[DB] Update result: matched={result.matched_count}, modified={result.modified_count}")
            
            if result.matched_count > 0:
                updated = db['website_content'].find_one({"page_id": page_id})
                return updated
            return None
        except Exception as e:
            print(f"[DB] Error: {e}")
            return None
    
    @classmethod
    def update_content_page4(cls, page_id: int, data: dict) -> dict | None:
        """Update page 4 (Contact) with separate fields: email, phone, phone_hours, response_time, about_us"""
        db = get_connection()
        if db is None:
            return None

        try:
            print(f"[DB] Updating page 4 with: email, phone, phone_hours, response_time, about_us")
            result = db['website_content'].update_one(
                {"page_id": page_id},
                {"$set": {
                    "email": data.get('email', ''),
                    "phone": data.get('phone', ''),
                    "phone_hours": data.get('phone_hours', ''),
                    "response_time": data.get('response_time', ''),
                    "about_us": data.get('about_us', ''),
                    "content_type": "separate_fields"
                }}
            )
            print(f"[DB] Update result: matched={result.matched_count}, modified={result.modified_count}")
            
            if result.matched_count > 0:
                updated = db['website_content'].find_one({"page_id": page_id})
                return updated
            return None
        except Exception as e:
            print(f"[DB] Error: {e}")
            return None