"""
MCP Server for Todo App
=======================

Yeh server MCP SDK compatible hai aur Claude Code ya kisi bhi MCP client ke saath
kaam kar sakta hai.

Usage:
    python mcp_server.py

Ya Claude Code mein add karein:
    claude mcp add todo-server python mcp_server.py
"""

import json
import sys
from typing import Any
from datetime import datetime

# Add app to path
sys.path.insert(0, ".")

from app.mcp_tools.add_task import (
    add_task_tool,
    AddTaskInput,
    ADD_TASK_TOOL_SCHEMA
)


# ============================================
# MCP Server Implementation
# ============================================
class MCPServer:
    """
    Simple MCP Server jo stdin/stdout use karta hai.
    """

    def __init__(self):
        self.tools = {
            "add_task": {
                "schema": ADD_TASK_TOOL_SCHEMA,
                "handler": self.handle_add_task
            }
        }

    def handle_add_task(self, arguments: dict) -> dict:
        """add_task tool ko execute karta hai."""
        try:
            # Input validation
            input_data = AddTaskInput(
                user_id=arguments.get("user_id", ""),
                title=arguments.get("title", ""),
                description=arguments.get("description")
            )

            # Tool execute karo
            result = add_task_tool(input_data)

            return {
                "task_id": result.task_id,
                "status": result.status,
                "title": result.title,
                "message": result.message
            }

        except Exception as e:
            return {
                "task_id": -1,
                "status": "error",
                "title": arguments.get("title", "Unknown"),
                "message": f"Error: {str(e)}"
            }

    def list_tools(self) -> list:
        """Saare available tools return karta hai."""
        return [tool["schema"] for tool in self.tools.values()]

    def call_tool(self, name: str, arguments: dict) -> Any:
        """Tool ko naam se call karta hai."""
        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")

        return self.tools[name]["handler"](arguments)

    def handle_request(self, request: dict) -> dict:
        """MCP request handle karta hai."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "todo-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }

            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.list_tools()
                    }
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = self.call_tool(tool_name, arguments)

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    def run(self):
        """MCP server start karta hai (stdin/stdout mode)."""
        print(f"Todo MCP Server started at {datetime.now()}", file=sys.stderr)

        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)


# ============================================
# Main Entry Point
# ============================================
if __name__ == "__main__":
    server = MCPServer()
    server.run()
