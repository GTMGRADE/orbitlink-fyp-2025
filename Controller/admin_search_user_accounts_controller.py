# controllers/admin_search_user_accounts_controller.py
from Entity.account_entity import AccountEntity

class AdminSearchUserAccountsController:
    def handle(self, keyword: str) -> list[dict]:
        """
        Search user accounts by keyword.

        Boundary responsibilities:
        - check session/admin auth
        - decide response format (empty list vs message)
        """
        return AccountEntity.search_user_accounts(keyword)
