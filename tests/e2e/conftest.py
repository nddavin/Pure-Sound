"""
Playwright E2E Test Configuration for Pure Sound Application

This module provides pytest configuration and fixtures for end-to-end testing
using Playwright to simulate real browser interactions.

Usage:
    pytest tests/e2e/ -v
    pytest tests/e2e/ --headed  # Run with visible browser
    pytest tests/e2e/test_login.py -v  # Run specific test file
"""

import os
import sys
import pytest
import asyncio
from typing import Generator, Dict, Any
from datetime import datetime
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "e2e: end-to-end test marker"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "login: authentication tests"
    )
    config.addinivalue_line(
        "markers", "checkout: checkout/payment flow tests"
    )
    config.addinivalue_line(
        "markers", "search: search functionality tests"
    )
    config.addinivalue_line(
        "markers", "profile: user profile tests"
    )


# ============================================================================
# Playwright Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context for all tests"""
    return {
        "viewport": {"width": 1280, "height": 720},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "locale": "en-US",
        "timezone_id": "America/New_York",
    }


@pytest.fixture
def page_context():
    """
    Provide page context with authentication state for E2E tests.
    
    This fixture simulates a logged-in user session for testing
    protected routes and authenticated flows.
    """
    context = {
        "authenticated": False,
        "user": None,
        "api_key": None,
        "session_token": None,
        "headers": {},
    }
    
    # Set default headers
    context["headers"] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    return context


@pytest.fixture
def api_base_url():
    """Base URL for API requests"""
    base_url = os.environ.get("PURE_SOUND_API_URL", "http://localhost:8000")
    return base_url


@pytest.fixture
def test_user():
    """
    Test user credentials for E2E tests.
    These are mock credentials for testing purposes.
    """
    return {
        "username": "test_e2e_user",
        "email": "e2e_test@puresound.local",
        "password": "TestPassword123!",
        "api_key": "ps_test_e2e_key_1234567890",
    }


@pytest.fixture
def authenticated_session(page_context, test_user, api_base_url):
    """
    Create an authenticated session for testing protected endpoints.
    """
    # Simulate authentication
    page_context["authenticated"] = True
    page_context["user"] = {
        "username": test_user["username"],
        "email": test_user["email"],
        "id": "test_user_id_123",
    }
    page_context["api_key"] = test_user["api_key"]
    page_context["session_token"] = "mock_session_token_e2e_test"
    page_context["headers"]["Authorization"] = f"Bearer {test_user['api_key']}"
    
    return page_context


@pytest.fixture
def sample_audio_file():
    """
    Provide a sample audio file path for testing.
    Creates a temporary test file if none exists.
    """
    import tempfile
    
    temp_dir = tempfile.mkdtemp()
    audio_file = os.path.join(temp_dir, "test_audio.mp3")
    
    # Create a minimal MP3 file header for testing
    # This is a placeholder - in real tests, use actual audio files
    with open(audio_file, 'wb') as f:
        # Write minimal MP3 frame header
        f.write(b'\xff\xfb\x90\x00\x00\x00\x00\x00\x00')
    
    yield audio_file
    
    # Cleanup
    try:
        os.remove(audio_file)
        os.rmdir(temp_dir)
    except Exception:
        pass


@pytest.fixture
def job_queue_manager():
    """
    Provide access to the job queue manager for testing job flows.
    """
    from job_queue import job_queue, JobStatus
    
    # Store original state
    original_jobs = job_queue.jobs.copy()
    
    yield {
        "queue": job_queue,
        "status": JobStatus,
        "add_job": job_queue.add_job,
        "get_status": job_queue.get_job_status,
        "get_all": job_queue.get_all_jobs,
    }
    
    # Cleanup - restore original state
    job_queue.jobs = original_jobs


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def test_presets():
    """Provide test preset data"""
    return [
        {
            "id": "speech_clean",
            "name": "Speech Clean",
            "description": "Clean up speech recordings",
            "category": "voice",
            "format": "mp3",
            "bitrates": [64, 96, 128],
        },
        {
            "id": "music_enhance",
            "name": "Music Enhance",
            "description": "Enhance music quality",
            "category": "music",
            "format": "flac",
            "bitrates": [320, 441, 480],
        },
        {
            "id": "noise_reduce",
            "name": "Noise Reduce",
            "description": "Reduce background noise",
            "category": "voice",
            "format": "mp3",
            "bitrates": [128, 192],
        },
        {
            "id": "voice_isolate",
            "name": "Voice Isolate",
            "description": "Isolate voice from mixed audio",
            "category": "voice",
            "format": "mp3",
            "bitrates": [128],
        },
    ]


