"""
TaskValidator class - Handles validation rules for task operations.
This validator follows the single responsibility principle for task-related validation.
"""

from typing import Any, Dict, List, Tuple, Optional
from backend.validation.base_validator import BaseValidator, ValidationError


class TaskValidator(BaseValidator):
    """
    Validator class for task-related operations.
    Validates task creation, updates, and other task-specific operations.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize the TaskValidator.

        Args:
            schema: Optional validation schema definition for tasks
        """
        # Define default schema if not provided
        if schema is None:
            schema = {
                "required": ["title"],
                "fields": {
                    "title": {
                        "type": str,
                        "min_length": 1,
                        "max_length": 200,
                        "required": True
                    },
                    "description": {
                        "type": str,
                        "max_length": 1000
                    },
                    "completed": {
                        "type": bool
                    },
                    "priority": {
                        "type": str,
                        "allowed_values": ["low", "medium", "high", "critical"],
                        "default": "medium"
                    },
                    "due_date": {
                        "type": str  # Would be validated as ISO date string in real implementation
                    }
                }
            }

        super().__init__(schema)

    def custom_validate(self, data: Dict[str, Any]) -> bool:
        """
        Custom validation logic specific to task operations.

        Args:
            data: Data to validate

        Returns:
            True if data is valid, False otherwise
        """
        is_valid = True

        # Validate title if present
        if "title" in data:
            title = data["title"]
            if not isinstance(title, str):
                self.add_error("Title must be a string", "title", title)
                is_valid = False
            elif len(title) < 1 or len(title) > 200:
                self.add_error("Title must be between 1 and 200 characters", "title", title)
                is_valid = False
            elif title.strip() == "":
                self.add_error("Title cannot be empty or whitespace only", "title", title)
                is_valid = False

        # Validate description if present
        if "description" in data:
            description = data["description"]
            if description is not None and not isinstance(description, str):
                self.add_error("Description must be a string", "description", description)
                is_valid = False
            elif description is not None and len(description) > 1000:
                self.add_error("Description cannot exceed 1000 characters", "description", description)
                is_valid = False

        # Validate completed if present
        if "completed" in data:
            completed = data["completed"]
            if not isinstance(completed, bool):
                self.add_error("Completed status must be a boolean", "completed", completed)
                is_valid = False

        # Validate priority if present
        if "priority" in data:
            priority = data["priority"]
            if priority is not None and priority not in ["low", "medium", "high", "critical"]:
                self.add_error("Priority must be one of: low, medium, high, critical", "priority", priority)
                is_valid = False

        # Validate due date if present (basic format check)
        if "due_date" in data:
            due_date = data["due_date"]
            if due_date is not None:
                if not isinstance(due_date, str):
                    self.add_error("Due date must be a string in ISO format", "due_date", due_date)
                    is_valid = False
                # In a real implementation, we would validate the ISO date format here

        # Validate user_id if present
        if "user_id" in data:
            user_id = data["user_id"]
            if not isinstance(user_id, str) or len(user_id) == 0:
                self.add_error("User ID must be a non-empty string", "user_id", user_id)
                is_valid = False

        # Validate task_id if present
        if "task_id" in data:
            task_id = data["task_id"]
            if not isinstance(task_id, str) or len(task_id) == 0:
                self.add_error("Task ID must be a non-empty string", "task_id", task_id)
                is_valid = False

        return is_valid

    def validate_task_creation(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Specific validation for task creation operations.

        Args:
            data: Task creation data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        # For task creation, ensure title is provided
        required_fields = ["title"]

        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == ""):
                self.add_error(f"Field '{field}' is required for task creation", field, data.get(field))

        # Run general validation
        return self.validate(data)

    def validate_task_update(self, data: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Specific validation for task update operations.

        Args:
            data: Task update data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        # For task updates, at least one field must be provided for update
        update_fields = ["title", "description", "completed", "priority", "due_date"]
        has_update_field = any(field in data for field in update_fields)

        if not has_update_field:
            self.add_error("At least one field must be provided for update", "update_fields", data)

        # Run general validation
        return self.validate(data)

    def validate_bulk_task_operations(self, tasks_data: List[Dict[str, Any]]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate data for bulk task operations.

        Args:
            tasks_data: List of task data dictionaries to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not isinstance(tasks_data, list):
            self.add_error("Bulk operations data must be a list", "tasks_data", tasks_data)
            return False, self.get_errors()

        if len(tasks_data) == 0:
            self.add_error("Bulk operations must include at least one task", "tasks_data", tasks_data)
            return False, self.get_errors()

        if len(tasks_data) > 100:  # Arbitrary limit
            self.add_error("Bulk operations are limited to 100 tasks at a time", "tasks_data", tasks_data)
            return False, self.get_errors()

        # Validate each task individually
        all_valid = True
        for i, task_data in enumerate(tasks_data):
            if not isinstance(task_data, dict):
                self.add_error(f"Task at index {i} must be a dictionary", f"tasks_data[{i}]", task_data)
                all_valid = False
                continue

            # Validate the individual task data
            task_valid, task_errors = self.validate(task_data)
            if not task_valid:
                # Add index context to the errors
                for error in task_errors:
                    error.field = f"tasks_data[{i}].{error.field}" if error.field else f"tasks_data[{i}]"
                    self.errors.append(error)
                all_valid = False

        return all_valid, self.get_errors()

    def validate_task_priority(self, priority: str) -> bool:
        """
        Validate a task priority value.

        Args:
            priority: Priority value to validate

        Returns:
            True if priority is valid, False otherwise
        """
        return priority in ["low", "medium", "high", "critical"]

    def validate_task_title(self, title: str) -> bool:
        """
        Validate a task title.

        Args:
            title: Title to validate

        Returns:
            True if title is valid, False otherwise
        """
        if not isinstance(title, str):
            return False

        return 1 <= len(title) <= 200 and title.strip() != ""

    def validate_task_description(self, description: str) -> bool:
        """
        Validate a task description.

        Args:
            description: Description to validate

        Returns:
            True if description is valid, False otherwise
        """
        if description is None:
            return True  # Description is optional

        if not isinstance(description, str):
            return False

        return len(description) <= 1000

    def validate_task_filters(self, filters: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """
        Validate filters for task queries.

        Args:
            filters: Filters to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        valid_filters = {"completed", "priority", "due_date", "search", "limit", "offset"}
        invalid_filters = set(filters.keys()) - valid_filters

        for invalid_filter in invalid_filters:
            self.add_error(f"Invalid filter: {invalid_filter}", invalid_filter, filters.get(invalid_filter))

        # Validate individual filter values
        if "completed" in filters:
            completed = filters["completed"]
            if completed is not None and not isinstance(completed, bool):
                self.add_error("Filter 'completed' must be a boolean", "completed", completed)

        if "priority" in filters:
            priority = filters["priority"]
            if priority is not None and not self.validate_task_priority(priority):
                self.add_error("Filter 'priority' must be one of: low, medium, high, critical", "priority", priority)

        if "limit" in filters:
            limit = filters["limit"]
            if not isinstance(limit, int) or limit <= 0:
                self.add_error("Filter 'limit' must be a positive integer", "limit", limit)

        if "offset" in filters:
            offset = filters["offset"]
            if not isinstance(offset, int) or offset < 0:
                self.add_error("Filter 'offset' must be a non-negative integer", "offset", offset)

        return len(self.errors) == 0, self.get_errors()

    def validate_task_pagination(self, limit: int, offset: int) -> Tuple[bool, List[ValidationError]]:
        """
        Validate pagination parameters for task queries.

        Args:
            limit: Number of items per page
            offset: Offset for pagination

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not isinstance(limit, int) or limit <= 0:
            self.add_error("Limit must be a positive integer", "limit", limit)

        if not isinstance(offset, int) or offset < 0:
            self.add_error("Offset must be a non-negative integer", "offset", offset)

        if limit > 100:  # Reasonable limit to prevent excessive data retrieval
            self.add_error("Limit cannot exceed 100", "limit", limit)

        return len(self.errors) == 0, self.get_errors()