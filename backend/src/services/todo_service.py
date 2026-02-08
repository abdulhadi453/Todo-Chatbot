from sqlmodel import Session, select
from typing import List, Optional

# Try relative import first (when running as a module)
try:
    from ..models.todo_model import (
        TodoTask, TodoTaskCreate, TodoTaskUpdate
    )
except ImportError:
    # Fall back to absolute import (when running directly)
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    src_dir = os.path.dirname(parent_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    from models.todo_model import (
        TodoTask, TodoTaskCreate, TodoTaskUpdate
    )
from datetime import datetime, timezone

# Handle import for toggle_task_completion function
try:
    from ..models.todo_model import TodoTaskPatch
except ImportError:
    # Fall back to absolute import (when running directly)
    from models.todo_model import TodoTaskPatch


def create_task(session: Session, todo_task: TodoTaskCreate, user_id: str) -> TodoTask:
    """Create a new todo task in the database"""
    import uuid
    from datetime import datetime, timezone
    # Create the task object with all the fields from the input plus the user_id
    current_time = datetime.now(timezone.utc)

    # Convert string date to datetime object if provided
    due_date_obj = None
    if todo_task.due_date:
        try:
            # Parse date string - handle both date-only and datetime formats
            date_str = todo_task.due_date
            if 'T' in date_str:  # Full datetime format
                # Handle timezone-aware format like "2026-12-31T10:00:00+00:00" or "2026-12-31T10:00:00Z"
                date_str = date_str.replace('Z', '+00:00')
                if '+' in date_str or date_str.endswith('-00:00'):
                    # Split date/time from timezone
                    if '+' in date_str:
                        dt_part = date_str.split('+')[0]
                    else:
                        dt_part = date_str.replace('-00:00', '')
                    # Parse the datetime part and make it timezone-aware
                    due_date_obj = datetime.fromisoformat(dt_part.replace('T', ' ')).replace(tzinfo=timezone.utc)
                else:
                    # Simple datetime format like "2026-12-31T10:00:00"
                    due_date_obj = datetime.fromisoformat(date_str.replace('T', ' ')).replace(tzinfo=timezone.utc)
            else:  # Date-only format like "2026-12-31"
                # Parse date string and convert to datetime with timezone
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                due_date_obj = datetime.combine(date_obj, datetime.min.time()).replace(tzinfo=timezone.utc)
        except Exception:
            # If parsing fails, keep as None
            due_date_obj = None

    db_task = TodoTask(
        id=str(uuid.uuid4()),  # Generate a unique string ID
        title=todo_task.title,
        description=todo_task.description,
        completed=todo_task.completed,
        category=todo_task.category,
        priority=todo_task.priority,
        due_date=due_date_obj,  # Convert string to datetime object
        user_id=user_id,  # Set user_id from the authenticated user
        created_at=current_time,
        updated_at=current_time
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def get_tasks_by_user(session: Session, user_id: str) -> List[TodoTask]:
    """Get all tasks for a specific user"""
    statement = select(TodoTask).where(TodoTask.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks


def get_task_by_id(session: Session, task_id: str, user_id: str) -> Optional[TodoTask]:
    """Get a specific task by ID for a specific user"""
    statement = select(TodoTask).where(TodoTask.id == task_id, TodoTask.user_id == user_id)
    task = session.exec(statement).first()
    return task


def update_task(
    session: Session,
    task_id: str,
    user_id: str,
    todo_task_update: TodoTaskUpdate
) -> Optional[TodoTask]:
    """Update a specific task by ID for a specific user"""
    db_task = get_task_by_id(session, task_id, user_id)
    if not db_task:
        return None

    update_data = todo_task_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == 'due_date' and value is not None:
            # Convert string date to datetime object
            try:
                if 'T' in value:  # ISO format with time
                    due_date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:  # Date only format (YYYY-MM-DD)
                    due_date_obj = datetime.fromisoformat(value + 'T00:00:00+00:00')
                setattr(db_task, field, due_date_obj)
            except ValueError:
                # If parsing fails, set to None
                setattr(db_task, field, None)
        elif hasattr(db_task, field):
            setattr(db_task, field, value)

    db_task.updated_at = datetime.now(timezone.utc)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def delete_task(session: Session, task_id: str, user_id: str) -> bool:
    """Delete a specific task by ID for a specific user"""
    db_task = get_task_by_id(session, task_id, user_id)
    if not db_task:
        return False

    session.delete(db_task)
    session.commit()
    return True


def toggle_task_completion(session: Session, task_id: str, user_id: str) -> Optional[TodoTask]:
    """Toggle the completion status of a specific task"""
    db_task = get_task_by_id(session, task_id, user_id)
    if not db_task:
        return None

    from datetime import datetime, timezone
    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.now(timezone.utc)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task