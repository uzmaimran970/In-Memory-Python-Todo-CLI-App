"""Console interface for todo application."""

from src.services.todo_manager import TodoManager
from src.models.task import TodoError, TaskNotFoundError, InvalidInputError


def display_menu():
    """Display the main menu options."""
    print("\n=== Todo Manager ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Toggle Task Completion")
    print("6. Exit")


def get_menu_choice() -> int:
    """Get and validate menu choice from user.

    Returns:
        Valid menu choice (1-6)
    """
    while True:
        try:
            choice = input("\nChoose an option: ").strip()
            if not choice:
                print("Error: Input cannot be empty.")
                continue
            choice_int = int(choice)
            if 1 <= choice_int <= 6:
                return choice_int
            else:
                print("Error: Please enter a number between 1 and 6.")
        except ValueError:
            print("Error: Please enter a valid number.")


def get_integer_input(prompt: str) -> int:
    """Get and validate integer input from user.

    Args:
        prompt: The prompt message to display

    Returns:
        Valid integer input
    """
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print("Error: Input cannot be empty.")
            continue
        try:
            return int(user_input)
        except ValueError:
            print("Error: Please enter a valid number.")


def handle_add_task(manager: TodoManager) -> None:
    """Handle adding a new task.

    Args:
        manager: The TodoManager instance
    """
    print("\n--- Add Task ---")

    # Get title with validation loop
    while True:
        title = input("Enter task title: ").strip()
        if not title:
            print("Error: Title cannot be empty. Please try again.")
            continue
        if len(title) > 200:
            print("Error: Title too long (max 200 characters). Please try again.")
            continue
        break

    # Get description with validation
    while True:
        description = input("Enter task description (optional): ")
        if len(description) > 1000:
            print("Error: Description too long (max 1000 characters). Please try again.")
            continue
        break

    # Add task
    try:
        task_id = manager.add_task(title, description)
        print(f"✓ Task added successfully (ID: {task_id})")
    except InvalidInputError as e:
        print(f"Error: {e}")


def handle_view_tasks(manager: TodoManager) -> None:
    """Handle viewing all tasks in table format.

    Args:
        manager: The TodoManager instance
    """
    print("\n=== Task List ===\n")

    tasks = manager.get_all_tasks()

    if not tasks:
        print("No tasks found. Add a task to get started!")
        return

    # Print table header
    print("┌" + "─" * 6 + "┬" + "─" * 40 + "┬" + "─" * 40 + "┬" + "─" * 15 + "┐")
    print("│ {:<4} │ {:<38} │ {:<38} │ {:<13} │".format("ID", "Title", "Description", "Status"))
    print("├" + "─" * 6 + "┼" + "─" * 40 + "┼" + "─" * 40 + "┼" + "─" * 15 + "┤")

    # Print each task
    for task in tasks:
        status = "Complete ✓" if task.completed else "Incomplete"

        # Truncate long text with ellipsis
        title = task.title[:35] + "..." if len(task.title) > 38 else task.title
        description = task.description[:35] + "..." if len(task.description) > 38 else task.description

        print("│ {:<4} │ {:<38} │ {:<38} │ {:<13} │".format(
            task.id,
            title,
            description if description else "-",
            status
        ))

    # Print table footer
    print("└" + "─" * 6 + "┴" + "─" * 40 + "┴" + "─" * 40 + "┴" + "─" * 15 + "┘")
    print(f"\nTotal tasks: {len(tasks)}")


def handle_update_task(manager: TodoManager) -> None:
    """Handle updating a task.

    Args:
        manager: The TodoManager instance
    """
    print("\n--- Update Task ---")

    task_id = get_integer_input("Enter task ID to update: ")

    # Check if task exists first
    try:
        task = manager.get_task(task_id)
        print(f"\nCurrent task: {task.title}")
        print(f"Current description: {task.description}\n")
    except TaskNotFoundError as e:
        print(f"Error: {e}")
        return

    # Get new title (optional)
    print("Enter new title (press Enter to keep current):")
    new_title = input().strip()
    if new_title and len(new_title) > 200:
        print("Error: Title too long (max 200 characters). Keeping current title.")
        new_title = None
    elif not new_title:
        new_title = None

    # Get new description (optional)
    print("Enter new description (press Enter to keep current):")
    new_description = input()
    if new_description and len(new_description) > 1000:
        print("Error: Description too long (max 1000 characters). Keeping current description.")
        new_description = None
    elif not new_description:
        new_description = None

    # Update task
    try:
        if new_title is None and new_description is None:
            print("Error: No changes made. At least one field must be updated.")
        else:
            manager.update_task(task_id, new_title, new_description)
            print(f"✓ Task {task_id} updated successfully")
    except (TaskNotFoundError, InvalidInputError) as e:
        print(f"Error: {e}")


def handle_delete_task(manager: TodoManager) -> None:
    """Handle deleting a task.

    Args:
        manager: The TodoManager instance
    """
    print("\n--- Delete Task ---")

    task_id = get_integer_input("Enter task ID to delete: ")

    try:
        manager.delete_task(task_id)
        print(f"✓ Task {task_id} deleted successfully")
    except TaskNotFoundError as e:
        print(f"Error: {e}")


def handle_toggle_completion(manager: TodoManager) -> None:
    """Handle toggling task completion status.

    Args:
        manager: The TodoManager instance
    """
    print("\n--- Toggle Task Completion ---")

    task_id = get_integer_input("Enter task ID to toggle completion: ")

    try:
        new_status = manager.toggle_completion(task_id)
        status_text = "Complete" if new_status else "Incomplete"
        print(f"✓ Task {task_id} marked as {status_text}")
    except TaskNotFoundError as e:
        print(f"Error: {e}")


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
            print("\nThank you for using Todo Manager. Goodbye!")
            break
