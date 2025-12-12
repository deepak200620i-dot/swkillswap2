// Authentication JavaScript

// API Base URL
const API_URL = 'https://swkillswap2-1.onrender.com/api';

// Signup Form Handler
if (document.getElementById('signup-form')) {
    const signupForm = document.getElementById('signup-form');
    const verifyBtn = document.getElementById('verify-btn');
    const resendBtn = document.getElementById('resend-btn');
    let userEmail = '';

    signupForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const fullName = document.getElementById('full_name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;

        // Validate passwords match
        if (password !== confirmPassword) {
            showAlert('Passwords do not match', 'danger');
            return;
        }

        // Show loading
        setLoading(true);

        try {
            // STEP 1: Send OTP
            const response = await fetch(`${API_URL}/auth/send-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    full_name: fullName,
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                userEmail = email; // Store for verification

                // Switch UI to OTP mode
                document.getElementById('signup-fields').style.display = 'none';
                document.getElementById('otp-section').style.display = 'block';

                showAlert('Verification code sent! Please check your email.', 'success');
                setLoading(false);
            } else {
                showAlert(data.error || 'Signup failed', 'danger');
                setLoading(false);
            }
        } catch (error) {
            showAlert('Network error. Please try again.', 'danger');
            setLoading(false);
        }
    });

    // STEP 2: Verify OTP
    if (verifyBtn) {
        verifyBtn.addEventListener('click', async function () {
            const otp = document.getElementById('otp').value;

            if (!otp || otp.length < 6) {
                showAlert('Please enter a valid 6-digit code', 'danger');
                return;
            }

            // Show loading on verify button
            const btnText = document.getElementById('verify-text');
            const btnSpinner = document.getElementById('verify-spinner');
            btnText.textContent = 'Verifying...';
            btnSpinner.style.display = 'inline-block';
            verifyBtn.disabled = true;

            try {
                const response = await fetch(`${API_URL}/auth/verify-email`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: userEmail,
                        otp: otp
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Save token and user data
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('user', JSON.stringify(data.user));

                    showAlert('Email verified successfully! Redirecting...', 'success');

                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
                } else {
                    showAlert(data.error || 'Verification failed', 'danger');
                    // Reset button
                    btnText.textContent = 'Verify Email';
                    btnSpinner.style.display = 'none';
                    verifyBtn.disabled = false;
                }
            } catch (error) {
                showAlert('Network error. Please try again.', 'danger');
                btnText.textContent = 'Verify Email';
                btnSpinner.style.display = 'none';
                verifyBtn.disabled = false;
            }
        });
    }

    // Resend OTP Handler
    if (resendBtn) {
        resendBtn.addEventListener('click', async function () {
            resendBtn.disabled = true;
            resendBtn.textContent = 'Sending...';

            try {
                const response = await fetch(`${API_URL}/auth/resend-otp`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email: userEmail
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert('New code sent to your email', 'success');
                } else {
                    showAlert(data.error || 'Failed to resend code', 'danger');
                }
            } catch (error) {
                showAlert('Network error', 'danger');
            } finally {
                resendBtn.disabled = false;
                resendBtn.textContent = 'Resend Code';
            }
        });
    }
}

// Login Form Handler
if (document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', async function (e) {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        // Show loading
        setLoading(true);

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Save token and user data
                localStorage.setItem('token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));

                // Show success and redirect
                showAlert('Login successful!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                showAlert(data.error || 'Login failed', 'danger');
                setLoading(false);
            }
        } catch (error) {
            showAlert('Network error. Please try again.', 'danger');
            setLoading(false);
        }
    });
}

// Helper Functions
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    alertContainer.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

function setLoading(isLoading) {
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const submitBtn = document.querySelector('button[type="submit"]');

    if (isLoading) {
        btnText.textContent = 'Please wait...';
        btnSpinner.style.display = 'inline-block';
        submitBtn.disabled = true;
    } else {
        btnText.textContent = document.getElementById('login-form') ? 'Login' : 'Sign Up';
        btnSpinner.style.display = 'none';
        submitBtn.disabled = false;
    }
}

// Check if user is already logged in
function checkLoggedIn() {
    const token = localStorage.getItem('token');
    if (token && (window.location.pathname === '/login' || window.location.pathname === '/signup')) {
        window.location.href = '/dashboard';
    }
}

checkLoggedIn();
