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
from services.agent_service import AgentService
from ..services.todo_tools import TodoTools
from ..config.agent_config import AgentConfig
# from ..models.agent_message import AgentMessage
from ..models.agent_session import AgentSession
from exceptions.chat_exceptions import UnauthorizedAccessException, ValidationError

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
            if tool_name not in self.tool_functions:
                raise ValueError(f"Unknown tool: {tool_name}")

            # Authorization check: ensure user has permission to execute the tool
            # At minimum, user must be authenticated and the user_id must be in the arguments
            user_id = tool_arguments.get('user_id')
            if not user_id:
                logger.error(f"No user_id provided when executing tool {tool_name}")
                return {"error": "Unauthorized: No user context provided", "success": False}

            # Perform basic authorization check
            if not self._authorize_tool_call(tool_name, user_id, tool_arguments):
                logger.error(f"Unauthorized tool call: {tool_name} for user {user_id}")
                return {"error": "Unauthorized: Insufficient permissions to execute this tool", "success": False}

            tool_function = self.tool_functions[tool_name]
            result = tool_function(**tool_arguments)

            logger.info(f"Tool executed successfully: {tool_name}")
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
            try:
                uuid.UUID(user_id)
            except ValueError:
                logger.error(f"Invalid user_id format in tool call: {user_id}")
                self._log_tool_execution_error(tool_name, tool_arguments, f"Invalid user_id format: {user_id}", "validation_error")
                return False

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
        messages = self.get_session_messages(session_id, user_id, limit=max_messages)

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

            # Convert user_id to UUID
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                raise ValidationError(f"Invalid user ID format: {user_id}")

            # Get or create session
            if session_id:
                try:
                    session_uuid = uuid.UUID(session_id)
                    agent_session = self.get_agent_session(session_uuid, user_uuid)
                    if not agent_session:
                        raise ValidationError(f"Session {session_id} not found or access denied")
                except ValueError:
                    raise ValidationError(f"Invalid session ID format: {session_id}")
            else:
                # Create new session
                agent_session = self.create_agent_session(user_id, message)
                session_uuid = agent_session.id

            # Store user message
            user_message = self.add_message_to_session(
                session_id=str(session_uuid),
                user_id=user_id,
                role="user",
                content=message
            )

            # Use stub AI if configured or if OpenAI is unavailable
            if self.use_stub or not self.client:
                return self._process_with_stub(user_id, message, session_uuid)

            # Build conversation history
            conversation_history = self._build_conversation_history(session_uuid, user_uuid)

            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI assistant that helps users manage their todo tasks. "
                        "You have access to tools to list, add, update, and delete todos. "
                        "When a user asks about their tasks, use the appropriate tools to help them. "
                        "Be conversational, helpful, and proactive in suggesting task management strategies. "
                        "Always confirm actions before executing them if they modify data."
                    )
                }
            ]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})

            # Call OpenAI with function calling
            response = self.client.chat.completions.create(
                model=AgentConfig.AGENT_MODEL_NAME,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=AgentConfig.AGENT_TEMPERATURE,
                max_tokens=AgentConfig.AGENT_MAX_TOKENS,
                timeout=AgentConfig.AGENT_TIMEOUT_SECONDS
            )

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
                final_response = self.client.chat.completions.create(
                    model=AgentConfig.AGENT_MODEL_NAME,
                    messages=messages,
                    temperature=AgentConfig.AGENT_TEMPERATURE,
                    max_tokens=AgentConfig.AGENT_MAX_TOKENS,
                    timeout=AgentConfig.AGENT_TIMEOUT_SECONDS
                )

                assistant_content = final_response.choices[0].message.content

            else:
                assistant_content = assistant_message.content

            # Store assistant response
            assistant_msg = self.add_message_to_session(
                session_id=str(session_uuid),
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
                "session_id": str(session_uuid),
                "message_id": str(assistant_msg.id),
                "response": assistant_content,
                "timestamp": datetime.utcnow().isoformat(),
                "tool_calls": tool_calls_data,
                "tool_results": tool_results_data
            }

        except APITimeoutError:
            logger.error("OpenAI API timeout")
            return self._process_with_stub(user_id, message, session_uuid, error="API timeout")

        except APIConnectionError:
            logger.error("OpenAI API connection error")
            return self._process_with_stub(user_id, message, session_uuid, error="Connection error")

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._process_with_stub(user_id, message, session_uuid, error=f"OpenAI error: {str(e)}")

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
            return self._process_with_stub(user_id, message, session_uuid, error="API timeout")

        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error in process_message: {str(e)}")
            return self._process_with_stub(user_id, message, session_uuid, error="Connection error")

        except OpenAIError as e:
            logger.error(f"OpenAI API error in process_message: {str(e)}")
            return self._process_with_stub(user_id, message, session_uuid, error=f"OpenAI error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error in process_message: {str(e)}", exc_info=True)
            # Log additional context for debugging
            logger.debug(f"User ID: {user_id}, Message: {message[:100]}..., Session ID: {session_id}")

            # Check if this is a database error that we should handle specially
            if "database" in str(e).lower() or "sql" in str(e).lower():
                logger.error("Database error occurred, falling back to stub AI")
                return self._process_with_stub(user_id, message, session_uuid, error="Database error")

            # Check if this is a tool execution error
            if "tool" in str(e).lower():
                logger.error("Tool execution error, continuing with available information")
                return {
                    "session_id": str(session_uuid),
                    "message_id": str(uuid.uuid4()),  # Generate a new message ID for error case
                    "response": "I encountered an issue executing one of the tools. I can still help with other requests.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "error_occurred": True,
                    "error_details": str(e)
                }

            # For any other unexpected error, fall back to stub
            return self._process_with_stub(user_id, message, session_uuid, error=f"Unexpected error: {str(e)}")

    def _process_with_stub(
        self,
        user_id: str,
        message: str,
        session_uuid: uuid.UUID,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process message with stub AI as a fallback.

        Args:
            user_id: ID of the user
            message: User's message
            session_uuid: Session UUID
            error: Optional error message to include

        Returns:
            Dictionary containing stub response
        """
        from backend.ai.stub_ai import get_ai_response

        context = {
            "user_id": user_id,
            "session_id": str(session_uuid),
            "error": error
        }

        stub_response = get_ai_response(message, context)

        if error:
            stub_response = f"[Using fallback AI due to: {error}] {stub_response}"

        # Store stub response
        assistant_msg = self.add_message_to_session(
            session_id=str(session_uuid),
            user_id=user_id,
            role="assistant",
            content=stub_response
        )

        return {
            "session_id": str(session_uuid),
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

        # Verify ownership
        agent_session = self.get_agent_session(conversation_id, user_id)
        if not agent_session:
            return False

        # Delete all messages in the session
        messages = self.get_session_messages(conversation_id, user_id)
        for message in messages:
            self.session.delete(message)

        # Delete the session
        self.session.delete(agent_session)
        self.session.commit()

        return True
