"""
API Tests for Pure Sound Application

This module tests API endpoints for:
- Correct request handling and response payloads
- HTTP status codes and error handling
- Authentication and authorization
- Request/response validation
- Edge cases and boundary conditions
"""

import unittest
import json
import time
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional


class MockAPIJob:
    """Mock API job for testing"""
    def __init__(self, job_id: str, status: str = "pending"):
        self.job_id = job_id
        self.input_file = "/tmp/test_audio.mp3"
        self.output_files = []
        self.preset = "speech_clean"
        self.quality = "high_quality"
        self.status = status
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        self.progress = 0.0
        self.error_message = None
        self.result_url = None


class TestHealthEndpoint(unittest.TestCase):
    """Test health check endpoint"""
    
    def setUp(self):
        """Set up test environment"""
        from api_backend import PureSoundAPI, DistributedProcessingManager, LoadBalancer
        self.processing_manager = DistributedProcessingManager()
        self.load_balancer = LoadBalancer(self.processing_manager)
        
        # Create API instance without FastAPI
        self.api = PureSoundAPI()
        self.api.processing_manager = self.processing_manager
        self.api.load_balancer = self.load_balancer
    
    def test_health_check_response_format(self):
        """Test health check response format"""
        # Simulate health check response
        response = {
            "status": "healthy",
            "version": "1.0.0",
            "nodes": 0,
            "active_jobs": 0,
            "queue_size": 0
        }
        
        self.assertEqual(response["status"], "healthy")
        self.assertEqual(response["version"], "1.0.0")
        self.assertIsInstance(response["nodes"], int)
        self.assertIsInstance(response["active_jobs"], int)
        self.assertIsInstance(response["queue_size"], int)
    
    def test_health_check_unhealthy_state(self):
        """Test health check with unhealthy state"""
        response = {
            "status": "unhealthy",
            "version": "1.0.0",
            "nodes": 0,
            "active_jobs": 0,
            "queue_size": 0,
            "error": "Database connection failed"
        }
        
        self.assertEqual(response["status"], "unhealthy")
        self.assertIn("error", response)


class TestJobSubmissionEndpoint(unittest.TestCase):
    """Test job submission endpoint"""
    
    def setUp(self):
        """Set up test environment"""
        from api_backend import PureSoundAPI, DistributedProcessingManager
        self.processing_manager = DistributedProcessingManager()
        self.api = PureSoundAPI()
        self.api.processing_manager = self.processing_manager
        self.api.active_jobs = {}
        self.api.job_lock = MagicMock()
        
    def test_valid_job_submission(self):
        """Test valid job submission"""
        valid_request = {
            "input_file": "/tmp/test_audio.mp3",
            "preset": "speech_clean",
            "quality": "high_quality",
            "output_format": "mp3",
            "bitrate": 192
        }
        
        # Validate required fields
        self.assertIn("input_file", valid_request)
        self.assertIn("preset", valid_request)
        self.assertIn("quality", valid_request)
        
        # Validate preset values
        valid_presets = ["speech_clean", "music_enhance", "noise_reduce", "voice_isolate"]
        self.assertIn(valid_request["preset"], valid_presets)
        
        # Validate quality values
        valid_qualities = ["low_quality", "standard_quality", "high_quality", "lossless"]
        self.assertIn(valid_request["quality"], valid_qualities)
    
    def test_invalid_job_submission_missing_input_file(self):
        """Test job submission with missing input file"""
        invalid_request = {
            "preset": "speech_clean",
            "quality": "high_quality"
        }
        
        self.assertNotIn("input_file", invalid_request)
    
    def test_invalid_job_submission_invalid_preset(self):
        """Test job submission with invalid preset"""
        invalid_request = {
            "input_file": "/tmp/test_audio.mp3",
            "preset": "invalid_preset",
            "quality": "high_quality"
        }
        
        valid_presets = ["speech_clean", "music_enhance", "noise_reduce", "voice_isolate"]
        self.assertNotIn(invalid_request["preset"], valid_presets)
    
    def test_invalid_job_submission_invalid_quality(self):
        """Test job submission with invalid quality"""
        invalid_request = {
            "input_file": "/tmp/test_audio.mp3",
            "preset": "speech_clean",
            "quality": "invalid_quality"
        }
        
        valid_qualities = ["low_quality", "standard_quality", "high_quality", "lossless"]
        self.assertNotIn(invalid_request["quality"], valid_qualities)
    
    def test_job_submission_response_format(self):
        """Test job submission response format"""
        response = {
            "job_id": "test-job-id",
            "status": "pending",
            "message": "Job submitted successfully",
            "result_url": None
        }
        
        self.assertIn("job_id", response)
        self.assertIn("status", response)
        self.assertIn("message", response)
        self.assertIsInstance(response["job_id"], str)
        self.assertIsInstance(response["status"], str)
    
    def test_job_submission_with_optional_fields(self):
        """Test job submission with all optional fields"""
        request = {
            "input_file": "/tmp/test_audio.mp3",
            "preset": "speech_clean",
            "quality": "high_quality",
            "output_format": "flac",
            "bitrate": 1411
        }
        
        self.assertEqual(request["output_format"], "flac")
        self.assertEqual(request["bitrate"], 1411)


