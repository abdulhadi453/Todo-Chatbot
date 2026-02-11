"""
Tool definitions for the AI agent to interact with todo functionality.
These tools provide the AI agent with capabilities to perform todo operations.
"""

from typing import Dict, Any, List, Optional
from sqlmodel import Session, select
from datetime import datetime
import uuid

from backend.handlers.task_handler import Task  # Assuming the task model exists from Phase II
from backend.models.agent_tool import AgentTool
from backend.models.tool_execution_log import ToolExecutionLog
from backend.models.user_context import UserContext  # Import UserContext for validation
from backend.exceptions.chat_exceptions import UnauthorizedAccessException, ValidationError


class TodoTools:
    """
    Collection of tools that allow the AI agent to perform todo-related operations.
    Each method corresponds to a specific tool that the agent can use.
    """

    def __init__(self, session: Session):
        """
        Initialize the todo tools with a database session.

        Args:
            session: Database session for data access
        """
        self.session = session

    def list_todos(self, user_id: str, limit: int = 10, offset: int = 0, completed: Optional[bool] = None) -> Dict[str, Any]:
        """
        List the user's todo items with optional filtering and pagination.

        Args:
            user_id: ID of the user whose todos to list
            limit: Maximum number of todos to return (default 10)
            offset: Offset for pagination (default 0)
            completed: Filter by completion status (None=all, True=completed, False=not completed)

        Returns:
            Dictionary containing list of todos and metadata
        """
        try:
            # Validate user context first
            if not self._validate_user_context(user_id):
                raise UnauthorizedAccessException(f"Invalid user context for user_id: {user_id}")

            # Create a SQLModel statement to get tasks for the user
            statement = select(Task).where(Task.user_id == user_id)

            # Add filter for completion status if specified
            if completed is not None:
                statement = statement.where(Task.completed == completed)

            # Apply pagination
            statement = statement.offset(offset).limit(limit)

            # Execute the query
            results = self.session.exec(statement).all()

            # Format results
            todos = []
            for task in results:
                todo = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
                todos.append(todo)

            # Get total count for pagination metadata
            count_statement = select(Task).where(Task.user_id == user_id)
            if completed is not None:
                count_statement = count_statement.where(Task.completed == completed)
            total_count = len(self.session.exec(count_statement).all())

            return {
                "todos": todos,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total_count,
                    "has_more": (offset + len(todos)) < total_count
                }
            }
        except UnauthorizedAccessException:
            raise  # Re-raise authorization errors
        except Exception as e:
            raise Exception(f"Error listing todos: {str(e)}")

    def add_todo(self, user_id: str, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new todo item for the user.

        Args:
            user_id: ID of the user adding the todo
            title: Title of the new todo
            description: Optional description of the todo

        Returns:
            Dictionary containing the created todo
        """
        try:
            # Validate user context first
            if not self._validate_user_context(user_id):
                raise UnauthorizedAccessException(f"Invalid user context for user_id: {user_id}")

            # Sanitize inputs
            sanitized_title = self._sanitize_input(title) if title else None
            sanitized_description = self._sanitize_input(description) if description else None

            # Validate inputs
            if not sanitized_title or not sanitized_title.strip():
                raise ValidationError("Title is required and cannot be empty")

            if len(sanitized_title) > 200:  # Assuming max length from data model
                raise ValidationError("Title cannot exceed 200 characters")

            if sanitized_description and len(sanitized_description) > 1000:  # Assuming max length from data model
                raise ValidationError("Description cannot exceed 1000 characters")

            # Create a new task
            task = Task(
                user_id=user_id,
                title=sanitized_title.strip(),
                description=sanitized_description.strip() if sanitized_description else None,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Add to session and commit
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            # Return the created task
            return {
                "success": True,
                "todo": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
            }
        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            raise Exception(f"Error adding todo: {str(e)}")

    def update_todo(self, user_id: str, todo_id: str, title: Optional[str] = None,
                    description: Optional[str] = None, completed: Optional[bool] = None,
                    due_date: Optional[str] = None, priority: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing todo item with context-aware enhancements.

        Args:
            user_id: ID of the user updating the todo
            todo_id: ID of the todo to update
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)
            due_date: New due date in ISO format (optional)
            priority: New priority level ('low', 'medium', 'high') (optional)

        Returns:
            Dictionary containing the updated todo
        """
        try:
            # Validate user context first
            if not self._validate_user_context(user_id):
                raise UnauthorizedAccessException(f"Invalid user context for user_id: {user_id}")

            # Validate user ownership of the todo
            if not self._validate_user_ownership(todo_id, user_id):
                raise UnauthorizedAccessException(f"Todo with ID {todo_id} not found or access denied")

            # Sanitize inputs
            sanitized_title = self._sanitize_input(title) if title is not None else None
            sanitized_description = self._sanitize_input(description) if description is not None else None
            sanitized_due_date = self._sanitize_input(due_date) if due_date is not None else None
            sanitized_priority = self._sanitize_input(priority) if priority is not None else None

            # Convert todo_id to UUID if it's a string
            try:
                todo_uuid = uuid.UUID(todo_id)
            except ValueError:
                raise ValidationError(f"Invalid todo ID: {todo_id}")

            # Get the existing task
            statement = select(Task).where(Task.id == todo_uuid, Task.user_id == user_id)
            task = self.session.exec(statement).first()

            if not task:
                raise UnauthorizedAccessException(f"Todo with ID {todo_id} not found or access denied")

            # Store original values for context comparison
            original_values = {
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "due_date": task.due_date,
                "priority": task.priority
            }

            # Update the task fields if provided
            if sanitized_title is not None:
                if not sanitized_title.strip():
                    raise ValidationError("Title cannot be empty")
                if len(sanitized_title) > 200:
                    raise ValidationError("Title cannot exceed 200 characters")

                # Context-aware: if title is being changed significantly, consider updating related fields
                task.title = sanitized_title.strip()

            if sanitized_description is not None:
                if len(sanitized_description) > 1000:
                    raise ValidationError("Description cannot exceed 1000 characters")
                task.description = sanitized_description.strip() if sanitized_description else None

            if completed is not None:
                # Context-aware: if marking as completed, update related context
                task.completed = completed

                # If task is being completed now, consider updating related context
                if completed and not original_values["completed"]:
                    # Task was just marked as complete
                    pass  # Could add completion tracking logic here
                elif not completed and original_values["completed"]:
                    # Task was unmarked as complete, revert any related actions
                    pass  # Could add logic to handle reverted completions

            if sanitized_due_date is not None:
                # Parse due date if provided
                parsed_due_date = None
                if sanitized_due_date:
                    try:
                        # Try to parse ISO format
                        parsed_due_date = datetime.fromisoformat(sanitized_due_date.replace('Z', '+00:00'))
                    except ValueError:
                        raise ValidationError("Due date must be in ISO format (YYYY-MM-DDTHH:MM:SS)")
                task.due_date = parsed_due_date

            if sanitized_priority is not None:
                if sanitized_priority not in ['low', 'medium', 'high']:
                    raise ValidationError("Priority must be 'low', 'medium', or 'high'")
                task.priority = sanitized_priority

            # Update timestamp
            task.updated_at = datetime.utcnow()

            # Commit changes
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "todo": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                },
                "context_changes_applied": self._analyze_context_changes(original_values, {
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "due_date": task.due_date,
                    "priority": task.priority
                })
            }
        except ValidationError:
            raise  # Re-raise validation errors
        except UnauthorizedAccessException:
            raise  # Re-raise authorization errors
        except Exception as e:
            raise Exception(f"Error updating todo: {str(e)}")

    def _analyze_context_changes(self, original: Dict, updated: Dict) -> List[str]:
        """
        Analyze what contextual changes were made to the todo.

        Args:
            original: Dictionary of original values
            updated: Dictionary of updated values

        Returns:
            List of context change descriptions
        """
        from typing import List  # Local import to avoid issues

        changes = []

        if original["title"] != updated["title"]:
            changes.append("title_updated")
        if original["description"] != updated["description"]:
            changes.append("description_updated")
        if original["completed"] != updated["completed"]:
            if updated["completed"]:
                changes.append("marked_as_complete")
            else:
                changes.append("marked_as_incomplete")
        if original["due_date"] != updated["due_date"]:
            changes.append("due_date_updated")
        if original["priority"] != updated["priority"]:
            changes.append("priority_updated")

        return changes

    def _validate_user_context(self, user_id: str) -> bool:
        """
        Validate that the user context is legitimate and the user has proper access rights.

        Args:
            user_id: ID of the user to validate

        Returns:
            True if user context is valid, False otherwise
        """
        try:
            # Validate user_id format
            user_uuid = uuid.UUID(user_id)

            # Comprehensive input validation
            if not user_id or not user_id.strip():
                raise ValidationError("User ID cannot be empty")

            # Check if user_id length is reasonable
            if len(user_id) > 100:
                raise ValidationError("User ID format is invalid")

            # In a real implementation, you would check against a users table:
            # from backend.src.models.user_model import User
            # user_record = self.session.exec(select(User).where(User.id == user_id)).first()
            # if not user_record:
            #     raise ValidationError("User does not exist")
            #
            # # Check user account status
            # if hasattr(user_record, 'disabled') and user_record.disabled:
            #     raise ValidationError("User account is disabled")

            # For this implementation, we'll just validate the format and assume user exists
            # A more robust implementation would include checks for:
            # - User account status (enabled/disabled)
            # - Account verification status
            # - Access level permissions
            # - Rate limiting based on user tier

            return True
        except ValueError:
            # Invalid UUID format
            raise ValidationError(f"Invalid user ID format: {user_id}")
        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            raise Exception(f"Error validating user context: {str(e)}")

    def _sanitize_input(self, input_text: str) -> str:
        """
        Sanitize user input to prevent injection attacks and other security issues.

        Args:
            input_text: Text to sanitize

        Returns:
            Sanitized text
        """
        if input_text is None:
            return None

        # Strip leading/trailing whitespace
        sanitized = input_text.strip()

        # Remove dangerous characters/sequences if needed
        # This is a basic implementation - in a real app, you might want more sophisticated sanitization

        # Block certain SQL injection patterns
        dangerous_patterns = [
            "DROP ", "DELETE ", "INSERT ", "UPDATE ", "SELECT ", "UNION ",
            "--", "/*", "*/", "xp_", "sp_"
        ]

        for pattern in dangerous_patterns:
            if pattern.upper() in sanitized.upper():
                raise ValidationError(f"Invalid input: contains forbidden pattern '{pattern}'")

        # Additional checks for potentially harmful input
        # Limit consecutive special characters to prevent regex attacks
        import re
        if re.search(r'[<>{}[\]\\^~]', sanitized) and len(re.findall(r'[<>{}[\]\\^~]', sanitized)) > 10:
            raise ValidationError("Input contains too many special characters")

        return sanitized

    def _validate_user_ownership(self, todo_id: str, user_id: str) -> bool:
        """
        Validate that the specified user owns the specified todo.

        Args:
            todo_id: ID of the todo to validate ownership for
            user_id: ID of the user claiming ownership

        Returns:
            True if user owns the todo, False otherwise
        """
        try:
            # Convert todo_id to UUID if it's a string
            try:
                todo_uuid = uuid.UUID(todo_id)
            except ValueError:
                raise ValidationError(f"Invalid todo ID: {todo_id}")

            # Check if the todo exists and belongs to the user
            statement = select(Task).where(Task.id == todo_uuid, Task.user_id == user_id)
            task = self.session.exec(statement).first()

            return task is not None
        except Exception as e:
            raise Exception(f"Error validating user ownership: {str(e)}")

    def delete_todo(self, user_id: str, todo_id: str) -> Dict[str, Any]:
        """
        Delete an existing todo item.

        Args:
            user_id: ID of the user deleting the todo
            todo_id: ID of the todo to delete

        Returns:
            Dictionary confirming deletion
        """
        try:
            # Validate user context first
            if not self._validate_user_context(user_id):
                raise UnauthorizedAccessException(f"Invalid user context for user_id: {user_id}")

            # Validate user ownership of the todo
            if not self._validate_user_ownership(todo_id, user_id):
                raise UnauthorizedAccessException(f"Todo with ID {todo_id} not found or access denied")

            # Convert todo_id to UUID if it's a string
            try:
                todo_uuid = uuid.UUID(todo_id)
            except ValueError:
                raise ValidationError(f"Invalid todo ID: {todo_id}")

            # Get the existing task
            statement = select(Task).where(Task.id == todo_uuid, Task.user_id == user_id)
            task = self.session.exec(statement).first()

            if not task:
                raise UnauthorizedAccessException(f"Todo with ID {todo_id} not found or access denied")

            # Delete the task
            self.session.delete(task)
            self.session.commit()

            return {
                "success": True,
                "message": f"Todo {todo_id} deleted successfully"
            }
        except ValidationError:
            raise  # Re-raise validation errors
        except UnauthorizedAccessException:
            raise  # Re-raise authorization errors
        except Exception as e:
            raise Exception(f"Error deleting todo: {str(e)}")

    def add_note_attachment(self, user_id: str, todo_id: str, note_title: str, note_content: str) -> Dict[str, Any]:
        """
        Attach a note to an existing todo item. This enhances the todo with additional
        context, details, or comments.

        Args:
            user_id: ID of the user attaching the note
            todo_id: ID of the todo to attach the note to
            note_title: Title of the note
            note_content: Content of the note

        Returns:
            Dictionary containing the updated todo with note information
        """
        try:
            # Validate user context first
            if not self._validate_user_context(user_id):
                raise UnauthorizedAccessException(f"Invalid user context for user_id: {user_id}")

            # Validate user ownership of the todo
            if not self._validate_user_ownership(todo_id, user_id):
                raise UnauthorizedAccessException(f"Todo with ID {todo_id} not found or access denied")

            # Validate inputs
            if not note_title or not note_title.strip():
                raise ValidationError("Note title cannot be empty")

            if len(note_title) > 200:
                raise ValidationError("Note title cannot exceed 200 characters")

            if not note_content or not note_content.strip():
                raise ValidationError("Note content cannot be empty")

            if len(note_content) > 5000:  # Reasonable limit for note content
                raise ValidationError("Note content cannot exceed 5000 characters")

            # Get the existing task to verify ownership and existence
            statement = select(Task).where(Task.id == uuid.UUID(todo_id), Task.user_id == user_id)
            task = self.session.exec(statement).first()

            if not task:
                raise UnauthorizedAccessException(f"Todo with ID {todo_id} not found or access denied")

            # Append the note to the existing description, or create a new one
            # In a more advanced implementation, you might want to create a separate notes table
            # For now, we'll append the note to the description field
            current_description = task.description or ""

            # Format the new note with a clear separator and timestamp
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            note_separator = "\n---\n" if current_description.strip() else ""
            new_note = f"{note_separator}[Note: {note_title}]({timestamp})\n{note_content}"

            # Combine existing description with the new note
            updated_description = current_description + new_note

            # Validate the new combined description length
            if len(updated_description) > 1000:  # Max length for description
                raise ValidationError("Combined description and notes exceed 1000 characters. Please shorten your note.")

            # Update the task with the new description containing the note
            task.description = updated_description
            task.updated_at = datetime.utcnow()

            # Commit the changes
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            # Return the updated task
            return {
                "success": True,
                "todo": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
            }
        except ValidationError:
            raise  # Re-raise validation errors
        except UnauthorizedAccessException:
            raise  # Re-raise unauthorized access errors
        except Exception as e:
            raise Exception(f"Error adding note attachment: {str(e)}")

    def create_reminder(self, user_id: str, title: str, description: Optional[str] = None,
                        due_date: Optional[str] = None, priority: Optional[str] = "medium") -> Dict[str, Any]:
        """
        Create a reminder (todo with a due date and reminder flag).

        Args:
            user_id: ID of the user creating the reminder
            title: Title of the reminder
            description: Optional description of the reminder
            due_date: Due date for the reminder (ISO format string)
            priority: Priority level ('low', 'medium', 'high')

        Returns:
            Dictionary containing the created reminder
        """
        try:
            # Validate user context first
            if not self._validate_user_context(user_id):
                raise UnauthorizedAccessException(f"Invalid user context for user_id: {user_id}")

            # Sanitize inputs
            sanitized_title = self._sanitize_input(title) if title else None
            sanitized_description = self._sanitize_input(description) if description else None
            sanitized_due_date = self._sanitize_input(due_date) if due_date else None
            sanitized_priority = self._sanitize_input(priority) if priority else None

            # Validate inputs
            if not sanitized_title or not sanitized_title.strip():
                raise ValidationError("Title is required and cannot be empty")

            if len(sanitized_title) > 200:  # Assuming max length from data model
                raise ValidationError("Title cannot exceed 200 characters")

            if sanitized_description and len(sanitized_description) > 1000:  # Assuming max length from data model
                raise ValidationError("Description cannot exceed 1000 characters")

            if sanitized_priority and sanitized_priority not in ['low', 'medium', 'high']:
                raise ValidationError("Priority must be 'low', 'medium', or 'high'")

            # Parse due date if provided
            parsed_due_date = None
            if sanitized_due_date:
                try:
                    # Try to parse ISO format
                    parsed_due_date = datetime.fromisoformat(sanitized_due_date.replace('Z', '+00:00'))
                except ValueError:
                    raise ValidationError("Due date must be in ISO format (YYYY-MM-DDTHH:MM:SS)")

            # Create a new task with reminder characteristics
            task = Task(
                user_id=user_id,
                title=sanitized_title.strip(),
                description=sanitized_description.strip() if sanitized_description else None,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                due_date=parsed_due_date,
                priority=sanitized_priority or "medium"
            )

            # Add to session and commit
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            # Return the created task
            return {
                "success": True,
                "reminder": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                }
            }
        except ValidationError:
            raise  # Re-raise validation errors
        except UnauthorizedAccessException:
            raise  # Re-raise authorization errors
        except Exception as e:
            raise Exception(f"Error creating reminder: {str(e)}")

    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get context information about the user.

        Args:
            user_id: ID of the user to get context for

        Returns:
            Dictionary containing user context information
        """
        try:
            # This would fetch user preferences, settings, and other context info
            # For now, returning a comprehensive context structure
            return {
                "user_id": user_id,
                "context": {
                    "recent_activity_summary": self._get_recent_activity_summary(user_id),
                    "common_todo_patterns": self._get_common_todo_patterns(user_id),
                    "preferences": self._get_user_preferences(user_id),
                    "reminder_stats": self._get_reminder_statistics(user_id)
                }
            }
        except Exception as e:
            raise Exception(f"Error getting user context: {str(e)}")

    def _get_reminder_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about user's reminders (tasks with due dates).

        Args:
            user_id: ID of the user to analyze

        Returns:
            Dictionary with reminder statistics
        """
        # Get all tasks for the user
        statement = select(Task).where(Task.user_id == user_id)
        all_tasks = self.session.exec(statement).all()

        # Separate tasks with and without due dates
        tasks_with_due_dates = [task for task in all_tasks if task.due_date is not None]
        overdue_tasks = [task for task in tasks_with_due_dates
                        if task.due_date and task.due_date < datetime.utcnow() and not task.completed]
        upcoming_tasks = [task for task in tasks_with_due_dates
                         if task.due_date and task.due_date >= datetime.utcnow() and not task.completed]

        return {
            "total_tasks": len(all_tasks),
            "tasks_with_due_dates": len(tasks_with_due_dates),
            "overdue_reminders": len(overdue_tasks),
            "upcoming_reminders": len(upcoming_tasks),
            "completed_reminders": len([task for task in tasks_with_due_dates if task.completed])
        }

    def _get_recent_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of the user's recent todo activity.

        Args:
            user_id: ID of the user to get activity for

        Returns:
            Dictionary with activity summary
        """
        # Get count of recent todos
        from datetime import timedelta
        recent_date = datetime.utcnow() - timedelta(days=7)

        statement = select(Task).where(
            Task.user_id == user_id,
            Task.created_at >= recent_date
        )
        recent_tasks = self.session.exec(statement).all()

        completed_recently = [task for task in recent_tasks if task.completed]
        pending_tasks = [task for task in recent_tasks if not task.completed]

        return {
            "recent_tasks_added": len(recent_tasks),
            "recently_completed": len(completed_recently),
            "pending_tasks": len(pending_tasks)
        }

    def _get_common_todo_patterns(self, user_id: str) -> List[str]:
        """
        Get common patterns in the user's todo creation habits.

        Args:
            user_id: ID of the user to analyze

        Returns:
            List of common patterns or topics
        """
        # Get all tasks for the user
        statement = select(Task).where(Task.user_id == user_id)
        all_tasks = self.session.exec(statement).all()

        # Analyze common keywords in titles/descriptions
        keywords = {}
        for task in all_tasks:
            text = (task.title + " " + (task.description or "")).lower()
            words = text.split()
            for word in words:
                # Filter out common stop words and short words
                if len(word) > 3 and word not in ["the", "and", "for", "with", "from", "that", "have", "they", "this", "had"]:
                    keywords[word] = keywords.get(word, 0) + 1

        # Return top 5 most common keywords
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [keyword for keyword, _ in sorted_keywords[:5]]

    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences related to todo management.

        Args:
            user_id: ID of the user to get preferences for

        Returns:
            Dictionary with user preferences
        """
        # In a real implementation, this would fetch from a user preferences table
        # For now, returning defaults
        return {
            "preferred_communication_style": "direct",
            "preferred_response_length": "concise",
            "common_working_hours": ["09:00", "17:00"],
            "notification_preferences": {
                "email": False,
                "push": True
            }
        }