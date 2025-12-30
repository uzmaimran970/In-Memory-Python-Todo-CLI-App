# Data Model: Todo Console Application

**Feature**: In-Memory Python Todo Console Application
**Date**: 2025-12-30
**Purpose**: Define entities, relationships, and state management

## Entities

### Task

**Description**: Represents a single todo item that a user wants to track.

**Attributes**:

| Field | Type | Required | Default | Validation | Description |
|-------|------|----------|---------|------------|-------------|
| `id` | `int` | Yes | Auto-generated | > 0, unique | Sequential identifier starting from 1 |
| `title` | `str` | Yes | N/A | Non-empty, max 200 chars | Short summary of the task |
| `description` | `str` | Yes | Empty string | Max 1000 chars | Detailed information about the task |
| `completed` | `bool` | Yes | `False` | N/A | Completion status of the task |

**Invariants**:
- ID is immutable once assigned
- ID must be unique across all tasks (even deleted ones - IDs are never reused)
- Title cannot be empty string or whitespace-only
- Description can be empty (default)

**Implementation**:
```python
from dataclasses import dataclass

@dataclass
class Task:
    """Represents a todo task with unique ID, title, description, and completion status."""
    id: int
    title: str
    description: str
    completed: bool = False

    def __post_init__(self):
        """Validate task data after initialization."""
        if not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("Task ID must be a positive integer")
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        if len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
```

---

## State Management

### TodoManager

**Description**: Central manager for all task operations. Maintains in-memory task storage and provides CRUD operations.

**State**:

| Attribute | Type | Description |
|-----------|------|-------------|
| `_tasks` | `dict[int, Task]` | Internal storage mapping task IDs to Task objects |
| `_next_id` | `int` | Counter for generating next unique task ID |

**State Transitions**:

```
[Empty State]
    ↓ add_task()
[Tasks Exist] ←→ update_task() / toggle_completion()
    ↓ delete_task()
[Empty State] (if last task deleted)
```

**Operations Interface**:

| Method | Inputs | Outputs | Side Effects | Exceptions |
|--------|--------|---------|--------------|------------|
| `add_task(title, description)` | title: str, description: str = "" | int (new task ID) | Increments `_next_id`, adds Task to `_tasks` | `InvalidInputError` if validation fails |
| `get_task(task_id)` | task_id: int | Task | None | `TaskNotFoundError` if ID doesn't exist |
| `get_all_tasks()` | None | list[Task] | None | Never raises |
| `update_task(task_id, title, description)` | task_id: int, title: str \| None, description: str \| None | None | Modifies Task in `_tasks` | `TaskNotFoundError`, `InvalidInputError` |
| `delete_task(task_id)` | task_id: int | None | Removes Task from `_tasks` | `TaskNotFoundError` |
| `toggle_completion(task_id)` | task_id: int | bool (new status) | Modifies Task.completed in `_tasks` | `TaskNotFoundError` |
| `task_count()` | None | int | None | Never raises |

---

## Relationships

**No relationships**: Tasks are independent entities. No parent-child, tag, category, or user relationships in Phase 1.

---

## Data Validation Rules

### Input Validation (performed by TodoManager before creating/updating Task)

**Title Validation**:
- MUST NOT be None
- MUST NOT be empty string
- MUST NOT be whitespace-only (e.g., "   ")
- MUST be ≤ 200 characters after stripping whitespace
- Special characters and Unicode ARE allowed

**Description Validation**:
- CAN be None (defaults to empty string)
- CAN be empty string
- MUST be ≤ 1000 characters
- Special characters and Unicode ARE allowed

**Task ID Validation** (for operations):
- MUST be an integer
- MUST exist in `_tasks` dictionary
- Non-existent IDs raise `TaskNotFoundError`

### Edge Case Handling

| Scenario | Behavior |
|----------|----------|
| Empty title provided | Raise `InvalidInputError("Title cannot be empty")` |
| Title with only spaces ("   ") | Strip spaces → Raise `InvalidInputError` if empty after strip |
| Very long title (201+ chars) | Raise `InvalidInputError("Title cannot exceed 200 characters")` |
| Very long description (1001+ chars) | Raise `InvalidInputError("Description cannot exceed 1000 characters")` |
| Update with both title and description None | Raise `InvalidInputError("At least one field must be provided for update")` |
| Delete non-existent task | Raise `TaskNotFoundError(f"Task {task_id} not found")` |
| Toggle non-existent task | Raise `TaskNotFoundError(f"Task {task_id} not found")` |
| Rapid task creation (100 tasks) | All succeed with unique IDs; counter increments correctly |

---

## Storage Strategy

### In-Memory Storage

**Data Structure**: Python dictionary (`dict[int, Task]`)

**Rationale**:
- O(1) lookup by task ID (required for update, delete, toggle operations)
- O(n) iteration for listing all tasks (acceptable for hackathon scale)
- Native Python structure, no external dependencies
- Easy to test and reason about

**Capacity**: No hard limit. Spec requires handling 100 tasks (SC-004), which is trivial for in-memory dict.

**Persistence**: NONE. All data lost on application exit (per FR-011).

**Concurrency**: Not required. Single-user, single-threaded application (per assumptions).

---

## Exception Hierarchy

```python
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
```

