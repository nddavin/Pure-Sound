"""
Smoke Tests for Pure Sound Application

Quick sanity checks on core backend stability post-deployment.
These tests are designed to run quickly and verify that essential 
functionality is working after deployment.

Usage:
    python test_smoke.py
    python test_smoke.py --quick    # Run only essential tests
    python test_smoke.py --verbose  # Show detailed output
"""

import sys
import time
import argparse
from typing import Dict, Any, List


# Test results collector
test_results: Dict[str, Dict[str, Any]] = {}


def smoke_test(name: str, description: str = ""):
    """Decorator to register a smoke test"""
    def decorator(func):
        test_results[name] = {
            "description": description,
            "func": func,
            "passed": False,
            "error": None,
            "time": 0
        }
        return func
    return decorator


# ============================================================================
# Core Component Smoke Tests
# ============================================================================

@smoke_test(
    name="config_manager",
    description="Verify configuration manager initializes correctly"
)
def test_config_manager():
    """Smoke test: Config manager initialization"""
    from config import config_manager
    
    assert config_manager is not None, "Config manager should exist"
    assert hasattr(config_manager, 'config'), "Config manager should have config"
    assert hasattr(config_manager, 'get_default_setting'), "Should have get_default_setting"
    assert hasattr(config_manager, 'set_default_setting'), "Should have set_default_setting"
    
    # Verify required sections exist
    assert "default_settings" in config_manager.config
    assert "model_paths" in config_manager.config
    assert "presets" in config_manager.config
    assert "output_formats" in config_manager.config


@smoke_test(
    name="preset_manager",
    description="Verify preset manager loads default presets"
)
def test_preset_manager():
    """Smoke test: Preset manager"""
    from presets import preset_manager
    
    assert preset_manager is not None, "Preset manager should exist"
    
    presets = preset_manager.get_all_presets()
    assert isinstance(presets, list), "Presets should be a list"
    assert len(presets) > 0, "Default presets should exist"
    
    # Verify first preset has required attributes
    first_preset = presets[0]
    assert hasattr(first_preset, 'name'), "Preset should have name"
    assert hasattr(first_preset, 'format'), "Preset should have format"
    assert hasattr(first_preset, 'bitrates'), "Preset should have bitrates"


@smoke_test(
    name="job_queue",
    description="Verify job queue initializes and accepts jobs"
)
def test_job_queue():
    """Smoke test: Job queue"""
    from job_queue import JobQueue, CompressionJob, JobStatus
    
    queue = JobQueue()
    assert queue is not None, "Job queue should exist"
    assert hasattr(queue, 'add_job'), "Should have add_job method"
    assert hasattr(queue, 'get_job_status'), "Should have get_job_status method"
    
    # Create test job
    job = CompressionJob(
        job_id="smoke_test_job",
        input_file="/tmp/test.wav",
        output_file="/tmp/test_output.mp3",
        bitrate=128,
        format="mp3"
    )
    
    # Add job
    job_id = queue.add_job(job)
    assert job_id == "smoke_test_job", "Should return correct job ID"
    
    # Retrieve job
    retrieved = queue.get_job_status("smoke_test_job")
    assert retrieved is not None, "Should retrieve job"
    assert retrieved.status == JobStatus.PENDING, "Job should be pending"


@smoke_test(
    name="encryption_manager",
    description="Verify encryption manager works correctly"
)
def test_encryption_manager():
    """Smoke test: Encryption manager"""
    from security import EncryptionManager
    
    manager = EncryptionManager()
    assert manager is not None, "Encryption manager should exist"
    
    # Test key generation
    key, salt = manager.generate_key("test_password")
    assert len(key) == 32, "Key should be 32 bytes"
    assert len(salt) == 16, "Salt should be 16 bytes"
    
    # Test encryption/decryption
    test_data = "Smoke test data"
    encrypted = manager.encrypt_data(test_data, key)
    assert encrypted != test_data, "Encrypted data should differ"
    
    decrypted = manager.decrypt_data(encrypted, key)
    assert decrypted.decode() == test_data, "Decryption should work"


