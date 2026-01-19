"""
MCP Skills Package - Todo App Phase 3
=====================================

Yeh package saare MCP skills contain karta hai.

Available Skills:
- add_task: Naya task create karna ✅
- list_tasks: Tasks fetch karna ✅
- complete_task: Task complete karna ✅
- delete_task: Task delete karna ✅
- update_task: Task update karna ✅

ALL 5 SKILLS COMPLETE! 🎉

Usage:
    from skills import (
        add_task, AddTaskInput, AddTaskOutput,
        list_tasks, ListTasksInput, ListTasksOutput,
        complete_task, CompleteTaskInput, CompleteTaskOutput,
        delete_task, DeleteTaskInput, DeleteTaskOutput,
        update_task, UpdateTaskInput, UpdateTaskOutput
    )

    # Add task
    result = add_task(AddTaskInput(
        user_id="user123",
        title="Buy groceries",
        description="Milk, eggs"
    ))

    # List tasks
    result = list_tasks(ListTasksInput(
        user_id="user123",
        status="pending"
    ))

    # Complete task
    result = complete_task(CompleteTaskInput(
        user_id="user123",
        task_id=3
    ))

    # Delete task (⚠️ PERMANENT!)
    result = delete_task(DeleteTaskInput(
        user_id="user123",
        task_id=2
    ))

    # Update task
    result = update_task(UpdateTaskInput(
        user_id="user123",
        task_id=1,
        title="Updated title"
    ))
"""

from .add_task import (
    add_task,
    add_task_async,
    AddTaskInput,
    AddTaskOutput,
    ADD_TASK_SCHEMA,
    handle_add_task_tool,
    get_skill_schema as get_add_task_schema,
    get_skill_info as get_add_task_info
)

from .list_tasks import (
    list_tasks,
    list_tasks_async,
    ListTasksInput,
    ListTasksOutput,
    TaskItem,
    LIST_TASKS_SCHEMA,
    handle_list_tasks_tool,
    get_skill_schema as get_list_tasks_schema,
    get_skill_info as get_list_tasks_info
)

from .complete_task import (
    complete_task,
    complete_task_async,
    toggle_task_async,
    CompleteTaskInput,
    CompleteTaskOutput,
    COMPLETE_TASK_SCHEMA,
    handle_complete_task_tool,
    get_skill_schema as get_complete_task_schema,
    get_skill_info as get_complete_task_info
)

from .delete_task import (
    delete_task,
    delete_task_async,
    DeleteTaskInput,
    DeleteTaskOutput,
    DELETE_TASK_SCHEMA,
    handle_delete_task_tool,
    get_skill_schema as get_delete_task_schema,
    get_skill_info as get_delete_task_info
)

from .update_task import (
    update_task,
    update_task_async,
    UpdateTaskInput,
    UpdateTaskOutput,
    UPDATE_TASK_SCHEMA,
    handle_update_task_tool,
    get_skill_schema as get_update_task_schema,
    get_skill_info as get_update_task_info
)

__all__ = [
    # add_task skill
    "add_task",
    "add_task_async",
    "AddTaskInput",
    "AddTaskOutput",
    "ADD_TASK_SCHEMA",
    "handle_add_task_tool",
    "get_add_task_schema",
    "get_add_task_info",

    # list_tasks skill
    "list_tasks",
    "list_tasks_async",
    "ListTasksInput",
    "ListTasksOutput",
    "TaskItem",
    "LIST_TASKS_SCHEMA",
    "handle_list_tasks_tool",
    "get_list_tasks_schema",
    "get_list_tasks_info",

    # complete_task skill
    "complete_task",
    "complete_task_async",
    "toggle_task_async",
    "CompleteTaskInput",
    "CompleteTaskOutput",
    "COMPLETE_TASK_SCHEMA",
    "handle_complete_task_tool",
    "get_complete_task_schema",
    "get_complete_task_info",

    # delete_task skill
    "delete_task",
    "delete_task_async",
    "DeleteTaskInput",
    "DeleteTaskOutput",
    "DELETE_TASK_SCHEMA",
    "handle_delete_task_tool",
    "get_delete_task_schema",
    "get_delete_task_info",

    # update_task skill
    "update_task",
    "update_task_async",
    "UpdateTaskInput",
    "UpdateTaskOutput",
    "UPDATE_TASK_SCHEMA",
    "handle_update_task_tool",
    "get_update_task_schema",
    "get_update_task_info",
]

__version__ = "1.0.0"
