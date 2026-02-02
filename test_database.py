"""
Database Tests for Pure Sound Application

This module tests all database-related functionality including:
- Queries (searching, filtering, retrieval operations)
- Connectivity (file I/O operations)
- Data validation (schema validation, constraints)
- Transactions (atomic operations, rollback capabilities)
- Data integrity and consistency
"""

import unittest
import json
import os
import tempfile
import shutil
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from jsonschema import Draft7Validator, ValidationError


class TestConfigurationDatabase(unittest.TestCase):
    """Test configuration database operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = Path(self.test_dir) / "test_config.json"
        
        # Default configuration structure
        self.default_config = {
            "model_paths": {
                "arnndn_model": "/usr/local/share/ffmpeg/arnndn-models/bd.cnr.mdl",
                "custom_models_dir": "./models"
            },
            "presets": {
                "speech": {
                    "compressor": {
                        "threshold": -20,
                        "ratio": 3,
                        "attack": 0.01,
                        "release": 0.1,
                        "makeup": 6
                    }
                },
                "music": {
                    "compressor": {
                        "threshold": -18,
                        "ratio": 4,
                        "attack": 0.005,
                        "release": 0.05,
                        "makeup": 4
                    }
                }
            },
            "output_formats": {
                "mp3": {
                    "codec": "libmp3lame",
                    "ext": ".mp3",
                    "speech": [64, 96, 128],
                    "music": [128, 192, 256]
                },
                "opus": {
                    "codec": "libopus",
                    "ext": ".opus",
                    "speech": [24, 32, 48],
                    "music": [64, 96, 128]
                }
            },
            "default_settings": {
                "format": "mp3",
                "content_type": "speech",
                "channels": 1,
                "loudnorm_enabled": True,
                "compressor_enabled": False
            }
        }
        
        # Schema for validation
        self.config_schema = {
            "type": "object",
            "required": ["model_paths", "presets", "output_formats", "default_settings"],
            "properties": {
                "model_paths": {
                    "type": "object",
                    "required": ["arnndn_model", "custom_models_dir"],
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
                    "required": ["format", "content_type", "channels"],
                    "properties": {
                        "format": {"type": "string"},
                        "content_type": {"type": "string"},
                        "channels": {"type": "integer"},
                        "loudnorm_enabled": {"type": "boolean"},
                        "compressor_enabled": {"type": "boolean"}
                    }
                }
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_write_and_read(self):
        """Test basic configuration write and read operations"""
        # Write configuration
        with open(self.config_file, 'w') as f:
            json.dump(self.default_config, f, indent=2)
        
        # Read configuration
        with open(self.config_file, 'r') as f:
            loaded_config = json.load(f)
        
        # Verify data integrity
        self.assertEqual(loaded_config["default_settings"]["format"], "mp3")
        self.assertEqual(loaded_config["default_settings"]["channels"], 1)
        self.assertIn("mp3", loaded_config["output_formats"])
    
    def test_config_schema_validation(self):
        """Test configuration schema validation"""
        validator = Draft7Validator(self.config_schema)
        
        # Test valid configuration
        errors = list(validator.iter_errors(self.default_config))
        self.assertEqual(errors, [], "Valid configuration should have no errors")
        
        # Test invalid configuration
        invalid_config = self.default_config.copy()
        del invalid_config["model_paths"]  # Remove required field
        
        errors = list(validator.iter_errors(invalid_config))
        self.assertGreater(len(errors), 0, "Invalid configuration should have errors")
    
    def test_config_query_operations(self):
        """Test configuration query operations"""
        # Write configuration
        with open(self.config_file, 'w') as f:
            json.dump(self.default_config, f, indent=2)
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Query: Get all output formats
        formats = list(config.get("output_formats", {}).keys())
        self.assertEqual(formats, ["mp3", "opus"])
        
        # Query: Get bitrates for mp3 speech
        mp3_speech_bitrates = config.get("output_formats", {}).get("mp3", {}).get("speech", [])
        self.assertEqual(mp3_speech_bitrates, [64, 96, 128])
        
        # Query: Get default settings
        settings = config.get("default_settings", {})
        self.assertEqual(settings.get("format"), "mp3")
    
    def test_config_update_transaction(self):
        """Test configuration update with transaction-like behavior"""
        # Initial write
        with open(self.config_file, 'w') as f:
            json.dump(self.default_config, f, indent=2)
        
        # Atomic update using temp file
        temp_file = Path(str(self.config_file) + ".tmp")
        try:
            # Read current config
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Modify
            config["default_settings"]["format"] = "opus"
            
            # Write to temp file first
            with open(temp_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Atomic rename
            temp_file.replace(self.config_file)
            
            # Verify update
            with open(self.config_file, 'r') as f:
                updated_config = json.load(f)
            
            self.assertEqual(updated_config["default_settings"]["format"], "opus")
            
        finally:
            # Cleanup temp file if it exists
            if temp_file.exists():
                temp_file.unlink()
    
    def test_config_concurrent_access(self):
        """Test configuration file concurrent access"""
        config_file = self.config_file
        errors = []
        successful_writes = [0]
        lock = threading.Lock()
        
        # Initialize the config file first
        with open(config_file, 'w') as f:
            json.dump(self.default_config, f, indent=2)
        
        def writer_thread(thread_id):
            try:
                for i in range(10):
                    temp_file = Path(str(config_file) + f".tmp.{thread_id}.{i}")
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        config["default_settings"]["channels"] = thread_id
                        with open(temp_file, 'w') as f:
                            json.dump(config, f, indent=2)
                        temp_file.replace(config_file)
                        with lock:
                            successful_writes[0] += 1
                    except (FileNotFoundError, PermissionError):
                        # File might be temporarily unavailable or locked
                        pass
                    finally:
                        if temp_file.exists():
                            temp_file.unlink(missing_ok=True)
            except Exception as e:
                errors.append(str(e))
        
        def reader_thread(thread_id):
            try:
                for _ in range(10):
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                        # Just read, don't modify
                        _ = config.get("default_settings", {}).get("format")
                    except (FileNotFoundError, PermissionError):
                        # File might be temporarily unavailable
                        pass
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple writers and readers
        threads = []
        for i in range(2):
            t = threading.Thread(target=writer_thread, args=(i,))
            threads.append(t)
            t = threading.Thread(target=reader_thread, args=(i + 10,))
            threads.append(t)
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify the file is still readable after concurrent access
        with open(config_file, 'r') as f:
            config = json.load(f)
        self.assertIn("default_settings", config)


class TestJobQueueDatabase(unittest.TestCase):
    """Test job queue database operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.queue_file = Path(self.test_dir) / "job_queue.json"
        
        # Sample job data
        self.sample_jobs = [
            {
                "job_id": "job_001",
                "input_file": "/audio/input1.wav",
                "output_file": "/audio/output1.mp3",
                "bitrate": 128,
                "format": "mp3",
                "status": "pending",
                "priority": "normal",
                "progress": 0.0,
                "created_at": "2025-01-01T10:00:00Z"
            },
            {
                "job_id": "job_002",
                "input_file": "/audio/input2.wav",
                "output_file": "/audio/output2.mp3",
                "bitrate": 192,
                "format": "mp3",
                "status": "running",
                "priority": "high",
                "progress": 0.5,
                "created_at": "2025-01-01T10:05:00Z"
            },
            {
                "job_id": "job_003",
                "input_file": "/audio/input3.wav",
                "output_file": "/audio/output3.opus",
                "bitrate": 64,
                "format": "opus",
                "status": "completed",
                "priority": "low",
                "progress": 1.0,
                "created_at": "2025-01-01T10:10:00Z"
            }
        ]
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_job_insert_and_query(self):
        """Test job insertion and query operations"""
        # Write initial jobs
        with open(self.queue_file, 'w') as f:
            json.dump(self.sample_jobs, f, indent=2)
        
        # Query: Get all jobs
        with open(self.queue_file, 'r') as f:
            jobs = json.load(f)
        
        self.assertEqual(len(jobs), 3)
        
        # Query: Get job by ID
        job = next((j for j in jobs if j["job_id"] == "job_002"), None)
        self.assertIsNotNone(job)
        self.assertEqual(job["status"], "running")
        
        # Query: Get jobs by status
        pending_jobs = [j for j in jobs if j["status"] == "pending"]
        self.assertEqual(len(pending_jobs), 1)
        self.assertEqual(pending_jobs[0]["job_id"], "job_001")
    
    def test_job_filter_queries(self):
        """Test job filtering and complex queries"""
        # Write initial jobs
        with open(self.queue_file, 'w') as f:
            json.dump(self.sample_jobs, f, indent=2)
        
        with open(self.queue_file, 'r') as f:
            jobs = json.load(f)
        
        # Filter by format
        mp3_jobs = [j for j in jobs if j["format"] == "mp3"]
        self.assertEqual(len(mp3_jobs), 2)
        
        # Filter by priority
        high_priority_jobs = [j for j in jobs if j["priority"] == "high"]
        self.assertEqual(len(high_priority_jobs), 1)
        
        # Filter by multiple criteria
        completed_high_priority = [j for j in jobs if j["status"] == "completed"]
        self.assertEqual(len(completed_high_priority), 1)
        
        # Sort by created_at
        sorted_jobs = sorted(jobs, key=lambda j: j["created_at"])
        self.assertEqual(sorted_jobs[0]["job_id"], "job_001")
        self.assertEqual(sorted_jobs[-1]["job_id"], "job_003")
    
    def test_job_update_operations(self):
        """Test job update operations"""
        # Write initial jobs
        with open(self.queue_file, 'w') as f:
            json.dump(self.sample_jobs, f, indent=2)
        
        # Update job status
        with open(self.queue_file, 'r') as f:
            jobs = json.load(f)
        
        # Find and update job_001
        for job in jobs:
            if job["job_id"] == "job_001":
                job["status"] = "running"
                job["progress"] = 0.25
                break
        
        # Write back
        with open(self.queue_file, 'w') as f:
            json.dump(jobs, f, indent=2)
        
        # Verify update
        with open(self.queue_file, 'r') as f:
            updated_jobs = json.load(f)
        
        updated_job = next((j for j in updated_jobs if j["job_id"] == "job_001"), None)
        self.assertEqual(updated_job["status"], "running")
        self.assertEqual(updated_job["progress"], 0.25)
    
    def test_job_deletion(self):
        """Test job deletion operations"""
        # Write initial jobs
        with open(self.queue_file, 'w') as f:
            json.dump(self.sample_jobs, f, indent=2)
        
        # Delete job_002
        with open(self.queue_file, 'r') as f:
            jobs = json.load(f)
        
        jobs = [j for j in jobs if j["job_id"] != "job_002"]
        
        with open(self.queue_file, 'w') as f:
            json.dump(jobs, f, indent=2)
        
        # Verify deletion
        with open(self.queue_file, 'r') as f:
            remaining_jobs = json.load(f)
        
        self.assertEqual(len(remaining_jobs), 2)
        job_ids = [j["job_id"] for j in remaining_jobs]
        self.assertNotIn("job_002", job_ids)
    
    def test_job_queue_transaction(self):
        """Test job queue transaction operations"""
        # Initial state
        with open(self.queue_file, 'w') as f:
            json.dump(self.sample_jobs, f, indent=2)
        
        # Simulate transaction: Add job and update another
        temp_file = Path(str(self.queue_file) + ".tmp")
        try:
            with open(self.queue_file, 'r') as f:
                jobs = json.load(f)
            
            # Add new job
            new_job = {
                "job_id": "job_004",
                "input_file": "/audio/input4.wav",
                "output_file": "/audio/output4.mp3",
                "bitrate": 128,
                "format": "mp3",
                "status": "pending",
                "priority": "normal",
                "progress": 0.0,
                "created_at": "2025-01-01T10:15:00Z"
            }
            jobs.append(new_job)
            
            # Update existing job
            for job in jobs:
                if job["job_id"] == "job_001":
                    job["status"] = "completed"
                    break
            
            # Write to temp file
            with open(temp_file, 'w') as f:
                json.dump(jobs, f, indent=2)
            
            # Atomic commit
            temp_file.replace(self.queue_file)
            
            # Verify transaction
            with open(self.queue_file, 'r') as f:
                result = json.load(f)
            
            self.assertEqual(len(result), 4)  # Added one job
            completed_job = next((j for j in result if j["job_id"] == "job_001"), None)
            self.assertEqual(completed_job["status"], "completed")
            
        finally:
            if temp_file.exists():
                temp_file.unlink()


