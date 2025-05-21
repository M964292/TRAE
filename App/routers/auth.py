from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..models import UserCreate, User
from ..database import get_supabase
from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        supabase = get_supabase()
        user = supabase.table("users").select("*").eq("id", user_id).single().execute()
        if not user.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/token", response_model=Dict[str, Any])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    supabase = get_supabase()
    user = supabase.table("users").select("*").eq("email", form_data.username).single().execute()
    
    if not user.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not pwd_context.verify(form_data.password, user.data.get("hashed_password")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.data.get("id")}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=Dict[str, Any])
async def register(user: UserCreate):
    supabase = get_supabase()
    existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
    
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = pwd_context.hash(user.password)
    user_data = {
        "email": user.email,
        "hashed_password": hashed_password,
        "full_name": user.full_name,
        "role": user.role,
        "specialization": user.specialization,
        "grade": user.grade,
        "class_name": user.class_name,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("users").insert(user_data).execute()
    return result.data[0]
