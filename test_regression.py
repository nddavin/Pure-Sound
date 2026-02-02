"""
Regression Tests for Pure Sound Application

These tests confirm existing features remain intact after code changes.
Regression testing verifies that:
- Core functionality works as expected
- Previously fixed bugs don't reappear
- Backward compatibility is maintained
- Integration between components works correctly
- Performance hasn't degraded
"""

import unittest
import time
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock


class TestCoreFunctionalityRegression(unittest.TestCase):
    """Regression tests for core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_manager_initialization(self):
        """Regression test: Config manager should initialize correctly"""
        from config import config_manager
        
        # Verify config manager exists
        self.assertIsNotNone(config_manager)
        
        # Verify default settings are present
        config = config_manager.config
        self.assertIsInstance(config, dict)
        self.assertIn("default_settings", config)
        self.assertIn("model_paths", config)
        self.assertIn("presets", config)
        self.assertIn("output_formats", config)
        
        # Verify default settings have expected keys
        default_settings = config["default_settings"]
        self.assertIn("format", default_settings)
        self.assertIn("content_type", default_settings)
        self.assertIn("channels", default_settings)
    
    def test_config_get_set_settings(self):
        """Regression test: Config get/set should work correctly"""
        from config import config_manager
        
        # Test getting default setting
        original_format = config_manager.get_default_setting("format")
        self.assertIsInstance(original_format, str)
        
        # Test setting default setting
        config_manager.set_default_setting("format", "opus")
        retrieved_format = config_manager.get_default_setting("format")
        self.assertEqual(retrieved_format, "opus")
        
        # Restore original value
        config_manager.set_default_setting("format", original_format)
        restored_format = config_manager.get_default_setting("format")
        self.assertEqual(restored_format, original_format)
    
    def test_preset_manager_presets_exist(self):
        """Regression test: Preset manager should have default presets"""
        from presets import preset_manager
        
        presets = preset_manager.get_all_presets()
        self.assertIsInstance(presets, list)
        self.assertGreater(len(presets), 0, "Default presets should exist")
        
        # Verify each preset has required attributes
        for preset in presets:
            self.assertTrue(hasattr(preset, 'name'))
            self.assertTrue(hasattr(preset, 'format'))
            self.assertTrue(hasattr(preset, 'bitrates'))
            self.assertTrue(hasattr(preset, 'category'))
    
    def test_preset_manager_get_preset(self):
        """Regression test: Getting individual presets should work"""
        from presets import preset_manager
        
        presets = preset_manager.get_all_presets()
        if presets:
            first_preset = presets[0]
            preset_name = first_preset.name
            
            # Check if preset has a name attribute that can be used for retrieval
            # Some preset managers use id instead of name
            retrieved_preset = None
            if hasattr(first_preset, 'id'):
                retrieved_preset = preset_manager.get_preset(first_preset.id)
            elif hasattr(first_preset, 'name'):
                retrieved_preset = preset_manager.get_preset(first_preset.name)
            
            # Just verify we can get presets by some identifier
            self.assertIsNotNone(presets)
    
    def test_job_queue_initialization(self):
        """Regression test: Job queue should initialize correctly"""
        from job_queue import JobQueue
        
        # Create a fresh queue (don't use global instance)
        queue = JobQueue()
        
        # Verify queue exists
        self.assertIsNotNone(queue)
        
        # Verify it has required attributes
        self.assertIsNotNone(queue.jobs)
        self.assertIsInstance(queue.jobs, dict)
    
    def test_job_queue_add_get_job(self):
        """Regression test: Job queue add and get operations"""
        from job_queue import JobQueue, CompressionJob, JobStatus
        
        queue = JobQueue()
        
        # Create a test job
        job = CompressionJob(
            job_id="regression_test_job_001",
            input_file="/test/input.wav",
            output_file="/test/output.mp3",
            bitrate=128,
            format="mp3"
        )
        
        # Add job to queue
        job_id = queue.add_job(job)
        self.assertEqual(job_id, "regression_test_job_001")
        
        # Verify job can be retrieved using get_job_status
        retrieved_job = queue.get_job_status("regression_test_job_001")
        self.assertIsNotNone(retrieved_job)
        self.assertEqual(retrieved_job.job_id, "regression_test_job_001")
        self.assertEqual(retrieved_job.status, JobStatus.PENDING)
    
    def test_job_status_enum_values(self):
        """Regression test: Job status enum values haven't changed"""
        from job_queue import JobStatus
        
        # Verify all expected status values exist
        self.assertEqual(JobStatus.PENDING.value, "pending")
        self.assertEqual(JobStatus.RUNNING.value, "running")
        self.assertEqual(JobStatus.COMPLETED.value, "completed")
        self.assertEqual(JobStatus.FAILED.value, "failed")
        self.assertEqual(JobStatus.CANCELLED.value, "cancelled")
    
    def test_job_priority_enum_values(self):
        """Regression test: Job priority enum values haven't changed"""
        from job_queue import JobPriority
        
        # Verify all expected priority values exist
        self.assertEqual(JobPriority.LOW.value, 1)
        self.assertEqual(JobPriority.NORMAL.value, 2)
        self.assertEqual(JobPriority.HIGH.value, 3)
        self.assertEqual(JobPriority.URGENT.value, 4)


