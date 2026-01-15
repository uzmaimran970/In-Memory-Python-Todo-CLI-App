"""
Cohere API Client for TodoAI Chatbot
Handles AI generation with tool calling support for task management
"""
import cohere
import os
import json
from typing import Optional
from app.config import settings

# Lazy load Cohere client to prevent startup crashes
_cohere_client = None

def get_cohere_client():
    """Get or create Cohere client with lazy initialization."""
    global _cohere_client
    if _cohere_client is None:
        api_key = settings.cohere_api_key
        if not api_key:
            print("[COHERE] WARNING: COHERE_API_KEY not set in settings!")
            return None
        try:
            _cohere_client = cohere.Client(api_key=api_key)
            print(f"[COHERE] Client initialized successfully")
        except Exception as e:
            print(f"[COHERE] Failed to initialize client: {e}")
            return None
    return _cohere_client

# System preamble defining TodoAI personality and capabilities
SYSTEM_PREAMBLE = """You are TodoAI. You MUST use tools for ALL task operations.

RULE: When user mentions ANY task action, ALWAYS call the tool. No exceptions!

TRIGGER WORDS → TOOL TO CALL:
- "add", "create", "banana", "likh" → add_task(title=...)
- "complete", "done", "hogya", "khatam", "finish", "mark" → complete_task(task_id=...)
- "delete", "remove", "hata", "nikaal" → delete_task(task_id=...)
- "show", "list", "dikhao", "batao", "dekh" → list_tasks()
- "update", "change", "edit" → update_task(task_id=...)

IMPORTANT: Even if user says "hogya hai" (past tense), they want you to MARK it complete. Call complete_task!

EXAMPLES:
- "task 5 complete hogya" → call complete_task(task_id="5")
- "task 3 ho gaya" → call complete_task(task_id="3")
- "doodh lana hai" → call add_task(title="doodh lana hai")
- "mere tasks" → call list_tasks()

LANGUAGE: Match user (Roman Urdu/English).
"""

