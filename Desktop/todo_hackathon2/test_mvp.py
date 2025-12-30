"""Test script for MVP validation."""

import sys
sys.path.insert(0, 'src')

from src.models.task import Task, TaskNotFoundError, InvalidInputError
from src.services.todo_manager import TodoManager

def test_mvp():
    """Run manual validation tests for User Story 1."""

    # Test 1: Create TodoManager and add tasks (T023)
    print("Test 1: Add task 'Buy groceries' with description")
    manager = TodoManager()
    id1 = manager.add_task('Buy groceries', 'Milk, eggs, bread')
    print(f"✓ Task added successfully (ID: {id1})")
    assert id1 == 1, "First task should have ID 1"

    # Test 2: Add multiple tasks and view (T024)
    print("\nTest 2: Add 3 tasks and view all")
    id2 = manager.add_task('Read book', 'Finish chapter 5')
    id3 = manager.add_task('Clean room', '')

    tasks = manager.get_all_tasks()
    print(f"✓ Total tasks: {len(tasks)}")
    assert len(tasks) == 3, "Should have 3 tasks"

    for task in tasks:
        status = "Complete" if task.completed else "Incomplete"
        print(f"  [ID: {task.id}] {task.title}")
        print(f"  Description: {task.description}")
        print(f"  Status: {status}")

    # Verify all tasks are incomplete initially
    assert all(not task.completed for task in tasks), "All tasks should be incomplete initially"
    print("✓ All tasks display correctly with ID, title, description, and status")

    # Test 3: View empty list (T025)
    print("\nTest 3: View tasks when list is empty")
    empty_manager = TodoManager()
    empty_tasks = empty_manager.get_all_tasks()
    assert len(empty_tasks) == 0, "Empty manager should have 0 tasks"
    print(f"✓ Empty list verified ({len(empty_tasks)} tasks)")

    # Test 4: Error handling for empty title (T026)
    print("\nTest 4: Try to add task with empty title")
    try:
        manager.add_task('', 'Should fail')
        print("✗ FAILED: Should have raised InvalidInputError")
        assert False, "Should have raised exception"
    except InvalidInputError as e:
        print(f"✓ Correctly raised error: {e}")

    # Additional validation tests
    print("\nTest 5: Verify ID uniqueness and auto-increment")
    assert id1 == 1 and id2 == 2 and id3 == 3, "IDs should be sequential"
    print("✓ Task IDs are unique and sequential (1, 2, 3)")

    print("\nTest 6: Verify task_count() method")
    count = manager.task_count()
    assert count == 3, f"Expected 3 tasks, got {count}"
    print(f"✓ task_count() returns correct value: {count}")

    print("\n" + "="*50)
    print("=== All MVP validation tests passed! ===")
    print("="*50)
    print("\nMVP is ready for interactive testing!")
    print("Run: python src/main.py")

if __name__ == "__main__":
    test_mvp()
