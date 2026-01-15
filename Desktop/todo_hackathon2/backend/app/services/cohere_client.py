"""
Cohere API Client for TodoAI Chatbot
Handles AI generation with tool calling support for task management
"""
from cohere import Client
from app.config import settings
from typing import Optional

if not settings.cohere_api_key:
    raise ValueError("COHERE_API_KEY missing! Check .env file or Railway variables.")

cohere_client = Client(api_key=settings.cohere_api_key)

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
        # Use the global client directly
        co = cohere_client

        # Try different models in order of preference
        models_to_try = ["command-r", "command", "command-light", "command-nightly"]
        response = None

        for model in models_to_try:
            try:
                response = co.chat(
                    model=model,
                    message=message,
                    preamble=SYSTEM_PREAMBLE,
                    chat_history=chat_history,
                    tools=MCP_TOOLS,
                    conversation_id=conversation_id
                )
                # If successful, break out of loop
                break
            except Exception as model_error:
                print(f"[COHERE] Model {model} not available: {model_error}")
                continue

        # If no model worked, return error message
        if response is None:
            print("[COHERE] No models available for chat_with_tools")
            return {
                "text": "AI service abhi available nahi hai. Kuch models available nahi hain.",
                "tool_calls": [],
                "conversation_id": conversation_id
            }

        return {
            "text": response.text or "",
            "tool_calls": [
                {
                    "name": tc.name,
                    "parameters": tc.parameters
                }
                for tc in (response.tool_calls or [])
            ],
            "conversation_id": response.conversation_id
        }
    except Exception as e:
        print(f"[COHERE] Error in chat_with_tools: {e}")
        return {
            "text": "Maaf kijiye, abhi AI service mein problem hai. Thodi der baad try karein.",
            "tool_calls": [],
            "conversation_id": conversation_id
        }


def continue_with_tool_results(
    tool_results: list[dict],
    conversation_id: str
) -> dict:
    """
    Continue conversation after tool execution with results.

    Args:
        tool_results: Results from executed tools
        conversation_id: Cohere conversation ID to continue

    Returns:
        dict containing final AI response
    """
    try:
        # Use the global client directly
        co = cohere_client

        # Try different models in order of preference
        models_to_try = ["command-r", "command", "command-light", "command-nightly"]
        response = None

        for model in models_to_try:
            try:
                response = co.chat(
                    model=model,
                    message="",
                    preamble=SYSTEM_PREAMBLE,
                    tool_results=tool_results,
                    conversation_id=conversation_id
                )
                # If successful, break out of loop
                break
            except Exception as model_error:
                print(f"[COHERE] Model {model} not available for continue_with_tool_results: {model_error}")
                continue

        # If no model worked, return error message
        if response is None:
            print("[COHERE] No models available for continue_with_tool_results")
            return {
                "text": "Tool execute ho gaya, lekin response mein problem aa gayi.",
                "tool_calls": [],
                "conversation_id": conversation_id
            }

        return {
            "text": response.text or "",
            "tool_calls": [],
            "conversation_id": response.conversation_id
        }
    except Exception as e:
        print(f"[COHERE] Error in continue_with_tool_results: {e}")
        return {
            "text": "Tool execute ho gaya, lekin response mein problem aa gayi.",
            "tool_calls": [],
            "conversation_id": conversation_id
        }
