import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Assuming 9 activities in the database
    # Check structure of one activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_valid():
    """Test successful signup for an activity."""
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    # Verify the participant was added
    resp = client.get("/activities")
    data = resp.json()
    assert "test@example.com" in data["Basketball Team"]["participants"]


def test_signup_duplicate():
    """Test attempting to signup for the same activity twice."""
    # First signup
    client.post("/activities/Soccer%20Club/signup?email=dup@example.com")
    # Second signup (should fail)
    response = client.post("/activities/Soccer%20Club/signup?email=dup@example.com")
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_nonexistent_activity():
    """Test signup for a non-existent activity."""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unreg_valid():
    """Test successful unregistration from an activity."""
    # First signup
    client.post("/activities/Art%20Club/signup?email=unreg@example.com")
    # Then unregister
    response = client.delete("/activities/Art%20Club/signup?email=unreg@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    # Verify the participant was removed
    resp = client.get("/activities")
    data = resp.json()
    assert "unreg@example.com" not in data["Art Club"]["participants"]


def test_unreg_not_signed():
    """Test unregistering a student who is not signed up."""
    response = client.delete("/activities/Drama%20Club/signup?email=notsigned@example.com")
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]


def test_unreg_nonexistent_activity():
    """Test unregistering from a non-existent activity."""
    response = client.delete("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_root_redirect():
    """Test root endpoint redirects to static index."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"