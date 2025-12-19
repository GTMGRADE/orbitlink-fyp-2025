class AccountEntity:
    """
    TEMPORARY entity (no DB).
    - Hardcoded admin auth
    - In-memory user list matching the API boundary schema
    """

    ADMIN_EMAIL = "admin@example.com"
    ADMIN_PASSWORD = "adminpass"

    #Match admin_users page 
    _USERS = [
        {"id": 1, "name": "Grace Fu", "role": "Business User", "email": "grace123@yahoo.com", "status": "Active"},
        {"id": 2, "name": "Denise Phua", "role": "Influencer User", "email": "denise456@gmail.com", "status": "Active"},
        {"id": 3, "name": "Rachel Ong", "role": "Business User", "email": "rachel789@hotmail.com", "status": "Suspended"},
    ]

    def __init__(self, email: str, role: str):
        self.email = email
        self.role = role

    @classmethod
    def authenticate(cls, email: str, password: str) -> "AccountEntity":
        email = (email or "").strip().lower()
        password = password or ""

        if email == cls.ADMIN_EMAIL and password == cls.ADMIN_PASSWORD:
            return cls(email=email, role="Admin")

        raise LoginError("Invalid email or password.")

    def to_dict(self) -> dict:
        return {"email": self.email, "role": self.role}

    # User account operations
    @classmethod
    def retrieve_user_accounts(cls) -> list[dict]:
        # return copies so other layers don't mutate the internal list accidentally
        return [u.copy() for u in cls._USERS]

    @classmethod
    def search_user_accounts(cls, keyword: str) -> list[dict]:
        kw = (keyword or "").strip().lower()
        if not kw:
            return []

        results = []
        for u in cls._USERS:
            haystack = f'{u.get("name","")} {u.get("email","")} {u.get("role","")} {u.get("status","")}'.lower()
            if kw in haystack:
                results.append(u.copy())
        return results

    @classmethod
    def get_user_by_id(cls, user_id: int) -> dict | None:
        for u in cls._USERS:
            if u["id"] == user_id:
                return u
        return None

    @classmethod
    def update_status(cls, user_id: int, status: str) -> bool:
        """
        Keep this for your diagram (update status), but make it REAL (not always True).
        """
        status = (status or "").strip()
        if status not in ("Active", "Suspended"):
            return False

        user = cls.get_user_by_id(user_id)
        if not user:
            return False

        user["status"] = status
        return True

    @classmethod
    def toggle_suspend(cls, user_id: int) -> dict | None:
        """
        Needed by your current endpoint:
        POST /api/admin/users/<id>/toggle-suspend
        """
        user = cls.get_user_by_id(user_id)
        if not user:
            return None

        user["status"] = "Suspended" if user["status"] == "Active" else "Active"
        return user.copy()

class LoginError(Exception):
    """Raised when login credentials are invalid."""
    pass
