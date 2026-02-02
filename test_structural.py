"""
Structural Tests for Pure Sound Application

These tests examine the data schemas, configuration structures,
file-based persistence formats, and data integrity constraints.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any, List
from jsonschema import Draft7Validator


class TestConfigurationSchema(unittest.TestCase):
    """Test configuration file structure and validation"""

    def setUp(self):
        """Set up test environment"""
        self.config_schema = {
            "type": "object",
            "required": ["model_paths", "presets", "output_formats", "default_settings"],
            "properties": {
                "model_paths": {
                    "type": "object",
                    "properties": {
                        "arnndn_model": {"type": "string"},
                        "custom_models_dir": {"type": "string"}
                    }
                },
                "presets": {"type": "object"},
                "output_formats": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "required": ["codec", "ext", "speech", "music"],
                        "properties": {
                            "codec": {"type": "string"},
                            "ext": {"type": "string"},
                            "speech": {"type": "array", "items": {"type": "integer"}},
                            "music": {"type": "array", "items": {"type": "integer"}}
                        }
                    }
                },
                "default_settings": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string"},
                        "content_type": {"type": "string"},
                        "channels": {"type": "integer"},
                        "loudnorm_enabled": {"type": "boolean"},
                        "compressor_enabled": {"type": "boolean"},
                        "multiband_enabled": {"type": "boolean"},
                        "ml_noise_reduction": {"type": "boolean"}
                    }
                }
            }
        }

    def test_compress_audio_config_schema(self):
        """Test compress_audio_config.json structure"""
        from config import config_manager
        
        config = config_manager.config
        
        # Validate against schema
        validator = Draft7Validator(self.config_schema)
        errors = list(validator.iter_errors(config))
        
        self.assertEqual(errors, [], f"Config validation errors: {errors}")
        
        # Verify required sections exist
        self.assertIn("model_paths", config)
        self.assertIn("presets", config)
        self.assertIn("output_formats", config)
        self.assertIn("default_settings", config)

    def test_output_format_structure(self):
        """Test output format configurations"""
        from config import config_manager
        
        output_formats = config_manager.config.get("output_formats", {})
        
        valid_formats = ["mp3", "aac", "ogg", "opus", "flac"]
        for format_name in output_formats:
            self.assertIn(format_name, valid_formats, f"Invalid format: {format_name}")
            
            format_config = output_formats[format_name]
            self.assertIn("codec", format_config)
            self.assertIn("ext", format_config)
            self.assertIn("speech", format_config)
            self.assertIn("music", format_config)
            
            # Verify bitrate arrays contain integers
            self.assertIsInstance(format_config["speech"], list)
            self.assertIsInstance(format_config["music"], list)

    def test_preset_structure(self):
        """Test preset configurations"""
        from config import config_manager
        
        presets = config_manager.config.get("presets", {})
        
        valid_presets = ["speech", "music", "custom"]
        for preset_name in presets:
            self.assertIn(preset_name, valid_presets, f"Invalid preset: {preset_name}")
            
            preset = presets[preset_name]
            if preset_name in ["speech", "music"]:
                # Verify compressor settings
                if "compressor" in preset:
                    compressor = preset["compressor"]
                    self.assertIn("threshold", compressor)
                    self.assertIn("ratio", compressor)
                    self.assertIn("attack", compressor)
                    self.assertIn("release", compressor)
                    self.assertIn("makeup", compressor)


class TestJobQueueSchema(unittest.TestCase):
    """Test job queue data structure and persistence"""

    def setUp(self):
        """Set up test environment"""
        self.job_schema = {
            "type": "object",
            "required": ["job_id", "input_file", "output_file", "bitrate", "format"],
            "properties": {
                "job_id": {"type": "string"},
                "input_file": {"type": "string"},
                "output_file": {"type": "string"},
                "bitrate": {"type": "integer"},
                "format": {"type": "string"},
                "filter_chain": {"type": ["string", "null"]},
                "channels": {"type": "integer"},
                "preserve_metadata": {"type": "boolean"},
                "priority": {"type": "string"},
                "status": {"type": "string"},
                "progress": {"type": "number"},
                "error_message": {"type": ["string", "null"]}
            }
        }

    def test_compression_job_structure(self):
        """Test CompressionJob dataclass structure from job_queue"""
        from job_queue import CompressionJob, JobPriority, JobStatus
        
        job = CompressionJob(
            job_id="test_job_001",
            input_file="/path/to/input.wav",
            output_file="/path/to/output.mp3",
            bitrate=128,
            format="mp3"
        )
        
        # Verify all required fields
        self.assertEqual(job.job_id, "test_job_001")
        self.assertEqual(job.input_file, "/path/to/input.wav")
        self.assertEqual(job.output_file, "/path/to/output.mp3")
        self.assertEqual(job.bitrate, 128)
        self.assertEqual(job.format, "mp3")
        
        # Verify default values
        self.assertEqual(job.priority, JobPriority.NORMAL)
        self.assertEqual(job.status, JobStatus.PENDING)
        self.assertEqual(job.progress, 0.0)
        self.assertTrue(job.preserve_metadata)
        self.assertEqual(job.channels, 1)

    def test_job_serialization(self):
        """Test job serialization and deserialization"""
        from job_queue import CompressionJob
        
        original_job = CompressionJob(
            job_id="test_job_002",
            input_file="/input.wav",
            output_file="/output.mp3",
            bitrate=192,
            format="mp3",
            filter_chain="loudnorm=I=-18",
            channels=2
        )
        
        # Serialize to dict
        job_dict = original_job.to_dict()
        
        # Verify required fields in dict
        self.assertIn("job_id", job_dict)
        self.assertIn("input_file", job_dict)
        self.assertIn("output_file", job_dict)
        
        # Deserialize back
        restored_job = CompressionJob.from_dict(job_dict)
        
        # Verify all fields match
        self.assertEqual(original_job.job_id, restored_job.job_id)
        self.assertEqual(original_job.input_file, restored_job.input_file)
        self.assertEqual(original_job.output_file, restored_job.output_file)
        self.assertEqual(original_job.bitrate, restored_job.bitrate)
        self.assertEqual(original_job.format, restored_job.format)

    def test_job_status_enum(self):
        """Test JobStatus enum values"""
        from job_queue import JobStatus
        
        self.assertEqual(JobStatus.PENDING.value, "pending")
        self.assertEqual(JobStatus.RUNNING.value, "running")
        self.assertEqual(JobStatus.COMPLETED.value, "completed")
        self.assertEqual(JobStatus.FAILED.value, "failed")
        self.assertEqual(JobStatus.CANCELLED.value, "cancelled")

    def test_job_priority_enum(self):
        """Test JobPriority enum values"""
        from job_queue import JobPriority
        
        self.assertEqual(JobPriority.LOW.value, 1)
        self.assertEqual(JobPriority.NORMAL.value, 2)
        self.assertEqual(JobPriority.HIGH.value, 3)
        self.assertEqual(JobPriority.URGENT.value, 4)


class TestPresetSchema(unittest.TestCase):
    """Test workflow preset structure"""

    def setUp(self):
        """Set up test environment"""
        self.preset_schema = {
            "type": "object",
            "required": ["name", "description", "icon", "category", "format", 
                         "bitrates", "content_type", "channels"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "icon": {"type": "string"},
                "category": {"type": "string"},
                "format": {"type": "string"},
                "bitrates": {"type": "array", "items": {"type": "integer"}},
                "content_type": {"type": "string"},
                "channels": {"type": "integer"},
                "loudnorm_enabled": {"type": "boolean"},
                "compressor_enabled": {"type": "boolean"},
                "multiband_enabled": {"type": "boolean"}
            }
        }

    def test_workflow_preset_structure(self):
        """Test WorkflowPreset dataclass structure"""
        from presets import WorkflowPreset
        
        preset = WorkflowPreset(
            name="Test Preset",
            description="A test preset",
            icon="🎵",
            category="test",
            format="mp3",
            bitrates=[64, 128, 192],
            content_type="music",
            channels=2
        )
        
        # Verify required fields
        self.assertEqual(preset.name, "Test Preset")
        self.assertEqual(preset.format, "mp3")
        self.assertEqual(preset.bitrates, [64, 128, 192])
        self.assertEqual(preset.content_type, "music")
        self.assertEqual(preset.channels, 2)

    def test_preset_serialization(self):
        """Test preset serialization"""
        from presets import WorkflowPreset
        
        preset = WorkflowPreset(
            name="Serialization Test",
            description="Test preset serialization",
            icon="🔧",
            category="test",
            format="aac",
            bitrates=[96, 128],
            content_type="speech",
            channels=1
        )
        
        # Serialize
        preset_dict = preset.to_dict()
        
        # Verify structure
        self.assertIn("name", preset_dict)
        self.assertIn("format", preset_dict)
        self.assertIn("bitrates", preset_dict)
        
        # Deserialize
        restored = WorkflowPreset.from_dict(preset_dict)
        
        self.assertEqual(preset.name, restored.name)
        self.assertEqual(preset.format, restored.format)
        self.assertEqual(preset.bitrates, restored.bitrates)

    def test_preset_manager_loads_presets(self):
        """Test that preset manager loads default presets"""
        from presets import preset_manager
        
        presets = preset_manager.get_all_presets()
        
        self.assertIsInstance(presets, list)
        self.assertGreater(len(presets), 0)
        
        # Verify each preset has required fields
        for preset in presets:
            self.assertTrue(hasattr(preset, 'name'))
            self.assertTrue(hasattr(preset, 'format'))
            self.assertTrue(hasattr(preset, 'bitrates'))
            self.assertTrue(hasattr(preset, 'category'))


class TestEventSchema(unittest.TestCase):
    """Test event system structure"""

    def test_event_structure(self):
        """Test Event dataclass structure"""
        from events import Event, EventPriority
        
        event = Event(
            name="test.event",
            data={"key": "value"},
            source="test_source",
            priority=EventPriority.HIGH
        )
        
        # Verify required fields
        self.assertEqual(event.name, "test.event")
        self.assertEqual(event.data, {"key": "value"})
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.priority, EventPriority.HIGH)
        self.assertIsInstance(event.timestamp, float)

    def test_event_priority_enum(self):
        """Test EventPriority enum values"""
        from events import EventPriority
        
        self.assertEqual(EventPriority.LOW.value, 1)
        self.assertEqual(EventPriority.NORMAL.value, 2)
        self.assertEqual(EventPriority.HIGH.value, 3)


class TestSecuritySchema(unittest.TestCase):
    """Test security-related data structures"""

    def test_user_structure(self):
        """Test User dataclass structure"""
        from security import User, Permission
        
        user = User(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            roles=["user"],
            permissions=[Permission.READ_AUDIO, Permission.WRITE_AUDIO]
        )
        
        self.assertEqual(user.user_id, "user_123")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertIn("user", user.roles)

    def test_audit_log_structure(self):
        """Test AuditLog structure"""
        from security import AuditLog
        
        log = AuditLog(
            log_id="log_001",
            timestamp=1234567890.0,
            user_id="user_123",
            action="user.login",
            resource="session",
            details={"outcome": "success"},
            ip_address="127.0.0.1",
            user_agent="TestAgent",
            outcome="success",
            risk_level="low"
        )
        
        self.assertEqual(log.log_id, "log_001")
        self.assertEqual(log.action, "user.login")
        self.assertEqual(log.user_id, "user_123")
        self.assertEqual(log.outcome, "success")

    def test_network_policy_structure(self):
        """Test NetworkPolicy dataclass structure"""
        from security import NetworkPolicy
        
        policy = NetworkPolicy(
            policy_id="test_policy",
            name="Test Policy",
            allowed_ips=["127.0.0.1", "192.168.1.0/24"],
            blocked_ips=["10.0.0.1"],
            enabled=True
        )
        
        self.assertEqual(policy.policy_id, "test_policy")
        self.assertEqual(policy.name, "Test Policy")
        self.assertIn("127.0.0.1", policy.allowed_ips)
        self.assertTrue(policy.enabled)


class TestAudioAnalysisSchema(unittest.TestCase):
    """Test audio analysis result structures"""

    def test_audio_file_info_structure(self):
        """Test AudioFileInfo dataclass"""
        from interfaces import AudioFileInfo
        
        info = AudioFileInfo(
            path="/path/to/audio.wav",
            codec="pcm_s16le",
            sample_rate=44100,
            channels=2,
            duration=120.5,
            bit_depth=16
        )
        
        self.assertEqual(info.codec, "pcm_s16le")
        self.assertEqual(info.sample_rate, 44100)
        self.assertEqual(info.channels, 2)
        self.assertEqual(info.duration, 120.5)

    def test_analysis_result_structure(self):
        """Test AnalysisResult dataclass"""
        from interfaces import AnalysisResult
        
        result = AnalysisResult(
            file_path="/path/to/audio.wav",
            content_type="speech",
            speech_probability=0.95,
            music_probability=0.05
        )
        
        self.assertEqual(result.content_type, "speech")
        self.assertEqual(result.speech_probability, 0.95)
        self.assertIsNotNone(result.recommended_bitrates)

    def test_interface_compression_job_structure(self):
        """Test CompressionJob dataclass from interfaces"""
        from interfaces import CompressionJob
        
        job = CompressionJob(
            job_id="job_001",
            input_file="/input.wav",
            output_file="/output.mp3",
            bitrate=128
        )
        
        self.assertEqual(job.job_id, "job_001")
        self.assertEqual(job.bitrate, 128)
        self.assertEqual(job.status, "pending")


class TestFilePersistenceSchema(unittest.TestCase):
    """Test file-based persistence structures"""

    def test_workflow_presets_json_structure(self):
        """Test workflow_presets.json structure"""
        presets_file = Path("workflow_presets.json")
        if not presets_file.exists():
            self.skipTest("workflow_presets.json not found")
        
        with open(presets_file, 'r') as f:
            presets_data = json.load(f)
        
        # Verify structure
        self.assertIsInstance(presets_data, dict)
        
        for preset_id, preset_data in presets_data.items():
            self.assertIsInstance(preset_id, str)
            self.assertIsInstance(preset_data, dict)
            self.assertIn("name", preset_data)
            self.assertIn("format", preset_data)
            self.assertIn("bitrates", preset_data)

    def test_custom_workflows_json_structure(self):
        """Test custom_workflows.json structure"""
        workflows_file = Path("custom_workflows.json")
        if not workflows_file.exists():
            self.skipTest("custom_workflows.json not found")
        
        with open(workflows_file, 'r') as f:
            workflows_data = json.load(f)
        
        # Verify structure
        self.assertIsInstance(workflows_data, dict)
        
        for workflow_id, workflow_data in workflows_data.items():
            self.assertIsInstance(workflow_id, str)
            self.assertIsInstance(workflow_data, dict)
            self.assertIn("name", workflow_data)
            self.assertIn("steps", workflow_data)
            self.assertIsInstance(workflow_data["steps"], list)

    def test_compress_audio_config_structure(self):
        """Test compress_audio_config.json structure"""
        config_file = Path("compress_audio_config.json")
        if not config_file.exists():
            self.skipTest("compress_audio_config.json not found")
        
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Verify required sections
        self.assertIn("model_paths", config_data)
        self.assertIn("presets", config_data)
        self.assertIn("output_formats", config_data)
        self.assertIn("default_settings", config_data)


class TestIndexConstraints(unittest.TestCase):
    """Test data integrity and constraints"""

    def test_format_values_valid(self):
        """Test that format values are valid"""
        from config import config_manager
        
        default_settings = config_manager.config.get("default_settings", {})
        format_value = default_settings.get("format")
        
        valid_formats = list(config_manager.config.get("output_formats", {}).keys())
        self.assertIn(format_value, valid_formats)

    def test_content_type_values_valid(self):
        """Test that content_type values are valid"""
        from config import config_manager
        
        default_settings = config_manager.config.get("default_settings", {})
        content_type = default_settings.get("content_type")
        
        valid_types = ["speech", "music"]
        self.assertIn(content_type, valid_types)

    def test_bitrate_values_positive(self):
        """Test that bitrate values are positive integers"""
        from config import config_manager
        
        output_formats = config_manager.config.get("output_formats", {})
        
        for format_name, format_config in output_formats.items():
            for bitrate in format_config.get("speech", []):
                self.assertGreater(bitrate, 0, f"Invalid bitrate in {format_name}")
            for bitrate in format_config.get("music", []):
                self.assertGreater(bitrate, 0, f"Invalid bitrate in {format_name}")

    def test_channels_values_valid(self):
        """Test that channel values are valid"""
        from config import config_manager
        
        default_settings = config_manager.config.get("default_settings", {})
        channels = default_settings.get("channels")
        
        self.assertIn(channels, [1, 2, 6], "Invalid channel value")  # mono, stereo, 5.1


class TestWorkflowSchema(unittest.TestCase):
    """Test custom workflow structure"""

    def test_workflow_step_enum(self):
        """Test WorkflowStep enum values"""
        from presets import WorkflowStep
        
        self.assertEqual(WorkflowStep.ANALYZE.value, "analyze")
        self.assertEqual(WorkflowStep.COMPRESS.value, "compress")
        self.assertEqual(WorkflowStep.NORMALIZE.value, "normalize")
        self.assertEqual(WorkflowStep.BATCH_PROCESS.value, "batch_process")

    def test_custom_workflow_structure(self):
        """Test CustomWorkflow dataclass structure"""
        from presets import CustomWorkflow, WorkflowStep, WorkflowStepConfig
        
        workflow = CustomWorkflow(
            id="workflow_001",
            name="Test Workflow",
            description="A test workflow",
            icon="🔧",
            category="custom"
        )
        
        # Add a step
        step = WorkflowStepConfig(
            step_type=WorkflowStep.ANALYZE,
            enabled=True,
            parameters={"param1": "value1"}
        )
        workflow.add_step(step)
        
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(len(workflow.steps), 1)
        self.assertEqual(workflow.steps[0].step_type, WorkflowStep.ANALYZE)


def run_structural_tests():
    """Run all structural tests"""
    print("=" * 80)
    print("Pure Sound - Structural Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestConfigurationSchema,
        TestJobQueueSchema,
        TestPresetSchema,
        TestEventSchema,
        TestSecuritySchema,
        TestAudioAnalysisSchema,
        TestFilePersistenceSchema,
        TestIndexConstraints,
        TestWorkflowSchema,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("STRUCTURAL TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ All structural tests passed!")
    else:
        print("\n❌ Some tests failed")
        
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
    success = run_structural_tests()
    exit(0 if success else 1)
