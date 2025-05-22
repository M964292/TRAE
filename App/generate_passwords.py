from App.utils.passwords import hash_password

# Генерируем хеш пароля для учителя
TEACHER_PASSWORD_HASH = hash_password('teacher123')
print('Teacher password hash:', TEACHER_PASSWORD_HASH)

# Генерируем хеш пароля для ученика
STUDENT_PASSWORD_HASH = hash_password('student123')
print('Student password hash:', STUDENT_PASSWORD_HASH)