# MCP Tool definitions for Cohere's tool calling
MCP_TOOLS = [
    {
        "name": "add_task",
        "description": "Create a new task. Use when user wants to add/create/remember something.",
        "parameter_definitions": {
            "title": {"type": "str", "description": "Task title (required)", "required": True},
            "description": {"type": "str", "description": "Task details (optional)", "required": False}
        }
    },
    {
        "name": "list_tasks",
        "description": "Get user's tasks. Use when user asks to see/show/list tasks.",
        "parameter_definitions": {
            "status": {"type": "str", "description": "Filter: all, pending, or completed", "required": False}
        }
    },
    {
        "name": "complete_task",
        "description": "Mark task as done. Use when user says task is finished/done/complete.",
        "parameter_definitions": {
            "task_id": {"type": "int", "description": "Task ID number to complete", "required": True}
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task permanently. Always confirm before using.",
        "parameter_definitions": {
            "task_id": {"type": "int", "description": "Task ID number to delete", "required": True}
        }
    },
    {
        "name": "update_task",
        "description": "Update/edit task title or description.",
        "parameter_definitions": {
            "task_id": {"type": "int", "description": "Task ID to update", "required": True},
            "title": {"type": "str", "description": "New title", "required": False},
            "description": {"type": "str", "description": "New description", "required": False}
        }
    },
    {
        "name": "get_user_info",
        "description": "Get user profile and task statistics.",
        "parameter_definitions": {}
    }
]

# Models to try - in order of preference with fallbacks
MODELS_TO_TRY = [
    "command",                 # Basic command model (fallback)
]


def chat_with_tools(
    message: str,
    chat_history: list[dict],
    conversation_id: Optional[str] = None
) -> dict:
    """
    Send a message to Cohere with tool calling support.
    """
    co = get_cohere_client()
    if co is None:
        return {
            "text": "AI service configure nahi hai. Please try again later.",
            "tool_calls": [],
            "conversation_id": conversation_id
        }

    # Prepare chat history in the correct format
    formatted_history = []
    for msg in chat_history:
        role = "USER" if msg.get("role") == "USER" else "CHATBOT"
        content = msg.get("message", "")
        if content:
            formatted_history.append({"role": role, "message": content})

    print(f"[COHERE] Processing: {message[:50]}...")

    # Try models in order
    last_error = None
    for model in MODELS_TO_TRY:
        try:
            print(f"[COHERE] Trying model: {model}")
            response = co.chat(
                model=model,
                message=message,
                chat_history=formatted_history,
                preamble=SYSTEM_PREAMBLE,
                tools=MCP_TOOLS
            )
            print(f"[COHERE] Success with {model}, finish_reason: {response.finish_reason}")

            # Extract response text
            response_text = response.text or ""

            # Extract tool calls
            tool_calls = []
            if response.tool_calls:
                for tc in response.tool_calls:
                    tool_calls.append({
                        "name": tc.name,
                        "parameters": tc.parameters
                    })
                print(f"[COHERE] Tool calls: {[t['name'] for t in tool_calls]}")

            return {
                "text": response_text,
                "tool_calls": tool_calls,
                "conversation_id": response.conversation_id or conversation_id or "default"
            }

        except Exception as e:
            last_error = str(e)
            print(f"[COHERE] Model {model} failed: {e}")
            continue

    # All models failed - provide a fallback response
    print(f"[COHERE] All models failed. Providing fallback response.")

    # Simple fallback logic for common queries
    message_lower = message.lower()

    if any(word in message_lower for word in ["hello", "hi", "hey", "namaste"]):
        fallback_text = "Hello! I am TodoAI, your task management assistant. How can I help you with your tasks today?"
    elif any(word in message_lower for word in ["task", "add", "create"]):
        fallback_text = "I can help you add tasks. Please provide the task title and description."
    elif any(word in message_lower for word in ["list", "show", "view", "my"]):
        fallback_text = "I can show your tasks. You can ask me to list your pending or completed tasks."
    elif any(word in message_lower for word in ["complete", "done", "finish"]):
        fallback_text = "I can mark tasks as complete. Please specify which task you want to mark as done."
    elif any(word in message_lower for word in ["delete", "remove"]):
        fallback_text = "I can delete tasks. Please specify which task you want to delete."
    else:
        fallback_text = "I'm your task management assistant. I can help you add, list, complete, or delete tasks. How can I assist you today?"

    return {
        "text": fallback_text,
        "tool_calls": [],
        "conversation_id": conversation_id or "default"
    }


def continue_with_tool_results(
    tool_results: list[dict],
    conversation_id: str,
    original_messages: list[dict] = None
) -> dict:
    """
    Continue conversation after tool execution with results.
    Format results nicely for user.
    """
    # Format tool results as human-readable response
    results_text = []

    for tr in tool_results:
        call_info = tr.get("call", {})
        outputs = tr.get("outputs", [{}])
        result = outputs[0] if outputs else {}
        tool_name = call_info.get("name", "")

        if result.get("status") == "success":
            if tool_name == "add_task":
                title = result.get("title", "task")
                results_text.append(f"Task '{title}' add ho gaya! ✓")

            elif tool_name == "list_tasks":
                tasks = result.get("tasks", [])
                if tasks:
                    lines = [f"\nAapke tasks ({len(tasks)}):"]
                    for i, t in enumerate(tasks, 1):
                        status = "✓" if t.get("completed") else "○"
                        lines.append(f"  {i}. [{t.get('id')}] {t.get('title')} {status}")
                    results_text.append("\n".join(lines))
                else:
                    results_text.append("Abhi koi task nahi hai. Naya task add karein!")

            elif tool_name == "complete_task":
                title = result.get("title", "task")
                results_text.append(f"Task '{title}' complete ho gaya! 🎉 Shabash!")

            elif tool_name == "delete_task":
                title = result.get("title", "task")
                results_text.append(f"Task '{title}' delete ho gaya. ✓")

            elif tool_name == "update_task":
                results_text.append(f"Task update ho gaya! ✓")

            elif tool_name == "get_user_info":
                user = result.get("user", {})
                stats = result.get("stats", {})
                name = user.get("name", "User")
                total = stats.get("total_tasks", 0)
                pending = stats.get("pending_tasks", 0)
                completed = stats.get("completed_tasks", 0)
                results_text.append(
                    f"Hello {name}!\n"
                    f"Total tasks: {total}\n"
                    f"Pending: {pending} | Completed: {completed}"
                )
            else:
                msg = result.get("message", "Done!")
                results_text.append(msg)
        else:
            # Error case
            error_msg = result.get("message", "Kuch problem ho gayi.")
            results_text.append(f"⚠️ {error_msg}")

    final_text = "\n".join(results_text) if results_text else "Kaam ho gaya!"

    return {
        "text": final_text,
        "tool_calls": [],
        "conversation_id": conversation_id
    }
