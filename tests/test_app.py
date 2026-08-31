from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_unregister_participant_success():
    activity_name = "Chess Club"
    email = "test.student@mergington.edu"
    activity = activities[activity_name]

    if email in activity["participants"]:
        activity["participants"].remove(email)

    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    unregister_response = client.delete(f"/activities/{activity_name}/participants/{email}")
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_missing_activity_returns_404():
    response = client.delete("/activities/Unknown Activity/participants/student@mergington.edu")
    assert response.status_code == 404
