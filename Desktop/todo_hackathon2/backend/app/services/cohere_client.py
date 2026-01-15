"""
Cohere API Client for TodoAI Chatbot
Handles AI generation with tool calling support for task management
"""
import cohere
import os
from typing import Optional

# Lazy load Cohere client to prevent startup crashes
_cohere_client = None

def get_cohere_client():
    """Get or create Cohere client with lazy initialization."""
    global _cohere_client
    if _cohere_client is None:
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            print("[COHERE] WARNING: COHERE_API_KEY not set!")
            return None
        _cohere_client = cohere.ClientV2(api_key=api_key)
        print(f"[COHERE] Client initialized successfully")
    return _cohere_client

# System preamble defining TodoAI personality and capabilities
SYSTEM_PREAMBLE = """You are TodoAI, a friendly and helpful task management assistant for a todo application.

LANGUAGE RULES:
- If the user writes in Roman Urdu/Hinglish (like "mujhe grocery leni hai"), respond in Roman Urdu
- If the user writes in English, respond in English
- Be warm, encouraging, and supportive in all interactions
- Use "aap" (respectful form) when addressing users in Roman Urdu

CAPABILITIES (use these tools to help users):
- add_task: Create new tasks for the user
- list_tasks: Show user's tasks (can filter by status: all, pending, completed)
- complete_task: Mark tasks as done
- delete_task: Remove tasks (ALWAYS ask for confirmation before deleting)
- update_task: Edit task title or description
- get_user_info: Get user profile and task statistics

BEHAVIOR GUIDELINES:
- For ambiguous requests, ask clarifying questions before acting
- ALWAYS confirm destructive actions (delete) before executing
- Provide helpful suggestions when appropriate
- Keep responses concise but friendly
- When showing task lists, format them nicely with numbers
- Celebrate when users complete tasks!

EXAMPLE INTERACTIONS:
- User: "add task buy milk" → Create task and confirm: "Task 'buy milk' add ho gaya!"
- User: "mere tasks dikhao" → Show their tasks in a nice format
- User: "task 1 delete karo" → Ask: "Kya aap sure hain ke 'task title' delete karna hai?"
"""

# MCP Tool definitions for Cohere's tool calling feature
MCP_TOOLS = [
    {
        "name": "add_task",
        "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something as a task.",
        "parameter_definitions": {
            "title": {
                "type": "str",
                "description": "The task title/description (required)",
                "required": True
            },
            "description": {
                "type": "str",
                "description": "Additional details about the task (optional)",
                "required": False
            }
        }
    },
    {
        "name": "list_tasks",
        "description": "Get the user's tasks. Can filter by status. Use this when user asks to see, show, or list their tasks.",
        "parameter_definitions": {
            "status": {
                "type": "str",
                "description": "Filter tasks by status: 'all' (default), 'pending', or 'completed'",
                "required": False
            }
        }
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed/done. Use this when user says a task is done, finished, or complete.",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "The ID number of the task to mark as complete",
                "required": True
            }
        }
    },
    {
        "name": "delete_task",
        "description": "Permanently delete a task. IMPORTANT: Always ask for confirmation before using this tool.",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "The ID number of the task to delete",
                "required": True
            }
        }
    },
    {
        "name": "update_task",
        "description": "Update/edit a task's title or description. Use when user wants to change or modify a task.",
        "parameter_definitions": {
            "task_id": {
                "type": "int",
                "description": "The ID number of the task to update",
                "required": True
            },
            "title": {
                "type": "str",
                "description": "New title for the task (optional)",
                "required": False
            },
            "description": {
                "type": "str",
                "description": "New description for the task (optional)",
                "required": False
            }
        }
    },
    {
        "name": "get_user_info",
        "description": "Get user profile information and task statistics. Use when user asks about their name, email, or task counts.",
        "parameter_definitions": {}
    }
]


