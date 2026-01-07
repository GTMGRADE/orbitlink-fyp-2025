# boundary/guestUser_boundary/register_ui.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import logging
from controller.guestUser_controller.register_controller import RegisterController
from controller.guestUser_controller.contact_controller import ContactController

logger = logging.getLogger(__name__)

register_bp = Blueprint('register', __name__, template_folder='templates')

@register_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    logger.info("Register page accessed")
    
    controller = RegisterController()
    contact_controller = ContactController()
    
    if request.method == 'POST':
        # Get form data (no role parameter)
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate required fields
        if not all([email, username, password]):
            flash('All fields are required', 'error')
            return render_template('register.html', **controller.get_register_page_data())
        
        # Register user (no role parameter)
        success, message, user_data = controller.register_user(email, username, password)
        
        if success:
            flash(message, 'success')
            return render_template('register.html', **controller.get_register_page_data())
        else:
            flash(message, 'error')
            return render_template('register.html', **controller.get_register_page_data())
    
    # GET request - show registration form
    register_data = controller.get_register_page_data()
    contact_data = contact_controller.get_contact_data()
    data = {**register_data, **contact_data}
    return render_template('register.html', **data)

@register_bp.route('/register/contact', methods=['POST'])
def register_contact_submit():
    """Handle contact form submission from register page"""
    try:
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate
        if not all([email, name, message]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all fields'
            }), 400
        
        # Send email
        controller = ContactController()
        success, result_message = controller.send_contact_email(email, name, message)
        
        return jsonify({
            'success': success,
            'message': result_message
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"Error in contact submission: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500