@smoke_test(
    name="authentication_manager",
    description="Verify authentication manager initializes"
)
def test_authentication_manager():
    """Smoke test: Authentication manager"""
    from security import AuthenticationManager
    
    manager = AuthenticationManager()
    assert manager is not None, "Authentication manager should exist"
    assert hasattr(manager, 'users'), "Should have users dict"
    assert hasattr(manager, 'active_sessions'), "Should have active_sessions dict"
    assert hasattr(manager, 'api_keys'), "Should have api_keys dict"
    
    # Test user creation
    user_id = manager.create_user(
        username="smoke_test_user",
        email="smoke@test.com",
        password="TestPassword123!"
    )
    assert user_id is not None, "User creation should return ID"
    assert "smoke_test_user" in manager.users, "User should be in users dict"
    
    # Test authentication
    session_id = manager.authenticate_user(
        username="smoke_test_user",
        password="TestPassword123!",
        ip_address="127.0.0.1"
    )
    assert session_id is not None, "Authentication should return session"


@smoke_test(
    name="network_security_manager",
    description="Verify network security manager initializes"
)
def test_network_security_manager():
    """Smoke test: Network security manager"""
    from security import NetworkSecurityManager, NetworkPolicy
    
    manager = NetworkSecurityManager()
    assert manager is not None, "Network security manager should exist"
    assert hasattr(manager, 'policies'), "Should have policies dict"
    assert hasattr(manager, 'blocked_ips'), "Should have blocked_ips set"
    assert hasattr(manager, 'rate_limits'), "Should have rate_limits dict"
    
    # Test policy creation
    policy = NetworkPolicy(
        policy_id="smoke_test_policy",
        name="Test Policy",
        allowed_ips=["127.0.0.1"],
        enabled=True
    )
    
    manager.add_network_policy(policy)
    assert "smoke_test_policy" in manager.policies, "Policy should be added"


@smoke_test(
    name="audit_logger",
    description="Verify audit logger initializes and logs"
)
def test_audit_logger():
    """Smoke test: Audit logger"""
    import tempfile
    import os
    
    from security import AuditLogger
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        logger = AuditLogger(log_directory=temp_dir)
        assert logger is not None, "Audit logger should exist"
        assert logger.log_directory.exists(), "Log directory should exist"
        
        # Test logging
        log_id = logger.log_event(
            action="smoke.test",
            user_id="test_user",
            resource="test_resource",
            details={"test": "data"},
            ip_address="127.0.0.1"
        )
        
        assert log_id is not None, "Log should return ID"
        assert len(log_id) > 10, "Log ID should be sufficiently long"
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


@smoke_test(
    name="event_bus",
    description="Verify event bus initializes and works"
)
def test_event_bus():
    """Smoke test: Event bus"""
    from events import event_bus, publish_event
    
    assert event_bus is not None, "Event bus should exist"
    
    # Test subscription
    events_received = []
    
    def handler(event):
        events_received.append(event)
    
    subscription_id = event_bus.subscribe("smoke.test", handler)
    assert subscription_id is not None, "Subscription should return ID"
    
    # Test publishing
    publish_event("smoke.test", {"key": "value"}, "test_source")
    
    # Wait for event
    time.sleep(0.1)
    
    assert len(events_received) == 1, "Should receive event"


@smoke_test(
    name="di_container",
    description="Verify DI container initializes"
)
def test_di_container():
    """Smoke test: DI container"""
    from di_container import di_container
    
    assert di_container is not None, "DI container should exist"
    
    # Test service registration
    from unittest.mock import Mock
    
    test_service = Mock()
    di_container.register_instance(Mock, test_service)
    
    # Test service retrieval
    retrieved = di_container.get_service(Mock)
    assert retrieved is not None, "Should retrieve service"
    assert retrieved == test_service, "Should return same service"