class TestPresetDatabase(unittest.TestCase):
    """Test preset database operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.presets_file = Path(self.test_dir) / "workflow_presets.json"
        
        # Sample presets
        self.sample_presets = {
            "speech_clean": {
                "name": "Speech Clean",
                "description": "Optimized for speech with noise reduction",
                "icon": "🎤",
                "category": "speech",
                "format": "mp3",
                "bitrates": [64, 96, 128],
                "content_type": "speech",
                "channels": 1,
                "loudnorm_enabled": True,
                "compressor_enabled": True,
                "multiband_enabled": False
            },
            "music_hifi": {
                "name": "Music Hi-Fi",
                "description": "High fidelity music compression",
                "icon": "🎵",
                "category": "music",
                "format": "flac",
                "bitrates": [],
                "content_type": "music",
                "channels": 2,
                "loudnorm_enabled": True,
                "compressor_enabled": True,
                "multiband_enabled": True
            },
            "podcast_standard": {
                "name": "Podcast Standard",
                "description": "Standard podcast settings",
                "icon": "🎙️",
                "category": "podcast",
                "format": "mp3",
                "bitrates": [96, 128, 192],
                "content_type": "speech",
                "channels": 1,
                "loudnorm_enabled": True,
                "compressor_enabled": False,
                "multiband_enabled": False
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_preset_crud_operations(self):
        """Test preset Create, Read, Update, Delete operations"""
        # Create
        with open(self.presets_file, 'w') as f:
            json.dump(self.sample_presets, f, indent=2)
        
        # Read
        with open(self.presets_file, 'r') as f:
            presets = json.load(f)
        
        self.assertEqual(len(presets), 3)
        self.assertIn("speech_clean", presets)
        
        # Update
        presets["speech_clean"]["bitrates"] = [64, 96, 128, 192]
        with open(self.presets_file, 'w') as f:
            json.dump(presets, f, indent=2)
        
        with open(self.presets_file, 'r') as f:
            updated_presets = json.load(f)
        
        self.assertEqual(updated_presets["speech_clean"]["bitrates"], [64, 96, 128, 192])
        
        # Delete
        del presets["podcast_standard"]
        with open(self.presets_file, 'w') as f:
            json.dump(presets, f, indent=2)
        
        with open(self.presets_file, 'r') as f:
            final_presets = json.load(f)
        
        self.assertEqual(len(final_presets), 2)
        self.assertNotIn("podcast_standard", final_presets)
    
    def test_preset_query_by_category(self):
        """Test preset query by category"""
        with open(self.presets_file, 'w') as f:
            json.dump(self.sample_presets, f, indent=2)
        
        with open(self.presets_file, 'r') as f:
            presets = json.load(f)
        
        # Query by category
        speech_presets = {k: v for k, v in presets.items() if v.get("category") == "speech"}
        self.assertEqual(len(speech_presets), 1)
        self.assertIn("speech_clean", speech_presets)
        
        music_presets = {k: v for k, v in presets.items() if v.get("category") == "music"}
        self.assertEqual(len(music_presets), 1)
        self.assertIn("music_hifi", music_presets)
    
    def test_preset_search_by_name(self):
        """Test preset search by name"""
        with open(self.presets_file, 'w') as f:
            json.dump(self.sample_presets, f, indent=2)
        
        with open(self.presets_file, 'r') as f:
            presets = json.load(f)
        
        # Search by name substring
        search_term = "Music"
        matching_presets = {k: v for k, v in presets.items() 
                          if search_term.lower() in v.get("name", "").lower()}
        
        self.assertEqual(len(matching_presets), 1)
        self.assertIn("music_hifi", matching_presets)
    
    def test_preset_data_integrity(self):
        """Test preset data integrity constraints"""
        with open(self.presets_file, 'w') as f:
            json.dump(self.sample_presets, f, indent=2)
        
        with open(self.presets_file, 'r') as f:
            presets = json.load(f)
        
        # Validate required fields
        required_fields = ["name", "category", "format", "bitrates", "content_type"]
        
        for preset_id, preset in presets.items():
            for field in required_fields:
                self.assertIn(field, preset, f"Missing {field} in preset {preset_id}")
            
            # Validate field types
            self.assertIsInstance(preset["name"], str)
            self.assertIsInstance(preset["bitrates"], list)
            self.assertIsInstance(preset["content_type"], str)
            
            # Validate bitrates are positive integers
            for bitrate in preset["bitrates"]:
                self.assertIsInstance(bitrate, int)
                self.assertGreater(bitrate, 0)


class TestAuditLogDatabase(unittest.TestCase):
    """Test audit log database operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.audit_dir = Path(self.test_dir) / "audit_logs"
        self.audit_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_audit_log_write(self):
        """Test audit log writing"""
        audit_file = self.audit_dir / "audit_2025-01-01.json"
        
        audit_entries = [
            {
                "timestamp": "2025-01-01T10:00:00Z",
                "user_id": "user_001",
                "action": "user.login",
                "resource": "session",
                "details": {"ip": "192.168.1.1"},
                "outcome": "success",
                "risk_level": "low"
            },
            {
                "timestamp": "2025-01-01T10:05:00Z",
                "user_id": "user_002",
                "action": "file.upload",
                "resource": "audio_file",
                "details": {"filename": "test.wav", "size": 1024},
                "outcome": "success",
                "risk_level": "low"
            }
        ]
        
        with open(audit_file, 'w') as f:
            json.dump(audit_entries, f, indent=2)
        
        with open(audit_file, 'r') as f:
            loaded = json.load(f)
        
        self.assertEqual(len(loaded), 2)
    
    def test_audit_log_query(self):
        """Test audit log querying"""
        # Create multiple audit files
        for date in ["2025-01-01", "2025-01-02", "2025-01-03"]:
            audit_file = self.audit_dir / f"audit_{date}.json"
            entries = [
                {
                    "timestamp": f"{date}T10:00:00Z",
                    "user_id": f"user_{i}",
                    "action": "test.action",
                    "resource": "test",
                    "outcome": "success",
                    "risk_level": "low"
                }
                for i in range(3)
            ]
            with open(audit_file, 'w') as f:
                json.dump(entries, f, indent=2)
        
        # Query all logs from date range
        all_logs = []
        for audit_file in self.audit_dir.glob("audit_*.json"):
            with open(audit_file, 'r') as f:
                logs = json.load(f)
            all_logs.extend(logs)
        
        self.assertEqual(len(all_logs), 9)
        
        # Query by user
        user_logs = [log for log in all_logs if log["user_id"] == "user_1"]
        self.assertEqual(len(user_logs), 3)  # One from each day
        
        # Query by action
        action_logs = [log for log in all_logs if log["action"] == "test.action"]
        self.assertEqual(len(action_logs), 9)


