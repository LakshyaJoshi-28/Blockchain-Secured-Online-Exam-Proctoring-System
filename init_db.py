# init_db.py
from config import DatabaseConfig
import mysql.connector

def initialize_database():
    try:
        # Connect without database to create it
        connection = mysql.connector.connect(
            host=DatabaseConfig.DB_HOST,
            user=DatabaseConfig.DB_USER,
            password=DatabaseConfig.DB_PASSWORD
        )
        cursor = connection.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DatabaseConfig.DB_NAME}")
        print("Database created successfully")
        
        # Use the database
        cursor.execute(f"USE {DatabaseConfig.DB_NAME}")
        
        # Create users table
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('Student', 'Examiner', 'Admin') NOT NULL,
            branch VARCHAR(50),
            enrollment_number VARCHAR(50),
            computer_code VARCHAR(20),
            wallet_address VARCHAR(42) UNIQUE,
            digital_id_hash VARCHAR(64) UNIQUE,
            is_active BOOLEAN DEFAULT TRUE,
            last_login TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(users_table)
        print("Users table created successfully")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    initialize_database()