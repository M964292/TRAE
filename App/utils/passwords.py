import secrets
import string
from passlib.context import CryptContext

# Создаем контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password(length: int = 12) -> str:
    """Генерирует безопасный пароль заданной длины"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in string.punctuation for c in password)
        ):
            return password

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return pwd_context.verify(plain_password, hashed_password)

# Пример использования:
if __name__ == "__main__":
    # Генерация нового безопасного пароля
    new_password = generate_password()
    print(f"Generated password: {new_password}")
    
    # Хеширование пароля
    hashed = hash_password(new_password)
    print(f"Hashed password: {hashed}")
    print()
    
    # Проверка пароля
    print(f"Password verification: {verify_password(new_password, hashed)}")
    
    # Генерация хешей для учителя и студента
    print('Teacher password hash:', hash_password('teacher123'))
    print('Student password hash:', hash_password('student123'))