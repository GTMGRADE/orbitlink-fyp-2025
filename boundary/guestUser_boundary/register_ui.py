from flask import Blueprint, render_template, request, redirect, url_for, flash
import logging
from controller.guestUser_controller.register_controller import RegisterController

logger = logging.getLogger(__name__)

register_bp = Blueprint('register', __name__, template_folder='templates')

@register_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    logger.info("Register page accessed")
    
    controller = RegisterController()
    
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validate required fields
        if not all([email, username, password, role]):
            flash('All fields are required', 'error')
            return render_template('register.html', **controller.get_register_page_data())
        
        # Register user
        success, message, user_data = controller.register_user(email, username, password, role)
        
        if success:
            flash(message, 'success')
            # STAY ON SAME PAGE instead of redirecting
            return render_template('register.html', **controller.get_register_page_data())
        else:
            flash(message, 'error')
            return render_template('register.html', **controller.get_register_page_data())
    
    # GET request - show registration form
    return render_template('register.html', **controller.get_register_page_data())