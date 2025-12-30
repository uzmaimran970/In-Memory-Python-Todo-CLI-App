# CLI Interface Contract Specification

**Feature**: In-Memory Python Todo Console Application
**Component**: Console CLI (Presentation Layer)
**Date**: 2025-12-30

## Overview

This document specifies the user interface contract for the console-based todo application. This defines the expected user experience and interaction patterns.

---

## Menu Interface

### Main Menu Display

**Format**:
```
=== Todo Manager ===
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Toggle Task Completion
6. Exit

Choose an option:
```

**Requirements**:
- Menu MUST be displayed after every operation completes
- Menu MUST display all 6 options with consistent numbering
- Menu MUST prompt for user input with clear indicator (`Choose an option:`)
- Menu MAY include decorative elements (borders, emojis) but MUST NOT obscure functionality

---

## Operation 1: Add Task

### User Flow

```
User selects: 1
System displays: "Enter task title: "
User enters: "Buy groceries"
System displays: "Enter task description (optional): "
User enters: "Milk, eggs, bread"
System displays: "✓ Task added successfully (ID: 1)"
[Return to main menu]
```

### Input Prompts

| Prompt | Required | Validation | Error Message |
|--------|----------|------------|---------------|
| "Enter task title: " | Yes | Non-empty, ≤200 chars | "Error: Title cannot be empty" or "Error: Title too long (max 200 characters)" |
| "Enter task description (optional): " | No | ≤1000 chars | "Error: Description too long (max 1000 characters)" |

### Success Output

**Format**: `"✓ Task added successfully (ID: {task_id})"`

**Example**: `✓ Task added successfully (ID: 1)`

### Error Handling

| Error Condition | User Message |
|----------------|--------------|
| Empty title | `"Error: Title cannot be empty. Please try again."` |
| Title too long | `"Error: Title too long (max 200 characters). Please try again."` |
| Description too long | `"Error: Description too long (max 1000 characters). Please try again."` |

**Behavior on Error**: Prompt user to re-enter (do NOT return to menu immediately)

---

## Operation 2: View Tasks

### User Flow (No Tasks)

```
User selects: 2
System displays:
"=== Task List ===
No tasks found. Add a task to get started!
"
[Return to main menu]
```

### User Flow (With Tasks)

```
User selects: 2
System displays:
"=== Task List ===

[ID: 1] Buy groceries
Description: Milk, eggs, bread
Status: Incomplete

[ID: 2] Read book
Description: Finish chapter 5
Status: Complete ✓

[ID: 3] Clean room
Description:
Status: Incomplete
"
[Return to main menu]
```

### Output Format (Per Task)

```
[ID: {task_id}] {title}
Description: {description}
Status: {Complete ✓ | Incomplete}

```

**Requirements**:
- Tasks MUST be displayed in ID order (ascending)
- Each task MUST show ID, title, description, and status
- Empty descriptions MUST be displayed as blank line (not "None" or "N/A")
- Completed tasks MUST have visual indicator (✓ or similar)
- Tasks MUST be separated by blank line for readability

---

## Operation 3: Update Task

### User Flow

```
User selects: 3
System displays: "Enter task ID to update: "
User enters: 1
System displays: "Enter new title (press Enter to keep current): "
User enters: "Buy groceries and fruits"
System displays: "Enter new description (press Enter to keep current): "
User enters: [presses Enter]
System displays: "✓ Task 1 updated successfully"
[Return to main menu]
```

### Input Prompts

| Prompt | Action on Empty Input | Validation |
|--------|----------------------|------------|
| "Enter task ID to update: " | Error | Must be integer, must exist |
| "Enter new title (press Enter to keep current): " | Keep current title | If provided: non-empty, ≤200 chars |
| "Enter new description (press Enter to keep current): " | Keep current description | If provided: ≤1000 chars |

### Success Output

**Format**: `"✓ Task {task_id} updated successfully"`

### Error Handling

| Error Condition | User Message |
|----------------|--------------|
| Invalid task ID (non-integer) | `"Error: Invalid task ID. Please enter a number."` |
| Task not found | `"Error: Task {task_id} not found. Please check the task list."` |
| New title empty | `"Error: Title cannot be empty. Keeping current title."` |
| Title too long | `"Error: Title too long (max 200 characters). Keeping current title."` |
| Description too long | `"Error: Description too long (max 1000 characters). Keeping current description."` |
| Both inputs empty | `"Error: No changes made. At least one field must be updated."` |

