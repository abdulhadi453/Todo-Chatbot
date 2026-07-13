"""Compatibility shim: re-export symbols from backend.config.database
so imports like `todo_backend.src.config.database` resolve to the real implementation.
"""
from importlib import import_module

_mod = import_module("backend.config.database")

# Re-export commonly used symbols
DATABASE_URL = getattr(_mod, "DATABASE_URL", None)
engine = getattr(_mod, "engine", None)
get_session = getattr(_mod, "get_session")
create_db_and_tables = getattr(_mod, "create_db_and_tables")
