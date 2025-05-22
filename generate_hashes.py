from passlib.context import CryptContext

# Создаем контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Генерируем хеши паролей
teacher_password_hash = pwd_context.hash("teacher123")
student_password_hash = pwd_context.hash("student123")

print("Teacher password hash:", teacher_password_hash)
print("Student password hash:", student_password_hash)
