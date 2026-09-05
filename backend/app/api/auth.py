from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session
from typing import Optional, Any

from app.database.session import get_db
from app.database.models import User
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class RegisterSchema(BaseModel):
    email: str
    password: str
    role: str = "candidate"  # "candidate", "recruiter", or "admin"
    class_level: Optional[int] = Field(default=None, ge=1, le=12)

    @model_validator(mode="after")
    def validate_candidate_class_level(self):
        if self.role == "candidate" and self.class_level is None:
            raise ValueError("Student class_level is required for candidate registration.")
        if self.role in ["recruiter", "admin"]:
            self.class_level = None
        return self

class LoginSchema(BaseModel):
    email: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserResponseSchema(BaseModel):
    id: str
    email: str
    role: str
    class_level: Optional[int] = None
    is_active: bool
    created_at: Any

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterSchema, db: Session = Depends(get_db)):
    """Registers a new candidate or recruiter account. Rejects duplicate emails."""
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email address is already registered."
        )

    if payload.role not in ["candidate", "recruiter", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be one of: 'candidate', 'recruiter', 'admin'."
        )

    hashed_pwd = get_password_hash(payload.password)
    new_user = User(
        email=payload.email,
        password_hash=hashed_pwd,
        role=payload.role,
        class_level=payload.class_level,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponseSchema(
        id=str(new_user.id),
        email=new_user.email,
        role=new_user.role,
        class_level=new_user.class_level,
        is_active=new_user.is_active,
        created_at=new_user.created_at
    )

@router.post("/login", response_model=TokenSchema)
def login_user(payload: LoginSchema, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns JWT bearer access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    access_token = create_access_token(subject=str(user.id), role=user.role)
    return TokenSchema(access_token=access_token, token_type="bearer", role=user.role)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency parsing JWT bearer token and returning current User model instance."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User account not found or inactive.")
    
    return user

@router.get("/me", response_model=UserResponseSchema)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns profile information for the authenticated user."""
    return UserResponseSchema(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        class_level=current_user.class_level,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
