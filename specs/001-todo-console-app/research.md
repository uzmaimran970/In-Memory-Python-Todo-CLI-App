# Research: Todo Console Application

**Feature**: In-Memory Python Todo Console Application
**Date**: 2025-12-30
**Purpose**: Resolve technical unknowns and establish architectural patterns

## Research Questions

### 1. Task Data Structure: Class vs Dictionary

**Question**: Should tasks be represented as classes or dictionaries?

**Decision**: Use dataclass for Task representation

**Rationale**:
- **Type Safety**: Dataclasses provide clear type hints and IDE autocomplete
- **Validation**: Can add `__post_init__` for validation logic
- **Immutability Option**: Can use `frozen=True` if needed
- **Serialization**: Easy to convert to/from dict when needed
- **Readability**: Self-documenting with explicit field definitions

**Alternatives Considered**:
- **Plain Dictionary**:
  - Pros: Simpler, more flexible, native JSON-like structure
  - Cons: No type safety, prone to typos in key names, harder to validate
  - Rejected because: For a structured application demonstrating best practices, type safety is valuable
- **NamedTuple**:
  - Pros: Immutable, typed, memory efficient
  - Cons: Immutable makes updates harder (need to recreate), less intuitive for beginners
  - Rejected because: Task updates are a core feature, immutability adds complexity
- **Custom Class with `__init__`**:
  - Pros: Full control, explicit
  - Cons: More boilerplate, dataclass does this better
  - Rejected because: Dataclass provides same benefits with less code

**Implementation Pattern**:
```python
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    title: str
    description: str
    completed: bool = False
```

---

### 2. Task ID Generation Strategy

**Question**: How should unique task IDs be generated?

**Decision**: Use auto-incrementing integer counter

**Rationale**:
- **Simplicity**: Single counter variable, increment on each add
- **Predictability**: User-friendly sequential IDs (1, 2, 3...)
- **Performance**: O(1) generation time
- **Deterministic**: Easy to reason about and test
- **No External Dependencies**: Pure Python, no UUID library needed

**Alternatives Considered**:
- **UUID (Universally Unique Identifier)**:
  - Pros: Globally unique, good for distributed systems
  - Cons: Not human-friendly (e.g., `550e8400-e29b-41d4-a716-446655440000`), overkill for single-user in-memory app
  - Rejected because: Spec requires "unique ID" not "globally unique", sequential integers are simpler
- **Hash-based IDs** (hash of title + timestamp):
  - Pros: Content-derived, collision-resistant
  - Cons: Not sequential, harder for users to reference, unnecessary complexity
  - Rejected because: Users need simple IDs to reference tasks (e.g., "delete task 5")
- **Timestamp-based IDs**:
  - Pros: Sortable by creation time
  - Cons: Possible collisions if tasks created rapidly, not human-friendly
  - Rejected because: Sequential integers are simpler and guaranteed unique

**Implementation Pattern**:
```python
class TodoManager:
    def __init__(self):
        self._tasks = {}  # {id: Task}
        self._next_id = 1

    def add_task(self, title: str, description: str) -> int:
        task_id = self._next_id
        self._tasks[task_id] = Task(task_id, title, description)
        self._next_id += 1
        return task_id
```

**ID Reuse After Deletion**: IDs are NOT reused. Counter continues incrementing even after deletions. This simplifies logic and avoids confusion (user deletes task 3, adds new task, it becomes task 4, not task 3 again).

---

### 3. Separation of Concerns Architecture

**Question**: How should business logic be separated from I/O handling?

**Decision**: Three-layer architecture (Data, Business Logic, Presentation)

**Rationale**:
- **Testability**: Business logic can be tested without console I/O
- **Maintainability**: Clear boundaries between layers
- **Scalability**: Easy to swap CLI for GUI/API later
- **Spec Compliance**: FR-012 explicitly requires this separation

**Architecture Layers**:

1. **Data Layer** (`models/task.py`):
   - Task dataclass definition
   - Pure data structures, no logic

2. **Business Logic Layer** (`services/todo_manager.py`):
   - TodoManager class with CRUD operations
   - No console I/O (no `input()` or `print()`)
   - Returns results/errors to caller
   - Stateless validation functions

3. **Presentation Layer** (`cli/console.py`):
   - Menu display and user input handling
   - Calls TodoManager methods
   - Formats output for console display
   - Error message presentation

**Alternatives Considered**:
- **Single File "main.py"**:
  - Pros: Simplest for tiny apps
  - Cons: Violates separation of concerns, hard to test, poor demonstration of architecture
  - Rejected because: Spec explicitly requires separation (FR-012), and we're demonstrating best practices
- **MVC (Model-View-Controller)**:
  - Pros: Well-known pattern
  - Cons: Overkill for CLI app, "View" and "Controller" blur in console context
  - Rejected because: Three-layer is simpler and more appropriate for CLI
- **Hexagonal/Ports & Adapters**:
  - Pros: Ultimate flexibility, dependency inversion
  - Cons: Over-engineering for a simple todo app
  - Rejected because: Too complex for Phase 1 hackathon scope

**Communication Pattern**:
```
User Input → CLI Layer → Business Logic Layer → Data Layer
                ↓               ↓
            Display ←──── Results/Errors
```

---

### 4. Error Handling Approach

**Question**: How should invalid user actions be handled?

**Decision**: Exception-based error handling with typed exceptions

**Rationale**:
- **Clarity**: Explicit exception types (e.g., `TaskNotFoundError`) vs generic errors
- **Pythonic**: Follows Python's EAFP (Easier to Ask Forgiveness than Permission) philosophy
- **Clean Code**: Business logic raises exceptions, CLI layer catches and displays
- **Testability**: Easy to verify exceptions are raised in tests

**Exception Hierarchy**:
```python
class TodoError(Exception):
    """Base exception for todo operations"""
    pass

class TaskNotFoundError(TodoError):
    """Raised when task ID doesn't exist"""
    pass

class InvalidInputError(TodoError):
    """Raised when input validation fails"""
    pass
```

**Alternatives Considered**:
- **Return Codes/Tuples** (success: bool, data: Any, error: str):
  - Pros: Explicit, no exception overhead
  - Cons: Callers might ignore errors, less Pythonic, verbose
  - Rejected because: Python exceptions are idiomatic, clean error propagation
- **Result/Option Types** (Rust/Haskell style with library like `returns`):
  - Pros: Type-safe error handling, forces error handling
  - Cons: Adds dependency, unfamiliar to beginners, overkill for simple app
  - Rejected because: Adds complexity, not needed for hackathon scope
- **Logging Only** (no exceptions, just log errors):
  - Pros: Non-disruptive
  - Cons: Silent failures, poor user experience
  - Rejected because: Spec requires clear error messages (FR-009)

**Implementation Pattern**:
```python
# Business Logic Layer
def delete_task(self, task_id: int) -> None:
    if task_id not in self._tasks:
        raise TaskNotFoundError(f"Task {task_id} not found")
    del self._tasks[task_id]

# CLI Layer
try:
    manager.delete_task(task_id)
    print(f"Task {task_id} deleted successfully")
except TaskNotFoundError as e:
    print(f"Error: {e}")
```

---

### 5. Command Handling in Console Environment

**Question**: How should user commands be parsed and dispatched?

**Decision**: Menu-driven interface with command dispatcher pattern

**Rationale**:
- **User-Friendly**: Numbered menu is intuitive for console apps
- **Extensible**: Easy to add new commands
- **Clear**: Explicit mapping from user choice to handler function
- **Error-Prone Reduction**: Menu validation is straightforward

