"""Integration tests for task CRUD endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_create_task_success(client: TestClient, auth_headers: dict):
    """Test creating a task with valid data."""
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["is_completed"] is False
    assert "id" in data


def test_create_task_without_auth(client: TestClient):
    """Test creating a task without authentication fails."""
    response = client.post(
        "/api/tasks",
        json={"title": "Test task"}
    )
    assert response.status_code == 401


def test_list_tasks_user_isolation(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user2: dict
):
    """Test that users only see their own tasks."""
    # User 1 creates task
    client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "User 1 task"}
    )

    # User 2 creates task
    client.post(
        "/api/tasks",
        headers=auth_headers_user2,
        json={"title": "User 2 task"}
    )

    # User 1 lists tasks - should only see their own
    response = client.get("/api/tasks", headers=auth_headers)
    data = response.json()
    assert data["total"] == 1
    assert data["tasks"][0]["title"] == "User 1 task"


def test_get_task_ownership_violation(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user2: dict
):
    """Test that users cannot access other users' tasks."""
    # User 1 creates task
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "User 1 task"}
    )
    task_id = response.json()["id"]

    # User 2 tries to access User 1's task
    response = client.get(f"/api/tasks/{task_id}", headers=auth_headers_user2)
    assert response.status_code == 403


def test_complete_task_lifecycle(client: TestClient, auth_headers: dict):
    """Test complete CRUD lifecycle."""
    # Create
    create_response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Lifecycle test"}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Read
    get_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 200

    # Update
    update_response = client.put(
        f"/api/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Updated title", "description": "Updated description"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated title"

    # Toggle completion
    toggle_response = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert toggle_response.status_code == 200
    assert toggle_response.json()["is_completed"] is True

    # Delete
    delete_response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    # Verify deletion
    get_deleted = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_deleted.status_code == 404


def test_task_filtering(client: TestClient, auth_headers: dict):
    """Test task filtering by status."""
    # Create pending task
    client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Pending task"}
    )

    # Create completed task
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Completed task"}
    )
    task_id = response.json()["id"]
    client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)

    # Filter pending
    pending_response = client.get("/api/tasks?status=pending", headers=auth_headers)
    assert pending_response.json()["total"] == 1

    # Filter completed
    completed_response = client.get("/api/tasks?status=completed", headers=auth_headers)
    assert completed_response.json()["total"] == 1

    # All tasks
    all_response = client.get("/api/tasks?status=all", headers=auth_headers)
    assert all_response.json()["total"] == 2


def test_update_task_success(client: TestClient, auth_headers: dict):
    """Test updating task title and description."""
    # Create task
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Original", "description": "Original desc"}
    )
    task_id = response.json()["id"]

    # Update
    update_response = client.put(
        f"/api/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Updated", "description": "Updated desc"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated"
    assert data["description"] == "Updated desc"


def test_delete_task_success(client: TestClient, auth_headers: dict):
    """Test deleting a task."""
    # Create task
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "To delete"}
    )
    task_id = response.json()["id"]

    # Delete
    delete_response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted_task_id"] == task_id

    # Verify deletion
    get_response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_toggle_completion_idempotent(client: TestClient, auth_headers: dict):
    """Test toggling completion multiple times."""
    # Create task
    response = client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"title": "Toggle test"}
    )
    task_id = response.json()["id"]

    # Toggle to true
    response1 = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert response1.json()["is_completed"] is True

    # Toggle back to false
    response2 = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert response2.json()["is_completed"] is False

    # Toggle back to true
    response3 = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert response3.json()["is_completed"] is True
