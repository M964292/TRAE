from App.utils.passwords import hash_password
from .models.user import UserCreate

# Генерируем хеш пароля для учителя
TEACHER_PASSWORD_HASH = hash_password('teacher123')
print('Teacher password hash:', TEACHER_PASSWORD_HASH)

# Генерируем хеш пароля для ученика
STUDENT_PASSWORD_HASH = hash_password('student123')
print('Student password hash:', STUDENT_PASSWORD_HASH)

# Сохраняем хеш пароля учителя в файл
with open('../config.py', 'a') as f:
    f.write(f"\nTEACHER_PASSWORD_HASH = '{TEACHER_PASSWORD_HASH}'\n")
    f.write(f"\nSTUDENT_PASSWORD_HASH = '{STUDENT_PASSWORD_HASH}'\n")
