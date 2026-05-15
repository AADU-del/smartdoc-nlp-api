

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.databases import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.middleware.auth_middleware import get_current_user


router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/register
    Creates a new user account and returns JWT tokens.
    201 = Created (more specific than 200 OK)

    Depends(get_db) = FastAPI dependency injection
    FastAPI creates a DB session, passes it here, closes it after
    We never manually open or close database connections
    """

    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="user"
    )
    db.add(new_user)      
    db.commit()           
    db.refresh(new_user)   

    token_data = {"sub": str(new_user.id), "role": new_user.role}

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer"
    }


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/login
    Validates credentials and returns JWT tokens.
    """
    # Find user by email
    user = db.query(User).filter(
        User.email == credentials.email
    ).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"  # vague on purpose
        )

    token_data = {"sub": str(user.id), "role": user.role}

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    GET /api/v1/auth/me
    Returns the currently logged in user's profile.
    Depends(get_current_user) = requires valid JWT token
    """
    return current_user


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    POST /api/v1/auth/refresh
    Takes a refresh token, returns a new access token.
    This way users don't have to log in every 30 minutes.
    """
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user = db.query(User).filter(
        User.id == int(payload.get("sub"))
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    token_data = {"sub": str(user.id), "role": user.role}

    return {
        "access_token": create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type": "bearer"
    }