---

## Operation 4: Delete Task

### User Flow

```
User selects: 4
System displays: "Enter task ID to delete: "
User enters: 2
System displays: "✓ Task 2 deleted successfully"
[Return to main menu]
```

### Input Prompts

| Prompt | Validation |
|--------|------------|
| "Enter task ID to delete: " | Must be integer, must exist |

### Success Output

**Format**: `"✓ Task {task_id} deleted successfully"`

### Error Handling

| Error Condition | User Message |
|----------------|--------------|
| Invalid task ID (non-integer) | `"Error: Invalid task ID. Please enter a number."` |
| Task not found | `"Error: Task {task_id} not found. Please check the task list."` |

### Optional Enhancement

**Confirmation Prompt** (recommended but not required):
```
System: "Are you sure you want to delete task {task_id}? (y/n): "
User: y
System: "✓ Task {task_id} deleted successfully"
```

---

## Operation 5: Toggle Task Completion

### User Flow (Incomplete → Complete)

```
User selects: 5
System displays: "Enter task ID to toggle completion: "
User enters: 1
System displays: "✓ Task 1 marked as Complete"
[Return to main menu]
```

### User Flow (Complete → Incomplete)

```
User selects: 5
System displays: "Enter task ID to toggle completion: "
User enters: 1
System displays: "✓ Task 1 marked as Incomplete"
[Return to main menu]
```

### Input Prompts

| Prompt | Validation |
|--------|------------|
| "Enter task ID to toggle completion: " | Must be integer, must exist |

### Success Output

**Format** (conditional):
- If now complete: `"✓ Task {task_id} marked as Complete"`
- If now incomplete: `"✓ Task {task_id} marked as Incomplete"`

### Error Handling

| Error Condition | User Message |
|----------------|--------------|
| Invalid task ID (non-integer) | `"Error: Invalid task ID. Please enter a number."` |
| Task not found | `"Error: Task {task_id} not found. Please check the task list."` |

---

## Operation 6: Exit

### User Flow

```
User selects: 6
System displays: "Thank you for using Todo Manager. Goodbye!"
[Application terminates]
```

**Requirements**:
- Application MUST exit cleanly (exit code 0)
- Exit message MUST be displayed
- No errors or warnings on exit

---

## Input Validation Contract

### Integer Input Validation

**Function**: Parse user input as integer for task IDs and menu choices

**Behavior**:
- Valid integer: Return parsed integer
- Non-integer: Display error and re-prompt
- Empty input: Display error and re-prompt

**Example**:
```python
def get_integer_input(prompt: str) -> int:
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print("Error: Input cannot be empty.")
            continue
        try:
            return int(user_input)
        except ValueError:
            print("Error: Please enter a valid number.")
```

### String Input Validation

**Function**: Validate string inputs for title and description

**Behavior for Title**:
- Empty/whitespace: Return error message
- >200 chars: Return error message
- Valid: Return stripped string

**Behavior for Description**:
- Empty: Return empty string (valid)
- >1000 chars: Return error message
- Valid: Return string as-is (no stripping)

---

## Error Message Standards

### Format

All error messages MUST:
- Start with `"Error: "`
- Be user-friendly (no stack traces or technical jargon)
- Provide actionable guidance when possible
- End with period

**Examples**:
- ✓ Good: `"Error: Task 5 not found. Please check the task list."`
- ✗ Bad: `"TaskNotFoundError: 5"`

### Exception Mapping

| Exception | User-Facing Message Template |
|-----------|------------------------------|
| `TaskNotFoundError(id)` | `"Error: Task {id} not found. Please check the task list."` |
| `InvalidInputError("Title cannot be empty")` | `"Error: Title cannot be empty. Please try again."` |
| `InvalidInputError("Title cannot exceed 200 characters")` | `"Error: Title too long (max 200 characters). Please try again."` |
| `InvalidInputError("Description cannot exceed 1000 characters")` | `"Error: Description too long (max 1000 characters). Please try again."` |
| `InvalidInputError("At least one field must be provided")` | `"Error: No changes made. At least one field must be updated."` |

