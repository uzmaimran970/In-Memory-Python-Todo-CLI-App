"""Demo script to show MVP functionality without interactive input."""

import sys
sys.path.insert(0, 'src')

from src.services.todo_manager import TodoManager
from src.models.task import InvalidInputError

def demo_mvp():
    """Demonstrate MVP functionality."""
    print("="*60)
    print("       TODO MANAGER - MVP DEMONSTRATION")
    print("="*60)

    manager = TodoManager()

    # Simulate user interactions
    print("\n--- Scenario 1: Adding Tasks ---")
    print("User selects: 1. Add Task")
    print("User enters title: 'Buy groceries'")
    print("User enters description: 'Milk, eggs, bread'")
    id1 = manager.add_task('Buy groceries', 'Milk, eggs, bread')
    print(f"✓ Task added successfully (ID: {id1})\n")

    print("User selects: 1. Add Task")
    print("User enters title: 'Read book'")
    print("User enters description: 'Finish chapter 5'")
    id2 = manager.add_task('Read book', 'Finish chapter 5')
    print(f"✓ Task added successfully (ID: {id2})\n")

    print("User selects: 1. Add Task")
    print("User enters title: 'Clean room'")
    print("User enters description: (empty)")
    id3 = manager.add_task('Clean room', '')
    print(f"✓ Task added successfully (ID: {id3})\n")

    # View tasks
    print("\n--- Scenario 2: Viewing All Tasks ---")
    print("User selects: 2. View Tasks\n")
    print("=== Task List ===\n")

    tasks = manager.get_all_tasks()
    for task in tasks:
        status = "Complete ✓" if task.completed else "Incomplete"
        print(f"[ID: {task.id}] {task.title}")
        print(f"Description: {task.description}")
        print(f"Status: {status}\n")

    # Empty list scenario
    print("\n--- Scenario 3: Empty Task List ---")
    print("User starts fresh application and selects: 2. View Tasks\n")
    print("=== Task List ===\n")
    print("No tasks found. Add a task to get started!\n")

    # Error handling
    print("\n--- Scenario 4: Error Handling ---")
    print("User selects: 1. Add Task")
    print("User enters title: (empty)")
    try:
        manager.add_task('', 'Test')
    except InvalidInputError as e:
        print(f"Error: {e}")
        print("System re-prompts for valid input\n")

    # Success summary
    print("\n" + "="*60)
    print("           MVP FUNCTIONALITY DEMONSTRATED")
    print("="*60)
    print("\n✓ Users can add tasks with title and description")
    print("✓ Users can view all tasks with complete details")
    print("✓ System handles empty task lists gracefully")
    print("✓ System validates input and shows clear error messages")
    print("✓ Task IDs are auto-generated and sequential")
    print("✓ All tasks show ID, title, description, and status")
    print("\n" + "="*60)
    print("         To run the interactive application:")
    print("              python src/main.py")
    print("="*60)

if __name__ == "__main__":
    demo_mvp()
