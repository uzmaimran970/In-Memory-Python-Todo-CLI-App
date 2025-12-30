# TodoManager Contract Specification

**Feature**: In-Memory Python Todo Console Application
**Component**: TodoManager (Business Logic Layer)
**Date**: 2025-12-30

## Overview

This document specifies the behavioral contract for the TodoManager class. All implementations MUST adhere to these specifications.

---

## Contract: `add_task`

**Signature**:
```python
def add_task(self, title: str, description: str = "") -> int
```

**Preconditions**:
- `title` is a string
- `description` is a string (can be empty)

**Postconditions** (on success):
- A new Task is created with:
  - `id`: unique integer (sequential)
  - `title`: stripped version of input title
  - `description`: exact input description (not stripped)
  - `completed`: False
- Task is stored in internal storage
- Next ID counter is incremented
- Returns the new task's ID

**Exceptions**:
- `InvalidInputError`: If title is empty, whitespace-only, or >200 characters
- `InvalidInputError`: If description >1000 characters

**Invariants**:
- Task IDs are unique and sequential (1, 2, 3, ...)
- IDs are never reused (even after deletion)

**Test Cases**:

| Input | Expected Output | Expected Exception |
|-------|----------------|-------------------|
| `add_task("Buy milk", "From store")` | Returns `1` (first task) | None |
| `add_task("Read book", "")` | Returns `2` | None |
| `add_task("", "Empty title")` | N/A | `InvalidInputError` |
| `add_task("   ", "Whitespace")` | N/A | `InvalidInputError` |
| `add_task("A"*201, "Too long")` | N/A | `InvalidInputError` |
| `add_task("Valid", "B"*1001)` | N/A | `InvalidInputError` |
| `add_task("  Trim me  ", "test")` | Returns ID, task.title = `"Trim me"` | None |

---

## Contract: `get_task`

**Signature**:
```python
def get_task(self, task_id: int) -> Task
```

**Preconditions**:
- `task_id` is an integer

**Postconditions** (on success):
- Returns the Task object with matching ID
- No side effects (task data unchanged)

**Exceptions**:
- `TaskNotFoundError`: If task_id does not exist in storage

**Invariants**:
- Same task_id always returns same Task object (until deleted/modified)

**Test Cases**:

| Scenario | Expected Output | Expected Exception |
|----------|----------------|-------------------|
| Get existing task (ID=1) | Returns Task with id=1 | None |
| Get non-existent task (ID=999) | N/A | `TaskNotFoundError` |
| Get deleted task | N/A | `TaskNotFoundError` |

---

## Contract: `get_all_tasks`

**Signature**:
```python
def get_all_tasks(self) -> list[Task]
```

**Preconditions**:
- None

**Postconditions**:
- Returns list of all Task objects currently in storage
- List is sorted by task ID (ascending)
- Empty list if no tasks exist
- No side effects

**Exceptions**:
- None (never raises)