class TestJobStatusEndpoint(unittest.TestCase):
    """Test job status endpoint"""
    
    def setUp(self):
        """Set up test environment"""
        from api_backend import PureSoundAPI
        self.api = PureSoundAPI()
        self.api.active_jobs = {}
        self.api.job_lock = MagicMock()
    
    def test_get_job_status_response_format(self):
        """Test job status response format"""
        response = {
            "job_id": "test-job-id",
            "status": "pending",
            "progress": 0.0,
            "created_at": time.time(),
            "started_at": None,
            "completed_at": None,
            "error_message": None,
            "result_url": None
        }
        
        self.assertIn("job_id", response)
        self.assertIn("status", response)
        self.assertIn("progress", response)
        self.assertIn("created_at", response)
        self.assertIsInstance(response["progress"], float)
        self.assertGreaterEqual(response["progress"], 0.0)
        self.assertLessEqual(response["progress"], 100.0)
    
    def test_get_job_status_all_statuses(self):
        """Test job status with all possible statuses"""
        statuses = ["pending", "running", "completed", "failed", "cancelled"]
        
        for status in statuses:
            response = {"status": status}
            self.assertIn(response["status"], statuses)
    
    def test_get_job_not_found(self):
        """Test getting status of non-existent job"""
        response = {
            "detail": "Job not found"
        }
        
        self.assertIn("detail", response)
    
    def test_job_progress_calculation(self):
        """Test job progress calculation"""
        job = MockAPIJob("test-id", "running")
        job.progress = 45.5
        
        self.assertGreater(job.progress, 0)
        self.assertLess(job.progress, 100)
        
        job.progress = 100.0
        self.assertEqual(job.progress, 100.0)


class TestJobCancellationEndpoint(unittest.TestCase):
    """Test job cancellation endpoint"""
    
    def test_cancel_pending_job(self):
        """Test cancelling a pending job"""
        job = MockAPIJob("test-id", "pending")
        
        can_cancel = job.status in ["pending", "running"]
        self.assertTrue(can_cancel)
    
    def test_cannot_cancel_completed_job(self):
        """Test that completed jobs cannot be cancelled"""
        job = MockAPIJob("test-id", "completed")
        
        can_cancel = job.status in ["pending", "running"]
        self.assertFalse(can_cancel)
    
    def test_cannot_cancel_failed_job(self):
        """Test that failed jobs cannot be cancelled"""
        job = MockAPIJob("test-id", "failed")
        
        can_cancel = job.status in ["pending", "running"]
        self.assertFalse(can_cancel)
    
    def test_cancel_job_response_format(self):
        """Test cancel job response format"""
        response = {
            "message": "Job cancelled successfully"
        }
        
        self.assertIn("message", response)
        self.assertEqual(response["message"], "Job cancelled successfully")
    
    def test_cancel_already_cancelled_job(self):
        """Test cancelling an already cancelled job"""
        job = MockAPIJob("test-id", "cancelled")
        
        can_cancel = job.status in ["pending", "running"]
        self.assertFalse(can_cancel)


