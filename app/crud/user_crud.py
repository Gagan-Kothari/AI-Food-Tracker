from sqlalchemy.orm import Session
from app.models import models


def add_user_to_database(db: Session, nm, mail, pwd):
    """
    Add a new user to the database.
    
    Args:
        db: Database session
        nm: User name
        mail: User email
        pwd: User password
        
    Returns:
        dict: Success/failure message and status
    """
    user = db.query(models.Users).filter(models.Users.email == mail).first()

    if user:
        return {"message": "user already exists", "status": False}

    user = models.Users(
        name=nm,
        email=mail,
        password=pwd
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"message": "success", "status": True}
        
    except Exception as e:
        return {"message": e, "status": False}


def verify_user_from_db(email, password, db):
    """
    Verify user credentials against the database.
    
    Args:
        email: User email
        password: User password
        db: Database session
        
    Returns:
        dict: User information and verification status
    """
    user = db.query(models.Users).filter(models.Users.email == email).first()

    if user and user.password == password:
        userid = str(user.id)
        username = user.name.capitalize()
        # Check if user is admin
        is_admin = email.lower() == "adminghh@gmail.com"
        return {"userid": userid,
                "username": username,
                "isAdmin": is_admin,
                "status": True}
    
    return {"userid": "",
            "username": "",
            "isAdmin": False,
            "status": False}


def get_user_points(db: Session, user_id: int):
    """
    Get the current points for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        dict: User points and status
    """
    try:
        user = db.query(models.Users).filter(models.Users.id == user_id).first()
        if user:
            return {"points": user.points, "status": True}
        else:
            return {"message": "User not found", "status": False}
    except Exception as e:
        return {"message": "Failed to get user points", "error": str(e), "status": False}
