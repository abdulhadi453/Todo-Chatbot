from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from config.database import get_session
# Try relative imports first (when running as a module)
try:
    from ..models.todo_model import (
        TodoTask, TodoTaskCreate, TodoTaskRead, TodoTaskUpdate, TodoTaskPatch
    )
    from ..services.todo_service import (
        create_task, get_tasks_by_user, get_task_by_id,
        update_task, delete_task, toggle_task_completion
    )
    from ..auth.auth_dependencies import get_user_from_token
except ImportError:
    # Fall back to absolute imports (when running directly)
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    src_dir = os.path.dirname(parent_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    from models.todo_model import (
        TodoTask, TodoTaskCreate, TodoTaskRead, TodoTaskUpdate, TodoTaskPatch
    )
    from services.todo_service import (
        create_task, get_tasks_by_user, get_task_by_id,
        update_task, delete_task, toggle_task_completion
    )
    from auth.auth_dependencies import get_user_from_token

router = APIRouter(prefix="/api")


@router.post("/tasks", response_model=TodoTaskRead, status_code=201)
def create_todo_task(
    todo_task: TodoTaskCreate,
    current_user_id: str = Depends(get_user_from_token),
    session: Session = Depends(get_session)
):
    """Create a new todo task for the authenticated user"""
    # Pass the authenticated user's ID to the service
    db_task = create_task(session, todo_task, current_user_id)
    return db_task


@router.get("/tasks", response_model=List[TodoTaskRead])
def read_user_tasks(
    current_user_id: str = Depends(get_user_from_token),
    session: Session = Depends(get_session)
):
    """Get all todo tasks for the authenticated user"""
    tasks = get_tasks_by_user(session, current_user_id)
    return tasks


@router.get("/tasks/{task_id}", response_model=TodoTaskRead)
def read_specific_task(
    task_id: str,
    current_user_id: str = Depends(get_user_from_token),
    session: Session = Depends(get_session)
):
    """Get a specific todo task by ID for the authenticated user"""
    task = get_task_by_id(session, task_id, current_user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=TodoTaskRead)
def update_todo_task(
    task_id: str,
    todo_task_update: TodoTaskUpdate,
    current_user_id: str = Depends(get_user_from_token),
    session: Session = Depends(get_session)
):
    """Update a specific todo task by ID for the authenticated user"""
    task = update_task(session, task_id, current_user_id, todo_task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_todo_task(
    task_id: str,
    current_user_id: str = Depends(get_user_from_token),
    session: Session = Depends(get_session)
):
    """Delete a specific todo task by ID for the authenticated user"""
    success = delete_task(session, task_id, current_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return


@router.patch("/tasks/{task_id}/complete", response_model=TodoTaskRead)
def toggle_complete_task(
    task_id: str,
    todo_task_patch: TodoTaskPatch,
    current_user_id: str = Depends(get_user_from_token),
    session: Session = Depends(get_session)
):
    """Toggle the completion status of a specific todo task"""
    task = toggle_task_completion(session, task_id, current_user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task