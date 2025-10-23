# services/user_service.py
from config import DatabaseConfig
from models.user import User
import hashlib
import mysql.connector
from mysql.connector import Error
import uuid

class UserService:
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_digital_id(email, enrollment_number):
        """Generate unique digital ID hash for blockchain"""
        unique_string = f"{email}{enrollment_number}{uuid.uuid4()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()
    
    @staticmethod
    def create_user(user_data):
        """Create new user with blockchain digital ID"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return {"error": "Database connection failed"}
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if email already exists
            cursor.execute("SELECT email FROM users WHERE email = %s", (user_data['email'],))
            if cursor.fetchone():
                return {"error": "Email already exists"}
            
            # Generate digital ID hash
            digital_id_hash = UserService.generate_digital_id(
                user_data['email'], 
                user_data.get('enrollment_number', '')
            )
            
            # Hash password
            hashed_password = UserService.hash_password(user_data['password'])
            
            # Insert user
            insert_query = """
            INSERT INTO users (
                name, email, password, role, branch, enrollment_number, 
                computer_code, wallet_address, digital_id_hash
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                user_data['name'],
                user_data['email'],
                hashed_password,
                user_data['role'],
                user_data.get('branch'),
                user_data.get('enrollment_number'),
                user_data.get('computer_code'),
                user_data.get('wallet_address'),
                digital_id_hash
            ))
            
            connection.commit()
            user_id = cursor.lastrowid
            
            # Get the created user
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user_record = cursor.fetchone()
            
            if user_record:
                return User(user_record)
            else:
                return {"error": "Failed to create user"}
            
        except Error as e:
            print(f"Error creating user: {e}")
            return {"error": f"Database error: {str(e)}"}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user and update last login"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            hashed_password = UserService.hash_password(password)
            
            # Check user credentials
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s AND is_active = TRUE",
                (email, hashed_password)
            )
            
            user_record = cursor.fetchone()
            
            if user_record:
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s",
                    (user_record['user_id'],)
                )
                connection.commit()
                return User(user_record)
            
            return None
            
        except Error as e:
            print(f"Error authenticating user: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user_record = cursor.fetchone()
            
            return User(user_record) if user_record else None
            
        except Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def get_all_users(role=None):
        """Get all users, optionally filtered by role"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            if role:
                cursor.execute("SELECT * FROM users WHERE role = %s", (role,))
            else:
                cursor.execute("SELECT * FROM users")
            
            users = cursor.fetchall()
            return [User(user) for user in users]
            
        except Error as e:
            print(f"Error getting users: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user information"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return False
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Build dynamic update query
            set_clause = []
            values = []
            
            allowed_fields = ['name', 'branch', 'enrollment_number', 'computer_code', 'wallet_address']
            
            for field in allowed_fields:
                if field in update_data and update_data[field] is not None:
                    set_clause.append(f"{field} = %s")
                    values.append(update_data[field])
            
            if not set_clause:
                return False
            
            values.append(user_id)
            update_query = f"UPDATE users SET {', '.join(set_clause)} WHERE user_id = %s"
            
            cursor.execute(update_query, values)
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Error updating user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def deactivate_user(user_id):
        """Deactivate user account"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return False
        
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET is_active = FALSE WHERE user_id = %s",
                (user_id,)
            )
            connection.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Error deactivating user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_record = cursor.fetchone()
            
            return User(user_record) if user_record else None
            
        except Error as e:
            print(f"Error getting user by email: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def get_user_by_digital_id(digital_id_hash):
        """Get user by blockchain digital ID"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return None
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE digital_id_hash = %s", (digital_id_hash,))
            user_record = cursor.fetchone()
            
            return User(user_record) if user_record else None
            
        except Error as e:
            print(f"Error getting user by digital ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def activate_user(user_id):
        """Activate user account"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return False
        
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET is_active = TRUE WHERE user_id = %s",
                (user_id,)
            )
            connection.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Error activating user: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return False
        
        cursor = None
        try:
            cursor = connection.cursor()
            hashed_password = UserService.hash_password(new_password)
            
            cursor.execute(
                "UPDATE users SET password = %s WHERE user_id = %s",
                (hashed_password, user_id)
            )
            connection.commit()
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"Error updating password: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

@staticmethod
def get_user_by_email(email):
    """Get user by email"""
    connection = DatabaseConfig.get_connection()
    if not connection:
        return None
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_record = cursor.fetchone()
        
        return User(user_record) if user_record else None
        
    except Error as e:
        print(f"Error getting user by email: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@staticmethod
def update_password(user_id, new_password):
    """Update user password"""
    connection = DatabaseConfig.get_connection()
    if not connection:
        return False
    
    cursor = None
    try:
        cursor = connection.cursor()
        hashed_password = UserService.hash_password(new_password)
        
        cursor.execute(
            "UPDATE users SET password = %s WHERE user_id = %s",
            (hashed_password, user_id)
        )
        connection.commit()
        return cursor.rowcount > 0
        
    except Error as e:
        print(f"Error updating password: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()