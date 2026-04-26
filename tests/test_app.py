import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    # Arrange
    expected_activities = [
        "Basketball Team", "Soccer Club", "Art Club", "Drama Club",
        "Debate Club", "Science Club", "Chess Club", "Programming Class", "Gym Class"
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == len(expected_activities)
    for activity in expected_activities:
        assert activity in data
        assert "description" in data[activity]
        assert "schedule" in data[activity]
        assert "max_participants" in data[activity]
        assert "participants" in data[activity]
        assert isinstance(data[activity]["participants"], list)


def test_signup_success():
    # Arrange
    activity_name = "Basketball Team"
    student_email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert student_email in data["message"]

    # Verify the student was added
    response = client.get("/activities")
    activities = response.json()
    assert student_email in activities[activity_name]["participants"]


def test_signup_nonexistent_activity():
    # Arrange
    activity_name = "Nonexistent Activity"
    student_email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_duplicate():
    # Arrange
    activity_name = "Soccer Club"
    student_email = "duplicate@example.com"

    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Act - Second signup with same email
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_unregister_success():
    # Arrange
    activity_name = "Art Club"
    student_email = "unregister@example.com"

    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert student_email in data["message"]

    # Verify the student was removed
    response = client.get("/activities")
    activities = response.json()
    assert student_email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_activity():
    # Arrange
    activity_name = "Nonexistent Activity"
    student_email = "student@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_not_enrolled():
    # Arrange
    activity_name = "Drama Club"
    student_email = "notenrolled@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"].lower()