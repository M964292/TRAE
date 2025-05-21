from typing import Optional, Dict, Any
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_supabase

# Настройка аутентификации
# Используем конфигурацию из config.py

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Password Flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить правильность пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создать JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """Проверить JWT токен"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except jwt.JWTError:
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Получить текущего пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        email = verify_token(token, credentials_exception)
        supabase = get_supabase()
        response = supabase.table("users").select("*").eq("email", email).execute()
        if not response.data:
            raise credentials_exception
        return response.data[0]
    except Exception:
        raise credentials_exception

def authenticate_user(email: str, password: str):
    """Аутентифицировать пользователя"""
    supabase = get_supabase()
    response = supabase.table("users").select("*").eq("email", email).execute()
    if not response.data:
        return False
    user = response.data[0]
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_user(user_data: Dict[str, Any]):
    """Создать нового пользователя"""
    supabase = get_supabase()
    try:
        response = supabase.table("users").insert(user_data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def check_teacher_password(password: str) -> bool:
    """Проверить пароль учителя"""
    return verify_password(password, TEACHER_PASSWORD_HASH)