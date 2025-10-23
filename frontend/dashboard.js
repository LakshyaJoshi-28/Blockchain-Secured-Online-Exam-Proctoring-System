// Check authentication
const token = localStorage.getItem('token');
const user = JSON.parse(localStorage.getItem('user'));

if (!token || !user) {
    window.location.href = 'index.html';
}

// Display user info
document.getElementById('userName').textContent = user.name;
document.getElementById('userRole').textContent = user.role;
document.getElementById('digitalId').textContent = user.digital_id_hash ? user.digital_id_hash.substring(0, 20) + '...' : 'Not assigned';

// Load profile details
function loadProfileDetails() {
    document.getElementById('viewName').textContent = user.name || '-';
    document.getElementById('viewEmail').textContent = user.email || '-';
    document.getElementById('viewEnrollment').textContent = user.enrollment_number || '-';
    document.getElementById('viewBranch').textContent = user.branch || '-';
    document.getElementById('viewComputerCode').textContent = user.computer_code || '-';
    document.getElementById('viewStatus').textContent = user.is_active ? '🟢 Active' : '🔴 Inactive';
    
    // Populate edit form
    document.getElementById('editName').value = user.name || '';
    document.getElementById('editBranch').value = user.branch || '';
    document.getElementById('editEnrollment').value = user.enrollment_number || '';
    document.getElementById('editComputerCode').value = user.computer_code || '';
}

// Toggle edit form
function toggleEditForm() {
    const profileView = document.getElementById('profileView');
    const editForm = document.getElementById('editForm');
    
    if (editForm.style.display === 'block') {
        editForm.style.display = 'none';
        profileView.style.display = 'grid';
    } else {
        editForm.style.display = 'block';
        profileView.style.display = 'none';
        loadProfileDetails(); // Refresh form data
    }
}

// Profile form handler
document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('editName').value,
        branch: document.getElementById('editBranch').value,
        enrollment_number: document.getElementById('editEnrollment').value,
        computer_code: document.getElementById('editComputerCode').value
    };

    try {
        showLoading();
        
        const response = await fetch(`http://localhost:5000/api/users/${user.user_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('✅ Profile updated successfully!', 'success');
            
            // Update local storage
            Object.assign(user, formData);
            localStorage.setItem('user', JSON.stringify(user));
            
            // Update displayed info
            document.getElementById('userName').textContent = user.name;
            loadProfileDetails();
            
            // Switch back to view mode
            setTimeout(() => {
                toggleEditForm();
                hideLoading();
            }, 1500);
        } else {
            showMessage(`❌ ${data.error || 'Failed to update profile'}`, 'error');
            hideLoading();
        }
    } catch (error) {
        console.error('Profile update error:', error);
        showMessage('🌐 Network error! Please try again.', 'error');
        hideLoading();
    }
});

// Show role-specific sections
if (user.role === 'Admin') {
    document.getElementById('adminSection').style.display = 'block';
} else if (user.role === 'Student') {
    document.getElementById('studentSection').style.display = 'block';
    document.getElementById('profileSection').style.display = 'block'; // Show profile section for students
} else if (user.role === 'Examiner') {
    document.getElementById('examinerSection').style.display = 'block';
}

// Load all users (Admin only)
async function loadAllUsers() {
    try {
        showLoading();
        const response = await fetch('http://localhost:5000/api/users', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayUsers(data.users);
        } else {
            showMessage('❌ Failed to load users', 'error');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showMessage('🌐 Network error!', 'error');
    } finally {
        hideLoading();
    }
}

function displayUsers(users) {
    const usersList = document.getElementById('usersList');
    usersList.innerHTML = users.map(user => `
        <div class="stat-card" style="text-align: left; margin-bottom: 15px;">
            <h4>${user.name} ${user.is_active ? '🟢' : '🔴'}</h4>
            <p><strong>Email:</strong> ${user.email}</p>
            <p><strong>Role:</strong> ${user.role}</p>
            <p><strong>Branch:</strong> ${user.branch || 'N/A'}</p>
            <p><strong>Enrollment:</strong> ${user.enrollment_number || 'N/A'}</p>
            <p><strong>Status:</strong> ${user.is_active ? 'Active' : 'Inactive'}</p>
        </div>
    `).join('');
}

// Loading and message functions
function showLoading() {
    // You can add a loading spinner here
    console.log('Loading...');
}

function hideLoading() {
    console.log('Loading complete');
}

function showMessage(text, type = 'info') {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';
    
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

// Initialize
loadProfileDetails();