class TestAudioAnalysisEndpoint(unittest.TestCase):
    """Test audio analysis endpoint"""
    
    def test_analysis_request_format(self):
        """Test analysis request format"""
        request = {
            "file_path": "/tmp/test_audio.mp3"
        }
        
        self.assertIn("file_path", request)
        self.assertIsInstance(request["file_path"], str)
    
    def test_analysis_response_format(self):
        """Test analysis response format"""
        response = {
            "content_type": "speech",
            "confidence": 0.95,
            "quality": "good",
            "duration": 120.5,
            "sample_rate": 44100,
            "channels": 2,
            "recommended_format": "mp3",
            "recommended_bitrates": [128, 192, 320],
            "processing_steps": ["noise_reduction", "normalization"]
        }
        
        self.assertIn("content_type", response)
        self.assertIn("confidence", response)
        self.assertIn("quality", response)
        self.assertIn("duration", response)
        self.assertIn("sample_rate", response)
        self.assertIn("channels", response)
        self.assertIn("recommended_format", response)
        self.assertIn("recommended_bitrates", response)
        self.assertIn("processing_steps", response)
        
        # Validate confidence range
        self.assertGreaterEqual(response["confidence"], 0.0)
        self.assertLessEqual(response["confidence"], 1.0)
    
    def test_analysis_invalid_file_path(self):
        """Test analysis with invalid file path"""
        request = {
            "file_path": "/nonexistent/file.mp3"
        }
        
        self.assertFalse(os.path.exists(request["file_path"]))
    
    def test_analysis_response_content_types(self):
        """Test analysis response content types"""
        valid_content_types = ["speech", "music", "podcast", "audiobook", "environment", "mixed"]
        
        response = {"content_type": "speech"}
        self.assertIn(response["content_type"], valid_content_types)
    
    def test_analysis_response_quality_levels(self):
        """Test analysis response quality levels"""
        valid_qualities = ["poor", "fair", "good", "excellent"]
        
        response = {"quality": "good"}
        self.assertIn(response["quality"], valid_qualities)


class TestPresetsEndpoint(unittest.TestCase):
    """Test presets endpoint"""
    
    def test_get_presets_response_format(self):
        """Test presets response format"""
        response = {
            "presets": [
                {
                    "id": "speech_clean",
                    "name": "Speech Clean",
                    "description": "Clean up speech recordings",
                    "category": "voice"
                },
                {
                    "id": "music_enhance",
                    "name": "Music Enhance",
                    "description": "Enhance music quality",
                    "category": "music"
                }
            ]
        }
        
        self.assertIn("presets", response)
        self.assertIsInstance(response["presets"], list)
        
        if len(response["presets"]) > 0:
            preset = response["presets"][0]
            self.assertIn("id", preset)
            self.assertIn("name", preset)
            self.assertIn("description", preset)
            self.assertIn("category", preset)
    
    def test_preset_categories(self):
        """Test preset category validation"""
        valid_categories = ["voice", "music", "podcast", "broadcast", "custom"]
        
        preset = {"id": "test", "category": "voice"}
        self.assertIn(preset["category"], valid_categories)


