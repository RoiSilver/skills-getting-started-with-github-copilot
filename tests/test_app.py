"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_state = {
        "Tennis Club": {
            "description": "Learn tennis skills and compete in friendly matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["james@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join our competitive basketball team",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "marcus@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and mixed media art",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and theatrical productions",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lily@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in debate competitions and develop argumentation skills",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["grace@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["aiden@mergington.edu", "lucas@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear current state
    activities.clear()
    # Restore initial state
    activities.update(initial_state)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Tennis Club" in data
        assert "Basketball Team" in data
    
    def test_get_activities_contains_activity_details(self, client, reset_activities):
        """Test that activity data contains required fields"""
        response = client.get("/activities")
        data = response.json()
        tennis = data["Tennis Club"]
        
        assert "description" in tennis
        assert "schedule" in tennis
        assert "max_participants" in tennis
        assert "participants" in tennis
        assert isinstance(tennis["participants"], list)
    
    def test_get_activities_contains_participants(self, client, reset_activities):
        """Test that participants list is included"""
        response = client.get("/activities")
        data = response.json()
        
        assert "james@mergington.edu" in data["Tennis Club"]["participants"]
        assert "alex@mergington.edu" in data["Basketball Team"]["participants"]


class TestSignup:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student"""
        response = client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "newstudent@mergington.edu" in activities["Tennis Club"]["participants"]
    
    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Art%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_duplicate_student_fails(self, client, reset_activities):
        """Test that signing up an already registered student fails"""
        response = client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "james@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_multiple_students(self, client, reset_activities):
        """Test signing up multiple different students"""
        response1 = client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        response2 = client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(activities["Tennis Club"]["participants"]) == 3


class TestUnregister:
    """Test the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        response = client.post(
            "/activities/Tennis%20Club/unregister",
            params={"email": "james@mergington.edu"}
        )
        assert response.status_code == 200
        assert "james@mergington.edu" not in activities["Tennis Club"]["participants"]
    
    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message"""
        response = client.post(
            "/activities/Tennis%20Club/unregister",
            params={"email": "james@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "james@mergington.edu" in data["message"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from a nonexistent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister",
            params={"email": "anyone@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering a non-registered student fails"""
        response = client.post(
            "/activities/Tennis%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_reduces_participant_count(self, client, reset_activities):
        """Test that unregistering reduces the participant count"""
        initial_count = len(activities["Basketball Team"]["participants"])
        client.post(
            "/activities/Basketball%20Team/unregister",
            params={"email": "alex@mergington.edu"}
        )
        final_count = len(activities["Basketball Team"]["participants"])
        
        assert final_count == initial_count - 1


class TestSignupAndUnregisterWorkflow:
    """Test workflows combining signup and unregister"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering"""
        email = "workflow@mergington.edu"
        
        # Sign up
        response1 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        response2 = client.post(
            "/activities/Chess%20Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
    
    def test_signup_after_unregister(self, client, reset_activities):
        """Test that a student can sign up again after unregistering"""
        email = "workflow2@mergington.edu"
        activity = "Drama%20Club"
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        assert email in activities["Drama Club"]["participants"]
        
        # Unregister
        client.post(f"/activities/{activity}/unregister", params={"email": email})
        assert email not in activities["Drama Club"]["participants"]
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert response.status_code == 200
        assert email in activities["Drama Club"]["participants"]