**Usage**:
- Business logic layer (TodoManager) raises these exceptions
- CLI layer catches and displays user-friendly messages
- All exceptions inherit from `TodoError` for easy catch-all handling if needed

---

## Complete TodoManager Implementation Specification

```python
from typing import Optional

class TodoManager:
    """Manages in-memory todo tasks with CRUD operations."""

    def __init__(self):
        """Initialize empty task storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> int:
        """
        Add a new task to the manager.

        Args:
            title: Task title (required, non-empty, max 200 chars)
            description: Task description (optional, max 1000 chars)

        Returns:
            int: The ID of the newly created task

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
        """
        Retrieve a task by ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Task: The task object

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def get_all_tasks(self) -> list[Task]:
        """
        Retrieve all tasks.

        Returns:
            list[Task]: List of all tasks, ordered by ID
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Update task title and/or description.

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
        """
        Delete a task by ID.

        Args:
            task_id: The ID of the task to delete

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def toggle_completion(self, task_id: int) -> bool:
        """
        Toggle task completion status.

        Args:
            task_id: The ID of the task to toggle

        Returns:
            bool: The new completion status

        Raises:
            TaskNotFoundError: If task_id doesn't exist
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        task = self._tasks[task_id]
        task.completed = not task.completed
        return task.completed

    def task_count(self) -> int:
        """
        Get the total number of tasks.

        Returns:
            int: Number of tasks currently stored
        """
        return len(self._tasks)
```

---

## Data Flow Diagrams

### Add Task Flow
```
User Input (CLI)
    ↓
Validate title/description
    ↓
TodoManager.add_task(title, desc)
    ↓
Generate ID (auto-increment)
    ↓
Create Task object
    ↓
Store in _tasks dict
    ↓
Return new task ID
    ↓
Display success message (CLI)
```

### Update Task Flow
```
User Input: task_id, new_title, new_description (CLI)
    ↓
TodoManager.update_task(task_id, title, desc)
    ↓
Check task exists → TaskNotFoundError if not
    ↓
Validate new title/description
    ↓
Update Task object fields
    ↓
Display success message (CLI)
```

### Delete Task Flow
```
User Input: task_id (CLI)
    ↓
TodoManager.delete_task(task_id)
    ↓
Check task exists → TaskNotFoundError if not
    ↓
Remove from _tasks dict
    ↓
Display success message (CLI)
```

### Toggle Completion Flow
```
User Input: task_id (CLI)
    ↓
TodoManager.toggle_completion(task_id)
    ↓
Check task exists → TaskNotFoundError if not
    ↓
Flip task.completed boolean
    ↓
Return new status
    ↓
Display updated status (CLI)
```

### View All Tasks Flow
```
User selects "View Tasks" (CLI)
    ↓
TodoManager.get_all_tasks()
    ↓
Retrieve all tasks from _tasks
    ↓
Sort by ID
    ↓
Return list[Task]
    ↓
Format and display (CLI)
```

---

## Testing Implications

### Unit Tests (TodoManager)

**Test Coverage Areas**:
1. **Add Task**:
   - Valid task creation
   - Empty title rejection
   - Title too long rejection
   - Description too long rejection
   - ID auto-increment correctness
   - ID uniqueness across multiple adds

2. **Get Task**:
   - Retrieve existing task
   - TaskNotFoundError for invalid ID

3. **Get All Tasks**:
   - Empty list when no tasks
   - Correct list with multiple tasks
   - Sorted by ID

4. **Update Task**:
   - Update title only
   - Update description only
   - Update both fields
   - TaskNotFoundError for invalid ID
   - InvalidInputError for empty title
   - InvalidInputError when no fields provided

5. **Delete Task**:
   - Delete existing task
   - TaskNotFoundError for invalid ID
   - Verify task no longer in get_all_tasks()

6. **Toggle Completion**:
   - Toggle from False to True
   - Toggle from True to False
   - TaskNotFoundError for invalid ID
   - Return value matches new status

7. **Task Count**:
   - Zero on initialization
   - Increases on add
   - Decreases on delete

### Manual Tests (CLI Integration)

Derived from spec acceptance scenarios:
- User Story 1: Add and view tasks
- User Story 2: Toggle completion
- User Story 3: Update task details
- User Story 4: Delete tasks
- Edge cases: Invalid inputs, empty list, etc.

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| `add_task()` | O(1) | O(1) | Dict insertion + counter increment |
| `get_task()` | O(1) | O(1) | Dict lookup |
| `get_all_tasks()` | O(n log n) | O(n) | Sorting n tasks |
| `update_task()` | O(1) | O(1) | Dict lookup + field assignment |
| `delete_task()` | O(1) | O(1) | Dict deletion |
| `toggle_completion()` | O(1) | O(1) | Dict lookup + boolean flip |

**Scale**: For 100 tasks (spec SC-004), all operations are effectively instant (<1ms).

---

## Assumptions

- **Single-threaded**: No concurrent access to TodoManager
- **Single-user**: No multi-user support or task ownership
- **No persistence**: Data lost on exit (explicit requirement)
- **UTF-8**: All strings use UTF-8 encoding
- **No undo**: Deletions are permanent (no trash/archive)
- **No audit log**: No history of changes tracked