**Command Flow**:
1. Display menu with numbered options
2. Get user input (menu choice)
3. Validate input is valid menu option
4. Dispatch to appropriate handler function
5. Handler gathers additional inputs if needed (e.g., task ID, title)
6. Handler calls business logic
7. Display result or error
8. Return to menu (loop until exit)

**Alternatives Considered**:
- **Command-Line Arguments** (like `git add`, `todo add "title"`):
  - Pros: Fast for power users, scriptable
  - Cons: Requires parsing library (argparse), less beginner-friendly, more complex
  - Rejected because: Spec emphasizes console interaction with prompts, not CLI args
- **REPL with Text Commands** (type "add task", "list tasks"):
  - Pros: Natural language feel
  - Cons: Requires parsing, ambiguous inputs, more error-prone
  - Rejected because: Menu is simpler and clearer
- **Nested Menus**:
  - Pros: Organizes many options
  - Cons: Only 5 operations, nesting adds unnecessary clicks
  - Rejected because: Flat menu sufficient for 5 operations

**Implementation Pattern**:
```python
def display_menu():
    print("\n=== Todo Manager ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Toggle Task Completion")
    print("6. Exit")

def run():
    manager = TodoManager()
    while True:
        display_menu()
        choice = input("Choose an option: ")

        if choice == "1":
            handle_add_task(manager)
        elif choice == "2":
            handle_view_tasks(manager)
        # ... etc
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
```

---

## Best Practices Summary

### Python 3.13+ Features to Leverage
- **Type Hints**: Use throughout for clarity and IDE support
- **Dataclasses**: For Task model
- **f-strings**: For formatted output
- **Match/Case** (Python 3.10+): Optional for command dispatching (more readable than if/elif)

### Testing Strategy
- **Unit Tests**: Test TodoManager methods in isolation (no I/O)
- **Manual Testing**: CLI interaction tested manually per acceptance scenarios
- **Test Cases**: Derived from spec acceptance scenarios
  - Add task → verify in list
  - Update → verify changes
  - Delete → verify removal
  - Toggle → verify status change
  - Invalid ID → verify error message

### Code Quality Standards
- **PEP 8**: Python style guide compliance
- **Docstrings**: For all public methods (Google style)
- **Type Hints**: All function signatures
- **Error Messages**: Clear, actionable, user-friendly
- **No Magic Numbers**: Use named constants where appropriate

### Performance Considerations
- **Storage**: Dictionary lookup O(1) for task retrieval by ID
- **List All**: O(n) iteration through tasks
- **Memory**: Negligible for 100 tasks (spec SC-004)
- **No Optimization Needed**: In-memory operations are instant for hackathon scale

---

## Technology Stack Summary

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.13+ | Spec requirement |
| Task Model | Dataclass | Type safety, clarity |
| ID Generation | Auto-increment int | Simple, user-friendly |
| Storage | Dict (in-memory) | Fast lookup, spec requirement |
| Architecture | 3-layer (Data/Logic/CLI) | Separation of concerns |
| Error Handling | Typed exceptions | Pythonic, clean |
| CLI Pattern | Menu-driven | User-friendly, simple |
| Input Validation | Exception-based | Clear error propagation |
| Testing | Manual + Unit (optional) | Hackathon scope, spec compliance |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep (adding features not in spec) | Medium | Strict adherence to FR-001 through FR-015, no extras |
| Over-engineering (complex patterns) | Medium | Use simplest solution that meets requirements |
| Poor error messages | Low | Review all error scenarios from spec edge cases |
| Mixed concerns (I/O in business logic) | Medium | Code review to verify layer separation |
| ID collision (unlikely with counter) | Low | Use counter pattern, test ID uniqueness |

---

## Next Steps (Phase 1)

1. Create `data-model.md` with detailed Task entity and TodoManager interface
2. Define contracts for all operations (input/output specifications)
3. Create `quickstart.md` for running and testing the application
4. Update agent context with Python best practices
