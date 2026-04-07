"""
Pytest configuration and fixtures for the FastAPI application tests.
Provides fixtures for app setup, test activities, and data management.
"""

import pytest
from copy import deepcopy
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a FastAPI TestClient for API testing."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def test_activities():
    """
    Fixture that provides a fresh copy of activities for testing.
    This ensures each test has isolated data and changes don't affect other tests.
    """
    return deepcopy(activities)


@pytest.fixture
def app_with_test_data():
    """
    Fixture that resets app activities to a known test state.
    Provides a controlled set of activities for testing.
    """
    # Save original state
    original_activities = deepcopy(activities)
    
    # Reset to default state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,  # Reduced for easier testing of capacity limits
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["emma@mergington.edu"]
        },
        "Empty Activity": {
            "description": "An activity with no participants",
            "schedule": "Mondays, 1:00 PM - 2:00 PM",
            "max_participants": 5,
            "participants": []
        }
    })
    
    yield activities
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def fresh_app():
    """
    Fixture that provides a fresh app instance with test activities pre-loaded.
    """
    # Clear current activities
    activities.clear()
    
    # Add test activities
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": []
        }
    })
    
    yield app
    
    # Cleanup - restore original state
    activities.clear()
