import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from config import DatabaseConfig
from services.user_service import UserService
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class PasswordResetService:
    
    @staticmethod
    def generate_otp(length=6):
        """Generate 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def send_otp_email(email, otp):
        """Send OTP to user's email"""
        try:
            # Email configuration from environment variables
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            email_username = os.getenv('EMAIL_USERNAME', 'lakshyaprojects28@gmail.com')  # UPDATED
            email_password = os.getenv('EMAIL_PASSWORD', 'cddu frgk snhj aowc')
            email_from = os.getenv('EMAIL_FROM', 'lakshyaprojects28@gmail.com')  # UPDATED

            print(f"📧 Attempting to send email to: {email}")
            print(f"🔐 Using SMTP: {smtp_server}:{smtp_port}")
            print(f"👤 Email username: {email_username}")

            # Validate credentials
            if not email_username or not email_password:
                print("❌ Email credentials missing in .env file")
                return False

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Password Reset OTP - Exam Proctoring System"
            message["From"] = email_from
            message["To"] = email

            # Create beautiful HTML email
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ 
                        font-family: 'Arial', sans-serif; 
                        line-height: 1.6; 
                        color: #333; 
                        margin: 0; 
                        padding: 0; 
                        background-color: #f4f4f4;
                    }}
                    .container {{ 
                        max-width: 600px; 
                        margin: 20px auto; 
                        background: white; 
                        border-radius: 10px; 
                        overflow: hidden;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; 
                        padding: 30px; 
                        text-align: center; 
                    }}
                    .header h1 {{ 
                        margin: 0; 
                        font-size: 24px; 
                    }}
                    .content {{ 
                        padding: 40px 30px; 
                    }}
                    .otp-container {{ 
                        background: #f8f9fa; 
                        border: 2px dashed #667eea; 
                        border-radius: 10px; 
                        padding: 20px; 
                        text-align: center; 
                        margin: 25px 0; 
                    }}
                    .otp-code {{ 
                        font-size: 42px; 
                        font-weight: bold; 
                        color: #667eea; 
                        letter-spacing: 8px; 
                        margin: 10px 0;
                    }}
                    .info-box {{ 
                        background: #e3f2fd; 
                        border-left: 4px solid #2196f3; 
                        padding: 15px; 
                        margin: 20px 0; 
                        border-radius: 4px;
                    }}
                    .footer {{ 
                        text-align: center; 
                        margin-top: 30px; 
                        padding-top: 20px; 
                        border-top: 1px solid #eee; 
                        color: #666; 
                        font-size: 12px; 
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔒 Blockchain Exam Proctoring</h1>
                        <p>Password Reset Request</p>
                    </div>
                    <div class="content">
                        <h2>Hello,</h2>
                        <p>You requested to reset your password for the <strong>Blockchain-Secured Online Exam Proctoring System</strong>.</p>
                        
                        <div class="otp-container">
                            <p style="margin: 0; color: #666;">Your One-Time Password is:</p>
                            <div class="otp-code">{otp}</div>
                            <p style="margin: 0; font-size: 12px; color: #888;">Valid for 10 minutes</p>
                        </div>
                        
                        <div class="info-box">
                            <strong>⚠️ Important:</strong>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>This OTP will expire in 10 minutes</li>
                                <li>Do not share this OTP with anyone</li>
                                <li>If you didn't request this, please ignore this email</li>
                            </ul>
                        </div>
                        
                        <p>Best regards,<br>
                        <strong>Exam Proctoring System Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create plain text version
            text = f"""
            PASSWORD RESET REQUEST - EXAM PROCTORING SYSTEM
            
            Hello,
            
            You requested to reset your password for the Blockchain-Secured Online Exam Proctoring System.
            
            Your One-Time Password (OTP) is: {otp}
            
            ⚠️ Important:
            • This OTP will expire in 10 minutes
            • Do not share this OTP with anyone  
            • If you didn't request this, please ignore this email
            
            Best regards,
            Exam Proctoring System Team
            """

            # Attach both versions
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)

            # Send email with detailed error handling
            print("🔄 Connecting to SMTP server...")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.set_debuglevel(1)  # Enable debug output
            
            print("🔐 Starting TLS...")
            server.starttls()
            
            print("🔑 Logging in to email...")
            server.login(email_username, email_password)
            
            print("📤 Sending email...")
            server.send_message(message)
            
            print("🔒 Closing connection...")
            server.quit()
            
            print(f"✅ OTP email successfully sent to: {email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication Failed: {e}")
            print("Please check:")
            print("1. Email username and password are correct")
            print("2. Gmail App Password is correct (16 characters)")
            print("3. 2-Factor Authentication is enabled in Gmail")
            return False
            
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False
    
    @staticmethod
    def create_reset_token(email):
        """Create password reset OTP for email"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return {"error": "Database connection failed"}
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Check if user exists
            user = UserService.get_user_by_email(email)
            if not user:
                return {"error": "Email not registered in our system"}
            
            # Generate OTP
            otp = PasswordResetService.generate_otp()
            expires_at = datetime.now() + timedelta(minutes=10)
            
            # Delete any existing tokens for this email
            cursor.execute("DELETE FROM password_reset_tokens WHERE email = %s", (email,))
            
            # Store new token
            cursor.execute("""
                INSERT INTO password_reset_tokens (email, token, expires_at) 
                VALUES (%s, %s, %s)
            """, (email, otp, expires_at))
            
            connection.commit()
            
            print(f"📧 Generated OTP: {otp} for {email}")
            
            # Send OTP via email
            email_sent = PasswordResetService.send_otp_email(email, otp)
            
            if email_sent:
                return {
                    "success": True, 
                    "message": "OTP has been sent to your registered email address. Please check your inbox and spam folder."
                }
            else:
                # Fallback for demo - show OTP in console
                print(f"🚨 EMAIL FAILED - OTP for {email}: {otp}")
                return {
                    "success": True,
                    "message": "OTP sent to email (check console for demo)",
                    "otp_demo": otp  # Remove this in production
                }
            
        except Exception as e:
            print(f"Reset token creation error: {e}")
            return {"error": "Failed to create reset token"}
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    @staticmethod
    def verify_reset_token(email, otp):
        """Verify if OTP is valid"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return False
        
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM password_reset_tokens 
                WHERE email = %s AND token = %s AND is_used = FALSE AND expires_at > NOW()
            """, (email, otp))
            
            token = cursor.fetchone()
            
            if token:
                # Mark token as used
                cursor.execute("UPDATE password_reset_tokens SET is_used = TRUE WHERE id = %s", (token['id'],))
                connection.commit()
                return True
            
            return False
            
        except Exception as e:
            print(f"Token verification error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def reset_password(email, new_password):
        """Reset user password"""
        connection = DatabaseConfig.get_connection()
        if not connection:
            return False
        
        cursor = None
        try:
            cursor = connection.cursor()
            
            # Hash new password
            hashed_password = UserService.hash_password(new_password)
            
            # Update password
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            connection.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Password reset error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()