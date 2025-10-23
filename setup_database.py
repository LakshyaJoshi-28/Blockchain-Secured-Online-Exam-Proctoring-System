# setup_database.py
from config import DatabaseConfig
import mysql.connector
from mysql.connector import Error
import hashlib
import uuid

def setup_database():
    try:
        connection = DatabaseConfig.get_connection()
        cursor = connection.cursor()
        
        print("Setting up default Admin and Examiner accounts...")
        
        # Default Admin Account
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        admin_digital_id = hashlib.sha256(f"admin@examsystem.comADMIN001{uuid.uuid4()}".encode()).hexdigest()
        
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role, digital_id_hash, is_active) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'System Admin', 
            'admin@examsystem.com', 
            admin_password,
            'Admin',
            admin_digital_id,
            True
        ))
        
        # Default Examiner Account
        examiner_password = hashlib.sha256("examiner123".encode()).hexdigest()
        examiner_digital_id = hashlib.sha256(f"examiner@examsystem.comEXAM001{uuid.uuid4()}".encode()).hexdigest()
        
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role, branch, digital_id_hash, is_active) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            'Exam Controller', 
            'examiner@examsystem.com', 
            examiner_password,
            'Examiner',
            'Computer Science',
            examiner_digital_id,
            True
        ))
        
        connection.commit()
        print("✅ Default accounts created successfully!")
        print("📧 Admin: admin@examsystem.com / admin123")
        print("📧 Examiner: examiner@examsystem.com / examiner123")
        
    except Error as e:
        print(f"❌ Error setting up database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database()