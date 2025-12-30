# Quickstart Guide: Todo Console Application

**Feature**: In-Memory Python Todo Console Application
**Date**: 2025-12-30
**Audience**: Developers implementing or testing the application

## Prerequisites

- **Python**: Version 3.13 or higher
- **Terminal**: Any terminal supporting standard input/output
- **Development Tools** (optional):
  - `mypy` for type checking
  - `pytest` for unit testing (if implementing tests)

## Project Structure

```
todo_hackathon2/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # Task dataclass, exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_manager.py      # TodoManager business logic
│   ├── cli/
│   │   ├── __init__.py
│   │   └── console.py           # CLI interface, menu, handlers
│   └── main.py                  # Application entry point
├── tests/                       # Optional unit tests
│   ├── __init__.py
│   ├── test_task.py
│   ├── test_todo_manager.py
│   └── test_cli.py
├── specs/
│   └── 001-todo-console-app/
│       ├── spec.md              # Feature specification
│       ├── plan.md              # Implementation plan
│       ├── research.md          # Architecture decisions
│       ├── data-model.md        # Data model specification
│       ├── quickstart.md        # This file
│       └── contracts/
│           ├── todo-manager-contract.md
│           └── cli-interface-contract.md
├── CLAUDE.md                    # Project instructions
└── README.md                    # User-facing documentation
```

## Quick Start: Running the Application

### Step 1: Navigate to Project Directory

```bash
cd /mnt/c/Users/pc/Desktop/todo_hackathon2
```

### Step 2: Run the Application

```bash
python src/main.py
```

**Expected Output**:
```
Welcome to Todo Manager!

=== Todo Manager ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Toggle Task Completion
6. Exit

Choose an option:
```

### Step 3: Try Adding a Task

```
Choose an option: 1
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread
✓ Task added successfully (ID: 1)
```

### Step 4: View Your Tasks

```
Choose an option: 2

=== Task List ===

[ID: 1] Buy groceries
Description: Milk, eggs, bread
Status: Incomplete
```

### Step 5: Mark Task as Complete

```
Choose an option: 5
Enter task ID to toggle completion: 1
✓ Task 1 marked as Complete
```

### Step 6: Exit Application

```
Choose an option: 6
Thank you for using Todo Manager. Goodbye!
```

## Implementation Phases

### Phase 1: Data Layer (models/task.py)

**What to implement**:
1. Task dataclass with validation
2. Exception classes (TodoError, TaskNotFoundError, InvalidInputError)

**Test**:
```python
from src.models.task import Task, InvalidInputError

# Valid task
task = Task(id=1, title="Test", description="Test desc", completed=False)
print(task)

# Invalid task (empty title)
try:
    Task(id=2, title="", description="Test")
except ValueError as e:
    print(f"Caught: {e}")
```

**Acceptance**:
- ✓ Task dataclass created with all fields
- ✓ Validation raises ValueError for empty title
- ✓ Validation raises ValueError for title >200 chars
- ✓ Validation raises ValueError for description >1000 chars

---

### Phase 2: Business Logic Layer (services/todo_manager.py)

**What to implement**:
1. TodoManager class with `__init__`
2. `add_task()` method
3. `get_task()` method
4. `get_all_tasks()` method
5. `update_task()` method
6. `delete_task()` method
7. `toggle_completion()` method
8. `task_count()` method

**Test**:
```python
from src.services.todo_manager import TodoManager
from src.models.task import TaskNotFoundError

manager = TodoManager()

# Add tasks
id1 = manager.add_task("Task 1", "Description 1")
id2 = manager.add_task("Task 2", "Description 2")
print(f"Added tasks: {id1}, {id2}")

# Get all tasks
tasks = manager.get_all_tasks()
print(f"Total tasks: {len(tasks)}")

# Toggle completion
manager.toggle_completion(id1)
print(f"Task {id1} completed: {manager.get_task(id1).completed}")

# Delete task
manager.delete_task(id2)
print(f"Remaining tasks: {manager.task_count()}")
```

**Acceptance**:
- ✓ All 8 methods implemented
- ✓ IDs auto-increment starting from 1
- ✓ TaskNotFoundError raised for invalid IDs
- ✓ InvalidInputError raised for validation failures
- ✓ All operations work correctly in isolation

---

### Phase 3: CLI Layer (cli/console.py)

**What to implement**:
1. `display_menu()` function
2. `get_menu_choice()` function
3. `handle_add_task(manager)` function
4. `handle_view_tasks(manager)` function
5. `handle_update_task(manager)` function
6. `handle_delete_task(manager)` function
7. `handle_toggle_completion(manager)` function
8. `run()` function (main loop)

**Test** (manual):
- Run `python src/main.py`
- Test each menu option
- Verify error messages for invalid inputs
- Verify success messages

**Acceptance**:
- ✓ Menu displays correctly
- ✓ All 5 operations accessible from menu
- ✓ Error messages user-friendly
- ✓ No crashes on invalid input
- ✓ Exit works cleanly

---

### Phase 4: Application Entry Point (main.py)

**What to implement**:
```python
from src.cli.console import run

if __name__ == "__main__":
    run()
```

**Test**:
```bash
python src/main.py
```

**Acceptance**:
- ✓ Application starts without errors
- ✓ All functionality accessible

---

### Phase 5: Integration Testing

**Manual Test Scenarios** (from spec acceptance scenarios):

#### Scenario 1: Add and View Tasks
1. Start application
2. Add task: "Buy milk" / "From store"
3. Add task: "Read book" / ""
4. View tasks
5. Verify both tasks displayed with IDs 1 and 2

