"""
TaskHandler class - Processes task-related requests and responses.
This handler delegates to the TaskService for business logic while handling HTTP concerns.
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from sqlmodel import Session
from backend.services.task_service import TaskService
from backend.validation.base_validator import TaskValidator
from backend.utils.response_utils import create_success_response, create_error_response
from backend.utils.error_utils import handle_error, ValidationError, NotFoundError
from backend.logging.app_logger import app_logger
from backend.core.dependency_injection import get_service


class TaskHandler:
    """
    Handler class for processing task-related requests and responses.
    Delegates business logic to TaskService while handling HTTP concerns like
    request parsing, response formatting, and error handling.
    """

    def __init__(self):
        """
        Initialize the TaskHandler with required services.
        """
        self.task_service = get_service(TaskService)
        self.validator = TaskValidator()

    def handle_create_task(
        self,
        session: Session,
        user_id: str,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle request to create a new task.

        Args:
            session: Database session
            user_id: ID of the user creating the task
            title: Title of the task
            description: Optional description of the task

        Returns:
            Response dictionary with created task information
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id, "title": title}
            if description is not None:
                data["description"] = description

            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                # Create error response with validation errors
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Create task via service
            task = self.task_service.create_task(session, user_id, title, description)

            # Log successful operation
            app_logger.info(
                f"Task created successfully: {task.id} for user {user_id}",
                extra_data={
                    "user_id": user_id,
                    "task_id": task.id,
                    "operation": "create_task"
                }
            )

            # Format response
            return create_success_response(
                data={
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "updated_at": task.updated_at.isoformat() if task.updated_at else None
                    }
                },
                message="Task created successfully",
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in create_task: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error creating task for user {user_id}: {str(e)}")
            return handle_error(e, context="create_task", user_id=user_id)

    def handle_get_task(self, session: Session, task_id: str, user_id: str) -> Dict[str, Any]:
        """
        Handle request to get a specific task.

        Args:
            session: Database session
            task_id: ID of the task to retrieve
            user_id: ID of the user requesting the task

        Returns:
            Response dictionary with task information
        """
        try:
            # Validate input parameters
            data = {"task_id": task_id, "user_id": user_id}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Get task via service
            task = self.task_service.get_task(session, task_id, user_id)

            if not task:
                app_logger.warning(
                    f"Task not found: {task_id} for user {user_id}",
                    extra_data={"user_id": user_id, "task_id": task_id}
                )
                return create_error_response(
                    error="TASK_NOT_FOUND",
                    message="Task not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Format response
            return create_success_response(
                data={
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "updated_at": task.updated_at.isoformat() if task.updated_at else None
                    }
                },
                message="Task retrieved successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in get_task: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error getting task {task_id} for user {user_id}: {str(e)}")
            return handle_error(e, context="get_task", user_id=user_id)

    def handle_get_all_tasks(
        self,
        session: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Handle request to get all tasks for a user.

        Args:
            session: Database session
            user_id: ID of the user whose tasks to retrieve
            limit: Maximum number of tasks to return
            offset: Offset for pagination

        Returns:
            Response dictionary with list of tasks
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id, "limit": limit, "offset": offset}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Validate limit range
            if not (1 <= limit <= 100):
                return create_error_response(
                    error="INVALID_LIMIT",
                    message="Limit must be between 1 and 100",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Get tasks via service
            tasks = self.task_service.get_all_tasks(session, user_id, limit, offset)

            # Format response
            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
                for task in tasks
            ]

            return create_success_response(
                data={
                    "tasks": tasks_data,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": len(tasks_data)  # This is actually just for this page, but in a real implementation we'd get the full count
                    }
                },
                message=f"Retrieved {len(tasks_data)} tasks"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in get_all_tasks: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error getting tasks for user {user_id}: {str(e)}")
            return handle_error(e, context="get_all_tasks", user_id=user_id)

    def handle_update_task(
        self,
        session: Session,
        task_id: str,
        user_id: str,
        **updates
    ) -> Dict[str, Any]:
        """
        Handle request to update a task.

        Args:
            session: Database session
            task_id: ID of the task to update
            user_id: ID of the user requesting the update
            **updates: Fields to update

        Returns:
            Response dictionary with updated task information
        """
        try:
            # Validate input parameters
            data = {"task_id": task_id, "user_id": user_id, **updates}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Update task via service
            updated_task = self.task_service.update_task(session, task_id, user_id, **updates)

            if not updated_task:
                app_logger.warning(
                    f"Task not found for update: {task_id} for user {user_id}",
                    extra_data={"user_id": user_id, "task_id": task_id}
                )
                return create_error_response(
                    error="TASK_NOT_FOUND",
                    message="Task not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"Task updated successfully: {updated_task.id} for user {user_id}",
                extra_data={
                    "user_id": user_id,
                    "task_id": updated_task.id,
                    "operation": "update_task",
                    "updated_fields": list(updates.keys())
                }
            )

            # Format response
            return create_success_response(
                data={
                    "task": {
                        "id": updated_task.id,
                        "title": updated_task.title,
                        "description": updated_task.description,
                        "completed": updated_task.completed,
                        "created_at": updated_task.created_at.isoformat() if updated_task.created_at else None,
                        "updated_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None
                    }
                },
                message="Task updated successfully"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in update_task: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
            return handle_error(e, context="update_task", user_id=user_id)

    def handle_delete_task(self, session: Session, task_id: str, user_id: str) -> Dict[str, Any]:
        """
        Handle request to delete a task.

        Args:
            session: Database session
            task_id: ID of the task to delete
            user_id: ID of the user requesting the deletion

        Returns:
            Response dictionary confirming deletion
        """
        try:
            # Validate input parameters
            data = {"task_id": task_id, "user_id": user_id}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Delete task via service
            deleted = self.task_service.delete_task(session, task_id, user_id)

            if not deleted:
                app_logger.warning(
                    f"Task not found for deletion: {task_id} for user {user_id}",
                    extra_data={"user_id": user_id, "task_id": task_id}
                )
                return create_error_response(
                    error="TASK_NOT_FOUND",
                    message="Task not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"Task deleted successfully: {task_id} for user {user_id}",
                extra_data={
                    "user_id": user_id,
                    "task_id": task_id,
                    "operation": "delete_task"
                }
            )

            # Format response
            return create_success_response(
                message="Task deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in delete_task: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
            return handle_error(e, context="delete_task", user_id=user_id)

    def handle_toggle_task_completion(self, session: Session, task_id: str, user_id: str) -> Dict[str, Any]:
        """
        Handle request to toggle a task's completion status.

        Args:
            session: Database session
            task_id: ID of the task to toggle
            user_id: ID of the user requesting the toggle

        Returns:
            Response dictionary with toggled task information
        """
        try:
            # Validate input parameters
            data = {"task_id": task_id, "user_id": user_id}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Toggle task completion via service
            updated_task = self.task_service.toggle_task_completion(session, task_id, user_id)

            if not updated_task:
                app_logger.warning(
                    f"Task not found for toggle: {task_id} for user {user_id}",
                    extra_data={"user_id": user_id, "task_id": task_id}
                )
                return create_error_response(
                    error="TASK_NOT_FOUND",
                    message="Task not found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Log successful operation
            app_logger.info(
                f"Task completion toggled: {updated_task.id} for user {user_id}",
                extra_data={
                    "user_id": user_id,
                    "task_id": updated_task.id,
                    "new_completion_status": updated_task.completed,
                    "operation": "toggle_task_completion"
                }
            )

            # Format response
            return create_success_response(
                data={
                    "task": {
                        "id": updated_task.id,
                        "title": updated_task.title,
                        "description": updated_task.description,
                        "completed": updated_task.completed,
                        "created_at": updated_task.created_at.isoformat() if updated_task.created_at else None,
                        "updated_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None
                    }
                },
                message=f"Task marked as {'completed' if updated_task.completed else 'pending'}"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in toggle_task_completion: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error toggling task {task_id} completion for user {user_id}: {str(e)}")
            return handle_error(e, context="toggle_task_completion", user_id=user_id)

    def handle_get_completed_tasks(self, session: Session, user_id: str) -> Dict[str, Any]:
        """
        Handle request to get completed tasks for a user.

        Args:
            session: Database session
            user_id: ID of the user whose completed tasks to retrieve

        Returns:
            Response dictionary with list of completed tasks
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Get completed tasks via service
            tasks = self.task_service.get_completed_tasks(session, user_id)

            # Format response
            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
                for task in tasks
            ]

            return create_success_response(
                data={
                    "tasks": tasks_data,
                    "total": len(tasks_data)
                },
                message=f"Retrieved {len(tasks_data)} completed tasks"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in get_completed_tasks: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error getting completed tasks for user {user_id}: {str(e)}")
            return handle_error(e, context="get_completed_tasks", user_id=user_id)

    def handle_search_tasks(
        self,
        session: Session,
        user_id: str,
        search_term: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Handle request to search tasks by title or description.

        Args:
            session: Database session
            user_id: ID of the user performing the search
            search_term: Term to search for
            limit: Maximum number of results to return
            offset: Offset for pagination

        Returns:
            Response dictionary with search results
        """
        try:
            # Validate input parameters
            data = {"user_id": user_id, "search_term": search_term, "limit": limit, "offset": offset}
            validation_result, errors = self.validator.validate(data)
            if not validation_result:
                error_details = [str(err) for err in errors]
                return create_error_response(
                    error="VALIDATION_FAILED",
                    message="Invalid input parameters",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"errors": error_details}
                )

            # Validate limit range
            if not (1 <= limit <= 100):
                return create_error_response(
                    error="INVALID_LIMIT",
                    message="Limit must be between 1 and 100",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Search tasks via service
            tasks = self.task_service.search_tasks(session, user_id, search_term, limit, offset)

            # Format response
            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
                for task in tasks
            ]

            return create_success_response(
                data={
                    "tasks": tasks_data,
                    "pagination": {
                        "limit": limit,
                        "offset": offset,
                        "total": len(tasks_data)
                    },
                    "search_term": search_term
                },
                message=f"Found {len(tasks_data)} tasks matching '{search_term}'"
            )

        except ValidationError as ve:
            app_logger.error(f"Validation error in search_tasks: {ve}", extra_data={"user_id": user_id})
            return create_error_response(
                error="VALIDATION_ERROR",
                message=str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            app_logger.error(f"Error searching tasks for user {user_id}: {str(e)}")
            return handle_error(e, context="search_tasks", user_id=user_id)