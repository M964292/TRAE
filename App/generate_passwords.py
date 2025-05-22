from utils.passwords import hash_password
from .models.user import UserCreate

print('Teacher password hash:', hash_password('teacher123'))
print('Student password hash:', hash_password('student123'))
