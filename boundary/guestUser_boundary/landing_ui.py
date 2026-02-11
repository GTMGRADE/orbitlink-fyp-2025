from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from controller.guestUser_controller.landing_controller import LandingPageController
from controller.guestUser_controller.contact_controller import ContactController
import logging

logger = logging.getLogger(__name__)

landing_bp = Blueprint('landing', __name__, template_folder='../../Templates')

@landing_bp.route('/')
def landing_page():
    logger.info("Landing page accessed")
    # Get landing data
    controller = LandingPageController()
    landing_data = controller.get_landing_data()
    
    # Get contact form data
    contact_controller = ContactController()
    contact_data = contact_controller.get_contact_data()
    
    # Merge data
    data = {**landing_data, **contact_data}
    return render_template('landing.html', **data)

@landing_bp.route('/contact', methods=['POST'])
def contact_submit():
    """Handle contact form submission"""
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