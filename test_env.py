from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Проверка значений переменных
print("SUPABASE_URL:", os.getenv('SUPABASE_URL'))
print("SUPABASE_KEY:", os.getenv('SUPABASE_KEY'))
