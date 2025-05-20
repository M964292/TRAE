import sys
import os

# Добавляем путь к папке app в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.passwords import hash_password

print('Teacher password hash:', hash_password('teacher123'))
print('Student password hash:', hash_password('student123'))
