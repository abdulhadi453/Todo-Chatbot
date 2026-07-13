import os

# Provide a compatibility package so tests importing `todo_backend.src.*`
# resolve into the existing `backend/src` directory.
# Set the package __path__ to the repo's `backend` directory so subpackage
# `src` maps to `backend/src` on disk.
__path__ = [os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))]
