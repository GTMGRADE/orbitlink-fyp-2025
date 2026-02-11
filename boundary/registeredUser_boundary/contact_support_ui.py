# boundary/registeredUser_boundary/contact_support_ui.py
import logging
from flask import Blueprint, render_template, request, jsonify
from Controller.guestUser_controller.contact_controller import ContactController

logger = logging.getLogger(__name__)

contact_support_bp = Blueprint("contact_support", __name__)

@contact_support_bp.route("/contact-support")
def contact_support_page():
    """Contact support page for registered users"""
    controller = ContactController()
    data = controller.get_contact_data()
    data['page_title'] = 'Contact Support - OrbitLink'
    
    # Get referrer information
    referrer = request.args.get('from', 'dashboard')
    data['referrer'] = referrer
    
    return render_template("contact_support.html", **data)

@contact_support_bp.route("/contact-support/submit", methods=["POST"])
def contact_support_submit():
    """Handle contact support form submission"""
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
        
        # Send email using existing ContactController
        controller = ContactController()
        success, result_message = controller.send_contact_email(email, name, message)
        
        return jsonify({
            'success': success,
            'message': result_message
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"Error in contact support submission: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500