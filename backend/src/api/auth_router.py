from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta
import uuid

from config.database import get_session
# Try relative imports first (when running as a module)
try:
    from ..auth.jwt_utils import create_access_token, create_refresh_token, verify_refresh_token
    from ..auth.auth_schemas import UserCreate, UserLogin, UserResponse, TokenRefresh, TokenRefreshResponse
    from ..models.todo_model import User, TokenResponse
    from ..auth.auth_dependencies import get_current_user
except ImportError:
    # Fall back to absolute imports (when running directly)
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    src_dir = os.path.dirname(parent_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    from auth.jwt_utils import create_access_token, create_refresh_token, verify_refresh_token
    from auth.auth_schemas import UserCreate, UserLogin, UserResponse, TokenRefresh, TokenRefreshResponse
    from models.todo_model import User, TokenResponse
    from auth.auth_dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    """Register a new user and return JWT tokens"""
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user
    db_user = User(
        email=user.email,
        password_hash=User.hash_password(user.password),
        name=user.name,
        id=str(uuid.uuid4())  # Generate a unique ID for the user
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.id, "email": db_user.email}
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": db_user.id, "email": db_user.email}
    )

    return TokenResponse(
        user_id=db_user.id,
        email=db_user.email,
        name=db_user.name,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/login", response_model=TokenResponse)
def login_user(user_credentials: UserLogin, session: Session = Depends(get_session)):
    """Authenticate user and return JWT tokens"""
    # Find user by email
    user = session.exec(select(User).where(User.email == user_credentials.email)).first()

    if not user or not user.verify_password(user_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": user.id, "email": user.email}
    )

    return TokenResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(token_refresh: TokenRefresh):
    """Refresh the access token using the refresh token"""
    # Verify the refresh token
    payload = verify_refresh_token(token_refresh.refresh_token)

    # Create new access token
    new_access_token = create_access_token(
        data={"sub": payload["sub"], "email": payload.get("email")}
    )

    return TokenRefreshResponse(
        access_token=new_access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get information about the currently authenticated user"""
    user = session.exec(select(User).where(User.id == current_user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        user_id=user.id,
        email=user.email,
        name=user.name,
        created_at=user.created_at.isoformat() if user.created_at else None
    )