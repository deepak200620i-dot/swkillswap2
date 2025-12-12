"""Email utility functions for sending verification emails"""
import random
from flask import current_app
from flask_mail import Message


def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_verification_email(mail, recipient_email, otp, full_name=None):
    """
    Send email verification OTP to user
    
    Args:
        mail: Flask-Mail instance
        recipient_email: Email address to send to
        otp: 6-digit OTP code
        full_name: Optional user's full name for personalization
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create personalized greeting
        greeting = f"Hi {full_name}," if full_name else "Hello,"
        
        msg = Message(
            subject="Verify Your SkillSwap Account",
            recipients=[recipient_email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Email body
        msg.body = f"""{greeting}

Thank you for signing up for SkillSwap!

Your email verification code is: {otp}

This code will expire in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.

If you didn't request this code, please ignore this email.

Best regards,
The SkillSwap Team
"""
        
        # HTML version (optional, for better formatting)
        msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50;">Welcome to SkillSwap!</h2>
                    <p>{greeting}</p>
                    <p>Thank you for signing up for SkillSwap!</p>
                    <p>Your email verification code is:</p>
                    <div style="background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #666; font-size: 14px;">
                        This code will expire in {current_app.config.get('OTP_EXPIRY_MINUTES', 10)} minutes.
                    </p>
                    <p style="color: #666; font-size: 14px;">
                        If you didn't request this code, please ignore this email.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">
                        Best regards,<br>
                        The SkillSwap Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        mail.send(msg)
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {str(e)}")
        return False


def send_password_reset_email(mail, recipient_email, reset_link, full_name=None):
    """
    Send password reset email (for future use)
    
    Args:
        mail: Flask-Mail instance
        recipient_email: Email address to send to
        reset_link: Password reset link
        full_name: Optional user's full name
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        greeting = f"Hi {full_name}," if full_name else "Hello,"
        
        msg = Message(
            subject="Reset Your SkillSwap Password",
            recipients=[recipient_email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.body = f"""{greeting}

We received a request to reset your SkillSwap password.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email.

Best regards,
The SkillSwap Team
"""
        
        msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4CAF50;">Password Reset Request</h2>
                    <p>{greeting}</p>
                    <p>We received a request to reset your SkillSwap password.</p>
                    <p>Click the button below to reset your password:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    <p style="color: #666; font-size: 14px;">
                        Or copy and paste this link into your browser:<br>
                        <a href="{reset_link}">{reset_link}</a>
                    </p>
                    <p style="color: #666; font-size: 14px;">
                        This link will expire in 1 hour.
                    </p>
                    <p style="color: #666; font-size: 14px;">
                        If you didn't request a password reset, please ignore this email.
                    </p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px;">
                        Best regards,<br>
                        The SkillSwap Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        mail.send(msg)
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {str(e)}")
        return False
