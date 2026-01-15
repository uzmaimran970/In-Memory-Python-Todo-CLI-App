"""
Cohere API Client for TodoAI Chatbot
Handles AI generation with tool calling support for task management
"""
import cohere
import os
import json
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
        try:
            _cohere_client = cohere.ClientV2(api_key=api_key)
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
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task. Use when user wants to add/create/remember something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title (required)"},
                    "description": {"type": "string", "description": "Task details (optional)"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Get user's tasks. Use when user asks to see/show/list tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter: all, pending, or completed"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark task as done. Use when user says task is finished/done/complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID number to complete"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task permanently. Always confirm before using.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID number to delete"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update/edit task title or description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to update"},
                    "title": {"type": "string", "description": "New title"},
                    "description": {"type": "string", "description": "New description"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_info",
            "description": "Get user profile and task statistics.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Models to try - only use currently available models
MODELS_TO_TRY = [
    "command-a-03-2025",  # Current working model
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

    # Build messages in V2 format
    messages = [{"role": "system", "content": SYSTEM_PREAMBLE}]

    # Add chat history
    for msg in chat_history:
        role = "user" if msg.get("role") == "USER" else "assistant"
        content = msg.get("message", "")
        if content:
            messages.append({"role": role, "content": content})

    # Add current message
    messages.append({"role": "user", "content": message})

    print(f"[COHERE] Processing: {message[:50]}...")

    # Try models in order
    last_error = None
    for model in MODELS_TO_TRY:
        try:
            print(f"[COHERE] Trying model: {model}")
            response = co.chat(
                model=model,
                messages=messages,
                tools=MCP_TOOLS
            )
            print(f"[COHERE] Success with {model}, finish_reason: {response.finish_reason}")

            # Extract response text
            response_text = ""
            tool_calls = []

            if response.message and response.message.content:
                for item in response.message.content:
                    if hasattr(item, 'text'):
                        response_text += item.text

            # Extract tool calls
            if response.message and response.message.tool_calls:
                for tc in response.message.tool_calls:
                    params = tc.function.arguments
                    if isinstance(params, str):
                        try:
                            params = json.loads(params)
                        except:
                            params = {}
                    tool_calls.append({
                        "name": tc.function.name,
                        "parameters": params,
                        "id": getattr(tc, 'id', 'tool_1')
                    })
                print(f"[COHERE] Tool calls: {[t['name'] for t in tool_calls]}")

            return {
                "text": response_text,
                "tool_calls": tool_calls,
                "conversation_id": conversation_id or "default"
            }

        except Exception as e:
            last_error = str(e)
            print(f"[COHERE] Model {model} failed: {e}")
            continue

    # All models failed
    print(f"[COHERE] All models failed. Last error: {last_error}")
    return {
        "text": f"AI temporarily unavailable. Error: {last_error[:100] if last_error else 'Unknown'}",
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
