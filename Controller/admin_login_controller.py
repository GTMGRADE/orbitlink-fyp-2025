# controllers/admin_login.py
from entity.account_entity import AccountEntity
from entity.account_entity import LoginError

class AdminLoginController:
    """
    Controller logic only:
    - validate input
    - call AccountEntity.authenticate()
    - return result to boundary
    Boundary decides session + redirect/render.
    """

    def handle(self, data: dict) -> dict:
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return {"ok": False, "error": "Email and password are required."}

        try:
            admin_account = AccountEntity.authenticate(email=email, password=password)
            return {"ok": True, "admin": admin_account.to_dict()}
        except LoginError:
            return {"ok": False, "error": "Invalid email or password."}