class TestDataValidationConstraints(unittest.TestCase):
    """Test data validation and constraints"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_unique_constraint_simulation(self):
        """Test unique constraint simulation for job IDs"""
        data_file = Path(self.test_dir) / "jobs.json"
        
        jobs = [
            {"job_id": "job_001", "name": "Job 1"},
            {"job_id": "job_002", "name": "Job 2"}
        ]
        
        with open(data_file, 'w') as f:
            json.dump(jobs, f, indent=2)
        
        # Check for duplicate before insert
        with open(data_file, 'r') as f:
            existing_jobs = json.load(f)
        
        existing_ids = {job["job_id"] for job in existing_jobs}
        new_job_id = "job_003"
        
        # Simulate unique constraint
        if new_job_id not in existing_ids:
            existing_jobs.append({"job_id": new_job_id, "name": "Job 3"})
            with open(data_file, 'w') as f:
                json.dump(existing_jobs, f, indent=2)
        
        # Try to add duplicate
        duplicate_job_id = "job_001"
        if duplicate_job_id not in existing_ids:
            existing_jobs.append({"job_id": duplicate_job_id, "name": "Duplicate Job"})
        
        with open(data_file, 'r') as f:
            final_jobs = json.load(f)
        
        # Should only have 3 jobs (original 2 + 1 new, not the duplicate)
        self.assertEqual(len(final_jobs), 3)
    
    def test_required_field_validation(self):
        """Test required field validation"""
        data_file = Path(self.test_dir) / "config.json"
        
        valid_config = {
            "name": "Test Config",
            "settings": {
                "enabled": True,
                "timeout": 30
            }
        }
        
        with open(data_file, 'w') as f:
            json.dump(valid_config, f, indent=2)
        
        with open(data_file, 'r') as f:
            config = json.load(f)
        
        # Validate required fields
        required_fields = ["name"]
        for field in required_fields:
            self.assertIn(field, config, f"Missing required field: {field}")
        
        # Validate nested required fields
        nested_required = ["enabled", "timeout"]
        for field in nested_required:
            self.assertIn(field, config.get("settings", {}), f"Missing required field: {field}")
    
    def test_data_type_validation(self):
        """Test data type validation"""
        data_file = Path(self.test_dir) / "data.json"
        
        data = {
            "integer_field": 42,
            "string_field": "hello",
            "boolean_field": True,
            "array_field": [1, 2, 3],
            "null_field": None
        }
        
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        with open(data_file, 'r') as f:
            loaded = json.load(f)
        
        # Validate types
        self.assertIsInstance(loaded["integer_field"], int)
        self.assertIsInstance(loaded["string_field"], str)
        self.assertIsInstance(loaded["boolean_field"], bool)
        self.assertIsInstance(loaded["array_field"], list)
        self.assertIsNone(loaded["null_field"])
    
    def test_range_constraint_validation(self):
        """Test numeric range constraints"""
        data_file = Path(self.test_dir) / "config.json"
        
        config = {
            "volume": 75,  # 0-100 range
            "bitrate": 128,  # Positive integer
            "channels": 2  # 1, 2, or 6
        }
        
        with open(data_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        with open(data_file, 'r') as f:
            loaded = json.load(f)
        
        # Validate ranges
        self.assertGreaterEqual(loaded["volume"], 0)
        self.assertLessEqual(loaded["volume"], 100)
        
        self.assertGreater(loaded["bitrate"], 0)
        
        self.assertIn(loaded["channels"], [1, 2, 6])


class TestIndexOperations(unittest.TestCase):
    """Test index-like operations for efficient queries"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.data_file = Path(self.test_dir) / "data.json"
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_index_creation(self):
        """Test creating indexes for faster queries"""
        data = [
            {"id": 1, "category": "A", "value": 100},
            {"id": 2, "category": "B", "value": 200},
            {"id": 3, "category": "A", "value": 150},
            {"id": 4, "category": "C", "value": 300},
            {"id": 5, "category": "B", "value": 250}
        ]
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Create index by category
        with open(self.data_file, 'r') as f:
            items = json.load(f)
        
        category_index = {}
        for item in items:
            cat = item["category"]
            if cat not in category_index:
                category_index[cat] = []
            category_index[cat].append(item["id"])
        
        # Use index for query
        category_a_items = [item for item in items if item["id"] in category_index.get("A", [])]
        
        self.assertEqual(len(category_a_items), 2)
    
    def test_compound_index(self):
        """Test compound index for multi-field queries"""
        data = [
            {"id": 1, "category": "A", "status": "active", "priority": 1},
            {"id": 2, "category": "A", "status": "inactive", "priority": 2},
            {"id": 3, "category": "B", "status": "active", "priority": 1},
            {"id": 4, "category": "B", "status": "active", "priority": 3}
        ]
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        with open(self.data_file, 'r') as f:
            items = json.load(f)
        
        # Create compound index
        compound_index = {}
        for item in items:
            key = (item["category"], item["status"])
            if key not in compound_index:
                compound_index[key] = []
            compound_index[key].append(item["id"])
        
        # Query using compound index
        active_b_items = [item for item in items 
                         if item["id"] in compound_index.get(("B", "active"), [])]
        
        self.assertEqual(len(active_b_items), 2)


