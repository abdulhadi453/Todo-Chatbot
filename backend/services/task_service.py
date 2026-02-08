"""
TaskService class - Handles all task-related business logic (CRUD operations, status management).
This service follows the single responsibility principle and provides clear task management functionality.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from backend.models.task import Task  # Assuming a Task model exists
from backend.core.dependency_injection import register_service, Injectable
from backend.utils.validator_utils import validate_required_fields
from backend.utils.error_utils import ValidationError, NotFoundError, ServiceError


@register_service
class TaskService(Injectable):
    """
    Service class for handling task-related business logic.
    Manages CRUD operations, status management, and other task-related functionality.
    """

    def __init__(self):
        """
        Initialize the TaskService.
        """
        pass

    def create_task(self, session: Session, user_id: str, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            user_id: ID of the user creating the task
            title: Title of the task
            description: Optional description of the task

        Returns:
            Created Task instance

        Raises:
            ValidationError: If required fields are missing or invalid
        """
        # Validate required fields
        data = {"user_id": user_id, "title": title}
        missing_fields = validate_required_fields(data, ["user_id", "title"])

        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

        # Validate title length
        if not (1 <= len(title) <= 200):  # Assuming max length of 200
            raise ValidationError("Title must be between 1 and 200 characters")

        # Create task instance
        task = Task(
            user_id=user_id,
            title=title,
            description=description or "",
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Add to session and commit
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    def get_task(self, session: Session, task_id: str, user_id: str) -> Optional[Task]:
        """
        Get a specific task by ID for a user.

        Args:
            session: Database session
            task_id: ID of the task to retrieve
            user_id: ID of the user requesting the task

        Returns:
            Task instance if found and owned by user, None otherwise
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        return task

    def get_all_tasks(self, session: Session, user_id: str, limit: int = 50, offset: int = 0) -> List[Task]:
        """
        Get all tasks for a user.

        Args:
            session: Database session
            user_id: ID of the user whose tasks to retrieve
            limit: Maximum number of tasks to return
            offset: Offset for pagination

        Returns:
            List of Task instances
        """
        statement = select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)
        tasks = session.exec(statement).all()
        return tasks

    def update_task(self, session: Session, task_id: str, user_id: str, **updates) -> Optional[Task]:
        """
        Update a task with the provided fields.

        Args:
            session: Database session
            task_id: ID of the task to update
            user_id: ID of the user requesting the update
            **updates: Fields to update

        Returns:
            Updated Task instance if successful, None if not found

        Raises:
            ValidationError: If invalid fields are provided
        """
        # Validate updates
        allowed_updates = {"title", "description", "completed"}
        invalid_fields = set(updates.keys()) - allowed_updates

        if invalid_fields:
            raise ValidationError(f"Invalid fields for update: {', '.join(invalid_fields)}")

        # Get the task
        task = self.get_task(session, task_id, user_id)
        if not task:
            return None

        # Apply updates
        for field, value in updates.items():
            if hasattr(task, field):
                setattr(task, field, value)

        # Update timestamp
        task.updated_at = datetime.utcnow()

        # Commit changes
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    def delete_task(self, session: Session, task_id: str, user_id: str) -> bool:
        """
        Delete a task.

        Args:
            session: Database session
            task_id: ID of the task to delete
            user_id: ID of the user requesting the deletion

        Returns:
            True if task was deleted, False if not found
        """
        task = self.get_task(session, task_id, user_id)
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True

    def toggle_task_completion(self, session: Session, task_id: str, user_id: str) -> Optional[Task]:
        """
        Toggle the completion status of a task.

        Args:
            session: Database session
            task_id: ID of the task to toggle
            user_id: ID of the user requesting the toggle

        Returns:
            Updated Task instance if successful, None if not found
        """
        task = self.get_task(session, task_id, user_id)
        if not task:
            return None

        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        # Commit changes
        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    def get_completed_tasks(self, session: Session, user_id: str) -> List[Task]:
        """
        Get all completed tasks for a user.

        Args:
            session: Database session
            user_id: ID of the user whose completed tasks to retrieve

        Returns:
            List of completed Task instances
        """
        statement = select(Task).where(Task.user_id == user_id, Task.completed == True)
        tasks = session.exec(statement).all()
        return tasks

    def get_pending_tasks(self, session: Session, user_id: str) -> List[Task]:
        """
        Get all pending (not completed) tasks for a user.

        Args:
            session: Database session
            user_id: ID of the user whose pending tasks to retrieve

        Returns:
            List of pending Task instances
        """
        statement = select(Task).where(Task.user_id == user_id, Task.completed == False)
        tasks = session.exec(statement).all()
        return tasks

    def get_task_summary(self, session: Session, user_id: str) -> Dict[str, int]:
        """
        Get a summary of tasks for a user.

        Args:
            session: Database session
            user_id: ID of the user whose task summary to retrieve

        Returns:
            Dictionary with counts of total, completed, and pending tasks
        """
        total_statement = select(Task).where(Task.user_id == user_id)
        total_tasks = len(session.exec(total_statement).all())

        completed_statement = select(Task).where(Task.user_id == user_id, Task.completed == True)
        completed_tasks = len(session.exec(completed_statement).all())

        pending_tasks = total_tasks - completed_tasks

        return {
            "total": total_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks
        }

    def bulk_update_tasks(self, session: Session, task_ids: List[str], user_id: str, **updates) -> Dict[str, Any]:
        """
        Bulk update multiple tasks.

        Args:
            session: Database session
            task_ids: List of task IDs to update
            user_id: ID of the user requesting the updates
            **updates: Fields to update

        Returns:
            Dictionary with counts of successful and failed updates
        """
        # Validate updates
        allowed_updates = {"completed"}
        invalid_fields = set(updates.keys()) - allowed_updates

        if invalid_fields:
            raise ValidationError(f"Bulk updates only allowed for: {', '.join(allowed_updates)}")

        success_count = 0
        failed_count = 0
        failed_ids = []

        for task_id in task_ids:
            try:
                # Update individual task
                updated_task = self.update_task(session, task_id, user_id, **updates)
                if updated_task:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(task_id)
            except Exception:
                failed_count += 1
                failed_ids.append(task_id)

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_ids": failed_ids
        }

    def search_tasks(self, session: Session, user_id: str, search_term: str, limit: int = 50, offset: int = 0) -> List[Task]:
        """
        Search tasks by title or description.

        Args:
            session: Database session
            user_id: ID of the user whose tasks to search
            search_term: Term to search for in titles and descriptions
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            List of matching Task instances
        """
        statement = select(Task).where(
            Task.user_id == user_id,
            (Task.title.contains(search_term)) | (Task.description.contains(search_term))
        ).offset(offset).limit(limit)

        tasks = session.exec(statement).all()
        return tasks