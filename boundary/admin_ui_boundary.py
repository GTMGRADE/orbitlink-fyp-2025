# boundary/admin_ui_boundary.py
from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify
from controller.admin_edit_website_content_controller import AdminEditWebsiteContentController
from entity.website_content_entity import WebsiteContentEntity

admin_ui_bp = Blueprint("admin_ui", __name__)

def is_admin_logged_in() -> bool:
    return session.get("user_type") == "admin"


# DEBUG: check what session you really have
@admin_ui_bp.get("/admin/debug-session")
def admin_debug_session():
    return jsonify(dict(session))


@admin_ui_bp.get("/admin")
def admin_home():
    if not is_admin_logged_in():
        return redirect(url_for("user.login_get"))
    return redirect(url_for("admin_ui.admin_users_page"))


@admin_ui_bp.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("landing.landing_page"))


@admin_ui_bp.get("/admin/users")
def admin_users_page():
    if session.get("user_type") != "admin":
        return redirect(url_for("user.login_get"))
    return render_template("admin_users.html")


@admin_ui_bp.get("/admin/reviews")
def admin_reviews_page():
    if not is_admin_logged_in():
        return redirect(url_for("user.login_get"))
    return render_template("admin_reviews.html")


@admin_ui_bp.get("/admin/edit-website")
def admin_edit_website_page():
    if not is_admin_logged_in():
        return redirect(url_for("user.login_get"))

    page_id = int(request.args.get("page_id", 1))
    page = WebsiteContentEntity.get_content(page_id)

    if page is None:
        return render_template("admin_web_editor.html", error="Page not found.", page_id=page_id)

    return render_template("admin_web_editor.html", page=page)


@admin_ui_bp.post("/admin/edit-website")
def admin_edit_website_submit():
    if not is_admin_logged_in():
        return redirect(url_for("user.login_get"))

    page_id = int(request.form.get("page_id", 1))
    updated_content = request.form.get("content", "")

    controller = AdminEditWebsiteContentController()
    result = controller.handle(page_id, updated_content)

    if result.get("ok"):
        return render_template("admin_web_editor.html", success="Updated!", page=result["page"])

    page = WebsiteContentEntity.get_content(page_id)
    return render_template(
        "admin_web_editor.html",
        error=result.get("error", "Content update failed."),
        page=page,
        page_id=page_id
    )