---

## Application Lifecycle

### Startup

```
[Application starts]
System displays:
"Welcome to Todo Manager!

=== Todo Manager ===
[Main menu...]
"
```

**Requirements**:
- Display welcome message once at startup
- Initialize empty TodoManager instance
- Display main menu

### Runtime Loop

```
while True:
    display_menu()
    choice = get_menu_choice()
    execute_operation(choice)
    if choice == 6:  # Exit
        break
```

**Requirements**:
- Menu MUST be displayed after each operation
- Invalid menu choices MUST display error and re-display menu
- Application MUST NOT crash on invalid input

### Shutdown

**Triggered by**: User selecting menu option 6 (Exit)

**Behavior**:
- Display exit message
- Exit with code 0
- No cleanup required (in-memory data is discarded)

---

## User Experience Requirements

### Response Time
- All operations MUST feel instant (<100ms for user feedback)
- No loading indicators needed

### Input Handling
- All inputs MUST be trimmed of leading/trailing whitespace (except descriptions)
- Empty inputs handled gracefully (error or default value, as specified)
- Invalid inputs MUST NOT crash the application

### Visual Clarity
- Clear section headers (e.g., `=== Todo Manager ===`)
- Consistent use of success indicators (✓)
- Consistent use of error prefix (`Error: `)
- Blank lines for readability between tasks and sections

### Accessibility
- No required colors (app must work in plain terminal)
- No required special characters (✓ is optional, can use "Complete"/"Incomplete")
- Clear text-only interface

---

## Command Dispatcher Pattern

### Implementation Structure

```python
def run():
    """Main application loop."""
    manager = TodoManager()
    print("Welcome to Todo Manager!\n")

    while True:
        display_menu()
        choice = get_menu_choice()

        if choice == 1:
            handle_add_task(manager)
        elif choice == 2:
            handle_view_tasks(manager)
        elif choice == 3:
            handle_update_task(manager)
        elif choice == 4:
            handle_delete_task(manager)
        elif choice == 5:
            handle_toggle_completion(manager)
        elif choice == 6:
            print("Thank you for using Todo Manager. Goodbye!")
            break
        else:
            print("Error: Invalid choice. Please select 1-6.")

def handle_add_task(manager: TodoManager) -> None:
    """Handle add task operation."""
    # Implementation...

def handle_view_tasks(manager: TodoManager) -> None:
    """Handle view tasks operation."""
    # Implementation...

# ... other handlers
```

**Requirements**:
- Each operation MUST have dedicated handler function
- Handlers MUST accept TodoManager instance
- Handlers MUST handle all exceptions from TodoManager
- Handlers MUST display appropriate success/error messages

---

## Testing CLI Interface

### Manual Test Cases

| Test Case | Steps | Expected Result |
|-----------|-------|----------------|
| TC-CLI-01: Display menu | Start app | Menu displays with 6 options |
| TC-CLI-02: Add task (valid) | Select 1, enter "Test", "Description" | Success message with ID |
| TC-CLI-03: Add task (empty title) | Select 1, enter "", "Description" | Error message, re-prompt |
| TC-CLI-04: View empty list | Start app, select 2 | "No tasks found" message |
| TC-CLI-05: View tasks | Add tasks, select 2 | All tasks displayed correctly |
| TC-CLI-06: Update task (title) | Add task, select 3, enter ID and new title | Success message |
| TC-CLI-07: Update task (not found) | Select 3, enter 999 | Task not found error |
| TC-CLI-08: Delete task | Add task, select 4, enter ID | Success message |
| TC-CLI-09: Toggle completion | Add task, select 5, enter ID | "Marked as Complete" |
| TC-CLI-10: Invalid menu choice | Enter 9 | Error message, menu redisplays |
| TC-CLI-11: Non-integer ID | Select 4, enter "abc" | Error message, re-prompt |
| TC-CLI-12: Exit | Select 6 | Goodbye message, clean exit |

### Acceptance Criteria

- All 12 test cases MUST pass
- No crashes or unhandled exceptions
- All error messages follow format standards
- User can complete all 5 core operations (Add, View, Update, Delete, Toggle)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-30 | Initial CLI contract specification |
