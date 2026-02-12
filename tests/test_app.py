"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create a test client
client = TestClient(app)


class TestActivities:
    """Tests for the /activities endpoint"""

    def test_get_activities(self):
        """Test that we can get all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for the signup endpoint"""

    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Soccer%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        result = response.json()
        assert "Signed up" in result["message"]
        assert "test@mergington.edu" in result["message"]

    def test_signup_duplicate_email(self):
        """Test that duplicate signups are rejected"""
        email = "duplicate@mergington.edu"
        activity = "Basketball%20Club"

        # First signup should succeed
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"]

    def test_signup_activity_not_found(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]


class TestDeleteParticipant:
    """Tests for the delete participant endpoint"""

    def test_delete_participant(self):
        """Test removing a participant from an activity"""
        email = "remove@mergington.edu"
        activity = "Drama%20Club"

        # First, sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200

        # Then, delete
        delete_response = client.delete(f"/activities/{activity}/participants/{email}")
        assert delete_response.status_code == 200
        result = delete_response.json()
        assert "Removed" in result["message"]

    def test_delete_nonexistent_participant(self):
        """Test deleting a participant who's not in the activity"""
        response = client.delete(
            "/activities/Art%20Workshop/participants/notinlist@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Participant not found" in result["detail"]

    def test_delete_from_invalid_activity(self):
        """Test deleting from a non-existent activity"""
        response = client.delete(
            "/activities/Fake%20Activity/participants/test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_delete_existing_participant(self):
        """Test deleting a participant that exists in the initial data"""
        # Chess Club has "michael@mergington.edu" in initial participants
        response = client.delete("/activities/Chess%20Club/participants/michael%40mergington.edu")
        assert response.status_code == 200
        result = response.json()
        assert "Removed" in result["message"]

        # Verify participant is gone
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


class TestRootRedirect:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
