"""
Chat Service for TodoAI Chatbot
Handles message processing, conversation management, and tool execution
"""
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from app.models import Conversation, Message, MessageRole, Task, User
from app.services.cohere_client import chat_with_tools, continue_with_tool_results


async def get_or_create_conversation(user_id: str, session: Session) -> Conversation:
    """
    Get existing conversation for user or create new one.
    Each user has exactly one conversation (simplified model).

    Args:
        user_id: Authenticated user ID
        session: Database session

    Returns:
        Conversation object
    """
    conversation = session.exec(
        select(Conversation).where(Conversation.user_id == user_id)
    ).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation


async def get_chat_history(
    conversation_id: str,
    session: Session,
    limit: int = 20
) -> list[dict]:
    """
    Get recent messages formatted for Cohere API.

    Args:
        conversation_id: Conversation ID
        session: Database session
        limit: Maximum messages to return (default 20)

    Returns:
        List of message dicts formatted for Cohere chat_history
    """
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()

    # Reverse to chronological order and format for Cohere
    return [
        {
            "role": "USER" if msg.role == MessageRole.USER else "CHATBOT",
            "message": msg.content
        }
        for msg in reversed(messages)
    ]


async def save_message(
    conversation_id: str,
    role: MessageRole,
    content: str,
    tool_calls: Optional[dict],
    session: Session
) -> Message:
    """
    Save a message to the database.

    Args:
        conversation_id: Parent conversation ID
        role: USER or ASSISTANT
        content: Message text
        tool_calls: Tool calls made (for assistant messages)
        session: Database session

    Returns:
        Saved Message object
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()

    session.commit()
    session.refresh(message)
    return message


async def execute_tool(
    tool_name: str,
    parameters: dict,
    user_id: str,
    session: Session
) -> dict:
    """
    Execute an MCP skill/tool and return the result.

    Args:
        tool_name: Name of the tool to execute
        parameters: Tool parameters from Cohere
        user_id: Authenticated user ID (for ownership)
        session: Database session

    Returns:
        dict with execution result
    """
    try:
        if tool_name == "add_task":
            # Create new task
            title = parameters.get("title", "")
            description = parameters.get("description")

            if not title:
                return {"status": "error", "message": "Task title is required"}

            new_task = Task(
                user_id=user_id,
                title=title,
                description=description,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            return {
                "status": "success",
                "task_id": new_task.id,
                "title": new_task.title,
                "message": f"Task '{title}' created successfully"
            }

        elif tool_name == "list_tasks":
            # Get user's tasks
            status_filter = parameters.get("status", "all")

            query = select(Task).where(Task.user_id == user_id)

            if status_filter == "pending":
                query = query.where(Task.completed == False)
            elif status_filter == "completed":
                query = query.where(Task.completed == True)

            query = query.order_by(Task.created_at.desc())
            tasks = session.exec(query).all()

            task_list = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed
                }
                for t in tasks
            ]

            return {
                "status": "success",
                "tasks": task_list,
                "total": len(tasks),
                "filter": status_filter
            }

        elif tool_name == "complete_task":
            # Mark task as complete
            task_id = parameters.get("task_id")
            if not task_id:
                return {"status": "error", "message": "Task ID is required"}

            task = session.get(Task, task_id)
            if not task:
                return {"status": "error", "message": f"Task {task_id} not found"}

            if task.user_id != user_id:
                return {"status": "error", "message": "Not authorized to modify this task"}

            if task.completed:
                return {
                    "status": "info",
                    "message": f"Task '{task.title}' is already completed"
                }

            task.completed = True
            task.updated_at = datetime.utcnow()
            session.commit()

            return {
                "status": "success",
                "task_id": task_id,
                "title": task.title,
                "message": f"Task '{task.title}' marked as complete"
            }

        elif tool_name == "delete_task":
            # Delete task
            task_id = parameters.get("task_id")
            if not task_id:
                return {"status": "error", "message": "Task ID is required"}

            task = session.get(Task, task_id)
            if not task:
                return {"status": "error", "message": f"Task {task_id} not found"}

            if task.user_id != user_id:
                return {"status": "error", "message": "Not authorized to delete this task"}

            title = task.title
            session.delete(task)
            session.commit()

            return {
                "status": "success",
                "task_id": task_id,
                "title": title,
                "message": f"Task '{title}' deleted successfully"
            }

        elif tool_name == "update_task":
            # Update task
            task_id = parameters.get("task_id")
            new_title = parameters.get("title")
            new_description = parameters.get("description")

            if not task_id:
                return {"status": "error", "message": "Task ID is required"}

            task = session.get(Task, task_id)
            if not task:
                return {"status": "error", "message": f"Task {task_id} not found"}

            if task.user_id != user_id:
                return {"status": "error", "message": "Not authorized to modify this task"}

            old_title = task.title
            if new_title:
                task.title = new_title
            if new_description is not None:
                task.description = new_description

            task.updated_at = datetime.utcnow()
            session.commit()

            return {
                "status": "success",
                "task_id": task_id,
                "old_title": old_title,
                "new_title": task.title,
                "message": f"Task updated successfully"
            }

        elif tool_name == "get_user_info":
            # Get user profile and stats
            user = session.exec(
                select(User).where(User.id == user_id)
            ).first()

            # Count tasks
            all_tasks = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            pending_count = sum(1 for t in all_tasks if not t.completed)
            completed_count = sum(1 for t in all_tasks if t.completed)

            return {
                "status": "success",
                "user": {
                    "name": user.name if user else "User",
                    "email": user.email if user else None
                },
                "stats": {
                    "total_tasks": len(all_tasks),
                    "pending_tasks": pending_count,
                    "completed_tasks": completed_count
                }
            }

        else:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    except Exception as e:
        print(f"[CHAT SERVICE] Tool execution error: {e}")
        return {"status": "error", "message": str(e)}


async def process_chat_message(
    user_id: str,
    message: str,
    session: Session
) -> dict:
    """
    Process a user's chat message through the AI and execute any tool calls.

    Args:
        user_id: Authenticated user ID
        message: User's message text
        session: Database session

    Returns:
        dict containing:
        - response: AI response text
        - conversation_id: Conversation ID
        - tool_calls: List of executed tools with results
    """
    # Get or create conversation
    conversation = await get_or_create_conversation(user_id, session)

    # Load chat history for context
    history = await get_chat_history(conversation.id, session)

    # Save user message
    await save_message(conversation.id, MessageRole.USER, message, None, session)

    # Call Cohere with tools
    ai_response = chat_with_tools(message, history, conversation.id)

    # Execute tool calls if any
    tool_results = []
    executed_tools = []

    if ai_response["tool_calls"]:
        for tool_call in ai_response["tool_calls"]:
            result = await execute_tool(
                tool_call["name"],
                tool_call["parameters"],
                user_id,
                session
            )
            tool_results.append({
                "call": tool_call,
                "outputs": [result]
            })
            executed_tools.append({
                "name": tool_call["name"],
                "result": result
            })

        # Continue conversation with tool results
        final_response = continue_with_tool_results(
            tool_results,
            ai_response["conversation_id"]
        )
        response_text = final_response["text"]
    else:
        response_text = ai_response["text"]

    # Ensure we have a response
    if not response_text:
        response_text = "Main aapki madad ke liye hazir hoon. Kya karna chahte hain?"

    # Save assistant response
    await save_message(
        conversation.id,
        MessageRole.ASSISTANT,
        response_text,
        {"tool_calls": executed_tools} if executed_tools else None,
        session
    )

    return {
        "response": response_text,
        "conversation_id": conversation.id,
        "tool_calls": executed_tools
    }