@smoke_test(
    name="cloud_storage_manager",
    description="Verify cloud storage manager initializes"
)
def test_cloud_storage_manager():
    """Smoke test: Cloud storage manager"""
    from api_backend import CloudStorageManager, CloudConfig, CloudProvider
    
    config = CloudConfig(
        provider=CloudProvider.LOCAL,
        region="us-east-1"
    )
    
    manager = CloudStorageManager(config)
    assert manager is not None, "Cloud storage manager should exist"


@smoke_test(
    name="distributed_processing_manager",
    description="Verify distributed processing manager initializes"
)
def test_distributed_processing_manager():
    """Smoke test: Distributed processing manager"""
    from api_backend import DistributedProcessingManager
    
    manager = DistributedProcessingManager()
    assert manager is not None, "Manager should exist"
    assert hasattr(manager, 'nodes'), "Should have nodes dict"
    assert hasattr(manager, 'active_jobs'), "Should have active_jobs dict"
    
    # Test node registration
    result = manager.register_node(
        "smoke_test_node",
        {"capabilities": {"cpu_cores": 4}, "status": "active"}
    )
    assert result is True, "Node registration should succeed"


@smoke_test(
    name="load_balancer",
    description="Verify load balancer initializes"
)
def test_load_balancer():
    """Smoke test: Load balancer"""
    from api_backend import DistributedProcessingManager, LoadBalancer
    
    processing_manager = DistributedProcessingManager()
    load_balancer = LoadBalancer(processing_manager)
    
    assert load_balancer is not None, "Load balancer should exist"
    assert hasattr(load_balancer, 'node_performance'), "Should have performance dict"


@smoke_test(
    name="audio_analysis_engine",
    description="Verify audio analysis engine initializes"
)
def test_audio_analysis_engine():
    """Smoke test: Audio analysis engine"""
    from audio_analysis_enhanced import audio_analysis_engine
    
    assert audio_analysis_engine is not None, "Audio analysis engine should exist"


@smoke_test(
    name="audio_processing_engine",
    description="Verify audio processing engine initializes"
)
def test_audio_processing_engine():
    """Smoke test: Audio processing engine"""
    from audio_processing_enhanced import audio_processing_engine
    
    assert audio_processing_engine is not None, "Audio processing engine should exist"
    
    # Verify available presets
    presets = audio_processing_engine.get_available_presets()
    assert isinstance(presets, list), "Presets should be a list"


# ============================================================================
# Quick Tests (Essential Only)
# ============================================================================

QUICK_TESTS = [
    "config_manager",
    "preset_manager",
    "job_queue",
    "encryption_manager",
    "authentication_manager",
    "di_container",
]


def run_smoke_test(test_name: str, verbose: bool = False) -> bool:
    """Run a single smoke test"""
    if test_name not in test_results:
        print(f"❌ Unknown test: {test_name}")
        return False
    
    test_info = test_results[test_name]
    func = test_info["func"]
    
    start_time = time.time()
    try:
        result = func()
        elapsed = time.time() - start_time
        
        test_info["passed"] = result
        test_info["time"] = elapsed
        
        if verbose:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name} ({elapsed:.3f}s)")
        
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        test_info["passed"] = False
        test_info["error"] = str(e)
        test_info["time"] = elapsed
        
        if verbose:
            print(f"  ❌ FAIL - {test_name} ({elapsed:.3f}s): {e}")
        
        return False


def run_all_smoke_tests(verbose: bool = False) -> tuple[bool, float]:
    """Run all smoke tests"""
    all_passed = True
    total_time = 0
    
    if verbose:
        print("\n" + "=" * 70)
        print("Running Smoke Tests...")
        print("=" * 70)
    
    for test_name in test_results:
        passed = run_smoke_test(test_name, verbose)
        total_time += test_results[test_name]["time"]
        
        if not passed and not verbose:
            all_passed = False
            # Print failure in non-verbose mode
            test_info = test_results[test_name]
            error = test_info.get("error", "Unknown error")
            print(f"  ❌ {test_name}: {error}")
    
    return all_passed, total_time


