"""
Unit tests for the FastAPI application endpoints.
Tests cover signup, unregister, and get activities functionality.
Includes tests for error cases, edge cases, and capacity limits.
"""

import pytest
from fastapi import HTTPException
from src.app import (
    signup_for_activity,
    unregister_from_activity,
    get_activities,
    activities
)
from copy import deepcopy


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_dict(self, app_with_test_data):
        """Test that get_activities returns a dictionary."""
        result = get_activities()
        assert isinstance(result, dict)
    
    def test_get_activities_contains_expected_keys(self, app_with_test_data):
        """Test that activities have all required keys."""
        result = get_activities()
        for activity_name, activity_data in result.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_get_activities_participants_is_list(self, app_with_test_data):
        """Test that participants is a list."""
        result = get_activities()
        for activity_data in result.values():
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_returns_all_activities(self, app_with_test_data):
        """Test that all activities are returned."""
        result = get_activities()
        assert "Chess Club" in result
        assert "Programming Class" in result
        assert "Empty Activity" in result
        assert len(result) == 3


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_successful(self, app_with_test_data):
        """Test successful signup for an activity."""
        email = "student1@mergington.edu"
        result = signup_for_activity("Programming Class", email)
        
        assert "message" in result
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_adds_participant(self, app_with_test_data):
        """Test that signup correctly adds participant to the list."""
        email = "newstudent@mergington.edu"
        initial_count = len(activities["Empty Activity"]["participants"])
        
        signup_for_activity("Empty Activity", email)
        
        assert len(activities["Empty Activity"]["participants"]) == initial_count + 1
        assert email in activities["Empty Activity"]["participants"]
    
    def test_signup_duplicate_registration_prevented(self, app_with_test_data):
        """Test that duplicate registration is prevented."""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity("Chess Club", email)
        
        assert exc_info.value.status_code == 400
        assert "already signed up" in exc_info.value.detail
    
    def test_signup_activity_not_found(self, app_with_test_data):
        """Test signup raises error when activity doesn't exist."""
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity("Nonexistent Activity", "student@mergington.edu")
        
        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail
    
    def test_signup_activity_full(self, app_with_test_data):
        """Test signup raises error when activity is at capacity."""
        # Chess Club has max 2 participants, already has michael@mergington.edu
        signup_for_activity("Chess Club", "second@mergington.edu")  # Fill it
        
        with pytest.raises(HTTPException) as exc_info:
            signup_for_activity("Chess Club", "third@mergington.edu")
        
        assert exc_info.value.status_code == 400
        assert "full" in exc_info.value.detail
    
    def test_signup_multiple_students_same_activity(self, app_with_test_data):
        """Test multiple different students can signup for same activity."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        signup_for_activity("Programming Class", email1)
        signup_for_activity("Programming Class", email2)
        
        assert email1 in activities["Programming Class"]["participants"]
        assert email2 in activities["Programming Class"]["participants"]
        assert len(activities["Programming Class"]["participants"]) == 3
    
    def test_signup_same_student_different_activities(self, app_with_test_data):
        """Test same student can signup for different activities."""
        email = "student@mergington.edu"
        
        signup_for_activity("Chess Club", email)
        signup_for_activity("Programming Class", email)
        
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_email_with_special_characters(self, app_with_test_data):
        """Test signup with valid email containing common special characters."""
        email = "student+tag@mergington.edu"
        
        result = signup_for_activity("Programming Class", email)
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_response_contains_message(self, app_with_test_data):
        """Test that signup response contains a success message."""
        result = signup_for_activity("Programming Class", "student@mergington.edu")
        
        assert "message" in result
        assert "Signed up" in result["message"]
        assert "student@mergington.edu" in result["message"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_successful(self, app_with_test_data):
        """Test successful unregistration from an activity."""
        email = "michael@mergington.edu"
        initial_count = len(activities["Chess Club"]["participants"])
        
        result = unregister_from_activity("Chess Club", email)
        
        assert "message" in result
        assert email not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1
    
    def test_unregister_removes_participant(self, app_with_test_data):
        """Test that unregister correctly removes participant from list."""
        email = "emma@mergington.edu"
        
        unregister_from_activity("Programming Class", email)
        
        assert email not in activities["Programming Class"]["participants"]
    
    def test_unregister_student_not_registered(self, app_with_test_data):
        """Test unregister raises error when student not registered."""
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity("Chess Club", "notregistered@mergington.edu")
        
        assert exc_info.value.status_code == 400
        assert "not registered" in exc_info.value.detail
    
    def test_unregister_activity_not_found(self, app_with_test_data):
        """Test unregister raises error when activity doesn't exist."""
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity("Nonexistent Activity", "student@mergington.edu")
        
        assert exc_info.value.status_code == 404
        assert "Activity not found" in exc_info.value.detail
    
    def test_unregister_cannot_unregister_twice(self, app_with_test_data):
        """Test that student cannot unregister twice from same activity."""
        email = "michael@mergington.edu"
        
        unregister_from_activity("Chess Club", email)
        
        with pytest.raises(HTTPException) as exc_info:
            unregister_from_activity("Chess Club", email)
        
        assert exc_info.value.status_code == 400
    
    def test_unregister_response_contains_message(self, app_with_test_data):
        """Test that unregister response contains a success message."""
        result = unregister_from_activity("Chess Club", "michael@mergington.edu")
        
        assert "message" in result
        assert "Unregistered" in result["message"]
    
    def test_unregister_one_participant_leaves_others(self, app_with_test_data):
        """Test that unregistering one participant doesn't affect others."""
        email1 = "student1@mergington.edu"
        email2 = "michael@mergington.edu"
        
        # Add another participant to Chess Club
        signup_for_activity("Chess Club", email1)
        
        # Unregister one
        unregister_from_activity("Chess Club", email1)
        
        # Other should still be there
        assert email2 in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1


