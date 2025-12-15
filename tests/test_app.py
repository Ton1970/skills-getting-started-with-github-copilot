from fastapi.testclient import TestClient

# Import the FastAPI app
from src.app import app


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers.get("location") == "/static/index.html"


def test_get_activities_returns_data():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    # Basic structure checks
    assert isinstance(data, dict)
    assert "Chess Club" in data
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert isinstance(chess.get("participants", []), list)


def test_signup_and_unregister_flow():
    activity = "Science Club"
    email = "testuser@mergington.edu"

    # Sign up new participant
    signup_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup_resp.status_code == 200
    assert f"Signed up {email} for {activity}" in signup_resp.json().get("message", "")

    # Verify participant now present in list
    activities_resp = client.get("/activities")
    assert activities_resp.status_code == 200
    participants = activities_resp.json()[activity]["participants"]
    assert email in participants

    # Duplicate signup should fail
    dup_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert dup_resp.status_code == 400

    # Unregister participant
    delete_resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert delete_resp.status_code == 200
    assert f"Unregistered {email} from {activity}" in delete_resp.json().get("message", "")

    # Verify participant removed
    activities_resp_2 = client.get("/activities")
    assert activities_resp_2.status_code == 200
    participants_after = activities_resp_2.json()[activity]["participants"]
    assert email not in participants_after

    # Unregistering again should 404
    delete_resp_2 = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert delete_resp_2.status_code == 404


def test_signup_nonexistent_activity_returns_404():
    resp = client.post("/activities/Nonexistent Activity/signup", params={"email": "x@x.com"})
    assert resp.status_code == 404