#### Scenario 2: Toggle Completion
1. Add task: "Test task" / "Test"
2. Note task ID (e.g., 1)
3. Toggle completion for ID 1
4. View tasks
5. Verify task shows "Complete ✓"
6. Toggle completion again
7. Verify task shows "Incomplete"

#### Scenario 3: Update Task
1. Add task: "Old Title" / "Old Description"
2. Update title to "New Title"
3. View tasks
4. Verify title changed, description unchanged

#### Scenario 4: Delete Task
1. Add 3 tasks
2. Delete task ID 2
3. View tasks
4. Verify only IDs 1 and 3 remain

#### Scenario 5: Error Handling
1. Try to add task with empty title → Error displayed
2. Try to delete task ID 999 → "Task not found" error
3. Try to update task ID 999 → "Task not found" error

**Acceptance**:
- ✓ All scenarios pass
- ✓ No crashes
- ✓ Data persists during session
- ✓ Data lost on restart (in-memory only)

---

## Development Workflow

### Using Claude Code + Spec-Kit Plus

#### Step 1: Review Specification
```bash
cat specs/001-todo-console-app/spec.md
```

#### Step 2: Review Planning Artifacts
```bash
cat specs/001-todo-console-app/research.md
cat specs/001-todo-console-app/data-model.md
cat specs/001-todo-console-app/contracts/todo-manager-contract.md
cat specs/001-todo-console-app/contracts/cli-interface-contract.md
```

#### Step 3: Generate Tasks
```bash
/sp.tasks
```

This will create `specs/001-todo-console-app/tasks.md` with detailed implementation tasks.

#### Step 4: Implement with Claude Code
Use Claude Code to implement each task incrementally:
- Start with data layer (Task model)
- Implement business logic (TodoManager)
- Add CLI interface
- Test integration

#### Step 5: Record Progress
After significant work, create a Prompt History Record:
```bash
/sp.phr
```

---

## Validation Checklist

### Code Quality
- [ ] Type hints on all function signatures
- [ ] Docstrings on all public methods (Google style)
- [ ] PEP 8 compliance (use `black` or `ruff` formatter)
- [ ] No hardcoded values (use constants where appropriate)

### Functionality
- [ ] All 5 core operations work (Add, View, Update, Delete, Toggle)
- [ ] Error messages clear and user-friendly
- [ ] No crashes on invalid input
- [ ] Task IDs unique and sequential
- [ ] In-memory storage works (no persistence)

### Architecture
- [ ] Business logic in `services/todo_manager.py`
- [ ] CLI logic in `cli/console.py`
- [ ] Data model in `models/task.py`
- [ ] No console I/O in TodoManager
- [ ] Clean separation of concerns

### Testing
- [ ] Manual test scenarios all pass
- [ ] Edge cases handled (empty inputs, invalid IDs, etc.)
- [ ] Application restarts with empty state

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution**: Ensure you're running from project root:
```bash
cd /mnt/c/Users/pc/Desktop/todo_hackathon2
python src/main.py
```

Or set PYTHONPATH:
```bash
export PYTHONPATH=/mnt/c/Users/pc/Desktop/todo_hackathon2
python src/main.py
```

### Issue: "TypeError: Task() takes no arguments"

**Solution**: Ensure Task is a dataclass:
```python
from dataclasses import dataclass

@dataclass
class Task:
    # ...
```

### Issue: Application crashes on invalid input

**Solution**: Wrap input handling in try-except:
```python
try:
    choice = int(input("Choose an option: "))
except ValueError:
    print("Error: Please enter a valid number.")
```

---

## Type Checking (Optional)

Install mypy:
```bash
pip install mypy
```

Run type checks:
```bash
mypy src/
```

Fix any type errors before finalizing implementation.

---

## Next Steps

After completing the basic implementation:

1. **Code Review**: Review against specification and contracts
2. **Manual Testing**: Execute all acceptance scenarios
3. **Documentation**: Update README.md with user instructions
4. **Commit**: Create git commit for Phase 1 completion
5. **Demo**: Prepare to demonstrate all features

---

## Success Criteria Validation

Verify against spec success criteria (SC-001 through SC-010):

| Criteria | How to Verify | Status |
|----------|---------------|--------|
| SC-001: Add and view in ≤3 selections | Manual test: Add → View | [ ] |
| SC-002: View complete task list | Manual test: View displays all fields | [ ] |
| SC-003: All 5 operations work without errors | Test each operation | [ ] |
| SC-004: Handle 100 tasks | Add 100 tasks, verify performance | [ ] |
| SC-005: Error messages clear | Test invalid inputs | [ ] |
| SC-006: 100% unique IDs | Add many tasks, verify no collisions | [ ] |
| SC-007: Toggle works correctly | Toggle incomplete→complete→incomplete | [ ] |
| SC-008: Data lost on restart | Restart app, verify empty list | [ ] |
| SC-009: Separation of concerns | Code review | [ ] |
| SC-010: Clean start/exit | Test startup and exit | [ ] |

---

## Resources

- **Specification**: `specs/001-todo-console-app/spec.md`
- **Research Decisions**: `specs/001-todo-console-app/research.md`
- **Data Model**: `specs/001-todo-console-app/data-model.md`
- **TodoManager Contract**: `specs/001-todo-console-app/contracts/todo-manager-contract.md`
- **CLI Contract**: `specs/001-todo-console-app/contracts/cli-interface-contract.md`
- **Python Docs**: https://docs.python.org/3.13/
- **Dataclasses**: https://docs.python.org/3/library/dataclasses.html

---

## Contact & Support

For questions about the specification or implementation approach, refer to the planning artifacts in `specs/001-todo-console-app/`.

**Happy Coding! 🚀**