class TestSignupAndUnregisterFlow:
    """Integration-style tests for signup and unregister workflows."""
    
    def test_signup_then_unregister_flow(self, app_with_test_data):
        """Test complete flow of signing up and then unregistering."""
        email = "student@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        signup_for_activity(activity, email)
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_from_activity(activity, email)
        assert email not in activities[activity]["participants"]
    
    def test_signup_unregister_signup_again(self, app_with_test_data):
        """Test that student can signup again after unregistering."""
        email = "student@mergington.edu"
        activity = "Programming Class"
        
        # Signup
        signup_for_activity(activity, email)
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_from_activity(activity, email)
        assert email not in activities[activity]["participants"]
        
        # Signup again - should work
        signup_for_activity(activity, email)
        assert email in activities[activity]["participants"]
    
    def test_capacity_released_after_unregister(self, app_with_test_data):
        """Test that capacity is released when someone unregisters."""
        activity = "Chess Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        email3 = "student3@mergington.edu"
        
        # Fill Chess Club (max 2): michael is already there
        signup_for_activity(activity, email1)
        
        # Try to add third - should fail
        with pytest.raises(HTTPException):
            signup_for_activity(activity, email2)
        
        # Unregister michael
        unregister_from_activity(activity, "michael@mergington.edu")
        
        # Now should be able to add
        signup_for_activity(activity, email2)
        assert email2 in activities[activity]["participants"]


class TestEdgeCases:
    """Tests for edge cases and unusual scenarios."""
    
    def test_signup_email_with_uppercase(self, app_with_test_data):
        """Test signup with uppercase email (should work as-is)."""
        email = "Student@Mergington.edu"
        signup_for_activity("Programming Class", email)
        
        # Email is stored exactly as provided
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_long_email(self, app_with_test_data):
        """Test signup with very long email address."""
        email = "very.long.student.name.with.many.parts@subdomain.mergington.edu"
        signup_for_activity("Programming Class", email)
        
        assert email in activities["Programming Class"]["participants"]
    
    def test_activity_name_with_spaces(self, app_with_test_data):
        """Test signup for activity name with spaces."""
        # "Programming Class" has spaces
        email = "student@mergington.edu"
        signup_for_activity("Programming Class", email)
        
        assert email in activities["Programming Class"]["participants"]
    
    def test_multiple_unregisters_different_members(self, app_with_test_data):
        """Test unregistering multiple different members."""
        activity = "Programming Class"
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        # Sign them all up (Programming Class has max 3, already has emma@mergington.edu)
        for email in emails:
            signup_for_activity(activity, email)
        
        # Unregister in different order
        unregister_from_activity(activity, emails[1])
        unregister_from_activity(activity, emails[0])
        
        # Should only have original participant
        assert len(activities[activity]["participants"]) == 1
        assert "emma@mergington.edu" in activities[activity]["participants"]
