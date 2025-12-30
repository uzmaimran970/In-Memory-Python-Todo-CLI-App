"""Task data model and exceptions for todo application."""

from dataclasses import dataclass


# Exception hierarchy (T004, T005, T006)
class TodoError(Exception):
    """Base exception for all todo application errors."""
    pass


class TaskNotFoundError(TodoError):
    """Raised when attempting to access a task that doesn't exist."""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")


class InvalidInputError(TodoError):
    """Raised when input validation fails."""
    pass


# Task dataclass (T007, T008)
@dataclass
class Task:
    """Represents a todo task with unique ID, title, description, and completion status.

    Attributes:
        id: Unique sequential integer identifier (starting from 1)
        title: Short summary of the task (non-empty, max 200 characters)
        description: Detailed information about the task (max 1000 characters)
        completed: Boolean flag indicating completion status (default: False)
    """
    id: int
    title: str
    description: str
    completed: bool = False

    def __post_init__(self):
        """Validate task data after initialization.

        Raises:
            ValueError: If validation fails for any field
        """
        # Validate ID
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("Task ID must be a positive integer")

        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")

        # Validate description
        if len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
