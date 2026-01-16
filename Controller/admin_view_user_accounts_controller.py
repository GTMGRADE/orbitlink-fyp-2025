# controllers/admin_view_user_accounts_controller.py
from entity.account_entity import AccountEntity

class AdminViewUserAccountsController:
    def handle(self) -> list[dict]:
        """
        Return all user accounts.

        Boundary responsibilities:
        - check session/admin auth
        - convert to JSON/HTML response
        """
        return AccountEntity.retrieve_user_accounts()