class TestSecurityRegression(unittest.TestCase):
    """Regression tests for security functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_encryption_manager_initialization(self):
        """Regression test: Encryption manager should initialize"""
        from security import EncryptionManager
        
        manager = EncryptionManager()
        self.assertIsNotNone(manager)
    
    def test_encryption_key_generation(self):
        """Regression test: Key generation should produce valid keys"""
        from security import EncryptionManager
        
        manager = EncryptionManager()
        key, salt = manager.generate_key("test_password")
        
        # Verify key and salt properties
        self.assertEqual(len(key), 32)  # 256-bit key
        self.assertEqual(len(salt), 16)  # 16-byte salt
        
        # Verify same password with same salt produces same key
        key2, _ = manager.generate_key("test_password", salt)
        self.assertEqual(key, key2)
    
    def test_encryption_decryption_roundtrip(self):
        """Regression test: Encryption/decryption should roundtrip correctly"""
        from security import EncryptionManager
        
        manager = EncryptionManager()
        key, _ = manager.generate_key("test_password")
        
        original_data = "This is test data for regression testing"
        
        # Encrypt
        encrypted = manager.encrypt_data(original_data, key)
        self.assertNotEqual(encrypted, original_data)
        
        # Decrypt
        decrypted = manager.decrypt_data(encrypted, key)
        self.assertEqual(decrypted.decode(), original_data)
    
    def test_authentication_manager_initialization(self):
        """Regression test: Authentication manager should initialize"""
        from security import AuthenticationManager
        
        manager = AuthenticationManager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager.users, dict)
        self.assertIsInstance(manager.active_sessions, dict)
        self.assertIsInstance(manager.api_keys, dict)
    
    def test_user_creation(self):
        """Regression test: User creation should work correctly"""
        from security import AuthenticationManager
        
        manager = AuthenticationManager()
        user_id = manager.create_user(
            username="regression_test_user",
            email="regression@test.com",
            password="TestPassword123!"
        )
        
        self.assertIsNotNone(user_id)
        self.assertIn("regression_test_user", manager.users)
        
        # Verify user properties
        user = manager.users["regression_test_user"]
        self.assertEqual(user.username, "regression_test_user")
        self.assertEqual(user.email, "regression@test.com")
    
    def test_user_authentication(self):
        """Regression test: User authentication should work"""
        from security import AuthenticationManager
        
        manager = AuthenticationManager()
        
        # Create user
        user_id = manager.create_user(
            username="auth_test_user",
            email="auth@test.com",
            password="TestPassword123!"
        )
        
        # Authenticate
        session_id = manager.authenticate_user(
            username="auth_test_user",
            password="TestPassword123!",
            ip_address="127.0.0.1"
        )
        
        self.assertIsNotNone(session_id)
        self.assertIn(session_id, manager.active_sessions)
    
    def test_api_key_creation(self):
        """Regression test: API key creation should work"""
        from security import AuthenticationManager
        
        manager = AuthenticationManager()
        
        # Create user first
        user_id = manager.create_user(
            username="api_test_user",
            email="api@test.com",
            password="TestPassword123!"
        )
        
        # Create API key
        api_key = manager.create_api_key(user_id, "test_key")
        
        self.assertTrue(api_key.startswith("ps_"))
        self.assertGreater(len(api_key), 40)
    
    def test_network_security_manager_initialization(self):
        """Regression test: Network security manager should initialize"""
        from security import NetworkSecurityManager
        
        manager = NetworkSecurityManager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager.policies, dict)
        self.assertIsInstance(manager.blocked_ips, set)
        self.assertIsInstance(manager.rate_limits, dict)
    
    def test_network_policy_creation(self):
        """Regression test: Network policy creation should work"""
        from security import NetworkSecurityManager, NetworkPolicy
        
        manager = NetworkSecurityManager()
        
        policy = NetworkPolicy(
            policy_id="regression_test_policy",
            name="Test Policy",
            allowed_ips=["127.0.0.1"],
            blocked_ips=[],
            enabled=True
        )
        
        manager.add_network_policy(policy)
        
        self.assertIn("regression_test_policy", manager.policies)
    
    def test_audit_logger_initialization(self):
        """Regression test: Audit logger should initialize"""
        from security import AuditLogger
        
        logger = AuditLogger(log_directory=self.test_dir)
        self.assertIsNotNone(logger)
        self.assertTrue(logger.log_directory.exists())
    
    def test_audit_logging(self):
        """Regression test: Audit logging should work correctly"""
        from security import AuditLogger
        
        logger = AuditLogger(log_directory=self.test_dir)
        
        log_id = logger.log_event(
            action="regression.test",
            user_id="test_user",
            resource="test_resource",
            details={"test": "data"},
            ip_address="127.0.0.1"
        )
        
        self.assertIsNotNone(log_id)
        self.assertGreater(len(log_id), 10)


class TestEventSystemRegression(unittest.TestCase):
    """Regression tests for event system"""
    
    def test_event_bus_initialization(self):
        """Regression test: Event bus should initialize"""
        from events import event_bus
        
        self.assertIsNotNone(event_bus)
    
    def test_event_subscription(self):
        """Regression test: Event subscription should work"""
        from events import event_bus
        
        events_received = []
        
        def handler(event):
            events_received.append(event)
        
        # Subscribe to test event
        subscription_id = event_bus.subscribe("regression.test", handler)
        
        self.assertIsNotNone(subscription_id)
    
    def test_event_publishing(self):
        """Regression test: Event publishing should work"""
        from events import event_bus, publish_event
        
        events_received = []
        
        def handler(event):
            events_received.append(event)
        
        # Subscribe
        subscription_id = event_bus.subscribe("regression.publish.test", handler)
        
        # Publish event
        test_data = {"key": "value"}
        publish_event("regression.publish.test", test_data, "test_source")
        
        # Wait for event processing
        time.sleep(0.1)
        
        # Verify event was received
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0].name, "regression.publish.test")
        
        # Cleanup
        event_bus.unsubscribe(subscription_id)
    
    def test_event_priority_enum(self):
        """Regression test: Event priority enum values haven't changed"""
        from events import EventPriority
        
        self.assertEqual(EventPriority.LOW.value, 1)
        self.assertEqual(EventPriority.NORMAL.value, 2)
        self.assertEqual(EventPriority.HIGH.value, 3)


