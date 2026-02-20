import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from Controller.guestUser_controller.mock_payment_controller import MockPaymentController
from Controller.guestUser_controller.contact_controller import ContactController
from services.email_service import send_welcome_email

logger = logging.getLogger(__name__)

payment_bp = Blueprint("payment", __name__)

@payment_bp.get("/payment")
def payment_page():
    """Mock payment page for new users"""
    user_id = session.get("user_id")
    
    if not user_id:
        return redirect(url_for("user.login_get"))
    
    # Check if user already has subscription
    controller = MockPaymentController(user_id)
    if controller.get_user_subscription_status():
        # Already subscribed, redirect to dashboard
        session['show_welcome_message'] = True
        return redirect(url_for("projects.projects_list"))
    
    # Get payment page data
    payment_data = controller.get_payment_page_data()
    
    # Get contact data
    contact_controller = ContactController()
    contact_data = contact_controller.get_contact_data()
    
    data = {**payment_data, **contact_data}
    return render_template("payment.html", **data)

@payment_bp.post("/payment/activate")
def activate_subscription():
    """Handle mock subscription activation"""
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please login first"
        }), 401
    
    # Validate required fields (mock validation)
    card_number = request.form.get("card_number", "").strip()
    expiry_date = request.form.get("expiry_date", "").strip()
    security_code = request.form.get("security_code", "").strip()
    terms_agreed = request.form.get("terms_agreed") == "on"
    
    # Mock validation
    errors = []
    if not card_number or len(card_number.replace(" ", "")) < 16:
        errors.append("Please enter a valid 16-digit card number")
    if not expiry_date or len(expiry_date) < 5:
        errors.append("Please enter a valid expiry date (MM/YY)")
    if not security_code or len(security_code) != 3:
        errors.append("Please enter a valid 3-digit security code")
    if not terms_agreed:
        errors.append("You must agree to the subscription terms")
    
    if errors:
        return jsonify({
            "success": False,
            "message": " ".join(errors)
        }), 400
    
    # Activate subscription
    controller = MockPaymentController(user_id)
    success, message = controller.activate_subscription()
    
    if success:
        # Send welcome email to the user
        try:
            user_data = controller.get_user_data()
            if user_data:
                email_sent, email_msg = send_welcome_email(
                    user_email=user_data.get('email'),
                    username=user_data.get('username')
                )
                if email_sent:
                    logger.info(f"Welcome email sent to {user_data.get('email')}")
                else:
                    logger.warning(f"Failed to send welcome email: {email_msg}")
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            # Don't fail the subscription activation if email fails
        
        # Clear session to require fresh login after activation
        session.pop("show_welcome_message", None)
        session.pop("registration_complete", None)
        session.pop("user_id", None)
        session.pop("user_type", None)
        return jsonify({
            "success": True,
            "message": "Subscription activated successfully!",
            "redirect": url_for("user.login_get", registered=1)
        })
    else:
        return jsonify({
            "success": False,
            "message": message
        }), 400

@payment_bp.route("/payment/contact", methods=["POST"])
def payment_contact_submit():
    """Handle contact form submission from payment page"""
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