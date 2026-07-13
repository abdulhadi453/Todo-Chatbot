"""Compatibility shim: re-export todo models from backend.src.models.todo_model
so imports under `todo_backend.src.models` resolve correctly.
"""
from importlib import import_module

_mod = import_module("backend.src.models.todo_model")

# Re-export all public names from the real module
from backend.src.models.todo_model import *  # noqa: F401,F403
