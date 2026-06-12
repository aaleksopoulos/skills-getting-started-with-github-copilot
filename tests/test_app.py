import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_chess_club(self):
        """Test that activities include Chess Club"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
    
    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, details in data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_valid_activity(self):
        """Test signing up for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_signup_for_nonexistent_activity(self):
        """Test signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant"""
        email = "testuser123@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Check count increased
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Chess Club"]["participants"])
        
        assert updated_count == initial_count + 1


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_from_valid_activity(self):
        """Test unregistering from an activity"""
        email = "removetest@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Programming Class/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Programming Class/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_unregister_nonexistent_participant(self):
        """Test unregistering non-existent participant returns 404"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_from_nonexistent_activity(self):
        """Test unregistering from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Fake Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "removeme@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Gym Class/signup?email={email}")
        
        # Get count before unregister
        before_response = client.get("/activities")
        before_count = len(before_response.json()["Gym Class"]["participants"])
        
        # Unregister
        client.delete(f"/activities/Gym Class/unregister?email={email}")
        
        # Check count decreased
        after_response = client.get("/activities")
        after_count = len(after_response.json()["Gym Class"]["participants"])
        
        assert after_count == before_count - 1
