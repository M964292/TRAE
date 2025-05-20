from typing import Optional, Dict, Any
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from .models import Student

# Загружаем переменные окружения
load_dotenv()

# Настройка аутентификации
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in environment")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Password Flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Примеры пользователей ---
TEACHER_PASSWORD_HASH = os.getenv("TEACHER_PASSWORD_HASH")
STUDENT_PASSWORD_HASH = os.getenv("STUDENT_PASSWORD_HASH")

if not TEACHER_PASSWORD_HASH or not STUDENT_PASSWORD_HASH:
    raise ValueError("Password hashes must be set in environment")

dummy_users_db = {
    "teacher": {
        "username": "teacher",
        "hashed_password": TEACHER_PASSWORD_HASH,
        "role": "teacher"
    },
    "student": {
        "username": "student",
        "hashed_password": STUDENT_PASSWORD_HASH,
        "role": "student"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить правильность пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Получить хеш пароля"""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Получить пользователя из базы"""
    return dummy_users_db.get(username)

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Аутентифицировать пользователя"""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Создать токен доступа"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_active_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Получить текущего активного пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

def check_teacher_password(password: str) -> bool:
    """Проверить пароль учителя"""
    return verify_password(password, TEACHER_PASSWORD_HASH)