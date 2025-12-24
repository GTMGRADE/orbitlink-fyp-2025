# controllers/admin_logout.py
class AdminLogoutController:
    def handle(self) -> dict:
        # Session clearing stays in boundary
        return {"ok": True}