def chat_with_tools(
    message: str,
    chat_history: list[dict],
    conversation_id: Optional[str] = None
) -> dict:
    """
    Send a message to Cohere with tool calling support.

    Args:
        message: User's message text
        chat_history: Previous messages formatted for Cohere
        conversation_id: Optional Cohere conversation ID for context

    Returns:
        dict containing:
        - text: AI response text
        - tool_calls: List of tools to execute (if any)
        - conversation_id: Cohere conversation ID
    """
    try:
        co = get_cohere_client()
        if co is None:
            return {
                "text": "AI service configure nahi hai. Admin se COHERE_API_KEY set karwayein.",
                "tool_calls": [],
                "conversation_id": conversation_id
            }

        # Convert chat history to V2 format
        messages = []

        # Add system message
        messages.append({
            "role": "system",
            "content": SYSTEM_PREAMBLE
        })

        # Add chat history
        for msg in chat_history:
            role = "user" if msg.get("role") == "USER" else "assistant"
            messages.append({
                "role": role,
                "content": msg.get("message", "")
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })

        # Convert tools to V2 format
        tools_v2 = []
        for tool in MCP_TOOLS:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            for param_name, param_def in tool.get("parameter_definitions", {}).items():
                tool_def["function"]["parameters"]["properties"][param_name] = {
                    "type": "string",
                    "description": param_def.get("description", "")
                }
                if param_def.get("required", False):
                    tool_def["function"]["parameters"]["required"].append(param_name)
            tools_v2.append(tool_def)

        print(f"[COHERE] Sending message: {message[:50]}...")

        response = co.chat(
            model="command-a-03-2025",
            messages=messages,
            tools=tools_v2
        )

        print(f"[COHERE] Response received, finish_reason: {response.finish_reason}")

        # Extract text from response
        response_text = ""
        tool_calls = []

        if response.message and response.message.content:
            for content_item in response.message.content:
                if hasattr(content_item, 'text'):
                    response_text += content_item.text
                elif hasattr(content_item, 'type') and content_item.type == 'text':
                    response_text += getattr(content_item, 'text', '')

        # Extract tool calls
        if response.message and response.message.tool_calls:
            for tc in response.message.tool_calls:
                import json
                params = tc.function.arguments
                if isinstance(params, str):
                    try:
                        params = json.loads(params)
                    except:
                        params = {}
                tool_calls.append({
                    "name": tc.function.name,
                    "parameters": params,
                    "id": tc.id
                })
            print(f"[COHERE] Tool calls: {[tc['name'] for tc in tool_calls]}")

        return {
            "text": response_text,
            "tool_calls": tool_calls,
            "conversation_id": conversation_id or "default"
        }
    except Exception as e:
        import traceback
        print(f"[COHERE] Error in chat_with_tools: {e}")
        print(f"[COHERE] Traceback: {traceback.format_exc()}")
        return {
            "text": f"AI mein error: {str(e)[:100]}. Thodi der baad try karein.",
            "tool_calls": [],
            "conversation_id": conversation_id
        }


def continue_with_tool_results(
    tool_results: list[dict],
    conversation_id: str,
    original_messages: list[dict] = None
) -> dict:
    """
    Continue conversation after tool execution with results.

    Args:
        tool_results: Results from executed tools
        conversation_id: Conversation ID for tracking
        original_messages: Original messages to continue from

    Returns:
        dict containing final AI response
    """
    try:
        co = get_cohere_client()
        if co is None:
            # Format tool results as a simple response
            results_text = []
            for tr in tool_results:
                call_info = tr.get("call", {})
                outputs = tr.get("outputs", [{}])
                result = outputs[0] if outputs else {}

                if result.get("status") == "success":
                    if call_info.get("name") == "add_task":
                        results_text.append(f"Task '{result.get('title')}' add ho gaya!")
                    elif call_info.get("name") == "list_tasks":
                        tasks = result.get("tasks", [])
                        if tasks:
                            task_lines = [f"  {i+1}. {t['title']} {'✓' if t['completed'] else '○'}" for i, t in enumerate(tasks)]
                            results_text.append(f"Aapke tasks:\n" + "\n".join(task_lines))
                        else:
                            results_text.append("Abhi koi task nahi hai.")
                    elif call_info.get("name") == "complete_task":
                        results_text.append(f"Task '{result.get('title')}' complete ho gaya! 🎉")
                    elif call_info.get("name") == "delete_task":
                        results_text.append(f"Task '{result.get('title')}' delete ho gaya.")
                    else:
                        results_text.append(result.get("message", "Done!"))
                else:
                    results_text.append(result.get("message", "Kuch problem ho gayi."))

            return {
                "text": "\n".join(results_text) if results_text else "Kaam ho gaya!",
                "tool_calls": [],
                "conversation_id": conversation_id
            }

        # Build messages with tool results for V2 API
        import json
        messages = [{"role": "system", "content": SYSTEM_PREAMBLE}]

        # Add tool results as assistant tool_call + tool response
        for tr in tool_results:
            call_info = tr.get("call", {})
            outputs = tr.get("outputs", [{}])

            # Add assistant message with tool call
            messages.append({
                "role": "assistant",
                "tool_calls": [{
                    "id": call_info.get("id", "tool_1"),
                    "type": "function",
                    "function": {
                        "name": call_info.get("name", "unknown"),
                        "arguments": json.dumps(call_info.get("parameters", {}))
                    }
                }]
            })

            # Add tool result message
            messages.append({
                "role": "tool",
                "tool_call_id": call_info.get("id", "tool_1"),
                "content": json.dumps(outputs[0] if outputs else {})
            })

        response = co.chat(
            model="command-a-03-2025",
            messages=messages
        )

        # Extract text from response
        response_text = ""
        if response.message and response.message.content:
            for content_item in response.message.content:
                if hasattr(content_item, 'text'):
                    response_text += content_item.text

        return {
            "text": response_text or "Kaam ho gaya!",
            "tool_calls": [],
            "conversation_id": conversation_id
        }
    except Exception as e:
        import traceback
        print(f"[COHERE] Error in continue_with_tool_results: {e}")
        print(f"[COHERE] Traceback: {traceback.format_exc()}")

        # Fallback: format tool results directly
        results_text = []
        for tr in tool_results:
            outputs = tr.get("outputs", [{}])
            result = outputs[0] if outputs else {}
            if result.get("message"):
                results_text.append(result["message"])

        return {
            "text": "\n".join(results_text) if results_text else "Kaam ho gaya!",
            "tool_calls": [],
            "conversation_id": conversation_id
        }
