"""
MCP (Model Context Protocol) server for the AI assistant integration.
This module implements the MCP server that exposes backend functionality to the AI agent.
"""

import asyncio
import json
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend.config.agent_config import agent_config
from backend.services.chat_service import ChatService
from backend.services.task_service import TaskService
from backend.database import get_session
from sqlmodel import Session


class MCPServer:
    """
    MCP (Model Context Protocol) server that exposes tools for AI agents.
    Provides a secure interface for AI agents to access backend functionality.
    """

    def __init__(self):
        """
        Initialize the MCP server with available tools.
        """
        self.tools = {}
        self.app = FastAPI(
            title="AI Assistant MCP Server",
            description="Model Context Protocol server for AI assistant integration",
            version="1.0.0"
        )

        # Register available tools
        self._register_default_tools()

        # Set up FastAPI routes
        self._setup_routes()

    def _register_default_tools(self):
        """
        Register the default tools available to the AI agent.
        """
        # Tool for listing todos
        self.tools["list_todos"] = {
            "name": "list_todos",
            "description": "List the user's todo items",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user whose todos to list"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of todos to return (default 10)"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset for pagination (default 0)"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Filter by completion status (null for all, true for completed, false for pending)"
                    }
                },
                "required": ["user_id"]
            }
        }

        # Tool for adding a todo
        self.tools["add_todo"] = {
            "name": "add_todo",
            "description": "Add a new todo item for the user",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user adding the todo"
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the new todo"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the todo"
                    }
                },
                "required": ["user_id", "title"]
            }
        }

        # Tool for updating a todo
        self.tools["update_todo"] = {
            "name": "update_todo",
            "description": "Update an existing todo item",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user whose todo to update"
                    },
                    "todo_id": {
                        "type": "string",
                        "description": "ID of the todo to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the todo (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the todo (optional)"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "New completion status for the todo (optional)"
                    }
                },
                "required": ["user_id", "todo_id"]
            }
        }

        # Tool for deleting a todo
        self.tools["delete_todo"] = {
            "name": "delete_todo",
            "description": "Delete an existing todo item",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user whose todo to delete"
                    },
                    "todo_id": {
                        "type": "string",
                        "description": "ID of the todo to delete"
                    }
                },
                "required": ["user_id", "todo_id"]
            }
        }

        # Tool for getting user context
        self.tools["get_user_context"] = {
            "name": "get_user_context",
            "description": "Get context information about the user",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "ID of the user to get context for"
                    }
                },
                "required": ["user_id"]
            }
        }

    def _setup_routes(self):
        """
        Set up the FastAPI routes for the MCP server.
        """
        @self.app.get("/tools")
        async def list_tools():
            """
            Return a list of all available tools.

            Returns:
                JSON response with all available tools and their schemas
            """
            return JSONResponse(content={
                "tools": list(self.tools.values())
            })

        @self.app.post("/invoke")
        async def invoke_tool(request: Dict[str, Any]):
            """
            Invoke a specific tool with the provided arguments.

            Args:
                request: Request containing 'name' and 'arguments' for the tool

            Returns:
                Result of the tool execution
            """
            tool_name = request.get("name")
            arguments = request.get("arguments", {})

            if not tool_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tool name is required"
                )

            if tool_name not in self.tools:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tool '{tool_name}' not found"
                )

            # Validate arguments against the tool's schema
            if not self._validate_arguments(tool_name, arguments):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid arguments for the specified tool"
                )

            # Execute the tool
            try:
                result = await self._execute_tool(tool_name, arguments)
                return JSONResponse(content={"result": result})
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error executing tool '{tool_name}': {str(e)}"
                )

    def _validate_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> bool:
        """
        Validate the arguments for a specific tool against its schema.

        Args:
            tool_name: Name of the tool to validate arguments for
            arguments: Arguments to validate

        Returns:
            True if arguments are valid, False otherwise
        """
        tool_schema = self.tools[tool_name]["input_schema"]
        properties = tool_schema.get("properties", {})
        required = tool_schema.get("required", [])

        # Check required fields
        for field in required:
            if field not in arguments:
                return False

        # Validate field types
        for field, value in arguments.items():
            if field in properties:
                prop_type = properties[field].get("type")
                if prop_type == "string" and not isinstance(value, str):
                    return False
                elif prop_type == "integer" and not isinstance(value, int):
                    return False
                elif prop_type == "boolean" and not isinstance(value, bool):
                    return False
                elif prop_type == "array" and not isinstance(value, list):
                    return False
                elif prop_type == "object" and not isinstance(value, dict):
                    return False

        return True

    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a specific tool with the provided arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            Result of the tool execution
        """
        # Create a new database session for this request
        with next(get_session()) as session:
            # Get user ID from arguments
            user_id = arguments.get("user_id")
            if not user_id:
                raise ValueError("User ID is required for all operations")

            # Initialize services with the session
            task_service = TaskService(session)

            # Execute the appropriate tool
            if tool_name == "list_todos":
                limit = arguments.get("limit", 10)
                offset = arguments.get("offset", 0)
                completed = arguments.get("completed")

                todos = task_service.get_user_tasks(
                    user_id=user_id,
                    limit=limit,
                    offset=offset,
                    completed=completed
                )

                return {
                    "todos": [
                        {
                            "id": str(todo.id),
                            "title": todo.title,
                            "description": todo.description or "",
                            "completed": todo.completed,
                            "created_at": todo.created_at.isoformat() if todo.created_at else None,
                            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None
                        }
                        for todo in todos
                    ]
                }

            elif tool_name == "add_todo":
                title = arguments["title"]
                description = arguments.get("description", "")

                new_todo = task_service.create_task(
                    user_id=user_id,
                    title=title,
                    description=description
                )

                return {
                    "success": True,
                    "todo": {
                        "id": str(new_todo.id),
                        "title": new_todo.title,
                        "description": new_todo.description or "",
                        "completed": new_todo.completed,
                        "created_at": new_todo.created_at.isoformat() if new_todo.created_at else None,
                        "updated_at": new_todo.updated_at.isoformat() if new_todo.updated_at else None
                    }
                }

            elif tool_name == "update_todo":
                todo_id = arguments["todo_id"]

                # Prepare update data
                update_data = {}
                if "title" in arguments:
                    update_data["title"] = arguments["title"]
                if "description" in arguments:
                    update_data["description"] = arguments["description"]
                if "completed" in arguments:
                    update_data["completed"] = arguments["completed"]

                updated_todo = task_service.update_task(
                    task_id=todo_id,
                    user_id=user_id,
                    **update_data
                )

                if not updated_todo:
                    raise ValueError(f"Todo with ID {todo_id} not found for user {user_id}")

                return {
                    "success": True,
                    "todo": {
                        "id": str(updated_todo.id),
                        "title": updated_todo.title,
                        "description": updated_todo.description or "",
                        "completed": updated_todo.completed,
                        "created_at": updated_todo.created_at.isoformat() if updated_todo.created_at else None,
                        "updated_at": updated_todo.updated_at.isoformat() if updated_todo.updated_at else None
                    }
                }

            elif tool_name == "delete_todo":
                todo_id = arguments["todo_id"]

                success = task_service.delete_task(
                    task_id=todo_id,
                    user_id=user_id
                )

                if not success:
                    raise ValueError(f"Todo with ID {todo_id} not found for user {user_id}")

                return {
                    "success": True,
                    "message": f"Todo {todo_id} deleted successfully"
                }

            elif tool_name == "get_user_context":
                # In a real implementation, we would fetch user context
                # For now, returning a placeholder response
                return {
                    "user_id": user_id,
                    "context": {
                        "preferences": {},
                        "usage_stats": {},
                        "last_accessed": None
                    }
                }

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

    def start_server(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Start the MCP server.

        Args:
            host: Host address to bind to (default: 0.0.0.0)
            port: Port to listen on (default: 8080)
        """
        import uvicorn

        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level=agent_config.LOG_LEVEL.lower()
        )


# Create a global instance of the MCP server
mcp_server = MCPServer()

# Export the app instance for mounting in the main application
app = mcp_server.app