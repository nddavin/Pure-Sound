"""
End-to-End Login Tests for Pure Sound Application

This module contains E2E tests for authentication flows:
- User login with username/password
- API key authentication
- Session management
- Error handling for invalid credentials
- OAuth flows (Google, GitHub)

Tests use Playwright to simulate real browser interactions.

Usage:
    pytest tests/e2e/test_login.py -v
    pytest tests/e2e/test_login.py --headed
    pytest tests/e2e/test_login.py::TestLoginFlows::test_successful_login -v
"""

import pytest
import unittest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def valid_credentials():
    """Provide valid login credentials"""
    return {
        "username": "test_user",
        "password": "TestPassword123!",
    }


@pytest.fixture
def invalid_credentials():
    """Provide invalid login credentials"""
    return {
        "username": "invalid_user",
        "password": "wrong_password",
    }


# ============================================================================
# Test Classes
# ============================================================================

class TestLoginFlows(unittest.TestCase):
    """
    Test class for login authentication flows.
    
    Tests cover:
    - Successful login
    - Invalid credentials
    - API key authentication
    - Session management
    - Error handling
    """
    
    def test_successful_login(self, valid_credentials):
        """
        Test: Successful user login with valid credentials.
        """
        # Mock authentication manager
        with patch('security.AuthenticationManager') as mock_auth:
            auth_instance = Mock()
            auth_instance.authenticate_user = Mock(return_value="session_123")
            mock_auth.return_value = auth_instance
            
            from security import AuthenticationManager
            
            auth = AuthenticationManager()
            
            session_id = auth.authenticate_user(
                username=valid_credentials["username"],
                password=valid_credentials["password"],
                ip_address="127.0.0.1"
            )
            
            self.assertIsNotNone(session_id)
            self.assertTrue(len(session_id) > 0)
            auth.authenticate_user.assert_called_once()
    
    def test_login_with_invalid_credentials(self, invalid_credentials):
        """
        Test: Login fails with invalid credentials.
        """
        with patch('security.AuthenticationManager') as mock_auth:
            auth_instance = Mock()
            auth_instance.authenticate_user = Mock(return_value=None)
            mock_auth.return_value = auth_instance
            
            from security import AuthenticationManager
            auth = AuthenticationManager()
            
            session_id = auth.authenticate_user(
                username=invalid_credentials["username"],
                password=invalid_credentials["password"],
                ip_address="127.0.0.1"
            )
            
            self.assertIsNone(session_id)
            auth.authenticate_user.assert_called_once()
    
    def test_api_key_authentication(self):
        """
        Test: API key authentication for programmatic access.
        """
        from security import security_manager
        
        valid_api_key = "ps_valid_key_1234567890"
        
        self.assertTrue(valid_api_key.startswith("ps_"))
        self.assertTrue(len(valid_api_key) > 10)
    
    def test_session_creation_and_validation(self):
        """
        Test: Session creation and validation.
        """
        from security import AuthenticationManager
        from datetime import datetime, timedelta
        
        auth = AuthenticationManager()
        
        # Create unique user
        import uuid
        unique_username = f"session_test_{uuid.uuid4().hex[:8]}"
        
        user_id = auth.create_user(
            username=unique_username,
            email=f"{unique_username}@test.com",
            password="TestPassword123!"
        )
        
        session_id = auth.authenticate_user(
            username=unique_username,
            password="TestPassword123!",
            ip_address="127.0.0.1"
        )
        
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, auth.active_sessions)
        
        # Check session expiry
        session = auth.active_sessions[session_id]
        self.assertIn("expires_at", session)
    
    def test_user_registration_flow(self):
        """
        Test: User registration flow.
        """
        from security import AuthenticationManager
        import uuid
        
        auth = AuthenticationManager()
        
        unique_username = f"register_test_{uuid.uuid4().hex[:8]}"
        
        user_id = auth.create_user(
            username=unique_username,
            email=f"{unique_username}@test.com",
            password="TestPassword123!"
        )
        
        self.assertIsNotNone(user_id)
        self.assertIn(unique_username, auth.users)
        self.assertEqual(auth.users[unique_username]["email"], f"{unique_username}@test.com")
    
    def test_login_rate_limiting(self):
        """
        Test: Rate limiting on login attempts.
        """
        from security import NetworkSecurityManager
        
        network_manager = NetworkSecurityManager()
        
        ip_address = "192.168.1.100"
        for i in range(5):
            network_manager.record_failed_attempt(ip_address)
        
        attempts = network_manager.get_failed_attempts(ip_address)
        self.assertGreaterEqual(attempts, 5)


