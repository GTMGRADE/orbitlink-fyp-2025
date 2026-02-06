from flask import Blueprint, jsonify, session, request
from Controller.admin_view_user_accounts_controller import AdminViewUserAccountsController
from Controller.admin_search_user_accounts_controller import AdminSearchUserAccountsController
from Controller.admin_suspend_user_account_controller import AdminSuspendUserAccountController
from Controller.admin_view_feedback_controller import AdminViewFeedbackController

admin_api_bp = Blueprint("admin_api", __name__)

#admin is determined by shared login session user_type
def require_admin():
    return session.get("user_type") == "admin"

@admin_api_bp.get("/api/admin/users")
def get_users():
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401

    controller = AdminViewUserAccountsController()
    users = controller.handle()
    return jsonify(users), 200


@admin_api_bp.get("/api/admin/users/search")
def search_users():
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401

    keyword = request.args.get("q", "")
    controller = AdminSearchUserAccountsController()
    users = controller.handle(keyword)
    return jsonify(users), 200


@admin_api_bp.post("/api/admin/users/<int:user_id>/toggle-suspend")
def toggle_suspend(user_id):
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401

    controller = AdminSuspendUserAccountController()
    result = controller.handle(user_id)

    if result.get("ok"):
        return jsonify({"ok": True, "user": result["user"]}), 200

    return jsonify({"error": result.get("error", "Request failed.")}), result.get("code", 400)


@admin_api_bp.get("/api/admin/feedback")
def get_feedback():
    if not require_admin():
        return jsonify({"error": "Unauthorized"}), 401

    controller = AdminViewFeedbackController()
    feedback = controller.handle()
    return jsonify(feedback), 200
