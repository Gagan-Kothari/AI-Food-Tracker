"""
Email service for sending contact form emails via SMTP or HTTP API
"""
import os
import smtplib
import ssl
import logging
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # Your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Gmail App Password (not regular password)
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "gagankothari6@gmail.com")

# Resend API (HTTP-based, works on Railway)
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
# Default: Use SMTP_USERNAME if available, otherwise use Resend's test domain
# Note: For production, you should verify your own domain/email in Resend
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL") or SMTP_USERNAME or "onboarding@resend.dev"


def send_email_via_resend(name: str, email: str, subject: str, message: str) -> dict:
    """
    Send email via Resend API (HTTP-based, works on Railway).
    
    Args:
        name: Sender's name
        email: Sender's email
        subject: Email subject
        message: Email message
        
    Returns:
        dict: Status and message
    """
    if not RESEND_API_KEY or not RESEND_FROM_EMAIL:
        return {"status": False, "message": "Resend API not configured"}
    
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        body_text = f"""
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
        
        payload = {
            "from": f"FoodTracker <{RESEND_FROM_EMAIL}>",
            "to": [CONTACT_EMAIL],
            "subject": f"Contact Form: {subject}",
            "text": body_text,
            "reply_to": email
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("Contact email sent via Resend from %s (%s)", name, email)
            return {
                "status": True,
                "message": "Email sent successfully"
            }
        else:
            logger.error("Resend API error: %s - %s", response.status_code, response.text)
            return {
                "status": False,
                "message": f"Failed to send email: {response.text}"
            }
    except Exception as e:
        logger.error("Resend API exception: %s", str(e))
        return {
            "status": False,
            "message": f"Failed to send email: {str(e)}"
        }


def send_email_via_smtp(name: str, email: str, subject: str, message: str) -> dict:
    """
    Send email via SMTP (tries multiple configurations).
    
    Args:
        name: Sender's name
        email: Sender's email
        subject: Email subject
        message: Email message
        
    Returns:
        dict: Status and message
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return {"status": False, "message": "SMTP credentials not configured"}
    
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
    text = msg.as_string()
    
    # Try port 587 with STARTTLS first
    try:
        logger.debug("Attempting SMTP connection to %s:%s (STARTTLS)", SMTP_SERVER, SMTP_PORT)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()  # Enable encryption
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, CONTACT_EMAIL, text)
        server.quit()
        
        logger.info("Contact email sent via SMTP (port %s) from %s (%s)", SMTP_PORT, name, email)
        return {
            "status": True,
            "message": "Email sent successfully"
        }
    except (OSError, ConnectionError) as e:
        logger.debug("Port %s failed: %s", SMTP_PORT, str(e))
        # Try port 465 with SSL
        try:
            logger.debug("Attempting SMTP connection to %s:465 (SSL)", SMTP_SERVER)
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(SMTP_SERVER, 465, context=context, timeout=10)
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, CONTACT_EMAIL, text)
            server.quit()
            
            logger.info("Contact email sent via SMTP (port 465 SSL) from %s (%s)", name, email)
            return {
                "status": True,
                "message": "Email sent successfully"
            }
        except Exception as ssl_error:
            logger.error("Both SMTP ports failed. Port 587: %s, Port 465: %s", str(e), str(ssl_error))
            return {
                "status": False,
                "message": f"SMTP connection failed. Railway may block SMTP ports. Consider using Resend API instead."
            }
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check username and password.")
        return {
            "status": False,
            "message": "Email authentication failed. Please check server configuration."
        }
    except Exception as e:
        logger.error("SMTP error: %s", str(e))
        return {
            "status": False,
            "message": f"Failed to send email: {str(e)}"
        }


def send_notification_email(to_email: str, subject: str, message: str) -> dict:
    """
    Send notification email to user. Tries Resend API first (works on Railway), 
    then falls back to SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Email message (plain text)
        
    Returns:
        dict: Status and message
    """
    try:
        # Try Resend API first (HTTP-based, works on Railway)
        if RESEND_API_KEY and RESEND_FROM_EMAIL:
            try:
                url = "https://api.resend.com/emails"
                headers = {
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "from": f"FoodTracker <{RESEND_FROM_EMAIL}>",
                    "to": [to_email],
                    "subject": subject,
                    "text": message
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    logger.info("Notification email sent via Resend to %s", to_email)
                    return {"status": True, "message": "Email sent successfully"}
                else:
                    logger.error("Resend API error: %s - %s", response.status_code, response.text)
            except Exception as e:
                logger.error("Resend API exception: %s", str(e))
        
        # Fall back to SMTP
        if SMTP_USERNAME and SMTP_PASSWORD:
            try:
                msg = MIMEMultipart()
                msg['From'] = SMTP_USERNAME
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))
                text = msg.as_string()
                
                # Try port 587 with STARTTLS first
                try:
                    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
                    server.starttls()
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.sendmail(SMTP_USERNAME, to_email, text)
                    server.quit()
                    logger.info("Notification email sent via SMTP to %s", to_email)
                    return {"status": True, "message": "Email sent successfully"}
                except (OSError, ConnectionError):
                    # Try port 465 with SSL
                    context = ssl.create_default_context()
                    server = smtplib.SMTP_SSL(SMTP_SERVER, 465, context=context, timeout=10)
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                    server.sendmail(SMTP_USERNAME, to_email, text)
                    server.quit()
                    logger.info("Notification email sent via SMTP (SSL) to %s", to_email)
                    return {"status": True, "message": "Email sent successfully"}
            except Exception as e:
                logger.error("SMTP error: %s", str(e))
        
        return {"status": False, "message": "Email service not configured"}
            
    except Exception as e:
        logger.error("Failed to send notification email: %s", str(e))
        return {"status": False, "message": f"Failed to send email: {str(e)}"}


def send_contact_email(name: str, email: str, subject: str, message: str) -> dict:
    """
    Send contact form email. Tries Resend API first (works on Railway), 
    then falls back to SMTP.
    
    Args:
        name: Sender's name
        email: Sender's email
        subject: Email subject
        message: Email message
        
    Returns:
        dict: Status and message
    """
    try:
        # Try Resend API first (HTTP-based, works on Railway)
        if RESEND_API_KEY and RESEND_FROM_EMAIL:
            logger.debug("Attempting to send email via Resend API...")
            result = send_email_via_resend(name, email, subject, message)
            if result.get("status"):
                return result
            logger.debug("Resend API failed, falling back to SMTP...")
        
        # Fall back to SMTP
        if SMTP_USERNAME and SMTP_PASSWORD:
            logger.debug("Attempting to send email via SMTP...")
            return send_email_via_smtp(name, email, subject, message)
        
        # No email service configured
        logger.error("No email service configured (neither Resend API nor SMTP)")
        return {
            "status": False,
            "message": "Email service not configured. Please contact support directly."
        }
            
    except Exception as e:
        logger.error("Failed to send contact email: %s", str(e))
        return {
            "status": False,
            "message": f"Failed to send email: {str(e)}"
        }
