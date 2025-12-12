# Quick Setup Guide - Email Verification

## 🚀 Quick Start (3 Steps)

### 1️⃣ Install Flask-Mail
```bash
pip install Flask-Mail==0.9.1
```

### 2️⃣ Configure Email in `.env`
Add these to your `.env` file:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Get Gmail App Password:**
1. Visit: https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to "App passwords" → Generate for "Mail"
4. Copy the 16-character password to `.env`

### 3️⃣ Run Database Migration
```bash
# If you have existing database, run:
psql -U your_username -d your_database -f database/migrations/add_email_verification.sql

# Or connect to your database and run:
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_otp VARCHAR(10);
ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_created_at TIMESTAMP;
```

---

## 📋 New API Endpoints

### Send OTP (Registration)
```bash
POST /api/auth/send-otp
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

### Verify Email
```bash
POST /api/auth/verify-email
{
  "email": "user@example.com",
  "otp": "123456"
}
```

### Resend OTP
```bash
POST /api/auth/resend-otp
{
  "email": "user@example.com"
}
```

---

## ✅ What Changed

- ✅ Registration now requires email verification
- ✅ Users receive 6-digit OTP via email
- ✅ OTP expires after 10 minutes
- ✅ Unverified users cannot log in
- ✅ Beautiful HTML email templates

---

## 🧪 Testing

1. Start your Flask app
2. Call `/api/auth/send-otp` with test email
3. Check your email for OTP
4. Call `/api/auth/verify-email` with OTP
5. Try logging in

---

## 📝 Frontend Updates Needed

Update your signup flow to:
1. Call `/send-otp` instead of `/signup`
2. Show OTP input screen
3. Call `/verify-email` with OTP
4. Handle verification success/errors

See [walkthrough.md](file:///C:/Users/sonli%20gupta/.gemini/antigravity/brain/066b3356-8003-4a97-a250-c66f4460a803/walkthrough.md) for complete details.
