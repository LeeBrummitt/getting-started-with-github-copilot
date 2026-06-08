from fastapi.testclient import TestClient
from src import app as app_module
from src.app import app

client = TestClient(app)


def test_root_redirect():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activities():
    # Arrange

    # Act
    response = client.get("/activities")
    body = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(body, dict)
    assert "Chess Club" in body
    assert "participants" in body["Chess Club"]


def test_signup_for_activity_success():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    if email in app_module.activities[activity_name]["participants"]:
        app_module.activities[activity_name]["participants"].remove(email)

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]

    # Cleanup
    app_module.activities[activity_name]["participants"].remove(email)


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "ghost@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})
    body = response.json()

    # Assert
    assert response.status_code == 404
    assert body["detail"] == "Activity not found"


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    if email not in app_module.activities[activity_name]["participants"]:
        client.post(url, params={"email": email})

    # Act
    duplicate_response = client.post(url, params={"email": email})
    body = duplicate_response.json()

    # Assert
    assert duplicate_response.status_code == 400
    assert body["detail"] == "Student already signed up for this activity"

    # Cleanup
    app_module.activities[activity_name]["participants"].remove(email)


def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    email = "remove-me@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup"
    delete_url = f"/activities/{activity_name}/participants"

    if email not in app_module.activities[activity_name]["participants"]:
        client.post(signup_url, params={"email": email})

    # Act
    response = client.delete(delete_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"
    url = f"/activities/{activity_name}/participants"

    if email in app_module.activities[activity_name]["participants"]:
        app_module.activities[activity_name]["participants"].remove(email)

    # Act
    response = client.delete(url, params={"email": email})
    body = response.json()

    # Assert
    assert response.status_code == 404
    assert body["detail"] == "Participant not found for this activity"