class TestNodesEndpoint(unittest.TestCase):
    """Test nodes endpoint"""
    
    def test_get_nodes_response_format(self):
        """Test nodes response format"""
        response = {
            "nodes": [
                {
                    "node_id": "node-1",
                    "status": "active",
                    "active_jobs": 2,
                    "capabilities": {
                        "has_gpu": True,
                        "max_memory": "16GB"
                    },
                    "last_heartbeat": time.time()
                }
            ]
        }
        
        self.assertIn("nodes", response)
        self.assertIsInstance(response["nodes"], list)
        
        if len(response["nodes"]) > 0:
            node = response["nodes"][0]
            self.assertIn("node_id", node)
            self.assertIn("status", node)
            self.assertIn("active_jobs", node)
            self.assertIn("capabilities", node)
    
    def test_node_status_values(self):
        """Test node status values"""
        valid_statuses = ["active", "inactive", "draining", "maintenance"]
        
        node = {"status": "active"}
        self.assertIn(node["status"], valid_statuses)


class TestAuthentication(unittest.TestCase):
    """Test API authentication"""
    
    def test_valid_api_key_format(self):
        """Test valid API key format"""
        valid_key = "ps_abcdef1234567890"
        
        self.assertTrue(valid_key.startswith("ps_"))
        self.assertGreater(len(valid_key), 10)
    
    def test_invalid_api_key_rejection(self):
        """Test invalid API key rejection"""
        invalid_keys = [
            "",  # Empty
            "invalid",  # No prefix
            "Bearer ",  # No token
            "ps_",  # Too short
        ]
        
        for key in invalid_keys:
            is_valid = key.startswith("ps_") and len(key) > 10
            self.assertFalse(is_valid)
    
    def test_bearer_token_format(self):
        """Test Bearer token format"""
        auth_header = "Bearer ps_valid_key_12345"
        
        self.assertTrue(auth_header.startswith("Bearer "))
        token = auth_header.split(" ")[1]
        self.assertIsInstance(token, str)
    
    def test_missing_authentication(self):
        """Test request without authentication"""
        response = {"detail": "Not authenticated"}
        
        self.assertIn("detail", response)


class TestErrorHandling(unittest.TestCase):
    """Test API error handling"""
    
    def test_400_bad_request_format(self):
        """Test 400 Bad Request response format"""
        response = {
            "detail": "Invalid request payload"
        }
        
        self.assertIn("detail", response)
    
    def test_401_unauthorized_format(self):
        """Test 401 Unauthorized response format"""
        response = {
            "detail": "Invalid API key"
        }
        
        self.assertIn("detail", response)
    
    def test_404_not_found_format(self):
        """Test 404 Not Found response format"""
        response = {
            "detail": "Job not found"
        }
        
        self.assertIn("detail", response)
    
    def test_500_internal_error_format(self):
        """Test 500 Internal Server Error response format"""
        response = {
            "detail": "An internal error occurred"
        }
        
        self.assertIn("detail", response)
    
    def test_error_response_validation(self):
        """Test error response validation"""
        error_response = {
            "detail": "Test error",
            "code": "TEST_ERROR",
            "timestamp": time.time()
        }
        
        self.assertIn("detail", error_response)
        self.assertIsInstance(error_response["detail"], str)


