# controllers/admin_suspend_user_account_controller.py
from entity.account_entity import AccountEntity

class AdminSuspendUserAccountController:
    def handle(self, user_id: str) -> dict:
        """
        Toggle a user's status between Active <-> Suspended.

        Matches boundary endpoint:
        POST /api/admin/users/<id>/toggle-suspend

        Returns:
        - {"ok": True, "user": {...}} on success
        - {"ok": False, "error": "...", "code": 404} if not found
        """
        updated_user = AccountEntity.toggle_suspend(user_id)

        if updated_user is None:
            return {"ok": False, "error": "User not found", "code": 404}

        return {"ok": True, "user": updated_user}
