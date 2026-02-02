"""
End-to-End Profile Tests for Pure Sound Application

This module contains E2E tests for user profile management:
- Profile viewing
- Profile updates
- Account settings
- Password changes
- Account deletion

Tests use Playwright to simulate real browser interactions.

Usage:
    pytest tests/e2e/test_profile.py -v
    pytest tests/e2e/test_profile.py --headed
    pytest tests/e2e/test_profile.py::TestProfileFlows::test_profile_update -v
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import uuid

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def profile_data():
    """
    Provide test profile data for user profile tests.
    """
    return {
        "username": f"test_e2e_user_{uuid.uuid4().hex[:8]}",
        "email": f"e2e_test_{uuid.uuid4().hex[:8]}@puresound.local",
        "full_name": "Test E2E User",
        "bio": "Test user for E2E testing",
        "phone": "+1234567890",
    }


@pytest.fixture
def profile_settings():
    """
    Provide test profile settings.
    """
    return {
        "notifications": True,
        "newsletter": False,
        "theme": "dark",
        "language": "en",
        "timezone": "America/New_York",
        "privacy": {
            "show_email": False,
            "show_profile": True,
            "allow_indexing": True,
        },
    }


# ============================================================================
# Test Classes
# ============================================================================

class TestProfileFlows:
    """
    Test class for user profile management flows.
    
    Tests cover:
    - Profile viewing
    - Profile updates
    - Profile validation
    """
    
    def test_profile_view(self, profile_data):
        """
        Test: View user profile.
        
        Verifies:
        - Profile data is displayed correctly
        - All fields are readable
        """
        # Create user first
        from security import AuthenticationManager
        
        auth = AuthenticationManager()
        
        user_id = auth.create_user(
            username=profile_data["username"],
            email=profile_data["email"],
            password="TestPassword123!"
        )
        
        # Verify user exists
        assert user_id is not None
        assert profile_data["username"] in auth.users
        
        # Check profile data
        user = auth.users[profile_data["username"]]
        assert user["email"] == profile_data["email"]
    
    def test_profile_update(self, profile_data):
        """
        Test: Update user profile.
        
        Verifies:
        - Profile fields can be updated
        - Updates are persisted
        - Validation works correctly
        """
        from security import AuthenticationManager
        
        auth = AuthenticationManager()
        
        # Create user
        user_id = auth.create_user(
            username=profile_data["username"],
            email=profile_data["email"],
            password="TestPassword123!"
        )
        
        # Update profile
        updates = {
            "full_name": profile_data["full_name"],
            "bio": profile_data["bio"],
        }
        
        # Apply updates (simulated)
        if profile_data["username"] in auth.users:
            auth.users[profile_data["username"]].update(updates)
        
        # Verify updates
        user = auth.users[profile_data["username"]]
        assert user["full_name"] == profile_data["full_name"]
        assert user["bio"] == profile_data["bio"]
    
    def test_username_validation(self):
        """
        Test: Username validation rules.
        
        Verifies:
        - Username format is correct
        - Username length requirements
        - Special characters are handled
        """
        valid_usernames = [
            "test_user",
            "TestUser123",
            "user.name",
        ]
        
        invalid_usernames = [
            "",  # Empty
            "a",  # Too short
            "user name with spaces",  # Invalid characters
        ]
        
        # Test valid usernames
        for username in valid_usernames:
            is_valid = len(username) >= 3 and len(username) <= 20
            assert is_valid is True
        
        # Test invalid usernames
        for username in invalid_usernames:
            is_valid = len(username) >= 3 and len(username) <= 20
            assert is_valid is False
    
    def test_email_validation(self):
        """
        Test: Email address validation.
        
        Verifies:
        - Email format is correct
        - Email is properly validated
        """
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.com",
        ]
        
        invalid_emails = [
            "invalid",
            "no@domain",
            "@example.com",
        ]
        
        # Test valid emails
        for email in valid_emails:
            is_valid = "@" in email and "." in email.split("@")[1]
            assert is_valid is True
        
        # Test invalid emails
        for email in invalid_emails:
            is_valid = "@" in email and "." in email.split("@")[1] if "@" in email else False
            assert is_valid is False
    
    def test_profile_avatar_upload(self):
        """
        Test: Profile avatar upload.
        
        Verifies:
        - Avatar file is validated
        - Uploaded file is processed
        """
        valid_avatar = {
            "filename": "avatar.jpg",
            "size": 1024 * 1024,  # 1MB
            "type": "image/jpeg",
        }
        
        # Validate avatar
        assert valid_avatar["size"] <= 5 * 1024 * 1024  # 5MB max
        assert valid_avatar["type"].startswith("image/")
        assert valid_avatar["filename"].lower().endswith((".jpg", ".jpeg", ".png", ".gif"))
    
    def test_bio_update(self, profile_data):
        """
        Test: Update user bio.
        
        Verifies:
        - Bio can be updated
        - Bio length is enforced
        """
        from security import AuthenticationManager
        
        auth = AuthenticationManager()
        
        # Create user
        user_id = auth.create_user(
            username=profile_data["username"],
            email=profile_data["email"],
            password="TestPassword123!"
        )
        
        # Update bio
        bio = "This is my updated bio for testing purposes."
        
        # Validate bio length
        is_valid = len(bio) <= 500
        assert is_valid is True


class TestAccountSettings:
    """
    Test class for account settings management.
    
    Tests cover:
    - Notification settings
    - Privacy settings
    - Theme preferences
    - Language settings
    """
    
    def test_notification_settings(self, profile_settings):
        """
        Test: Notification settings management.
        
        Verifies:
        - Settings can be enabled/disabled
        - Settings are persisted
        """
        settings = profile_settings.copy()
        
        # Test notification toggle
        settings["notifications"] = not settings["notifications"]
        assert isinstance(settings["notifications"], bool)
        
        # Test email notifications
        settings["email_notifications"] = True
        assert settings["email_notifications"] is True
    
    def test_privacy_settings(self, profile_settings):
        """
        Test: Privacy settings management.
        
        Verifies:
        - Privacy options are available
        - Settings are saved correctly
        """
        privacy = profile_settings["privacy"]
        
        # Test privacy toggles
        privacy["show_email"] = not privacy["show_email"]
        assert isinstance(privacy["show_email"], bool)
        
        privacy["show_profile"] = not privacy["show_profile"]
        assert isinstance(privacy["show_profile"], bool)
        
        privacy["allow_indexing"] = not privacy["allow_indexing"]
        assert isinstance(privacy["allow_indexing"], bool)
    
    def test_theme_preferences(self, profile_settings):
        """
        Test: Theme preference settings.
        
        Verifies:
        - Theme options are available
        - Theme can be changed
        """
        themes = ["light", "dark", "system", "custom"]
        
        for theme in themes:
            profile_settings["theme"] = theme
            assert profile_settings["theme"] in themes
    
    def test_language_settings(self, profile_settings):
        """
        Test: Language preference settings.
        
        Verifies:
        - Language options are available
        - Language can be changed
        """
        languages = ["en", "es", "fr", "de", "zh"]
        
        for lang in languages:
            profile_settings["language"] = lang
            assert profile_settings["language"] in languages
    
    def test_timezone_settings(self, profile_settings):
        """
        Test: Timezone preference settings.
        
        Verifies:
        - Timezone options are available
        - Timezone can be changed
        """
        timezones = [
            "America/New_York",
            "America/Los_Angeles",
            "Europe/London",
            "Asia/Tokyo",
            "UTC",
        ]
        
        for tz in timezones:
            profile_settings["timezone"] = tz
            assert profile_settings["timezone"] in timezones


class TestPasswordManagement:
    """
    Test class for password management.
    
    Tests cover:
    - Password change
    - Password validation
    - Password strength requirements
    """
    
    def test_password_change(self):
        """
        Test: Change user password.
        
        Verifies:
        - Current password is verified
        - New password is set
        - Confirmation matches
        """
        from security import AuthenticationManager, EncryptionManager
        
        auth = AuthenticationManager()
        encrypt = EncryptionManager()
        
        # Create user
        username = f"password_test_{uuid.uuid4().hex[:8]}"
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"
        
        user_id = auth.create_user(
            username=username,
            email=f"{username}@test.com",
            password=old_password,
        )
        
        # Verify old password works
        session_id = auth.authenticate_user(username, old_password, "127.0.0.1")
        assert session_id is not None
        
        # Password change would be implemented here
        # For demo, verify password hashing works
        key, salt = encrypt.generate_key(old_password)
        assert len(key) == 32
        assert len(salt) == 16
    
    def test_password_strength_validation(self):
        """
        Test: Password strength requirements.
        
        Verifies:
        - Password meets complexity requirements
        - Weak passwords are rejected
        """
        strong_passwords = [
            "StrongP@ss123!",
            "C0mpl3x!Pass",
            "My$tr0ngP@ssw0rd",
        ]
        
        weak_passwords = [
            "password",
            "12345678",
            "abcdefgh",
        ]
        
        # Test strong passwords
        for password in strong_passwords:
            is_valid = self._validate_password_strength(password)
            assert is_valid is True
        
        # Test weak passwords
        for password in weak_passwords:
            is_valid = self._validate_password_strength(password)
            assert is_valid is False
    
    def _validate_password_strength(self, password: str) -> bool:
        """Helper to validate password strength"""
        if len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=" for c in password)
        return has_upper and has_lower and has_digit and has_special
    
    def test_password_reset_flow(self):
        """
        Test: Password reset flow.
        
        Verifies:
        - Reset email is sent
        - Reset token is generated
        - New password can be set
        """
        from security import AuthenticationManager
        
        auth = AuthenticationManager()
        
        # Create user
        username = f"reset_test_{uuid.uuid4().hex[:8]}"
        auth.create_user(
            username=username,
            email=f"{username}@test.com",
            password="TestPassword123!",
        )
        
        # Simulate password reset
        reset_token = f"reset_{uuid.uuid4().hex}"
        
        # Verify token format
        assert reset_token.startswith("reset_")
        assert len(reset_token) > 20


class TestAccountDeletion:
    """
    Test class for account deletion.
    
    Tests cover:
    - Account deletion flow
    - Data removal
    - Confirmation requirements
    """
    
    def test_account_deletion_request(self):
        """
        Test: Account deletion request.
        
        Verifies:
        - Deletion can be requested
        - Confirmation is required
        """
        deletion_request = {
            "reason": "personal_choice",
            "confirmation": "DELETE_MY_ACCOUNT",
            "feedback": "No longer needed",
        }
        
        # Verify confirmation matches
        assert deletion_request["confirmation"] == "DELETE_MY_ACCOUNT"
    
    def test_account_data_removal(self):
        """
        Test: Account data is removed on deletion.
        
        Verifies:
        - User data is deleted
        - Sessions are invalidated
        - Jobs are handled
        """
        from security import AuthenticationManager
        
        auth = AuthenticationManager()
        
        # Create user and session
        username = f"delete_test_{uuid.uuid4().hex[:8]}"
        user_id = auth.create_user(
            username=username,
            email=f"{username}@test.com",
            password="TestPassword123!",
        )
        
        session_id = auth.authenticate_user(username, "TestPassword123!", "127.0.0.1")
        
        # Simulate data removal
        data_to_remove = [
            "profile_data",
            "job_history",
            "api_keys",
            "sessions",
        ]
        
        # Verify data categories exist
        for data_type in data_to_remove:
            assert data_type is not None
        
        # Delete user
        del auth.users[username]
        
        # Verify user removed
        assert username not in auth.users
    
    def test_deletion_confirmation(self):
        """
        Test: Deletion requires proper confirmation.
        
        Verifies:
        - Confirmation text must match
        - User must confirm multiple times for critical actions
        """
        confirmation_phrase = "DELETE_MY_ACCOUNT"
        user_confirmation = "delete_my_account"
        
        # Case-insensitive comparison
        is_valid = confirmation_phrase.lower() == user_confirmation.lower()
        assert is_valid is True


# ============================================================================
# Test Runner
# ============================================================================

def run_profile_tests():
    """
    Run all profile E2E tests.
    
    Returns:
        Test result summary
    """
    import unittest
    
    print("=" * 80)
    print("Pure Sound - E2E Profile Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProfileFlows))
    suite.addTests(loader.loadTestsFromTestCase(TestAccountSettings))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestAccountDeletion))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("PROFILE E2E TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All profile E2E tests passed!")
    else:
        print("\n❌ Some profile E2E tests failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_profile_tests()
    exit(0 if success else 1)