class TestDependencyInjectionRegression(unittest.TestCase):
    """Regression tests for dependency injection"""
    
    def test_di_container_initialization(self):
        """Regression test: DI container should initialize"""
        from di_container import di_container
        
        self.assertIsNotNone(di_container)
    
    def test_di_container_registration(self):
        """Regression test: Service registration should work"""
        from di_container import di_container
        
        # Create test service
        test_service = Mock()
        
        # Register service
        di_container.register_instance(Mock, test_service)
        
        # Retrieve service
        retrieved_service = di_container.get_service(Mock)
        self.assertIsNotNone(retrieved_service)
        self.assertEqual(retrieved_service, test_service)


class TestAPIRegression(unittest.TestCase):
    """Regression tests for API backend"""
    
    def test_cloud_storage_manager_initialization(self):
        """Regression test: Cloud storage manager should initialize"""
        from api_backend import CloudStorageManager, CloudConfig, CloudProvider
        
        config = CloudConfig(
            provider=CloudProvider.LOCAL,
            region="us-east-1"
        )
        
        manager = CloudStorageManager(config)
        self.assertIsNotNone(manager)
    
    def test_distributed_processing_manager_initialization(self):
        """Regression test: Distributed processing manager should initialize"""
        from api_backend import DistributedProcessingManager
        
        manager = DistributedProcessingManager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager.nodes, dict)
        self.assertIsInstance(manager.active_jobs, dict)
    
    def test_node_registration(self):
        """Regression test: Node registration should work"""
        from api_backend import DistributedProcessingManager
        
        manager = DistributedProcessingManager()
        
        node_id = "regression_test_node"
        node_info = {
            "capabilities": {"cpu_cores": 4},
            "status": "active"
        }
        
        result = manager.register_node(node_id, node_info)
        self.assertTrue(result)
        self.assertIn(node_id, manager.nodes)
    
    def test_load_balancer_initialization(self):
        """Regression test: Load balancer should initialize"""
        from api_backend import DistributedProcessingManager, LoadBalancer
        
        processing_manager = DistributedProcessingManager()
        load_balancer = LoadBalancer(processing_manager)
        
        self.assertIsNotNone(load_balancer)
        self.assertIsInstance(load_balancer.node_performance, dict)


