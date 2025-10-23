# test_setup.py
from init_db import initialize_database

print("Initializing database...")
initialize_database()
print("Database setup completed!")

print("\nTesting basic imports...")
try:
    from config import DatabaseConfig
    from models.user import User
    from services.user_service import UserService
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")