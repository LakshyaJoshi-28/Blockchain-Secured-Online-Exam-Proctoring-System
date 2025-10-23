const API_BASE_URL = 'http://localhost:5000/api';
let currentEmail = '';

// Step navigation
function goToStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step${stepNumber}`).classList.add('active');
    clearMessage();
}

// Show message
function showMessage(text, type = 'info') {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
}

// Clear message
function clearMessage() {
    const messageDiv = document.getElementById('message');
    messageDiv.style.display = 'none';
}

// Show loading
function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

// Hide loading
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Step 1: Email form
document.getElementById('emailForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('resetEmail').value;
    currentEmail = email;

    try {
        showLoading();
        clearMessage();

        const response = await fetch(`${API_BASE_URL}/password/reset-request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(`OTP sent to ${email}. Check your email (and console for demo).`, 'success');
            setTimeout(() => {
                goToStep(2);
                hideLoading();
            }, 2000);
        } else {
            showMessage(data.error || 'Failed to send OTP', 'error');
            hideLoading();
        }
    } catch (error) {
        showMessage('Network error! Please check your connection.', 'error');
        hideLoading();
    }
});

// Step 2: OTP verification
document.getElementById('otpForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const otp = document.getElementById('resetOTP').value;

    try {
        showLoading();
        clearMessage();

        const response = await fetch(`${API_BASE_URL}/password/verify-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                email: currentEmail, 
                otp: otp 
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('OTP verified successfully!', 'success');
            setTimeout(() => {
                goToStep(3);
                hideLoading();
            }, 1500);
        } else {
            showMessage(data.error || 'Invalid OTP', 'error');
            hideLoading();
        }
    } catch (error) {
        showMessage('Network error! Please try again.', 'error');
        hideLoading();
    }
});

// Step 3: New password
document.getElementById('passwordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (newPassword !== confirmPassword) {
        showMessage('Passwords do not match!', 'error');
        return;
    }

    if (newPassword.length < 6) {
        showMessage('Password must be at least 6 characters long', 'error');
        return;
    }

    try {
        showLoading();
        clearMessage();

        const response = await fetch(`${API_BASE_URL}/password/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                email: currentEmail, 
                new_password: newPassword 
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Password reset successfully!', 'success');
            setTimeout(() => {
                goToStep(4);
                hideLoading();
            }, 1500);
        } else {
            showMessage(data.error || 'Failed to reset password', 'error');
            hideLoading();
        }
    } catch (error) {
        showMessage('Network error! Please try again.', 'error');
        hideLoading();
    }
});