**Invariants**:
- Returned list length equals `task_count()`
- Returned list is a snapshot (modifying it doesn't affect internal storage)

**Test Cases**:

| Scenario | Expected Output |
|----------|----------------|
| No tasks exist | `[]` |
| 3 tasks exist (IDs 1, 3, 5) | `[Task(1), Task(3), Task(5)]` (sorted) |
| After adding task | List contains new task |
| After deleting task | List excludes deleted task |

---

## Contract: `update_task`

**Signature**:
```python
def update_task(
    self,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> None
```

**Preconditions**:
- `task_id` is an integer
- At least one of `title` or `description` is not None

**Postconditions** (on success):
- If `title` provided: task's title is updated to stripped value
- If `description` provided: task's description is updated to exact value
- Task ID and completion status remain unchanged
- No return value

**Exceptions**:
- `TaskNotFoundError`: If task_id does not exist
- `InvalidInputError`: If both title and description are None
- `InvalidInputError`: If title is empty, whitespace-only, or >200 characters
- `InvalidInputError`: If description >1000 characters

**Invariants**:
- Task ID never changes
- Completion status never changes (use `toggle_completion` for that)
- Fields not provided remain unchanged

**Test Cases**:

| Scenario | Expected Behavior | Expected Exception |
|----------|------------------|-------------------|
| Update title only | Title changes, description unchanged | None |
| Update description only | Description changes, title unchanged | None |
| Update both fields | Both change | None |
| Update with None for both | N/A | `InvalidInputError` |
| Update non-existent task | N/A | `TaskNotFoundError` |
| Update title to "" | N/A | `InvalidInputError` |
| Update title to "   " | N/A | `InvalidInputError` |
| Update title to 201 chars | N/A | `InvalidInputError` |
| Update description to 1001 chars | N/A | `InvalidInputError` |

---

## Contract: `delete_task`

**Signature**:
```python
def delete_task(self, task_id: int) -> None
```

**Preconditions**:
- `task_id` is an integer

**Postconditions** (on success):
- Task with `task_id` is removed from storage
- Task no longer appears in `get_all_tasks()`
- `task_count()` decreases by 1
- No return value

**Exceptions**:
- `TaskNotFoundError`: If task_id does not exist

**Invariants**:
- Deleted task ID is never reused
- Other tasks remain unchanged

**Test Cases**:

| Scenario | Expected Behavior | Expected Exception |
|----------|------------------|-------------------|
| Delete existing task | Task removed, count decreases | None |
| Delete non-existent task | N/A | `TaskNotFoundError` |
| Delete same task twice | First succeeds, second fails | `TaskNotFoundError` on second |
| Delete task, then add new | New task gets next sequential ID (not deleted ID) | None |

---

## Contract: `toggle_completion`

**Signature**:
```python
def toggle_completion(self, task_id: int) -> bool
```

**Preconditions**:
- `task_id` is an integer

**Postconditions** (on success):
- Task's `completed` field is flipped (False → True, or True → False)
- Returns the new completion status
- Task ID, title, and description remain unchanged

**Exceptions**:
- `TaskNotFoundError`: If task_id does not exist

**Invariants**:
- Toggling twice returns to original state
- Return value always matches task's new `completed` field

**Test Cases**:

| Scenario | Initial State | Expected Return | Final State | Exception |
|----------|--------------|----------------|-------------|-----------|
| Toggle incomplete task | `completed=False` | `True` | `completed=True` | None |
| Toggle complete task | `completed=True` | `False` | `completed=False` | None |
| Toggle twice | `completed=False` | 1st: `True`, 2nd: `False` | `completed=False` | None |
| Toggle non-existent task | N/A | N/A | N/A | `TaskNotFoundError` |

---

## Contract: `task_count`

**Signature**:
```python
def task_count(self) -> int
```

**Preconditions**:
- None

**Postconditions**:
- Returns the number of tasks currently in storage
- No side effects

**Exceptions**:
- None (never raises)

**Invariants**:
- Count equals `len(get_all_tasks())`
- Count starts at 0
- Increases by 1 on `add_task`
- Decreases by 1 on `delete_task`
- Unchanged by `update_task`, `toggle_completion`, or `get_*` operations

**Test Cases**:

| Scenario | Expected Count |
|----------|---------------|
| Initial state | 0 |
| After adding 1 task | 1 |
| After adding 3 tasks | 3 |
| After deleting 1 task | 2 |
| After deleting all tasks | 0 |

---

## Cross-Cutting Concerns

### Thread Safety
**Not Required**: TodoManager is designed for single-threaded use. No concurrent access guarantees.

### Immutability
**Task Objects**: Task objects returned by `get_task` and `get_all_tasks` are NOT immutable. Callers MUST NOT modify them directly. Use `update_task` and `toggle_completion` for modifications.

### Logging
**Not Specified**: Logging is optional and not part of the contract. Implementations may log for debugging but MUST NOT rely on logging for correctness.

### Performance
**Expected Complexity**:
- `add_task`: O(1)
- `get_task`: O(1)
- `get_all_tasks`: O(n log n) due to sorting
- `update_task`: O(1)
- `delete_task`: O(1)
- `toggle_completion`: O(1)
- `task_count`: O(1)

Where n = number of tasks.

---

## Contract Validation

### How to Verify Compliance

1. **Type Checking**: Run `mypy` on implementation
2. **Unit Tests**: Implement all test cases from above
3. **Property-Based Tests** (optional): Use `hypothesis` to generate random inputs
4. **Manual Testing**: Test with CLI integration

### Required Test Coverage

Minimum tests to verify contract compliance:

| Operation | Minimum Test Count |
|-----------|-------------------|
| `add_task` | 6 (valid, empty title, whitespace, too long title/desc, trimming) |
| `get_task` | 2 (exists, not found) |
| `get_all_tasks` | 3 (empty, multiple tasks, after add/delete) |
| `update_task` | 8 (title only, desc only, both, neither, not found, empty title, too long) |
| `delete_task` | 3 (exists, not found, double delete) |
| `toggle_completion` | 3 (false→true, true→false, not found) |
| `task_count` | 4 (empty, after add, after delete, multiple ops) |

**Total**: ~29 unit tests minimum

---

## Exception Contract

### `TodoError` (Base Exception)

**Purpose**: Base class for all domain-specific exceptions

**Usage**: Catch this to handle all todo-related errors

```python
try:
    manager.add_task("", "")
except TodoError as e:
    print(f"Todo error: {e}")
```

### `TaskNotFoundError`

**Attributes**:
- `task_id`: int - The ID that was not found
- `message`: str - Error message

**String Representation**: `"Task {task_id} not found"`

**When Raised**:
- `get_task` with invalid ID
- `update_task` with invalid ID
- `delete_task` with invalid ID
- `toggle_completion` with invalid ID

### `InvalidInputError`

**Attributes**:
- `message`: str - Descriptive error message

**When Raised**:
- `add_task` with empty/whitespace title
- `add_task` with title >200 chars
- `add_task` with description >1000 chars
- `update_task` with both title and description None
- `update_task` with empty/whitespace title
- `update_task` with title >200 chars
- `update_task` with description >1000 chars

---

## Example Usage Scenarios

### Scenario 1: Happy Path (Create, View, Complete, Delete)

```python
manager = TodoManager()

# Add tasks
id1 = manager.add_task("Buy milk", "From grocery store")
id2 = manager.add_task("Read book", "Finish chapter 5")

# View all
tasks = manager.get_all_tasks()
assert len(tasks) == 2

# Complete first task
new_status = manager.toggle_completion(id1)
assert new_status == True

# Delete second task
manager.delete_task(id2)

# View updated list
tasks = manager.get_all_tasks()
assert len(tasks) == 1
assert tasks[0].completed == True
```

### Scenario 2: Error Handling

```python
manager = TodoManager()

# Try to add task with empty title
try:
    manager.add_task("", "No title")
except InvalidInputError as e:
    print(f"Error: {e}")  # "Title cannot be empty"

# Add valid task
id1 = manager.add_task("Valid task", "Description")

# Try to delete non-existent task
try:
    manager.delete_task(999)
except TaskNotFoundError as e:
    print(f"Error: {e}")  # "Task 999 not found"

# Try to update with no fields
try:
    manager.update_task(id1, title=None, description=None)
except InvalidInputError as e:
    print(f"Error: {e}")  # "At least one field must be provided"
```

### Scenario 3: Update Operations

```python
manager = TodoManager()
id1 = manager.add_task("Original Title", "Original Description")

# Update title only
manager.update_task(id1, title="New Title")
task = manager.get_task(id1)
assert task.title == "New Title"
assert task.description == "Original Description"

# Update description only
manager.update_task(id1, description="New Description")
task = manager.get_task(id1)
assert task.title == "New Title"
assert task.description == "New Description"
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-30 | Initial contract specification |
