"""
Email service for sending contact form emails via SMTP
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # Your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Gmail App Password (not regular password)
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "gagankothari6@gmail.com")


def send_contact_email(name: str, email: str, subject: str, message: str) -> dict:
    """
    Send contact form email via SMTP.
    
    Args:
        name: Sender's name
        email: Sender's email
        subject: Email subject
        message: Email message
        
    Returns:
        dict: Status and message
    """
    try:
        # Check if email credentials are configured
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("ERROR: SMTP_USERNAME or SMTP_PASSWORD not configured")
            return {
                "status": False,
                "message": "Email service not configured. Please contact support directly."
            }
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = CONTACT_EMAIL
        msg['Subject'] = f"Contact Form: {subject}"
        msg['Reply-To'] = email
        
        # Create email body
        body = f"""
New contact form submission from FoodTracker:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This email was sent from the FoodTracker contact form.
Reply directly to this email to respond to {name} ({email}).
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Enable encryption
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            text = msg.as_string()
            server.sendmail(SMTP_USERNAME, CONTACT_EMAIL, text)
            server.quit()
            
            print(f"SUCCESS: Contact email sent from {name} ({email})")
            return {
                "status": True,
                "message": "Email sent successfully"
            }
        except smtplib.SMTPAuthenticationError:
            print("ERROR: SMTP authentication failed. Check username and password.")
            return {
                "status": False,
                "message": "Email authentication failed. Please check server configuration."
            }
        except smtplib.SMTPException as e:
            print(f"ERROR: SMTP error: {str(e)}")
            return {
                "status": False,
                "message": f"Failed to send email: {str(e)}"
            }
        except Exception as e:
            print(f"ERROR: Unexpected error sending email: {str(e)}")
            return {
                "status": False,
                "message": f"Failed to send email: {str(e)}"
            }
            
    except Exception as e:
        print(f"ERROR: Failed to send contact email: {str(e)}")
        return {
            "status": False,
            "message": f"Failed to send email: {str(e)}"
        }

