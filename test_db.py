from App.database import get_supabase
from App.models.user import UserCreate

# Получаем клиент Supabase
supabase = get_supabase()

# Пример данных для нового пользователя
test_user = UserCreate(
    email="test@example.com",
    password="testpassword",
    full_name="Test User",
    role="student"
)

# Попробуем создать пользователя
try:
    response = supabase.table("users").insert({
        "email": test_user.email,
        "hashed_password": test_user.password,  # В реальности нужно хешировать пароль
        "full_name": test_user.full_name,
        "role": test_user.role,
        "is_active": True
    }).execute()
    
    print("Пользователь успешно создан!", response.data)
    
    # Попробуем получить пользователя
    user = supabase.table("users").select("*").eq("email", test_user.email).execute()
    print("Полученный пользователь:", user.data)
    
except Exception as e:
    print(f"Ошибка: {e}")