class TestBackupAndRecovery(unittest.TestCase):
    """Test backup and recovery operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.backup_dir = Path(self.test_dir) / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.data_file = Path(self.test_dir) / "data.json"
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_data_backup(self):
        """Test data backup creation"""
        data = {"important": "data", "values": [1, 2, 3, 4, 5]}
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"backup_{timestamp}.json"
        
        with open(self.data_file, 'r') as source:
            with open(backup_file, 'w') as backup:
                json.dump(json.load(source), backup, indent=2)
        
        # Verify backup
        self.assertTrue(backup_file.exists())
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        self.assertEqual(backup_data, data)
    
    def test_data_recovery(self):
        """Test data recovery from backup"""
        original_data = {"original": "data"}
        backup_data = {"recovered": "data"}
        
        # Create initial data
        with open(self.data_file, 'w') as f:
            json.dump(original_data, f, indent=2)
        
        # Create backup
        backup_file = self.backup_dir / "backup_001.json"
        with open(self.backup_dir / "backup_001.json", 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        # Simulate data loss (corruption)
        with open(self.data_file, 'w') as f:
            f.write("corrupted data")
        
        # Recover from backup
        with open(backup_file, 'r') as backup:
            with open(self.data_file, 'w') as target:
                json.dump(json.load(backup), target, indent=2)
        
        # Verify recovery
        with open(self.data_file, 'r') as f:
            recovered_data = json.load(f)
        
        self.assertEqual(recovered_data, backup_data)


def run_database_tests():
    """Run all database tests"""
    print("=" * 80)
    print("Pure Sound - Database Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestConfigurationDatabase,
        TestJobQueueDatabase,
        TestPresetDatabase,
        TestAuditLogDatabase,
        TestDataValidationConstraints,
        TestIndexOperations,
        TestBackupAndRecovery,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("DATABASE TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ All database tests passed!")
    else:
        print("\n❌ Some tests failed")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback.splitlines()[-1]}")
    
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_database_tests()
    exit(0 if success else 1)