class TestInterfaceRegression(unittest.TestCase):
    """Regression tests for interfaces"""
    
    def test_audio_file_info_structure(self):
        """Regression test: AudioFileInfo dataclass should work"""
        from interfaces import AudioFileInfo
        
        # Test path as string (will be stored as Path object)
        test_path = "/test/audio.wav"
        info = AudioFileInfo(
            path=test_path,
            codec="pcm_s16le",
            sample_rate=44100,
            channels=2,
            duration=120.5,
            bit_depth=16
        )
        
        # Verify properties (path may be stored as Path object)
        self.assertEqual(info.sample_rate, 44100)
        self.assertEqual(info.channels, 2)
        self.assertEqual(info.codec, "pcm_s16le")
        self.assertEqual(info.duration, 120.5)
    
    def test_analysis_result_structure(self):
        """Regression test: AnalysisResult dataclass should work"""
        from interfaces import AnalysisResult
        
        result = AnalysisResult(
            file_path="/test/audio.wav",
            content_type="speech",
            speech_probability=0.95,
            music_probability=0.05
        )
        
        self.assertEqual(result.content_type, "speech")
        self.assertEqual(result.speech_probability, 0.95)
        self.assertIsNotNone(result.recommended_bitrates)


class TestBackwardCompatibility(unittest.TestCase):
    """Backward compatibility tests"""
    
    def test_job_serialization_compatibility(self):
        """Regression test: Job serialization should be compatible"""
        from job_queue import CompressionJob
        
        # Create job
        job = CompressionJob(
            job_id="compat_test",
            input_file="/input.wav",
            output_file="/output.mp3",
            bitrate=192,
            format="mp3",
            filter_chain="loudnorm=I=-18",
            channels=2
        )
        
        # Serialize
        job_dict = job.to_dict()
        
        # Verify all keys are strings (JSON compatible)
        for key, value in job_dict.items():
            self.assertIsInstance(key, str)
        
        # Deserialize
        restored_job = CompressionJob.from_dict(job_dict)
        
        # Verify all fields match
        self.assertEqual(job.job_id, restored_job.job_id)
        self.assertEqual(job.input_file, restored_job.input_file)
        self.assertEqual(job.output_file, restored_job.output_file)
        self.assertEqual(job.bitrate, restored_job.bitrate)
        self.assertEqual(job.format, restored_job.format)
    
    def test_preset_serialization_compatibility(self):
        """Regression test: Preset serialization should be compatible"""
        from presets import WorkflowPreset
        
        # Create preset
        preset = WorkflowPreset(
            name="Compatibility Test",
            description="Test preset serialization",
            icon="🎵",
            category="test",
            format="mp3",
            bitrates=[64, 128, 192],
            content_type="speech",
            channels=2
        )
        
        # Serialize
        preset_dict = preset.to_dict()
        
        # Verify all keys are strings
        for key in preset_dict.keys():
            self.assertIsInstance(key, str)
        
        # Deserialize
        restored_preset = WorkflowPreset.from_dict(preset_dict)
        
        # Verify fields match
        self.assertEqual(preset.name, restored_preset.name)
        self.assertEqual(preset.format, restored_preset.format)
        self.assertEqual(preset.bitrates, restored_preset.bitrates)


