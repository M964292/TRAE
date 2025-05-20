TEACHER_PASSWORD = "teacher123"  # Можно заменить на более безопасный способ хранения

def check_teacher_password(password: str) -> bool:
    return password == TEACHER_PASSWORD