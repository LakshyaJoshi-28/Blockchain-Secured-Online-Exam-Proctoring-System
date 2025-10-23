from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from services.user_service import UserService
from services.password_reset_service import PasswordResetService
from models.user import User
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# CORS Configuration
CORS(app)

# JWT Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = UserService.get_user_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
                
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Role-based access control decorator
def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in required_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

@app.route('/')
def home():
    return jsonify({
        'message': 'Blockchain-Secured Online Exam Proctoring System API',
        'status': 'Server is running',
        'endpoints': {
            'register': 'POST /api/register',
            'login': 'POST /api/login',
            'profile': 'GET /api/profile',
            'users': 'GET /api/users (Admin only)',
            'password_reset': 'POST /api/password/reset-request'
        }
    })

# User Registration
@app.route('/api/register', methods=['POST'])
@cross_origin()
def register():
    """User registration endpoint - ONLY STUDENTS CAN REGISTER"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        data['role'] = 'Student'
        
        student_required_fields = ['enrollment_number', 'branch', 'computer_code']
        for field in student_required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field.replace("_", " ").title()} is required for student registration'}), 400
        
        user = UserService.create_user(data)
        
        if user and not hasattr(user, 'error'):
            token = jwt.encode({
                'user_id': user.user_id,
                'email': user.email,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'Student registered successfully',
                'user': user.to_dict(),
                'token': token
            }), 201
        elif user and hasattr(user, 'error'):
            return jsonify({'error': user['error']}), 400
        else:
            return jsonify({'error': 'Failed to create student account'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Login
@app.route('/api/login', methods=['POST'])
@cross_origin()
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = UserService.authenticate_user(data['email'], data['password'])
        
        if user:
            token = jwt.encode({
                'user_id': user.user_id,
                'email': user.email,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': token
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials or inactive account'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Password Reset Routes - ADD THESE
@app.route('/api/password/reset-request', methods=['POST', 'OPTIONS'])
@cross_origin()
def request_password_reset():
    """Request password reset OTP"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        print(f"📧 Password reset requested for: {data['email']}")
        
        result = PasswordResetService.create_reset_token(data['email'])
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        else:
            return jsonify(result), 200
            
    except Exception as e:
        print(f"❌ Password reset error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/password/verify-otp', methods=['POST', 'OPTIONS'])
@cross_origin()
def verify_reset_otp():
    """Verify reset OTP"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('otp'):
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        is_valid = PasswordResetService.verify_reset_token(data['email'], data['otp'])
        
        if is_valid:
            return jsonify({'success': True, 'message': 'OTP verified successfully'}), 200
        else:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/password/reset', methods=['POST', 'OPTIONS'])
@cross_origin()
def reset_password():
    """Reset password after OTP verification"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('new_password'):
            return jsonify({'error': 'Email and new password are required'}), 400
        
        # Reset password
        success = PasswordResetService.reset_password(data['email'], data['new_password'])
        
        if success:
            return jsonify({'success': True, 'message': 'Password reset successfully'}), 200
        else:
            return jsonify({'error': 'Failed to reset password'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Existing profile and user management routes
@app.route('/api/profile', methods=['GET'])
@cross_origin()
@token_required
def get_profile(current_user):
    """Get user profile"""
    return jsonify({'user': current_user.to_dict()}), 200

@app.route('/api/users', methods=['GET'])
@cross_origin()
@token_required
@role_required(['Admin'])
def get_all_users(current_user):
    """Get all users (Admin only)"""
    role = request.args.get('role')
    users = UserService.get_all_users(role)
    
    if users is not None:
        return jsonify({'users': [user.to_dict() for user in users]}), 200
    else:
        return jsonify({'error': 'Failed to fetch users'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@cross_origin()
@token_required
def update_user(current_user, user_id):
    """Update user profile"""
    if current_user.role != 'Admin' and current_user.user_id != user_id:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    try:
        data = request.get_json()
        success = UserService.update_user(user_id, data)
        
        if success:
            updated_user = UserService.get_user_by_id(user_id)
            return jsonify({
                'message': 'User updated successfully',
                'user': updated_user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Failed to update user'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Blockchain-Secured Online Exam Proctoring System...")
    print("Server running on http://localhost:5000")
    print("CORS enabled for frontend: http://localhost:8000")
    app.run(debug=True, port=5000)