def run_quick_smoke_tests(verbose: bool = False) -> tuple[bool, float]:
    """Run only essential smoke tests"""
    all_passed = True
    total_time = 0
    
    if verbose:
        print("\n" + "=" * 70)
        print("Running Quick Smoke Tests (Essential Only)...")
        print("=" * 70)
    
    for test_name in QUICK_TESTS:
        if test_name not in test_results:
            continue
            
        passed = run_smoke_test(test_name, verbose)
        total_time += test_results[test_name]["time"]
        
        if not passed and not verbose:
            all_passed = False
            test_info = test_results[test_name]
            error = test_info.get("error", "Unknown error")
            print(f"  ❌ {test_name}: {error}")
    
    return all_passed, total_time


def print_summary(all_passed: bool, total_time: float, quick_mode: bool):
    """Print test summary"""
    mode = "Quick" if quick_mode else "Full"
    passed_count = sum(1 for t in test_results.values() if t["passed"])
    failed_count = sum(1 for t in test_results.values() if not t["passed"])
    
    # Filter to relevant tests for count
    if quick_mode:
        relevant_tests = {k: v for k, v in test_results.items() if k in QUICK_TESTS}
        passed_count = sum(1 for v in relevant_tests.values() if v["passed"])
        failed_count = sum(1 for v in relevant_tests.values() if not v["passed"])
        total = len(QUICK_TESTS)
    else:
        relevant_tests = test_results
        total = len(test_results)
    
    print("\n" + "=" * 70)
    print(f"SMOKE TEST SUMMARY ({mode} Mode)")
    print("=" * 70)
    print(f"Tests run: {total}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Total time: {total_time:.3f}s")
    
    if all_passed:
        print("\n✅ All smoke tests passed!")
        print("\nBackend stability verified:")
        if "config_manager" in [k for k in test_results.keys() if test_results[k]["passed"]]:
            print("  ✓ Configuration system working")
        if "preset_manager" in [k for k in test_results.keys() if test_results[k]["passed"]]:
            print("  ✓ Preset system working")
        if "job_queue" in [k for k in test_results.keys() if test_results[k]["passed"]]:
            print("  ✓ Job queue working")
        if "encryption_manager" in [k for k in test_results.keys() if test_results[k]["passed"]]:
            print("  ✓ Encryption system working")
        if "authentication_manager" in [k for k in test_results.keys() if test_results[k]["passed"]]:
            print("  ✓ Authentication system working")
        if "di_container" in [k for k in test_results.keys() if test_results[k]["passed"]]:
            print("  ✓ Dependency injection working")
    else:
        print("\n❌ Some smoke tests failed!")
        print("\nFailed tests:")
        for test_name, test_info in relevant_tests.items():
            if not test_info["passed"]:
                error = test_info.get("error", "Unknown error")
                print(f"  ❌ {test_name}: {error}")
    
    print("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Smoke tests for Pure Sound backend stability"
    )
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Run only essential tests (faster)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tests"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Available smoke tests:")
        for test_name, test_info in test_results.items():
            essential = " (essential)" if test_name in QUICK_TESTS else ""
            print(f"  - {test_name}: {test_info['description']}{essential}")
        return
    
    print("\n" + "=" * 70)
    print(" Pure Sound - Smoke Tests")
    print(" Quick checks on core backend stability post-deployment")
    print("=" * 70)
    
    if args.quick:
        all_passed, total_time = run_quick_smoke_tests(args.verbose)
    else:
        all_passed, total_time = run_all_smoke_tests(args.verbose)
    
    print_summary(all_passed, total_time, args.quick)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
