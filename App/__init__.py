from .main import app
from .routers import test_router, auth_router
from .auth import auth as auth_module
from .database import database as database_module
from .. import supabase_client
