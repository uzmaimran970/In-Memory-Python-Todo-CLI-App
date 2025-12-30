"""Interactive demonstration of the Todo Manager application."""

import sys
sys.path.insert(0, 'src')

from src.services.todo_manager import TodoManager
from src.models.task import InvalidInputError, TaskNotFoundError


def print_separator():
    """Print a visual separator."""
    print("\n" + "="*60 + "\n")


def simulate_user_action(action_description):
    """Print user action."""
    print(f"👤 USER ACTION: {action_description}")
    print("-" * 60)


def display_menu():
    """Display the main menu."""
    print("\n=== Todo Manager ===")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Toggle Task Completion")
    print("6. Exit")


def main():
    """Run complete interactive demonstration."""
    manager = TodoManager()

    print("="*60)
    print("         TODO MANAGER - INTERACTIVE DEMONSTRATION")
    print("="*60)
    print("\nWelcome to Todo Manager!\n")

    # Scenario 1: Add first task
    print_separator()
    simulate_user_action("Selecting option 1 (Add Task)")
    display_menu()
    print("\nChoose an option: 1")

    print("\n--- Add Task ---")
    print("Enter task title: Buy groceries")
    print("Enter task description (optional): Milk, eggs, bread")

    id1 = manager.add_task("Buy groceries", "Milk, eggs, bread")
    print(f"✓ Task added successfully (ID: {id1})")

    # Scenario 2: Add second task
    print_separator()
    simulate_user_action("Selecting option 1 (Add Task) again")
    display_menu()
    print("\nChoose an option: 1")

    print("\n--- Add Task ---")
    print("Enter task title: Read Python book")
    print("Enter task description (optional): Complete chapter 5")

    id2 = manager.add_task("Read Python book", "Complete chapter 5")
    print(f"✓ Task added successfully (ID: {id2})")

    # Scenario 3: Add third task with empty description
    print_separator()
    simulate_user_action("Adding a task with empty description")
    display_menu()
    print("\nChoose an option: 1")

    print("\n--- Add Task ---")
    print("Enter task title: Clean desk")
    print("Enter task description (optional): [Press Enter - empty]")

    id3 = manager.add_task("Clean desk", "")
    print(f"✓ Task added successfully (ID: {id3})")

    # Scenario 4: View all tasks
    print_separator()
    simulate_user_action("Selecting option 2 (View Tasks)")
    display_menu()
    print("\nChoose an option: 2")

    print("\n=== Task List ===\n")
    tasks = manager.get_all_tasks()
    for task in tasks:
        status = "Complete ✓" if task.completed else "Incomplete"
        print(f"[ID: {task.id}] {task.title}")
        print(f"Description: {task.description}")
        print(f"Status: {status}\n")

    # Scenario 5: Toggle completion
    print_separator()
    simulate_user_action("Selecting option 5 (Toggle Task Completion)")
    display_menu()
    print("\nChoose an option: 5")

    print("\n--- Toggle Task Completion ---")
    print("Enter task ID to toggle completion: 1")

    new_status = manager.toggle_completion(1)
    status_text = "Complete" if new_status else "Incomplete"
    print(f"✓ Task 1 marked as {status_text}")

    # Scenario 6: View updated tasks
    print_separator()
    simulate_user_action("Viewing tasks after toggling completion")
    display_menu()
    print("\nChoose an option: 2")

    print("\n=== Task List ===\n")
    tasks = manager.get_all_tasks()
    for task in tasks:
        status = "Complete ✓" if task.completed else "Incomplete"
        print(f"[ID: {task.id}] {task.title}")
        print(f"Description: {task.description}")
        print(f"Status: {status}\n")

    # Scenario 7: Update a task
    print_separator()
    simulate_user_action("Selecting option 3 (Update Task)")
    display_menu()
    print("\nChoose an option: 3")

    print("\n--- Update Task ---")
    print("Enter task ID to update: 2")
    task = manager.get_task(2)
    print(f"\nCurrent task: {task.title}")
    print(f"Current description: {task.description}\n")
    print("Enter new title (press Enter to keep current): Read Python 3.12 book")
    print("Enter new description (press Enter to keep current): [Press Enter]")

    manager.update_task(2, title="Read Python 3.12 book")
    print("✓ Task 2 updated successfully")

    # Scenario 8: Mark another task complete
    print_separator()
    simulate_user_action("Marking task 2 as complete")
    display_menu()
    print("\nChoose an option: 5")

    print("\n--- Toggle Task Completion ---")
    print("Enter task ID to toggle completion: 2")

    new_status = manager.toggle_completion(2)
    status_text = "Complete" if new_status else "Incomplete"
    print(f"✓ Task 2 marked as {status_text}")

    # Scenario 9: Delete a task
    print_separator()
    simulate_user_action("Selecting option 4 (Delete Task)")
    display_menu()
    print("\nChoose an option: 4")

    print("\n--- Delete Task ---")
    print("Enter task ID to delete: 3")

    manager.delete_task(3)
    print("✓ Task 3 deleted successfully")

    # Scenario 10: View final list
    print_separator()
    simulate_user_action("Viewing final task list")
    display_menu()
    print("\nChoose an option: 2")

    print("\n=== Task List ===\n")
    tasks = manager.get_all_tasks()
    for task in tasks:
        status = "Complete ✓" if task.completed else "Incomplete"
        print(f"[ID: {task.id}] {task.title}")
        print(f"Description: {task.description}")
        print(f"Status: {status}\n")

    print(f"Total tasks: {len(tasks)}")

    # Scenario 11: Error handling - invalid task ID
    print_separator()
    simulate_user_action("Testing error handling with invalid task ID")
    display_menu()
    print("\nChoose an option: 5")

    print("\n--- Toggle Task Completion ---")
    print("Enter task ID to toggle completion: 999")

    try:
        manager.toggle_completion(999)
    except TaskNotFoundError as e:
        print(f"Error: {e}")

    # Scenario 12: Error handling - empty title
    print_separator()
    simulate_user_action("Testing error handling with empty title")
    display_menu()
    print("\nChoose an option: 1")

    print("\n--- Add Task ---")
    print("Enter task title: [Press Enter - empty]")

    try:
        manager.add_task("", "Test")
    except InvalidInputError as e:
        print(f"Error: {e}")
        print("System re-prompts for valid input")

    # Scenario 13: Exit
    print_separator()
    simulate_user_action("Selecting option 6 (Exit)")
    display_menu()
    print("\nChoose an option: 6")

    print("\nThank you for using Todo Manager. Goodbye!")

    # Summary
    print_separator()
    print("         INTERACTIVE DEMONSTRATION COMPLETE")
    print("="*60)
    print("\n✅ All features demonstrated:")
    print("   • Add tasks with title and description")
    print("   • View all tasks with complete details")
    print("   • Toggle task completion status")
    print("   • Update task title and description")
    print("   • Delete tasks")
    print("   • Error handling for invalid inputs")
    print("   • Clean exit")
    print("\n🚀 To run the real interactive application:")
    print("   python src/main.py")
    print("\n   (You will be able to enter your own inputs)")
    print("="*60)


if __name__ == "__main__":
    main()
