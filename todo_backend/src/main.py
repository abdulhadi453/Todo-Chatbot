"""Compatibility shim: expose `app` from the real backend.src.main
so tests that import `todo_backend.src.main` continue to work.
"""
from importlib import import_module

_mod = import_module("backend.src.main")
app = getattr(_mod, "app")