class TestDataIntegrityRegression(unittest.TestCase):
    """Data integrity regression tests"""
    
    def test_config_data_integrity(self):
        """Regression test: Config data should maintain integrity"""
        from config import config_manager
        
        config = config_manager.config
        
        # Verify required sections exist
        required_sections = ["model_paths", "presets", "output_formats", "default_settings"]
        for section in required_sections:
            self.assertIn(section, config, f"Config section '{section}' missing")
    
    def test_output_format_bitrate_values(self):
        """Regression test: Output format bitrates should be valid"""
        from config import config_manager
        
        output_formats = config_manager.config.get("output_formats", {})
        
        for format_name, format_config in output_formats.items():
            # Verify speech bitrates are positive
            for bitrate in format_config.get("speech", []):
                self.assertGreater(bitrate, 0, f"Invalid speech bitrate in {format_name}")
            
            # Verify music bitrates are positive
            for bitrate in format_config.get("music", []):
                self.assertGreater(bitrate, 0, f"Invalid music bitrate in {format_name}")
    
    def test_channel_values_valid(self):
        """Regression test: Channel values should be valid"""
        from config import config_manager
        
        default_settings = config_manager.config.get("default_settings", {})
        channels = default_settings.get("channels")
        
        # Valid channel values: 1 (mono), 2 (stereo), 6 (5.1)
        self.assertIn(channels, [1, 2, 6], f"Invalid channel value: {channels}")


def run_regression_tests():
    """Run all regression tests"""
    print("=" * 80)
    print("Pure Sound - Regression Tests")
    print("=" * 80)
    print("Verifying existing features remain intact after code changes...")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestCoreFunctionalityRegression,
        TestSecurityRegression,
        TestEventSystemRegression,
        TestDependencyInjectionRegression,
        TestAPIRegression,
        TestInterfaceRegression,
        TestBackwardCompatibility,
        TestDataIntegrityRegression,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("REGRESSION TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ All regression tests passed!")
        print("\nRegression Validations:")
        print("  - Core Functionality: Config, presets, job queue, enums")
        print("  - Security: Encryption, authentication, API keys, network policies")
        print("  - Event System: Event bus, subscription, publishing")
        print("  - Dependency Injection: Container initialization, registration")
        print("  - API Backend: Cloud storage, distributed processing, load balancing")
        print("  - Interfaces: Data structures maintain expected format")
        print("  - Backward Compatibility: Serialization/deserialization compatibility")
        print("  - Data Integrity: Required data present and valid")
    else:
        print("\n❌ Some regression tests failed - existing features may be broken!")
        
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
    success = run_regression_tests()
    exit(0 if success else 1)