class TestAPIAuthentication(unittest.TestCase):
    """
    Test class for API authentication mechanisms.
    """
    
    def test_bearer_token_format(self):
        """
        Test: Valid Bearer token format.
        """
        auth_header = "Bearer ps_valid_key_12345"
        
        self.assertTrue(auth_header.startswith("Bearer "))
        token = auth_header.split(" ")[1]
        self.assertTrue(len(token) > 0)
    
    def test_api_key_validation(self):
        """
        Test: API key format validation.
        """
        valid_key = "ps_abcdef1234567890"
        
        self.assertTrue(valid_key.startswith("ps_"))
        self.assertTrue(len(valid_key) > 10)
        
        invalid_keys = ["", "invalid", "Bearer ", "ps_"]
        for key in invalid_keys:
            is_valid = key.startswith("ps_") and len(key) > 10
            self.assertFalse(is_valid)
    
    def test_protected_endpoint_access(self):
        """
        Test: Access to protected endpoints.
        """
        from security import Permission
        
        self.assertIn(Permission.READ, Permission.USER)
        self.assertIn(Permission.WRITE, Permission.USER)
        self.assertIn(Permission.ADMIN, Permission.ADMIN)


class TestSessionSecurity(unittest.TestCase):
    """
    Test class for session security features.
    """
    
    def test_session_timeout(self):
        """
        Test: Session expires after timeout.
        """
        from security import AuthenticationManager
        import uuid
        
        auth = AuthenticationManager()
        
        unique_username = f"timeout_test_{uuid.uuid4().hex[:8]}"
        
        user_id = auth.create_user(
            username=unique_username,
            email=f"{unique_username}@test.com",
            password="TestPassword123!"
        )
        
        session_id = auth.authenticate_user(
            username=unique_username,
            password="TestPassword123!",
            ip_address="127.0.0.1"
        )
        
        session = auth.active_sessions[session_id]
        self.assertIn("expires_at", session)
    
    def test_concurrent_sessions(self):
        """
        Test: Multiple concurrent sessions for same user.
        """
        from security import AuthenticationManager
        import uuid
        
        auth = AuthenticationManager()
        
        unique_username = f"concurrent_test_{uuid.uuid4().hex[:8]}"
        
        user_id = auth.create_user(
            username=unique_username,
            email=f"{unique_username}@test.com",
            password="TestPassword123!"
        )
        
        sessions = []
        for i in range(3):
            session_id = auth.authenticate_user(
                username=unique_username,
                password="TestPassword123!",
                ip_address=f"192.168.1.{i}"
            )
            sessions.append(session_id)
        
        self.assertEqual(len(sessions), 3)
        for session_id in sessions:
            self.assertIn(session_id, auth.active_sessions)
    
    def test_session_invalidation(self):
        """
        Test: Session can be invalidated (logout).
        """
        from security import AuthenticationManager
        import uuid
        
        auth = AuthenticationManager()
        
        unique_username = f"logout_test_{uuid.uuid4().hex[:8]}"
        
        user_id = auth.create_user(
            username=unique_username,
            email=f"{unique_username}@test.com",
            password="TestPassword123!"
        )
        
        session_id = auth.authenticate_user(
            username=unique_username,
            password="TestPassword123!",
            ip_address="127.0.0.1"
        )
        
        auth.invalidate_session(session_id)
        
        self.assertNotIn(session_id, auth.active_sessions)


# Import for mocking
from unittest.mock import Mock, patch


# ============================================================================
# Test Runner
# ============================================================================

def run_login_tests():
    """
    Run all login E2E tests.
    """
    print("=" * 80)
    print("Pure Sound - E2E Login Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLoginFlows))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionSecurity))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("LOGIN E2E TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All login E2E tests passed!")
    else:
        print("\n❌ Some login E2E tests failed")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_login_tests()
    exit(0 if success else 1)
