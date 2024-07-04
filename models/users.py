from sqlalchemy import Column, Integer, String, DateTime, Boolean
# import datetime

from models import Base
from datetime import datetime

class User(Base):
    """User model."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

