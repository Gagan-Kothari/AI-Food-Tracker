import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import models
from app.whatsapp_alerts import send_whatsapp_message
from app.email_service import send_notification_email


def generate_coupon_code(length: int = 12) -> str:
    """
    Generate a random coupon code.
    
    Args:
        length: Length of the coupon code (default: 12)
        
    Returns:
        str: Random coupon code (alphanumeric, uppercase)
    """
    alphabet = string.ascii_uppercase + string.digits
    # Exclude confusing characters: 0, O, I, 1
    alphabet = alphabet.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def get_available_coupons(db: Session):
    """
    Get all active coupons available for redemption.
    
    Args:
        db: Database session
        
    Returns:
        list: List of active coupons
    """
    try:
        now = datetime.now()
        coupons = db.query(models.Coupons).filter(
            models.Coupons.is_active == True,
            models.Coupons.valid_until > now
        ).all()
        
        return [
            {
                "id": coupon.id,
                "name": coupon.name,
                "description": coupon.description or f"Get {coupon.discount} on {coupon.name}",
                "points_required": coupon.points_required,
                "discount": coupon.discount,
                "valid_until": coupon.valid_until.isoformat() if coupon.valid_until else None
            }
            for coupon in coupons
        ]
    except Exception as e:
        print(f"Error getting coupons: {str(e)}")
        return []


def claim_coupon(db: Session, user_id: int, coupon_id: int):
    """
    Claim a coupon for a user.
    
    Args:
        db: Database session
        user_id: User ID
        coupon_id: Coupon ID
        
    Returns:
        dict: Status and coupon details
    """
    try:
        # Check if user exists and has enough points
        user = db.query(models.Users).filter(models.Users.id == user_id).first()
        if not user:
            return {
                "status": False,
                "message": "User not found"
            }
        
        # Get coupon
        coupon = db.query(models.Coupons).filter(
            models.Coupons.id == coupon_id,
            models.Coupons.is_active == True
        ).first()
        
        if not coupon:
            return {
                "status": False,
                "message": "Coupon not found or inactive"
            }
        
        # Check if coupon is still valid
        if coupon.valid_until and coupon.valid_until < datetime.now():
            return {
                "status": False,
                "message": "Coupon has expired"
            }
        
        # Check if user has enough points
        if user.points < coupon.points_required:
            return {
                "status": False,
                "message": f"Insufficient points. You need {coupon.points_required} points, but you have {user.points}."
            }
        
        # Generate coupon code
        coupon_code = generate_coupon_code()
        
        # Deduct points from user
        user.points -= coupon.points_required
        
        # Create coupon claim record
        claim = models.CouponClaims(
            user_id=user_id,
            coupon_id=coupon_id,
            coupon_code=coupon_code,
            claimed_at=datetime.now(),
            is_used=False
        )
        
        db.add(claim)
        db.commit()
        db.refresh(claim)
        
        # Send WhatsApp notification using coupon_alert template
        try:
            phone_number = user.phone_number
            if phone_number:
                # Format message for coupon_alert template: "AI Based Grocery Recommendation: {{1}}. End of message"
                message = f"🎉 Congratulations! You've successfully claimed a {coupon.name} coupon!\n\n"
                message += f"Coupon Code: {coupon_code}\n"
                message += f"Discount: {coupon.discount}\n"
                message += f"Valid until: {coupon.valid_until.strftime('%Y-%m-%d') if coupon.valid_until else 'N/A'}\n\n"
                message += f"Use this code at checkout to avail your discount. Thank you for using FoodTracker! 🍎"
                
                send_whatsapp_message(
                    to_phone=phone_number,
                    message=message,
                    template_name="coupon_alert"
                )
        except Exception as e:
            print(f"Error sending WhatsApp notification: {str(e)}")
            # Don't fail the claim if WhatsApp fails
        
        # Send email notification alongside WhatsApp
        if user.email:
            try:
                email_subject = f"FoodTracker - Coupon Claimed: {coupon.name}"
                email_result = send_notification_email(user.email, email_subject, message)
                if email_result.get("status"):
                    print(f"DEBUG: Coupon claim notification email sent to {user.email}")
            except Exception as e:
                print(f"ERROR: Failed to send coupon claim email: {str(e)}")
        
        return {
            "status": True,
            "message": "Coupon claimed successfully",
            "coupon_name": coupon.name,
            "coupon_code": coupon_code,
            "discount": coupon.discount,
            "remaining_points": user.points
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error claiming coupon: {str(e)}")
        return {
            "status": False,
            "message": f"Failed to claim coupon: {str(e)}"
        }

