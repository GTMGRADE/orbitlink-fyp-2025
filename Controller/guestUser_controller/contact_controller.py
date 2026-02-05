import logging
from flask_mail import Message
from flask import current_app

logger = logging.getLogger(__name__)

class ContactController:
    def __init__(self):
        pass
    
    def send_contact_email(self, email, name, message):
        """
        Send contact form email to the company
        Returns: (success, message)
        """
        try:
            # Create email message
            msg = Message(
                subject=f"New Contact Form Message from {name}",
                recipients=["orbitlinkteam@gmail.com"],  # Your company email
                body=f"""
Name: {name}
Email: {email}
Message:
{message}
                """,
                reply_to=email
            )
            
            # Send email
            from flask_mail import Mail
            mail = Mail(current_app)
            mail.send(msg)
            
            logger.info(f"Contact form email sent from {name} ({email})")
            return True, "Thank you! Your message has been sent successfully."
            
        except Exception as e:
            logger.error(f"Error sending contact email: {str(e)}")
            return False, "Oops! Something went wrong. Please try again later."
    
    def get_contact_data(self):
        """Get data for contact form"""
        # Return empty dict - LandingPageController provides all contact data
        return {}
