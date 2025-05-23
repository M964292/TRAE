import os
import sys

# Добавляем путь к пакету в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .App import main, models, database, config
from .App.routers import auth, test
from .supabase_client import supabase_client
