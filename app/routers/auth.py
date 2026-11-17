"""
Authentication endpoints.

Currently:
    POST /api/auth/register  -> create a new user account
    POST /api/auth/login     -> check email + password, return a JWT
    GET  /api/auth/me        -> return the logged-in user (requires a JWT)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.security import create_access_token, hash_password, verify_password

# prefix="/auth" + the "/api" prefix added in main.py -> "/api/auth/..."
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,          # shape of the response (no password!)
    status_code=status.HTTP_201_CREATED,  # 201 = a new resource was created
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Store emails in lowercase so "Harsh@Example.com" and "harsh@example.com"
    # count as the same account.
    email = user_in.email.lower()

    # 1. Check if the email is already taken
    existing_user = db.scalars(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    # 2. Create the user with a HASHED password (never the plain one)
    new_user = User(email=email, hashed_password=hash_password(user_in.password))

    # 3. Save to the database
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        # Safety net: if two requests register the same email at the same
        # moment, the database's UNIQUE constraint stops the second one.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    # 4. Reload the row so we get values set by the database (id, created_at)
    db.refresh(new_user)

    # FastAPI converts this User object into UserResponse JSON
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # Same lowercase rule as registration, so the emails always match
    email = credentials.email.lower()

    # 1. Find the user by email
    user = db.scalars(select(User).where(User.email == email)).first()

    # 2. Check the user exists AND the password is correct.
    #    We use ONE generic message for both cases so attackers can't
    #    find out which emails are registered.
    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Disabled accounts cannot log in
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # 4. Create the JWT and return it (status 200 OK by default)
    access_token = create_access_token(user.id)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    # get_current_user already did all the checks (token, user exists, active).
    # If we reach this line, current_user is the logged-in user.
    return current_user
