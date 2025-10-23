# models/user.py
from config import DatabaseConfig
import hashlib
import uuid
from datetime import datetime

class User:
    def __init__(self, user_data):
        self.user_id = user_data.get('user_id')
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.role = user_data.get('role')
        self.branch = user_data.get('branch')
        self.enrollment_number = user_data.get('enrollment_number')
        self.computer_code = user_data.get('computer_code')
        self.wallet_address = user_data.get('wallet_address')
        self.digital_id_hash = user_data.get('digital_id_hash')
        self.is_active = user_data.get('is_active', True)
        self.last_login = user_data.get('last_login')
        self.created_at = user_data.get('created_at')
    
    @staticmethod
    def generate_digital_id(email, enrollment_number):
        """Generate unique digital ID hash for blockchain"""
        unique_string = f"{email}{enrollment_number}{uuid.uuid4()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'branch': self.branch,
            'enrollment_number': self.enrollment_number,
            'computer_code': self.computer_code,
            'wallet_address': self.wallet_address,
            'digital_id_hash': self.digital_id_hash,
            'is_active': self.is_active,
            'last_login': self.last_login,
            'created_at': self.created_at
        }