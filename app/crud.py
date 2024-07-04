from sqlalchemy.orm import Session
from . import schemas
from models.users import User


def get_user(db: Session, username:str):
    """Get a user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """Get a user by email."""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all users."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user."""
    password_hash = user.password_hash
    db_user = User(username=user.username , password_hash=password_hash, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
