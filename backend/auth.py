
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from backend.auth_schemas import (
    RegisterRequest,
    RegisterResponse,
    UserResponse,
    BusinessResponse,
    LoginRequest,
    LoginResponse,
)

from backend.database import get_db
from backend.models import User, Business, BusinessMember
from backend.security import hash_password, verify_password, create_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.security import decode_access_token
import jwt


router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user



@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
    )

    business = Business(
        business_name=data.business_name,
    )

    try:
        db.add_all([user, business])
        db.flush()

        membership = BusinessMember(
            user_id=user.id,
            business_id=business.id,
            role="owner",
        )

        db.add(membership)
        db.commit()

        db.refresh(user)
        db.refresh(business)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to create account. The email may already be registered.",
        )

    access_token = create_access_token(user_id=user.id)

    return RegisterResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        business=BusinessResponse.model_validate(business),
    )



@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user_id=user.id)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )
    


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