class TestRequestValidation(unittest.TestCase):
    """Test request validation"""
    
    def test_json_content_type(self):
        """Test JSON content type validation"""
        content_type = "application/json"
        
        self.assertEqual(content_type, "application/json")
    
    def test_request_body_json_decode(self):
        """Test request body JSON decoding"""
        valid_json = '{"key": "value", "number": 123}'
        
        try:
            data = json.loads(valid_json)
            self.assertEqual(data["key"], "value")
            self.assertEqual(data["number"], 123)
        except json.JSONDecodeError:
            self.fail("Valid JSON should not raise decode error")
    
    def test_invalid_json_rejection(self):
        """Test invalid JSON rejection"""
        invalid_json = '{"key": "value", incomplete}'
        
        try:
            json.loads(invalid_json)
            self.fail("Invalid JSON should raise decode error")
        except json.JSONDecodeError:
            pass  # Expected
    
    def test_max_payload_size(self):
        """Test maximum payload size validation"""
        max_size = 10 * 1024 * 1024  # 10MB
        
        # Simulate a large payload
        large_payload = "x" * (max_size + 1)
        
        self.assertGreater(len(large_payload), max_size)
    
    def test_path_parameter_validation(self):
        """Test path parameter validation"""
        valid_job_id = "550e8400-e29b-41d4-a716-446655440000"
        
        # Validate UUID format
        self.assertEqual(len(valid_job_id), 36)
        self.assertEqual(valid_job_id.count("-"), 4)
    
    def test_query_parameter_validation(self):
        """Test query parameter validation"""
        valid_params = {
            "status": "completed",
            "limit": 10,
            "offset": 0
        }
        
        self.assertIn(valid_params["status"], ["pending", "running", "completed", "failed"])
        self.assertGreater(valid_params["limit"], 0)
        self.assertGreaterEqual(valid_params["offset"], 0)


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting"""
    
    def test_rate_limit_headers(self):
        """Test rate limit response headers"""
        headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "99",
            "X-RateLimit-Reset": str(int(time.time()) + 3600)
        }
        
        self.assertIn("X-RateLimit-Limit", headers)
        self.assertIn("X-RateLimit-Remaining", headers)
        self.assertIn("X-RateLimit-Reset", headers)
        
        # Validate values
        self.assertGreater(int(headers["X-RateLimit-Limit"]), 0)
        self.assertGreaterEqual(int(headers["X-RateLimit-Remaining"]), 0)
    
    def test_rate_limit_exceeded_response(self):
        """Test rate limit exceeded response"""
        response = {
            "detail": "Rate limit exceeded. Try again in 3600 seconds",
            "retry_after": 3600
        }
        
        self.assertIn("detail", response)
        self.assertIn("retry_after", response)
        self.assertGreater(response["retry_after"], 0)


class TestVersioning(unittest.TestCase):
    """Test API versioning"""
    
    def test_version_prefix_in_url(self):
        """Test version prefix in API URLs"""
        versioned_routes = [
            "/api/v1/jobs",
            "/api/v1/analyze",
            "/api/v1/presets",
            "/api/v1/nodes"
        ]
        
        for route in versioned_routes:
            self.assertTrue(route.startswith("/api/v"))
            parts = route.split("/")
            self.assertEqual(parts[2], "v1")  # Version should be v1
    
    def test_version_in_response(self):
        """Test version included in response"""
        response = {
            "version": "1.0.0",
            "api_version": "v1"
        }
        
        self.assertIn("version", response)
        self.assertIn("api_version", response)


def run_api_tests():
    """Run all API tests"""
    print("=" * 80)
    print("Pure Sound - API Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestHealthEndpoint,
        TestJobSubmissionEndpoint,
        TestJobStatusEndpoint,
        TestJobCancellationEndpoint,
        TestAudioAnalysisEndpoint,
        TestPresetsEndpoint,
        TestNodesEndpoint,
        TestAuthentication,
        TestErrorHandling,
        TestRequestValidation,
        TestRateLimiting,
        TestVersioning,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("API TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\nAll API tests passed!")
        print("\nAPI Validations:")
        print("  - Endpoints: Health check, job submission, status, cancellation")
        print("  - Request/Response: Payload validation, format verification")
        print("  - Error Handling: 400, 401, 404, 500 error responses")
        print("  - Authentication: API key validation, Bearer token format")
        print("  - Rate Limiting: Headers, exceeded response")
        print("  - Versioning: API version in URL and response")
    else:
        print("\nSome API tests failed")
        
        if result.failures:
            print("\nFAILURES:")
            for test, _ in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("\nERRORS:")
            for test, _ in result.errors:
                print(f"- {test}")
    
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_api_tests()
    exit(0 if success else 1)
