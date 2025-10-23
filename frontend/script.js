const API_BASE_URL = 'http://localhost:5000/api';

// DOM Elements
const loginSection = document.getElementById('loginSection');
const registerSection = document.getElementById('registerSection');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const loading = document.getElementById('loading');
const messageDiv = document.getElementById('message');

// Show/Hide Forms
function showRegister() {
    loginSection.classList.remove('active');
    registerSection.classList.add('active');
    clearMessage();
}

function showLogin() {
    registerSection.classList.remove('active');
    loginSection.classList.add('active');
    clearMessage();
}

// Show Message
function showMessage(text, type = 'info') {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
}

// Clear Message
function clearMessage() {
    messageDiv.style.display = 'none';
    messageDiv.textContent = '';
}

// Show Loading
function showLoading() {
    loading.style.display = 'block';
}

// Hide Loading
function hideLoading() {
    loading.style.display = 'none';
}

// Test Backend Connection
async function testBackendConnection() {
    try {
        const response = await fetch(API_BASE_URL.replace('/api', ''));
        if (response.ok) {
            console.log('✅ Backend connection successful');
            showMessage('Backend connected successfully!', 'success');
            setTimeout(() => clearMessage(), 3000);
            return true;
        }
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
        showMessage('⚠️ Backend server not reachable. Please make sure backend is running on port 5000.', 'error');
        return false;
    }
}

// Register Form Handler - UPDATED
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('regName').value,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value,
        enrollment_number: document.getElementById('regEnrollment').value,
        branch: document.getElementById('regBranch').value,
        computer_code: document.getElementById('regComputerCode').value
    };

    // Validation
    if (!formData.enrollment_number || !formData.branch || !formData.computer_code) {
        showMessage('Please fill all student details!', 'error');
        return;
    }

    try {
        showLoading();
        clearMessage();

        console.log('📤 Sending registration request to:', `${API_BASE_URL}/register`);
        console.log('📝 Data:', formData);

        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        console.log('📨 Response status:', response.status);

        const data = await response.json();
        console.log('📩 Response data:', data);

        if (response.ok) {
            showMessage('🎉 Student registration successful! You can now login.', 'success');
            
            setTimeout(() => {
                showLogin();
                registerForm.reset();
            }, 2000);
        } else {
            showMessage(`❌ ${data.error || 'Registration failed!'}`, 'error');
        }
    } catch (error) {
        console.error('💥 Registration error:', error);
        showMessage(`🌐 Network Error: ${error.message}. Please check:\n1. Backend server is running\n2. No firewall blocking\n3. Try refreshing the page`, 'error');
    } finally {
        hideLoading();
    }
});

// Login Form Handler
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value
    };

    try {
        showLoading();
        clearMessage();

        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('✅ Login successful! Redirecting...', 'success');
            
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showMessage(`❌ ${data.error || 'Login failed!'}`, 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage(`🌐 Network Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

// Check if user is already logged in
function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = 'dashboard.html';
    }
}

// Initialize - Test connection on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    setTimeout(() => testBackendConnection(), 1000);
});