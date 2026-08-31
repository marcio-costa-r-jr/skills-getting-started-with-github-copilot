import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=True)

    assert response.status_code == 200
    assert len(response.history) == 1
    assert response.history[0].status_code == 307
    assert response.history[0].headers["location"] == "/static/index.html"
    assert str(response.url).endswith("/static/index.html")


def test_get_activities_returns_activity_list(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert payload["Chess Club"]["participants"]


def test_signup_for_activity_success(client):
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    activity = activities[activity_name]

    if email in activity["participants"]:
        activity["participants"].remove(email)

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_duplicate_returns_400(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_missing_activity_returns_404(client):
    response = client.post("/activities/Unknown Activity/signup?email=student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_success(client):
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    activity = activities[activity_name]

    if email not in activity["participants"]:
        activity["participants"].append(email)

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_missing_activity_returns_404(client):
    response = client.delete("/activities/Unknown Activity/participants/student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_missing_student_returns_404(client):
    activity_name = "Chess Club"
    email = "not.registered@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"
