# config.py
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'exam_proctoring_system')
    
    @staticmethod
    def get_connection():
        try:
            connection = mysql.connector.connect(
                host=DatabaseConfig.DB_HOST,
                user=DatabaseConfig.DB_USER,
                password=DatabaseConfig.DB_PASSWORD,
                database=DatabaseConfig.DB_NAME
            )
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None