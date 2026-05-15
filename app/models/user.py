# models/user.py — defines the 'users' table in MySQL
# This Python class = one table in the database
# Each variable = one column in that table
# SQLAlchemy reads this and creates the actual table for us

from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.sql import func
from app.databases import Base

class User(Base):
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)


    email = Column(String(255), unique=True, nullable=False, index=True)


    hashed_password = Column(String(255), nullable=False)

    role = Column(
        Enum("admin", "user", "readonly"),
        default="user",
        nullable=False
    )

    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"