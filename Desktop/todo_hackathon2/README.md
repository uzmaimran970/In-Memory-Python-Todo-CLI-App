# Todo Console Application

A simple, in-memory command-line todo list manager built with Python 3.12+.

## Features

### Current Features (MVP - User Story 1)

✅ **Add Tasks**: Create tasks with a title and optional description
✅ **View Tasks**: Display all tasks with ID, title, description, and completion status
✅ **Menu-Driven Interface**: Easy-to-use console menu
✅ **Input Validation**: Clear error messages for invalid inputs
✅ **Auto-Generated IDs**: Sequential task IDs starting from 1

### Coming Soon (User Stories 2-4)

- Toggle task completion status
- Update task title and description
- Delete tasks

## Quick Start

### Prerequisites

- Python 3.12 or higher

### Installation

1. Clone or download this repository
2. Navigate to the project directory

### Running the Application

```bash
python src/main.py
```

Or from the repository root:

```bash
python3 src/main.py
```

## Usage

When you run the application, you'll see a menu with the following options:

```
=== Todo Manager ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Toggle Task Completion
6. Exit
```

### Adding a Task

1. Select option `1` from the menu
2. Enter the task title (required, max 200 characters)
3. Enter the task description (optional, max 1000 characters)
4. The system will confirm with a success message and task ID

**Example:**
```
Choose an option: 1

--- Add Task ---
Enter task title: Buy groceries
Enter task description (optional): Milk, eggs, bread
✓ Task added successfully (ID: 1)
```

### Viewing All Tasks

1. Select option `2` from the menu
2. All tasks will be displayed with their details

**Example:**
```
Choose an option: 2

=== Task List ===

[ID: 1] Buy groceries
Description: Milk, eggs, bread
Status: Incomplete

[ID: 2] Read book
Description: Finish chapter 5
Status: Incomplete
```

### Exiting the Application

Select option `6` to exit gracefully.

## Project Structure

```
todo_hackathon2/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # Task dataclass and exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_manager.py      # Business logic (CRUD operations)
│   ├── cli/
│   │   ├── __init__.py
│   │   └── console.py           # Command-line interface
│   └── main.py                  # Application entry point
├── specs/
│   └── 001-todo-console-app/    # Feature specifications and planning
├── test_mvp.py                  # Automated validation tests
├── demo_mvp.py                  # MVP demonstration script
└── README.md                    # This file
```

## Architecture

The application follows a clean three-layer architecture:

### Data Layer (`src/models/task.py`)
- `Task` dataclass: Represents a todo item
- Exception classes: `TodoError`, `TaskNotFoundError`, `InvalidInputError`

### Business Logic Layer (`src/services/todo_manager.py`)
- `TodoManager` class: Manages task operations (add, view, update, delete, toggle)
- No console I/O - pure business logic
- In-memory storage using a dictionary

### Presentation Layer (`src/cli/console.py`)
- Menu display and user input handling
- Error message formatting
- Calls business logic methods

## Testing

### Run Automated Tests

```bash
python test_mvp.py
```

This validates:
- Adding tasks
- Viewing tasks
- Empty list handling
- Input validation
- ID uniqueness and sequential generation

### Run Demonstration

```bash
python demo_mvp.py
```

Shows all MVP functionality without interactive input.

## Technical Details

- **Language**: Python 3.12+
- **Dependencies**: Standard library only (dataclasses, typing)
- **Storage**: In-memory (data lost on exit)
- **Platform**: Cross-platform (Linux, macOS, Windows)

## Design Decisions

### Why Dataclass for Task?
- Type safety and IDE autocomplete
- Built-in validation via `__post_init__`
- Clear, self-documenting code

### Why Auto-Incrementing IDs?
- User-friendly (users can easily reference "task 1", "task 2")
- Simple and deterministic
- No external dependencies

### Why In-Memory Storage?
- Per specification requirements (Phase 1 scope)
- Simplicity - no database setup needed
- Fast operations (O(1) lookups)

## Limitations

- **No Persistence**: All data is lost when the application exits
- **Single User**: No multi-user support
- **No Concurrency**: Single-threaded operation
- **No Undo**: Deletions are permanent

## Success Criteria (MVP)

✅ Users can add tasks and view them in ≤3 menu selections
✅ All task details displayed (ID, title, description, status)
✅ Handles 100+ tasks without performance issues
✅ Clear error messages for invalid inputs
✅ 100% unique task IDs
✅ Clean separation of concerns (business logic vs. UI)
✅ Clean startup and exit

## Development

This project follows Spec-Driven Development (SDD) practices:

- **Specification**: `specs/001-todo-console-app/spec.md`
- **Implementation Plan**: `specs/001-todo-console-app/plan.md`
- **Task Breakdown**: `specs/001-todo-console-app/tasks.md`
- **Architecture Decisions**: `specs/001-todo-console-app/research.md`
- **Data Model**: `specs/001-todo-console-app/data-model.md`
- **Contracts**: `specs/001-todo-console-app/contracts/`

## Next Steps

To add more functionality:

1. **User Story 2**: Toggle task completion (Phase 4 in tasks.md)
2. **User Story 3**: Update task details (Phase 5 in tasks.md)
3. **User Story 4**: Delete tasks (Phase 6 in tasks.md)

See `specs/001-todo-console-app/tasks.md` for detailed implementation tasks.

## License

This project is part of a hackathon demonstration and is provided as-is for educational purposes.

## Support

For issues or questions about the specification or implementation approach, refer to the planning artifacts in `specs/001-todo-console-app/`.
