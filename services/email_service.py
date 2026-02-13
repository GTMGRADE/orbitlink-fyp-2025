"""
Email service for sending welcome and notification emails
"""
import logging
from flask_mail import Message, Mail
from flask import current_app

logger = logging.getLogger(__name__)

def send_welcome_email(user_email, username):
    """
    Send welcome email to newly registered user after subscription activation
    
    Args:
        user_email: User's email address
        username: User's username
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        subject = "Welcome to OrbitLink - Your Account is Ready! 🎉"
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #f24822 0%, #ff7043 100%); color: white; padding: 30px 20px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .content {{ padding: 30px; }}
        .login-box {{ background: #f9f9f9; border: 2px solid #f24822; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .login-box h3 {{ color: #f24822; margin-top: 0; }}
        .info-line {{ margin: 10px 0; padding: 8px; background: white; border-radius: 4px; }}
        .feature-list {{ background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .feature-item {{ margin: 10px 0; padding-left: 25px; position: relative; }}
        .feature-item:before {{ content: "✅"; position: absolute; left: 0; }}
        .cta-button {{ display: inline-block; background: #f24822; color: white !important; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
        .footer {{ background: #1e3167; color: white; padding: 20px; text-align: center; font-size: 14px; }}
        .highlight {{ color: #f24822; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Welcome to OrbitLink!</h1>
        </div>
        
        <div class="content">
            <p><strong>Hi {username},</strong></p>
            
            <p>Your account has been successfully activated! You're all set to start analyzing YouTube engagement with powerful Social Network Analysis tools.</p>
            
            <div class="login-box">
                <h3>🔐 Your Login Details</h3>
                <div class="info-line"><strong>Email:</strong> {user_email}</div>
                <div class="info-line"><strong>Username:</strong> {username}</div>
            </div>
            
            <div class="feature-list">
                <h3>🎁 What's Included</h3>
                <p>Your <span class="highlight">30-day free trial</span> has started! Explore all features:</p>
                <div class="feature-item">Sentiment Analysis - Understand audience emotions</div>
                <div class="feature-item">Engagement Detection - Identify key participants</div>
                <div class="feature-item">Community Detection - Discover user clusters</div>
                <div class="feature-item">Predictive Analytics - Forecast engagement trends</div>
                <p style="margin-top: 15px; font-size: 14px;">After 30 days, your subscription will automatically renew at <strong>$49/month</strong>.</p>
            </div>
            
            <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">📚 Quick Start Guide</h3>
                <ol>
                    <li>Create your first project</li>
                    <li>Analyze YouTube channel or video comments</li>
                    <li>Run comprehensive SNA analyses</li>
                    <li>Export professional PDF reports</li>
                </ol>
            </div>
            
            <p style="margin-top: 30px; font-size: 14px; color: #666;">
                <strong>Need help?</strong> Contact us at <a href="mailto:orbitlinkteam@gmail.com">orbitlinkteam@gmail.com</a>
            </p>
            
            <p style="margin-top: 20px;">
                Happy analyzing!<br>
                <strong>The OrbitLink Team</strong>
            </p>
        </div>
        
        <div class="footer">
            <p>© 2026 OrbitLink Analytics Platform. All rights reserved.</p>
            <p style="font-size: 12px; margin-top: 10px; opacity: 0.8;">This is an automated message.</p>
        </div>
    </div>
</body>
</html>
"""
        
        text_body = f"""
Hi {username},

Welcome to OrbitLink! 🚀 

Your account has been successfully activated!

🔐 Your Login Details:
- Email: {user_email}
- Username: {username}

🎁 What's Included:
Your 30-day free trial has started! Explore all features:
✅ Sentiment Analysis
✅ Engagement Detection  
✅ Community Detection
✅ Predictive Analytics

After 30 days, your subscription renews at $49/month.

📚 Quick Start:
1. Create your first project
2. Analyze YouTube channel/video comments
3. Run comprehensive SNA analyses
4. Export professional PDF reports

Need help? Contact us at orbitlinkteam@gmail.com

Happy analyzing!  
The OrbitLink Team
"""
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=text_body,
            html=html_body
        )
        
        # Use current_app to get the mail instance
        mail = Mail(current_app)
        mail.send(msg)
        
        logger.info(f"Welcome email sent successfully to {user_email}")
        return True, "Welcome email sent successfully"
        
    except Exception as e:
        logger.error(f"Error sending welcome email to {user_email}: {str(e)}")
        return False, f"Error sending welcome email: {str(e)}"
