from flask import Blueprint, request, jsonify
from database import get_db
from utils import (
    hash_password,
    verify_password,
    generate_token,
    validate_email,
    validate_password,
    sanitize_input,
)
from utils.email_utils import generate_otp, send_verification_email
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/send-otp", methods=["POST"])
def send_otp():
    """Send OTP to user's email for verification"""
    try:
        data = request.get_json()
        
        # Validate required fields
        email = sanitize_input(data.get("email", ""))
        full_name = sanitize_input(data.get("full_name", ""))
        password = data.get("password", "")
        
        if not email or not password or not full_name:
            return (
                jsonify({"error": "Email, password, and full name are required"}),
                400,
            )
        
        # Validate email
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        # Check if user already exists
        db = get_db()
        existing_user = db.execute(
            "SELECT id, email_verified FROM users WHERE email = %s", (email,)
        ).fetchone()
        
        if existing_user and existing_user["email_verified"]:
            return jsonify({"error": "Email already registered and verified"}), 409
        
        # Generate OTP
        otp = generate_otp()
        otp_created_at = datetime.now()
        
        # Hash password
        password_hash = hash_password(password)
        
        # Default profile picture
        names = full_name.strip().split()
        if len(names) >= 2:
            initials = f"{names[0][0]}{names[-1][0]}"
        elif names:
            initials = names[0][:2]
        else:
            initials = "SS"
        
        default_pic = f"https://ui-avatars.com/api/?name={initials}&background=random"
        
        # If user exists but not verified, update their info and OTP
        if existing_user:
            db.execute(
                "UPDATE users SET password_hash = %s, full_name = %s, profile_picture = %s, email_otp = %s, otp_created_at = %s WHERE email = %s",
                (password_hash, full_name, default_pic, otp, otp_created_at, email),
            )
        else:
            # Insert new user (unverified)
            db.execute(
                "INSERT INTO users (email, password_hash, full_name, profile_picture, email_verified, email_otp, otp_created_at) VALUES (%s, %s, %s, %s, FALSE, %s, %s)",
                (email, password_hash, full_name, default_pic, otp, otp_created_at),
            )
        
        db.commit()
        
        # Send verification email
        from app import mail
        email_sent = send_verification_email(mail, email, otp, full_name)
        
        if not email_sent:
            return jsonify({"error": "Failed to send verification email. Please try again."}), 500
        
        return (
            jsonify(
                {
                    "message": "Verification code sent to your email",
                    "email": email,
                }
            ),
            200,
        )
    
    except Exception as e:
        return jsonify({"error": f"Failed to send OTP: {str(e)}"}), 500


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    """Verify email with OTP"""
    try:
        data = request.get_json()
        
        email = sanitize_input(data.get("email", ""))
        otp = data.get("otp", "").strip()
        
        if not email or not otp:
            return jsonify({"error": "Email and OTP are required"}), 400
        
        # Find user
        db = get_db()
        user = db.execute(
            "SELECT id, email, full_name, email_otp, otp_created_at, email_verified FROM users WHERE email = %s",
            (email,),
        ).fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if already verified
        if user["email_verified"]:
            return jsonify({"error": "Email already verified"}), 400
        
        # Check if OTP exists
        if not user["email_otp"]:
            return jsonify({"error": "No OTP found. Please request a new one."}), 400
        
        # Check if OTP matches
        if user["email_otp"] != otp:
            return jsonify({"error": "Invalid OTP"}), 400
        
        # Check if OTP expired (10 minutes)
        from flask import current_app
        otp_expiry_minutes = current_app.config.get('OTP_EXPIRY_MINUTES', 10)
        
        if user["otp_created_at"]:
            otp_age = datetime.now() - user["otp_created_at"]
            if otp_age > timedelta(minutes=otp_expiry_minutes):
                return jsonify({"error": "OTP expired. Please request a new one."}), 400
        
        # Verify user
        db.execute(
            "UPDATE users SET email_verified = TRUE, email_otp = NULL, otp_created_at = NULL WHERE email = %s",
            (email,),
        )
        db.commit()
        
        # Generate token
        token = generate_token(user["id"], user["email"])
        
        return (
            jsonify(
                {
                    "message": "Email verified successfully",
                    "token": token,
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "full_name": user["full_name"],
                    },
                }
            ),
            200,
        )
    
    except Exception as e:
        return jsonify({"error": f"Verification failed: {str(e)}"}), 500


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    """Resend OTP to user's email"""
    try:
        data = request.get_json()
        email = sanitize_input(data.get("email", ""))
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Find user
        db = get_db()
        user = db.execute(
            "SELECT id, email, full_name, email_verified FROM users WHERE email = %s",
            (email,),
        ).fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if user["email_verified"]:
            return jsonify({"error": "Email already verified"}), 400
        
        # Generate new OTP
        otp = generate_otp()
        otp_created_at = datetime.now()
        
        # Update OTP
        db.execute(
            "UPDATE users SET email_otp = %s, otp_created_at = %s WHERE email = %s",
            (otp, otp_created_at, email),
        )
        db.commit()
        
        # Send verification email
        from app import mail
        email_sent = send_verification_email(mail, email, otp, user["full_name"])
        
        if not email_sent:
            return jsonify({"error": "Failed to send verification email. Please try again."}), 500
        
        return jsonify({"message": "Verification code resent to your email"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to resend OTP: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()

        email = sanitize_input(data.get("email", ""))
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Find user
        db = get_db()
        user = db.execute(
            "SELECT id, email, password_hash, full_name, bio, profile_picture, email_verified FROM users WHERE email = %s",
            (email,),
        ).fetchone()

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # Check if email is verified
        if not user["email_verified"]:
            return jsonify({
                "error": "Email not verified. Please verify your email first.",
                "email_verified": False
            }), 403

        # Verify password
        if not verify_password(password, user["password_hash"]):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate token
        token = generate_token(user["id"], user["email"])

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "token": token,
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "full_name": user["full_name"],
                        "bio": user["bio"],
                        "profile_picture": user["profile_picture"],
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Get current user info (requires authentication)"""
    from utils import token_required

    @token_required
    def _get_user(current_user):
        try:
            db = get_db()
            user = db.execute(
                "SELECT id, email, full_name, bio, profile_picture, location, availability FROM users WHERE id = %s",
                (current_user["user_id"],),
            ).fetchone()

            if not user:
                return jsonify({"error": "User not found"}), 404

            return (
                jsonify(
                    {
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "full_name": user["full_name"],
                            "bio": user["bio"],
                            "profile_picture": user["profile_picture"],
                            "location": user["location"],
                            "availability": user["availability"],
                        }
                    }
                ),
                200,
            )

        except Exception as e:
            return jsonify({"error": f"Failed to fetch user: {str(e)}"}), 500

    return _get_user()
