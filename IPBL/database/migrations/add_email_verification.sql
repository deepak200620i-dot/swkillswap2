-- Migration: Add email verification columns to users table
-- Run this if you have an existing database

-- Add email_verified column (default FALSE for existing users)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;

-- Add email_otp column for storing OTP codes
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_otp VARCHAR(10);

-- Add otp_created_at column for OTP expiration tracking
ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_created_at TIMESTAMP;

-- Optional: Set existing users as verified (if you want to grandfather them in)
-- Uncomment the line below if you want existing users to be automatically verified
-- UPDATE users SET email_verified = TRUE WHERE email_verified IS NULL OR email_verified = FALSE;