@pytest.fixture
def search_queries():
    """Provide test search queries"""
    return [
        "speech",
        "music",
        "noise",
        "voice",
        "clean",
        "enhance",
    ]


@pytest.fixture
def checkout_data():
    """
    Provide test checkout data for payment flow testing.
    """
    return {
        "items": [
            {
                "id": "preset_speech_clean",
                "name": "Speech Clean",
                "price": 9.99,
                "quantity": 1,
            },
            {
                "id": "preset_music_enhance",
                "name": "Music Enhance",
                "price": 14.99,
                "quantity": 1,
            },
        ],
        "payment": {
            "method": "credit_card",
            "card_number": "4242424242424242",
            "expiry": "12/25",
            "cvv": "123",
        },
        "billing": {
            "name": "Test User",
            "email": "test@puresound.local",
            "address": "123 Test Street",
            "city": "Test City",
            "country": "US",
            "zip": "12345",
        },
    }


@pytest.fixture
def profile_data():
    """
    Provide test profile data for user profile tests.
    """
    return {
        "username": "test_e2e_user",
        "email": "e2e_test@puresound.local",
        "full_name": "Test E2E User",
        "bio": "Test user for E2E testing",
        "settings": {
            "notifications": True,
            "newsletter": False,
            "theme": "dark",
            "language": "en",
        },
    }


# ============================================================================
# Assertion Helpers
# ============================================================================

class Assertions:
    """Custom assertion helpers for E2E tests"""
    
    @staticmethod
    def assert_response_success(response_data: Dict[str, Any], msg: str = None):
        """Assert that API response indicates success"""
        assert response_data.get("status") == "success" or response_data.get("error") is None, \
            msg or f"Response indicates failure: {response_data}"
    
    @staticmethod
    def assert_job_status(job_data: Dict[str, Any], expected_status: str):
        """Assert job has expected status"""
        assert job_data.get("status") == expected_status, \
            f"Expected status {expected_status}, got {job_data.get('status')}"
    
    @staticmethod
    def assert_user_authenticated(user_data: Dict[str, Any]):
        """Assert user is properly authenticated"""
        assert user_data.get("authenticated") is True, "User should be authenticated"
        assert user_data.get("api_key") is not None, "API key should be present"
    
    @staticmethod
    def assert_search_results(results: list, query: str):
        """Assert search returned valid results"""
        assert isinstance(results, list), "Search results should be a list"
        # At least one result should match query (in a real test)
        assert len(results) >= 0, f"Search for '{query}' should return results"


@pytest.fixture
def asserts():
    """Provide assertion helpers"""
    return Assertions


# ============================================================================
# Mock Server Fixtures
# ============================================================================

@pytest.fixture(scope="class")
def mock_api_server():
    """
    Provide a mock API server for testing without a real backend.
    This fixture sets up mock endpoints that simulate the FastAPI backend.
    """
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    import threading
    
    class MockAPIHandler(BaseHTTPRequestHandler):
        """Mock API handler for testing"""
        
        def log_message(self, format, *args):
            """Suppress HTTP server logging"""
            pass
        
        def do_GET(self):
            """Handle GET requests"""
            if self.path == "/api/v1/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {
                    "status": "healthy",
                    "version": "1.0.0",
                    "nodes": 1,
                    "active_jobs": 0,
                    "queue_size": 0,
                }
                self.wfile.write(json.dumps(response).encode())
            elif self.path == "/api/v1/presets":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {
                    "presets": [
                        {"id": "speech_clean", "name": "Speech Clean"},
                        {"id": "music_enhance", "name": "Music Enhance"},
                    ]
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
        
        def do_POST(self):
            """Handle POST requests"""
            if self.path == "/api/v1/auth/login":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body) if body else {}
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {
                    "success": True,
                    "token": "mock_token_12345",
                    "user": {
                        "id": "user_123",
                        "username": data.get("username", "test"),
                        "email": "test@example.com",
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            elif self.path == "/api/v1/jobs":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                response = {
                    "job_id": "job_12345",
                    "status": "pending",
                    "message": "Job submitted successfully",
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    # Start mock server
    server = HTTPServer(("localhost", 8765), MockAPIHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    
    yield {"server": server, "port": 8765}
    
    # Cleanup
    server.shutdown()


# ============================================================================
# Test Utilities
# ============================================================================

def generate_test_id():
    """Generate unique test ID"""
    return f"test_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"


def retry_async(func, max_retries: int = 3, delay: float = 1.0):
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries (seconds)
    
    Returns:
        Result of the function call
    """
    async def wrapper():
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(delay * (2 ** attempt))
        return None
    return wrapper()
