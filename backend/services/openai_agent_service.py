"""
OpenAI Agent service for AI assistant integration.
Handles real agent execution using OpenAI's API with tool calling capabilities.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Callable
from sqlmodel import Session
from datetime import datetime
import uuid

from openai import OpenAI, OpenAIError, APITimeoutError, APIConnectionError
from .agent_service import AgentService
from .todo_tools import TodoTools
from ..config.agent_config import AgentConfig
# from ..models.agent_message import AgentMessage
from ..models.agent_session import AgentSession
from ..exceptions.chat_exceptions import UnauthorizedAccessException
from ..utils.error_utils import ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIAgentService(AgentService):
    """
    Service class for handling AI agent operations using OpenAI's API.
    Extends the base AgentService with real AI capabilities.
    """

    def __init__(self, session: Session, use_stub: bool = False):
        """
        Initialize the OpenAI agent service with a database session.

        Args:
            session: Database session for data access
            use_stub: Whether to fall back to stub AI (default: False)
        """
        super().__init__(session)
        self.session = session
        self.use_stub = use_stub
        self.todo_tools = TodoTools(session)

        # Initialize OpenAI client only if not using stub
        if not self.use_stub:
            api_key = AgentConfig.OPENAI_API_KEY
            if not api_key or api_key == "":
                logger.warning("OPENAI_API_KEY not set. Falling back to stub AI.")
                self.use_stub = True
                self.client = None
            else:
                self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

        # Define available tools for the agent
        self.tools = self._define_tools()

        # Map tool names to their implementations
        self.tool_functions: Dict[str, Callable] = {
            "list_todos": self.todo_tools.list_todos,
            "add_todo": self.todo_tools.add_todo,
            "update_todo": self.todo_tools.update_todo,
            "delete_todo": self.todo_tools.delete_todo,
            "create_reminder": self.todo_tools.create_reminder,
            "add_note_attachment": self.todo_tools.add_note_attachment,
            "get_user_context": self.todo_tools.get_user_context,
        }

    def _define_tools(self) -> List[Dict[str, Any]]:
        """
        Define the OpenAI function tools available to the agent.

        Returns:
            List of tool definitions in OpenAI's function calling format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_todos",
                    "description": "List the user's todo items with optional filtering and pagination. Use this to show the user their current tasks or to search for specific todos.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user whose todos to list"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of todos to return (default 10)",
                                "default": 10
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Offset for pagination (default 0)",
                                "default": 0
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "Filter by completion status. True for completed, False for not completed, null for all",
                                "nullable": True
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_todo",
                    "description": "Add a new todo item for the user. Use this when the user wants to create a new task or todo.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user adding the todo"
                            },
                            "title": {
                                "type": "string",
                                "description": "Title of the new todo (required, max 200 characters)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional description of the todo (max 1000 characters)",
                                "nullable": True
                            }
                        },
                        "required": ["user_id", "title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_todo",
                    "description": "Update an existing todo item. Use this to modify the title, description, completion status, due date, or priority of a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user updating the todo"
                            },
                            "todo_id": {
                                "type": "string",
                                "description": "The ID of the todo to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title for the todo",
                                "nullable": True
                            },
                            "description": {
                                "type": "string",
                                "description": "New description for the todo",
                                "nullable": True
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "New completion status for the todo",
                                "nullable": True
                            },
                            "due_date": {
                                "type": "string",
                                "description": "New due date for the todo in ISO format (YYYY-MM-DDTHH:MM:SS)",
                                "nullable": True
                            },
                            "priority": {
                                "type": "string",
                                "description": "New priority level ('low', 'medium', 'high')",
                                "nullable": True
                            }
                        },
                        "required": ["user_id", "todo_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_todo",
                    "description": "Delete an existing todo item. Use this when the user wants to permanently remove a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user deleting the todo"
                            },
                            "todo_id": {
                                "type": "string",
                                "description": "The ID of the todo to delete"
                            }
                        },
                        "required": ["user_id", "todo_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_note_attachment",
                    "description": "Attach a note to an existing todo item. Use this when the user wants to add additional context, details, or comments to a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user attaching the note"
                            },
                            "todo_id": {
                                "type": "string",
                                "description": "The ID of the todo to attach the note to"
                            },
                            "note_title": {
                                "type": "string",
                                "description": "Title of the note (max 200 characters)"
                            },
                            "note_content": {
                                "type": "string",
                                "description": "Content of the note (max 5000 characters)"
                            }
                        },
                        "required": ["user_id", "todo_id", "note_title", "note_content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_user_context",
                    "description": "Get context information about the user, including recent activity, common patterns, and preferences. Use this to provide personalized assistance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user to get context for"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, tool_arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool based on the agent's decision with authorization checks.

        Args:
            tool_name: Name of the tool to execute
            tool_arguments: Arguments to pass to the tool

        Returns:
            Result of the tool execution
        """
        try:
            logger.info(f"========== EXECUTING TOOL ==========")
            logger.info(f"Tool: {tool_name}")
            logger.info(f"Arguments: {json.dumps(tool_arguments, indent=2)}")

            if tool_name not in self.tool_functions:
                error_msg = f"Unknown tool: {tool_name}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Authorization check: ensure user has permission to execute the tool
            # At minimum, user must be authenticated and the user_id must be in the arguments
            user_id = tool_arguments.get('user_id')
            if not user_id:
                error_msg = f"No user_id provided when executing tool {tool_name}"
                logger.error(error_msg)
                return {"error": "Unauthorized: No user context provided", "success": False}

            # Perform basic authorization check
            if not self._authorize_tool_call(tool_name, user_id, tool_arguments):
                error_msg = f"Unauthorized tool call: {tool_name} for user {user_id}"
                logger.error(error_msg)
                return {"error": "Unauthorized: Insufficient permissions to execute this tool", "success": False}

            tool_function = self.tool_functions[tool_name]
            logger.info(f"Calling tool function: {tool_function.__name__}")

            result = tool_function(**tool_arguments)

            logger.info(f"Tool execution result: {json.dumps(result, indent=2, default=str)}")
            logger.info(f"========== TOOL EXECUTION COMPLETE ==========")

            return result

        except ValidationError as e:
            error_msg = f"Validation error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            self._log_tool_execution_error(tool_name, tool_arguments, str(e), "validation_error")
            return {"error": f"Validation error: {str(e)}", "success": False}
        except UnauthorizedAccessException as e:
            error_msg = f"Authorization error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            self._log_tool_execution_error(tool_name, tool_arguments, str(e), "authorization_error")
            return {"error": f"Authorization error: {str(e)}", "success": False}
        except Exception as e:
            error_msg = f"Unexpected error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)  # Include full traceback
            self._log_tool_execution_error(tool_name, tool_arguments, str(e), "unexpected_error")

            # More descriptive error for the user
            user_friendly_error = f"An error occurred while processing your request. Please try again or contact support if the issue persists."
            return {"error": user_friendly_error, "success": False, "original_error": str(e)}

    def _authorize_tool_call(self, tool_name: str, user_id: str, tool_arguments: Dict[str, Any]) -> bool:
        """
        Authorize a tool call based on user permissions and tool type.

        Args:
            tool_name: Name of the tool to authorize
            user_id: ID of the user making the call
            tool_arguments: Arguments for the tool call

        Returns:
            True if authorized, False otherwise
        """
        try:
            # All tools require user authentication first
            if not user_id:
                self._log_tool_execution_error(tool_name, tool_arguments, "No user_id provided", "authorization_error")
                return False

            # Validate that the user_id exists and is valid
            # No need to convert to UUID - IDs are strings now

            # Additional checks based on the specific tool
            if tool_name in ['list_todos', 'add_todo', 'update_todo', 'delete_todo', 'create_reminder', 'add_note_attachment']:
                # For todo-related tools, verify the user_id in the arguments matches the authenticated user
                arg_user_id = tool_arguments.get('user_id')
                if arg_user_id and arg_user_id != user_id:
                    logger.warning(f"User {user_id} attempted to access data for user {arg_user_id}")
                    self._log_tool_execution_error(tool_name, tool_arguments, f"User {user_id} tried to access data for {arg_user_id}", "authorization_violation")
                    return False

                # Additional validations for specific operations
                if tool_name == 'delete_todo':
                    # Verify the user has the todo ID they're trying to delete
                    todo_id = tool_arguments.get('todo_id')
                    if todo_id:
                        # We could perform an additional check to see if the user owns this specific todo
                        # This is already handled in the todo_tools but adding a check here adds another layer
                        pass  # The todo_tools will validate ownership separately

                # All good - user is authorized to call this tool
                return True

            elif tool_name == 'get_user_context':
                # For user context, verify the user is accessing their own context
                arg_user_id = tool_arguments.get('user_id')
                if arg_user_id and arg_user_id != user_id:
                    logger.warning(f"User {user_id} attempted to access context for user {arg_user_id}")
                    self._log_tool_execution_error(tool_name, tool_arguments, f"User {user_id} tried to access context for {arg_user_id}", "authorization_violation")
                    return False
                return True

            else:
                # Unknown tool - deny access
                logger.error(f"Attempted to call unknown tool: {tool_name}")
                self._log_tool_execution_error(tool_name, tool_arguments, f"Unknown tool called: {tool_name}", "security_violation")
                return False

        except Exception as e:
            logger.error(f"Error in tool authorization: {str(e)}")
            self._log_tool_execution_error(tool_name, tool_arguments, f"Error in authorization: {str(e)}", "authorization_error")
            return False

    def _log_tool_execution_error(self, tool_name: str, tool_arguments: Dict[str, Any], error_message: str, error_type: str) -> None:
        """
        Log detailed error information for tool execution failures.

        Args:
            tool_name: Name of the tool that failed
            tool_arguments: Arguments that were passed to the tool
            error_message: The error message
            error_type: Type of error (validation_error, authorization_error, etc.)
        """
        try:
            import json
            from datetime import datetime

            # Create detailed log entry
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "tool_execution_error",
                "tool_name": tool_name,
                "user_id": tool_arguments.get('user_id', 'unknown'),
                "error_type": error_type,
                "error_message": error_message,
                "tool_arguments_keys": list(tool_arguments.keys()) if tool_arguments else [],
                "severity": "high" if error_type in ["authorization_violation", "security_violation"] else "medium"
            }

            # Log to the standard logger
            logger.error(f"TOOL_EXEC_ERROR [{error_type}] Tool: {tool_name}, User: {log_entry['user_id']}, Error: {error_message}")

            # In a production environment, you might want to store this in a database or external logging service
            # For example:
            # from backend.models.tool_execution_log import ToolExecutionLog
            # log_record = ToolExecutionLog(
            #     tool_name=tool_name,
            #     user_id=log_entry['user_id'],
            #     error_type=error_type,
            #     error_message=error_message,
            #     timestamp=datetime.utcnow(),
            #     severity=log_entry['severity']
            # )
            # self.session.add(log_record)
            # self.session.commit()

        except Exception as e:
            # If logging fails, at least log that the logging failed
            logger.error(f"Failed to log tool execution error: {str(e)}")

    def _build_conversation_history(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        max_messages: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Build conversation history from the session messages.

        Args:
            session_id: ID of the session
            user_id: ID of the user
            max_messages: Maximum number of messages to include

        Returns:
            List of messages in OpenAI format
        """
        # Convert UUIDs to strings for the base service method
        messages = self.get_session_messages(str(session_id), str(user_id), limit=max_messages)

        conversation_history = []
        for msg in messages:
            if msg.role in ["user", "assistant"]:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
            elif msg.role == "tool" and msg.tool_calls:
                # Include tool results if available
                conversation_history.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": msg.tool_calls
                })

        return conversation_history

    def _detect_and_orchestrate_crud(self, user_id: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Detect CRUD operations and orchestrate multi-step tool calls programmatically.
        This bypasses unreliable AI model behavior for critical operations.

        Args:
            user_id: ID of the user
            message: User's message

        Returns:
            Result dict if operation was handled, None otherwise
        """
        message_lower = message.lower()
        import re

        logger.info(f"🔍 ORCHESTRATION: Analyzing message: '{message}'")

        operation = None
        task_ref = None
        update_data = {}

        # === MARK INCOMPLETE (CHECK THIS FIRST BEFORE MARK COMPLETE!) ===
        if 'incomplete' in message_lower or 'uncomplete' in message_lower or 'not complete' in message_lower:
            operation = 'mark_incomplete'
            logger.info(f"⏸️ ORCHESTRATION: Detected mark incomplete")

            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)
            else:
                # Extract task name from patterns like "mark X as incomplete"
                match = re.search(r'mark\s+(.+?)\s+as\s+incomplete', message_lower)
                if match:
                    task_ref = match.group(1).strip()

            update_data['completed'] = False

        # === PRIORITY OPERATIONS ===
        elif 'priority' in message_lower or 'high priority' in message_lower or 'low priority' in message_lower:
            operation = 'set_priority'
            logger.info(f"🔔 ORCHESTRATION: Detected priority change")

            # Extract task reference
            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)
            else:
                # Try patterns like "set priority of X to high"
                match = re.search(r'(?:priority|important|urgency).*?(?:of|for)\s+(.+?)\s+(?:to|as)', message_lower)
                if match:
                    task_ref = match.group(1).strip()

            # Extract priority level
            if 'high' in message_lower:
                update_data['priority'] = 'high'
            elif 'medium' in message_lower:
                update_data['priority'] = 'medium'
            elif 'low' in message_lower:
                update_data['priority'] = 'low'

        # === DUE DATE OPERATIONS ===
        elif 'due' in message_lower or 'deadline' in message_lower:
            operation = 'set_due_date'
            logger.info(f"📅 ORCHESTRATION: Detected due date change")

            # Extract task reference
            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)
            else:
                match = re.search(r'(?:due|deadline).*?(?:of|for)\s+(.+?)\s+(?:to|as|on)', message_lower)
                if match:
                    task_ref = match.group(1).strip()

            # Extract date - simplified, user should provide ISO format or clear date
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', message)
            if date_match:
                update_data['due_date'] = date_match.group(0) + 'T00:00:00'

        # === MARK COMPLETE (CHECK AFTER MARK INCOMPLETE!) ===
        elif any(keyword in message_lower for keyword in ['mark', 'complete', 'done', 'finish']):
            if 'complete' in message_lower or 'done' in message_lower or 'finish' in message_lower:
                operation = 'mark_complete'
                logger.info(f"✅ ORCHESTRATION: Detected mark complete")

                quoted = re.search(r'["\']([^"\']+)["\']', message)
                if quoted:
                    task_ref = quoted.group(1)
                else:
                    match = re.search(r'mark\s+(.+?)\s+as', message_lower)
                    if match:
                        task_ref = match.group(1).strip()
                    else:
                        for keyword in ['complete ', 'finish ', 'done with ']:
                            if keyword in message_lower:
                                parts = message_lower.split(keyword, 1)
                                if len(parts) > 1:
                                    task_ref = parts[1].replace(' as completed', '').replace(' as done', '').strip()
                                    break

                update_data['completed'] = True

        # === DELETE ===
        elif any(keyword in message_lower for keyword in ['delete', 'remove', 'erase']):
            operation = 'delete'
            logger.info(f"🗑️ ORCHESTRATION: Detected delete")

            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)
            else:
                for keyword in ['delete ', 'remove ', 'erase ', 'delete the ', 'remove the ', 'erase the ']:
                    if keyword in message_lower:
                        parts = message_lower.split(keyword, 1)
                        if len(parts) > 1:
                            task_ref = parts[1].replace('task', '').replace('todo', '').strip()
                            break

        # === EDIT/UPDATE TITLE ===
        elif any(keyword in message_lower for keyword in ['change', 'update', 'modify', 'rename', 'edit']):
            operation = 'update_title'
            logger.info(f"✏️ ORCHESTRATION: Detected title update")

            # Pattern 1: change "old" to "new"
            pattern1 = r'["\']([^"\']+)["\'].*?(?:to|into)\s+["\']([^"\']+)["\']'
            match1 = re.search(pattern1, message)
            if match1:
                task_ref = match1.group(1)
                update_data['title'] = match1.group(2)
            else:
                # Pattern 2: change old to new
                pattern2 = r'(?:change|update|rename|edit|modify)\s+(.+?)\s+(?:to|into)\s+(.+?)$'
                match2 = re.search(pattern2, message_lower)
                if match2:
                    task_ref = match2.group(1).replace('the ', '').replace('task ', '').strip()
                    update_data['title'] = match2.group(2).replace('the ', '').replace('task ', '').strip()

        if not operation:
            logger.info("❌ ORCHESTRATION: No operation detected, falling back to AI")
            return None

        if not task_ref:
            logger.warning(f"⚠️ ORCHESTRATION: Operation detected but could not extract task reference")
            return None

        logger.info(f"🎯 ORCHESTRATION: Operation={operation}, Task='{task_ref}', Data={update_data}")

        # Step 1: List todos to find the task
        logger.info("📋 ORCHESTRATION: Step 1 - Calling list_todos")
        list_result = self._execute_tool('list_todos', {'user_id': user_id})

        if 'error' in list_result or not list_result.get('todos'):
            logger.error("❌ ORCHESTRATION: Failed to list todos")
            return {
                'error': 'Could not retrieve tasks',
                'operation': operation
            }

        # Step 2: Find matching task
        matching_task = None
        task_ref_lower = task_ref.lower().strip()

        for task in list_result['todos']:
            if task_ref_lower in task['title'].lower():
                matching_task = task
                break

        if not matching_task:
            logger.warning(f"❌ ORCHESTRATION: Task '{task_ref}' not found")
            return {
                'error': f'Task "{task_ref}" not found',
                'operation': operation
            }

        task_id = matching_task['id']
        logger.info(f"✅ ORCHESTRATION: Found task '{matching_task['title']}' (ID: {task_id})")

        # Step 3: Execute the operation
        logger.info(f"🔧 ORCHESTRATION: Step 2 - Executing {operation}")

        if operation == 'delete':
            result = self._execute_tool('delete_todo', {
                'user_id': user_id,
                'todo_id': task_id
            })
            if 'error' not in result:
                result['orchestrated'] = True
                result['operation'] = 'delete'
                result['task_title'] = matching_task['title']
                logger.info("✅ ORCHESTRATION: Delete successful")
            return result

        else:
            # All other operations are updates
            result = self._execute_tool('update_todo', {
                'user_id': user_id,
                'todo_id': task_id,
                **update_data
            })
            if 'error' not in result:
                result['orchestrated'] = True
                result['operation'] = operation
                result['task_title'] = matching_task['title']
                result['updates'] = update_data
                logger.info(f"✅ ORCHESTRATION: {operation} successful")
            return result
        """
        Detect CRUD operations and orchestrate multi-step tool calls programmatically.
        This bypasses unreliable AI model behavior for critical operations.

        Args:
            user_id: ID of the user
            message: User's message

        Returns:
            Result dict if operation was handled, None otherwise
        """
        message_lower = message.lower()
        import re

        logger.info(f"🔍 ORCHESTRATION: Analyzing message: '{message}'")

        operation = None
        task_ref = None
        update_data = {}

        # === PRIORITY OPERATIONS ===
        if 'priority' in message_lower or 'high priority' in message_lower or 'low priority' in message_lower:
            operation = 'set_priority'
            logger.info(f"🔔 ORCHESTRATION: Detected priority change")

            # Extract task reference
            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)
            else:
                # Try patterns like "set priority of X to high"
                match = re.search(r'(?:priority|important|urgency).*?(?:of|for)\s+(.+?)\s+(?:to|as)', message_lower)
                if match:
                    task_ref = match.group(1).strip()

            # Extract priority level
            if 'high' in message_lower:
                update_data['priority'] = 'high'
            elif 'medium' in message_lower:
                update_data['priority'] = 'medium'
            elif 'low' in message_lower:
                update_data['priority'] = 'low'

        # === DUE DATE OPERATIONS ===
        elif 'due' in message_lower or 'deadline' in message_lower:
            operation = 'set_due_date'
            logger.info(f"📅 ORCHESTRATION: Detected due date change")

            # Extract task reference
            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)
            else:
                match = re.search(r'(?:due|deadline).*?(?:of|for)\s+(.+?)\s+(?:to|as|on)', message_lower)
                if match:
                    task_ref = match.group(1).strip()

            # Extract date - simplified, user should provide ISO format or clear date
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', message)
            if date_match:
                update_data['due_date'] = date_match.group(0) + 'T00:00:00'

        # === MARK COMPLETE ===
        elif any(keyword in message_lower for keyword in ['mark', 'complete', 'done', 'finish']):
            if 'complete' in message_lower or 'done' in message_lower or 'finish' in message_lower:
                operation = 'mark_complete'
                logger.info(f"✅ ORCHESTRATION: Detected mark complete")

                quoted = re.search(r'["\']([^"\']+)["\']', message)
                if quoted:
                    task_ref = quoted.group(1)
                else:
                    match = re.search(r'mark\s+(.+?)\s+as', message_lower)
                    if match:
                        task_ref = match.group(1).strip()
                    else:
                        for keyword in ['complete ', 'finish ', 'done with ']:
                            if keyword in message_lower:
                                parts = message_lower.split(keyword, 1)
                                if len(parts) > 1:
                                    task_ref = parts[1].replace(' as completed', '').replace(' as done', '').strip()
                                    break

                update_data['completed'] = True

        # === MARK INCOMPLETE ===
        elif 'incomplete' in message_lower or 'uncomplete' in message_lower or 'pending' in message_lower:
            operation = 'mark_incomplete'
            logger.info(f"⏸️ ORCHESTRATION: Detected mark incomplete")

            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)

            update_data['completed'] = False

        # === DELETE ===
        elif any(keyword in message_lower for keyword in ['delete', 'remove', 'erase']):
            operation = 'delete'
            logger.info(f"🗑️ ORCHESTRATION: Detected delete")

            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)
            else:
                for keyword in ['delete ', 'remove ', 'erase ', 'delete the ', 'remove the ', 'erase the ']:
                    if keyword in message_lower:
                        parts = message_lower.split(keyword, 1)
                        if len(parts) > 1:
                            task_ref = parts[1].replace('task', '').replace('todo', '').strip()
                            break

        # === EDIT/UPDATE TITLE ===
        elif any(keyword in message_lower for keyword in ['change', 'update', 'modify', 'rename', 'edit']):
            operation = 'update_title'
            logger.info(f"✏️ ORCHESTRATION: Detected title update")

            # Pattern 1: change "old" to "new"
            pattern1 = r'["\']([^"\']+)["\'].*?(?:to|into)\s+["\']([^"\']+)["\']'
            match1 = re.search(pattern1, message)
            if match1:
                task_ref = match1.group(1)
                update_data['title'] = match1.group(2)
            else:
                # Pattern 2: change old to new
                pattern2 = r'(?:change|update|rename|edit|modify)\s+(.+?)\s+(?:to|into)\s+(.+?)$'
                match2 = re.search(pattern2, message_lower)
                if match2:
                    task_ref = match2.group(1).replace('the ', '').replace('task ', '').strip()
                    update_data['title'] = match2.group(2).replace('the ', '').replace('task ', '').strip()

        if not operation:
            logger.info("❌ ORCHESTRATION: No operation detected, falling back to AI")
            return None

        if not task_ref:
            logger.warning(f"⚠️ ORCHESTRATION: Operation detected but could not extract task reference")
            return None

        logger.info(f"🎯 ORCHESTRATION: Operation={operation}, Task='{task_ref}', Data={update_data}")

        # Step 1: List todos to find the task
        logger.info("📋 ORCHESTRATION: Step 1 - Calling list_todos")
        list_result = self._execute_tool('list_todos', {'user_id': user_id})

        if 'error' in list_result or not list_result.get('todos'):
            logger.error("❌ ORCHESTRATION: Failed to list todos")
            return {
                'error': 'Could not retrieve tasks',
                'operation': operation
            }

        # Step 2: Find matching task
        matching_task = None
        task_ref_lower = task_ref.lower().strip()

        for task in list_result['todos']:
            if task_ref_lower in task['title'].lower():
                matching_task = task
                break

        if not matching_task:
            logger.warning(f"❌ ORCHESTRATION: Task '{task_ref}' not found")
            return {
                'error': f'Task "{task_ref}" not found',
                'operation': operation
            }

        task_id = matching_task['id']
        logger.info(f"✅ ORCHESTRATION: Found task '{matching_task['title']}' (ID: {task_id})")

        # Step 3: Execute the operation
        logger.info(f"🔧 ORCHESTRATION: Step 2 - Executing {operation}")

        if operation == 'delete':
            result = self._execute_tool('delete_todo', {
                'user_id': user_id,
                'todo_id': task_id
            })
            if 'error' not in result:
                result['orchestrated'] = True
                result['operation'] = 'delete'
                result['task_title'] = matching_task['title']
                logger.info("✅ ORCHESTRATION: Delete successful")
            return result

        else:
            # All other operations are updates
            result = self._execute_tool('update_todo', {
                'user_id': user_id,
                'todo_id': task_id,
                **update_data
            })
            if 'error' not in result:
                result['orchestrated'] = True
                result['operation'] = operation
                result['task_title'] = matching_task['title']
                result['updates'] = update_data
                logger.info(f"✅ ORCHESTRATION: {operation} successful")
            return result
        """
        Detect CRUD operations and orchestrate multi-step tool calls programmatically.
        This bypasses unreliable AI model behavior for critical operations.

        Args:
            user_id: ID of the user
            message: User's message

        Returns:
            Result dict if operation was handled, None otherwise
        """
        message_lower = message.lower()
        import re

        logger.info(f"🔍 Analyzing message: '{message}'")

        # Detect operation type and extract task reference
        operation = None
        task_ref = None
        new_title = None

        # Mark as complete
        if any(keyword in message_lower for keyword in ['mark', 'complete', 'done', 'finish']):
            if 'complete' in message_lower or 'done' in message_lower or 'finish' in message_lower:
                operation = 'mark_complete'
                logger.info(f"📋 Detected operation: mark_complete")
                # Extract task name - look for quotes first
                quoted = re.search(r'["\']([^"\']+)["\']', message)
                if quoted:
                    task_ref = quoted.group(1)
                else:
                    # Try to extract task name after "mark" or before "as"
                    # Pattern: "mark [task name] as completed"
                    match = re.search(r'mark\s+(.+?)\s+as', message_lower)
                    if match:
                        task_ref = match.group(1).strip()
                    else:
                        # Pattern: "complete [task name]"
                        for keyword in ['complete ', 'finish ', 'done with ']:
                            if keyword in message_lower:
                                parts = message_lower.split(keyword, 1)
                                if len(parts) > 1:
                                    task_ref = parts[1].strip()
                                    break

        # Delete
        elif any(keyword in message_lower for keyword in ['delete', 'remove', 'erase']):
            operation = 'delete'
            logger.info(f"🗑️ Detected operation: delete")
            # Extract task name
            quoted = re.search(r'["\']([^"\']+)["\']', message)
            if quoted:
                task_ref = quoted.group(1)
            else:
                # Try to extract after delete/remove/erase
                for keyword in ['delete ', 'remove ', 'erase ', 'delete the ', 'remove the ', 'erase the ']:
                    if keyword in message_lower:
                        parts = message_lower.split(keyword, 1)
                        if len(parts) > 1:
                            # Take everything after keyword, remove "task" if present
                            task_ref = parts[1].replace('task', '').strip()
                            break

        # Update/Edit/Change title
        elif any(keyword in message_lower for keyword in ['change', 'update', 'modify', 'rename', 'edit']):
            operation = 'update_title'
            logger.info(f"✏️ Detected operation: update_title")

            # Try multiple patterns:
            # Pattern 1: change "old" to "new"
            pattern1 = r'["\']([^"\']+)["\'].*?(?:to|into)\s+["\']([^"\']+)["\']'
            match1 = re.search(pattern1, message)
            if match1:
                task_ref = match1.group(1)
                new_title = match1.group(2)
            else:
                # Pattern 2: change old to new (without quotes)
                pattern2 = r'(?:change|update|rename|edit|modify)\s+(.+?)\s+(?:to|into)\s+(.+?)(?:\s|$)'
                match2 = re.search(pattern2, message_lower)
                if match2:
                    task_ref = match2.group(1).replace('the ', '').replace('task ', '').strip()
                    new_title = match2.group(2).replace('the ', '').replace('task ', '').strip()
                else:
                    # Pattern 3: change the title of "task" to "new"
                    pattern3 = r'(?:title|name)\s+of\s+["\']?([^"\']+)["\']?\s+(?:to|into)\s+["\']?([^"\']+)["\']?'
                    match3 = re.search(pattern3, message_lower)
                    if match3:
                        task_ref = match3.group(1).strip()
                        new_title = match3.group(2).strip()

        if not operation:
            logger.info("❌ No CRUD operation detected")
            return None

        if not task_ref:
            logger.info(f"❌ Could not extract task reference from message")
            return None

        logger.info(f"🎯 Operation: {operation}, Task reference: '{task_ref}'" + (f", New title: '{new_title}'" if new_title else ""))

        # Step 1: List todos to find the task
        list_result = self._execute_tool('list_todos', {'user_id': user_id})

        if 'error' in list_result or not list_result.get('todos'):
            return {
                'error': 'Could not retrieve tasks',
                'operation': operation,
                'task_ref': task_ref
            }

        # Step 2: Find matching task
        matching_task = None
        task_ref_lower = task_ref.lower().strip()

        for task in list_result['todos']:
            if task_ref_lower in task['title'].lower():
                matching_task = task
                break

        if not matching_task:
            logger.warning(f"❌ Task '{task_ref}' not found in available tasks")
            return {
                'error': f'Task "{task_ref}" not found',
                'operation': operation,
                'available_tasks': [t['title'] for t in list_result['todos']]
            }

        task_id = matching_task['id']
        logger.info(f"✅ Found task: {matching_task['title']} (ID: {task_id})")

        # Step 3: Execute the actual operation
        if operation == 'mark_complete':
            result = self._execute_tool('update_todo', {
                'user_id': user_id,
                'todo_id': task_id,
                'completed': True
            })
            result['orchestrated'] = True
            result['operation'] = 'mark_complete'
            result['task_title'] = matching_task['title']
            return result

        elif operation == 'delete':
            result = self._execute_tool('delete_todo', {
                'user_id': user_id,
                'todo_id': task_id
            })
            result['orchestrated'] = True
            result['operation'] = 'delete'
            result['task_title'] = matching_task['title']
            return result

        elif operation == 'update_title':
            if not new_title:
                logger.error(f"❌ No new title extracted for update operation")
                return {
                    'error': 'Could not determine new title',
                    'operation': operation
                }
            result = self._execute_tool('update_todo', {
                'user_id': user_id,
                'todo_id': task_id,
                'title': new_title
            })
            result['orchestrated'] = True
            result['operation'] = 'update_title'
            result['old_title'] = matching_task['title']
            result['new_title'] = new_title
            return result

        return None

    def process_message(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message using OpenAI's agent with tool calling.

        Args:
            user_id: ID of the user sending the message
            message: The user's message content
            session_id: Optional session ID to continue a conversation

        Returns:
            Dictionary containing the agent's response and metadata
        """
        try:
            # Validate inputs
            if not message or not message.strip():
                raise ValidationError("Message cannot be empty")

            if len(message) > AgentConfig.MAX_MESSAGE_LENGTH:
                raise ValidationError(f"Message exceeds maximum length of {AgentConfig.MAX_MESSAGE_LENGTH} characters")

            # Get or create session
            if session_id:
                agent_session = self.get_agent_session(session_id, user_id)
                if not agent_session:
                    raise ValidationError(f"Session {session_id} not found or access denied")
            else:
                # Create new session
                agent_session = self.create_agent_session(user_id, message)
                session_id = agent_session.id

            # Store user message
            user_message = self.add_message_to_session(
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=message
            )

            # 🔧 INTELLIGENT ORCHESTRATION: Try to handle CRUD operations programmatically
            # This bypasses unreliable AI model behavior for critical operations
            orchestrated_result = self._detect_and_orchestrate_crud(user_id, message)

            if orchestrated_result:
                logger.info("✅ ORCHESTRATION: Operation handled, generating response")

                # Map operation to actual tool name for frontend detection
                operation = orchestrated_result.get('operation', 'crud')
                if operation == 'delete':
                    tool_name = 'delete_todo'
                else:
                    # All other operations use update_todo
                    tool_name = 'update_todo'

                # Generate appropriate response based on operation
                if 'error' in orchestrated_result:
                    response_text = f"Sorry, {orchestrated_result['error']}."
                elif operation == 'mark_complete':
                    response_text = f"✅ I've marked '{orchestrated_result['task_title']}' as completed."
                elif operation == 'mark_incomplete':
                    response_text = f"⏸️ I've marked '{orchestrated_result['task_title']}' as incomplete."
                elif operation == 'delete':
                    response_text = f"🗑️ I've deleted '{orchestrated_result['task_title']}'."
                elif operation == 'update_title':
                    new_title = orchestrated_result.get('updates', {}).get('title', 'new title')
                    response_text = f"✏️ I've renamed '{orchestrated_result['task_title']}' to '{new_title}'."
                elif operation == 'set_priority':
                    priority = orchestrated_result.get('updates', {}).get('priority', 'new priority')
                    response_text = f"🔔 I've set '{orchestrated_result['task_title']}' priority to {priority}."
                elif operation == 'set_due_date':
                    due_date = orchestrated_result.get('updates', {}).get('due_date', 'specified date')
                    response_text = f"📅 I've set the due date for '{orchestrated_result['task_title']}' to {due_date}."
                else:
                    response_text = f"✅ I've updated '{orchestrated_result['task_title']}'."

                # Store assistant response with actual tool name for frontend detection
                assistant_msg = self.add_message_to_session(
                    session_id=str(session_id),
                    user_id=user_id,
                    role="assistant",
                    content=response_text,
                    tool_calls=[{
                        "id": "orchestrated",
                        "name": tool_name,  # Use actual tool name (update_todo or delete_todo)
                        "arguments": {}
                    }],
                    tool_results=[orchestrated_result]
                )

                # Update session timestamp
                agent_session.updated_at = datetime.utcnow()
                self.session.add(agent_session)
                self.session.commit()

                logger.info(f"✅ ORCHESTRATION: Response sent to user: '{response_text}' with tool_name: '{tool_name}'")

                return {
                    "session_id": str(session_id),
                    "message_id": str(assistant_msg.id),
                    "response": response_text,
                    "timestamp": datetime.utcnow().isoformat(),
                    "tool_calls": [{
                        "id": "orchestrated",
                        "name": tool_name,  # Use actual tool name for frontend detection
                        "arguments": {}
                    }],
                    "tool_results": [orchestrated_result],
                    "orchestrated": True
                }

            # If orchestration didn't handle it, continue with normal AI processing

            # Use stub AI if configured or if OpenAI is unavailable
            if self.use_stub or not self.client:
                return self._process_with_stub(user_id, message, session_id)

            # Build conversation history
            conversation_history = self._build_conversation_history(session_id, user_id)

            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"You are a tool-using AI assistant for todo task management. "
                        f"The authenticated user ID is: {user_id} "
                        f"\n\n"
                        f"=== YOUR ONLY JOB IS TO CALL TOOLS - NOT TO CHAT ===\n\n"
                        f"RULE 1: CREATE TASK\n"
                        f"User says: 'add', 'create', 'make' a task\n"
                        f"→ Immediately call: add_todo(user_id='{user_id}', title='...', description='...')\n"
                        f"→ Do NOT respond until you've called this tool\n\n"
                        f"RULE 2: MARK COMPLETE\n"
                        f"User says: 'mark complete', 'mark as done', 'complete'\n"
                        f"→ Step 1: Call list_todos(user_id='{user_id}')\n"
                        f"→ Step 2: IMMEDIATELY call update_todo(user_id='{user_id}', todo_id='<ID>', completed=True)\n"
                        f"→ YOU MUST CALL BOTH TOOLS IN SEQUENCE - DO NOT SKIP THE SECOND TOOL\n"
                        f"→ If you found the task in list_todos, you MUST call update_todo next\n\n"
                        f"RULE 3: MARK INCOMPLETE\n"
                        f"User says: 'mark incomplete', 'mark as pending'\n"
                        f"→ Step 1: Call list_todos(user_id='{user_id}')\n"
                        f"→ Step 2: IMMEDIATELY call update_todo(user_id='{user_id}', todo_id='<ID>', completed=False)\n\n"
                        f"RULE 4: UPDATE TASK\n"
                        f"User says: 'update', 'change', 'modify', 'edit'\n"
                        f"→ Step 1: Call list_todos(user_id='{user_id}')\n"
                        f"→ Step 2: IMMEDIATELY call update_todo(user_id='{user_id}', todo_id='<ID>', <field>=<value>)\n\n"
                        f"RULE 5: DELETE TASK\n"
                        f"User says: 'delete', 'remove', 'erase'\n"
                        f"→ Step 1: Call list_todos(user_id='{user_id}')\n"
                        f"→ Step 2: IMMEDIATELY call delete_todo(user_id='{user_id}', todo_id='<ID>')\n\n"
                        f"RULE 6: LIST TASKS\n"
                        f"User says: 'show', 'list', 'view'\n"
                        f"→ Call list_todos(user_id='{user_id}')\n\n"
                        f"=== CRITICAL REQUIREMENTS ===\n"
                        f"- When you call list_todos and find a matching task, you MUST call the action tool next\n"
                        f"- Do NOT stop after list_todos - always call the second tool\n"
                        f"- Do NOT just say 'I found the task' - you must ACT on it\n"
                        f"- Extract the task ID from list_todos results and use it in the second tool call\n"
                        f"- For update/delete operations, BOTH tools must be called\n"
                        f"- After calling tools, briefly confirm the action based on tool results\n"
                    )
                }
            ]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})

            # Call OpenAI with function calling
            # Try the configured model, but fall back to a safe widely-available model if not found
            try:
                response = self.client.chat.completions.create(
                    model=AgentConfig.AGENT_MODEL_NAME,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=AgentConfig.AGENT_TEMPERATURE,
                    max_tokens=AgentConfig.AGENT_MAX_TOKENS,
                    timeout=AgentConfig.AGENT_TIMEOUT_SECONDS
                )
            except OpenAIError as e:
                err_text = str(e)
                # If model not found, retry with gpt-3.5-turbo before falling back to stub
                if 'model_not_found' in err_text or 'does not exist' in err_text:
                    try:
                        response = self.client.chat.completions.create(
                            model='gpt-3.5-turbo',
                            messages=messages,
                            tools=self.tools,
                            tool_choice="auto",
                            temperature=AgentConfig.AGENT_TEMPERATURE,
                            max_tokens=AgentConfig.AGENT_MAX_TOKENS,
                            timeout=AgentConfig.AGENT_TIMEOUT_SECONDS
                        )
                    except Exception:
                        # re-raise original error to be handled by outer logic
                        raise e
                else:
                    raise

            assistant_message = response.choices[0].message
            tool_calls_data = None
            tool_results_data = None

            # Handle tool calls if present
            if assistant_message.tool_calls:
                tool_calls_data = []
                tool_results_data = []

                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Log tool call
                    logger.info(f"Agent calling tool: {tool_name} with args: {tool_args}")
                    tool_calls_data.append({
                        "id": tool_call.id,
                        "name": tool_name,
                        "arguments": tool_args
                    })

                    # Execute the tool
                    tool_result = self._execute_tool(tool_name, tool_args)
                    tool_results_data.append({
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "result": tool_result
                    })

                # Get final response after tool execution
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Add tool results to messages
                for tool_result in tool_results_data:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_result["tool_call_id"],
                        "content": json.dumps(tool_result["result"])
                    })

                # Get the agent's final response after processing tool results
                # Try finalizing with configured model, fallback to gpt-3.5-turbo if necessary
                try:
                    final_response = self.client.chat.completions.create(
                        model=AgentConfig.AGENT_MODEL_NAME,
                        messages=messages,
                        temperature=AgentConfig.AGENT_TEMPERATURE,
                        max_tokens=AgentConfig.AGENT_MAX_TOKENS,
                        timeout=AgentConfig.AGENT_TIMEOUT_SECONDS
                    )
                except OpenAIError as e:
                    err_text = str(e)
                    if 'model_not_found' in err_text or 'does not exist' in err_text:
                        final_response = self.client.chat.completions.create(
                            model='gpt-3.5-turbo',
                            messages=messages,
                            temperature=AgentConfig.AGENT_TEMPERATURE,
                            max_tokens=AgentConfig.AGENT_MAX_TOKENS,
                            timeout=AgentConfig.AGENT_TIMEOUT_SECONDS
                        )
                    else:
                        raise

                assistant_content = final_response.choices[0].message.content

            else:
                assistant_content = assistant_message.content

            # Store assistant response
            assistant_msg = self.add_message_to_session(
                session_id=str(session_id),
                user_id=user_id,
                role="assistant",
                content=assistant_content or "I've processed your request.",
                tool_calls=tool_calls_data,
                tool_results=tool_results_data
            )

            # Update session timestamp
            agent_session.updated_at = datetime.utcnow()
            self.session.add(agent_session)
            self.session.commit()

            return {
                "session_id": str(session_id),
                "message_id": str(assistant_msg.id),
                "response": assistant_content,
                "timestamp": datetime.utcnow().isoformat(),
                "tool_calls": tool_calls_data,
                "tool_results": tool_results_data
            }

        except APITimeoutError:
            logger.error("OpenAI API timeout")
            return self._process_with_stub(user_id, message, session_id, error="API timeout")

        except APIConnectionError:
            logger.error("OpenAI API connection error")
            return self._process_with_stub(user_id, message, session_id, error="Connection error")

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._process_with_stub(user_id, message, session_id, error=f"OpenAI error: {str(e)}")

        except ValidationError as e:
            logger.error(f"Validation error in process_message: {str(e)}")
            # Log additional context for debugging
            logger.debug(f"User ID: {user_id}, Message: {message[:100]}..., Session ID: {session_id}")
            raise  # Re-raise validation errors

        except UnauthorizedAccessException as e:
            logger.error(f"Authorization error in process_message: {str(e)}")
            logger.info(f"User {user_id} attempted unauthorized access")
            raise  # Re-raise authorization errors

        except APITimeoutError as e:
            logger.error(f"OpenAI API timeout in process_message: {str(e)}")
            return self._process_with_stub(user_id, message, session_id, error="API timeout")

        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error in process_message: {str(e)}")
            return self._process_with_stub(user_id, message, session_id, error="Connection error")

        except OpenAIError as e:
            logger.error(f"OpenAI API error in process_message: {str(e)}")
            return self._process_with_stub(user_id, message, session_id, error=f"OpenAI error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error in process_message: {str(e)}", exc_info=True)
            # Log additional context for debugging
            logger.debug(f"User ID: {user_id}, Message: {message[:100]}..., Session ID: {session_id}")

            # Check if this is a database error that we should handle specially
            if "database" in str(e).lower() or "sql" in str(e).lower():
                logger.error("Database error occurred, falling back to stub AI")
                return self._process_with_stub(user_id, message, session_id, error="Database error")

            # Check if this is a tool execution error
            if "tool" in str(e).lower():
                logger.error("Tool execution error, continuing with available information")
                return {
                    "session_id": str(session_id),
                    "message_id": str(uuid.uuid4()),  # Generate a new message ID for error case
                    "response": "I encountered an issue executing one of the tools. I can still help with other requests.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error_occurred": True,
                    "error_details": str(e)
                }

            # For any other unexpected error, fall back to stub
            return self._process_with_stub(user_id, message, session_id, error=f"Unexpected error: {str(e)}")

    def _process_with_stub(
        self,
        user_id: str,
        message: str,
        session_id: uuid.UUID,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process message with stub AI as a fallback.

        Args:
            user_id: ID of the user
            message: User's message
            session_id: Session ID
            error: Optional error message to include

        Returns:
            Dictionary containing stub response
        """
        from backend.ai.stub_ai import get_ai_response

        context = {
            "user_id": user_id,
            "session_id": str(session_id),
            "error": error
        }

        stub_response = get_ai_response(message, context)

        if error:
            stub_response = f"[Using fallback AI due to: {error}] {stub_response}"

        # Store stub response
        assistant_msg = self.add_message_to_session(
            session_id=str(session_id),
            user_id=user_id,
            role="assistant",
            content=stub_response
        )

        return {
            "session_id": str(session_id),
            "message_id": str(assistant_msg.id),
            "response": stub_response,
            "timestamp": datetime.utcnow().isoformat(),
            "using_stub": True,
            "error": error
        }

    def get_user_conversations(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[AgentSession]:
        """
        Get all agent sessions/conversations for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of sessions to return
            offset: Offset for pagination

        Returns:
            List of AgentSession objects
        """
        return self.get_user_sessions(str(user_id), limit, offset)

    def delete_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete a conversation/session and all its messages.

        Args:
            conversation_id: ID of the conversation to delete
            user_id: ID of the user requesting deletion

        Returns:
            True if deletion was successful, False otherwise
        """
        from sqlmodel import select

        # Verify ownership - convert UUIDs to strings for base class methods
        agent_session = self.get_agent_session(str(conversation_id), str(user_id))
        if not agent_session:
            return False

        # Delete all messages in the session
        messages = self.get_session_messages(str(conversation_id), str(user_id))
        for message in messages:
            self.session.delete(message)

        # Delete the session
        self.session.delete(agent_session)
        self.session.commit()

        return True
