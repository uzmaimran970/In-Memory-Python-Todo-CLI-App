"""TodoManager - Business logic for task management."""

from typing import Optional
from src.models.task import Task, TaskNotFoundError, InvalidInputError


class TodoManager:
    """Manages in-memory todo tasks with CRUD operations.

    This class maintains task storage and provides methods for adding, retrieving,
    updating, deleting, and toggling task completion status. All task IDs are
    auto-generated sequential integers starting from 1.

    Attributes:
        _tasks: Internal dictionary mapping task IDs to Task objects
        _next_id: Counter for generating the next unique task ID
    """

    def __init__(self):
        """Initialize empty task storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> int:
        """Add a new task to the manager.

        Args:
            title: Task title (required, non-empty, max 200 chars)
            description: Task description (optional, max 1000 chars)

        Returns:
            The ID of the newly created task

        Raises:
            InvalidInputError: If title is empty or exceeds length limits
        """
        # Validation
        if not title or not title.strip():
            raise InvalidInputError("Title cannot be empty")
        if len(title) > 200:
            raise InvalidInputError("Title cannot exceed 200 characters")
        if len(description) > 1000:
            raise InvalidInputError("Description cannot exceed 1000 characters")

        # Create and store task
        task_id = self._next_id
        task = Task(
            id=task_id,
            title=title.strip(),
            description=description,
            completed=False
        )
        self._tasks[task_id] = task
        self._next_id += 1

        return task_id

    def get_task(self, task_id: int) -> Task:
        """Retrieve a task by ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The task object

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks.

        Returns:
            List of all tasks, ordered by ID (ascending)
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """Update task title and/or description.

        Args:
            task_id: The ID of the task to update
            title: New title (if provided)
            description: New description (if provided)

        Raises:
            TaskNotFoundError: If task_id doesn't exist
            InvalidInputError: If validation fails or no fields provided
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        if title is None and description is None:
            raise InvalidInputError("At least one field (title or description) must be provided")

        task = self._tasks[task_id]

        # Update title if provided
        if title is not None:
            if not title or not title.strip():
                raise InvalidInputError("Title cannot be empty")
            if len(title) > 200:
                raise InvalidInputError("Title cannot exceed 200 characters")
            task.title = title.strip()

        # Update description if provided
        if description is not None:
            if len(description) > 1000:
                raise InvalidInputError("Description cannot exceed 1000 characters")
            task.description = description

    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID.

        Args:
            task_id: The ID of the task to delete

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def toggle_completion(self, task_id: int) -> bool:
        """Toggle task completion status.

        Args:
            task_id: The ID of the task to toggle

        Returns:
            The new completion status

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        task = self._tasks[task_id]
        task.completed = not task.completed
        return task.completed

    def task_count(self) -> int:
        """Get the total number of tasks.

        Returns:
            Number of tasks currently stored
        """
        return len(self._tasks)
