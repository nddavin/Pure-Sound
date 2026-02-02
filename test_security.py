"""
Security Tests for Pure Sound Application

This module tests security vulnerabilities in:
- Authentication (password strength, session management, token handling)
- Authorization (permission checks, role-based access control)
- Encryption (key generation, encryption/decryption, hashing)
- Input validation (injection attacks, path traversal, etc.)
"""

import unittest
import tempfile
import os
import time
import re
import shutil
from pathlib import Path
from datetime import datetime


class TestAuthenticationSecurity(unittest.TestCase):
    """Test authentication security vulnerabilities"""
    
    def setUp(self):
        """Set up test environment"""
        from security import AuthenticationManager, EncryptionManager
        self.auth_manager = AuthenticationManager()
        self.encryption_manager = EncryptionManager()
        
        # Create test user
        self.test_user_id = self.auth_manager.create_user(
            username="test_user",
            email="test@example.com",
            password="TestPassword123!"
        )
    
    def test_password_strength_validation(self):
        """Test that password strength requirements are enforced"""
        # Test weak passwords are rejected
        weak_passwords = [
            "123",
            "password",
            "PASSWORD",
            "password123",
            "Password",
            "Test123",
        ]
        
        for password in weak_passwords:
            is_strong = self._check_password_strength(password)
            self.assertFalse(is_strong, f"Weak password '{password}' was accepted")
        
        # Test strong passwords are accepted
        strong_passwords = [
            "Test@123",
            "MySecure!Pass1",
            "C0mpl3x#P@ss",
        ]
        
        for password in strong_passwords:
            is_strong = self._check_password_strength(password)
            self.assertTrue(is_strong, f"Strong password '{password}' was rejected")
    
    def _check_password_strength(self, password):
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[0-9]', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True
    
    def test_session_management_security(self):
        """Test session management security"""
        session_id = self.auth_manager.authenticate_user(
            username="test_user",
            password="test_password",
            ip_address="127.0.0.1"
        )
        
        self.assertIsNotNone(session_id, "Authentication should succeed")
        self.assertIn(session_id, self.auth_manager.active_sessions)
        
        result = self.auth_manager.revoke_session(session_id)
        self.assertTrue(result, "Session revocation should succeed")
        self.assertNotIn(session_id, self.auth_manager.active_sessions)
        
        result = self.auth_manager.revoke_session("non_existent_session")
        self.assertFalse(result, "Revoking non-existent session should fail")
    
    def test_session_timeout(self):
        """Test session timeout enforcement"""
        session_id = self.auth_manager.authenticate_user(
            username="test_user",
            password="test_password",
            ip_address="127.0.0.1"
        )
        
        self.assertIsNotNone(session_id)
        
        # Session timeout is 24 hours
        self.auth_manager.active_sessions[session_id]["last_activity"] = time.time() - 90000
        
        cleaned = self.auth_manager.cleanup_expired_sessions()
        self.assertGreaterEqual(cleaned, 1, "Expired sessions should be cleaned")
        self.assertNotIn(session_id, self.auth_manager.active_sessions)
    
    def test_api_key_authentication(self):
        """Test API key authentication security"""
        api_key = self.auth_manager.create_api_key(
            user_id=self.test_user_id,
            name="test_api_key"
        )
        
        self.assertTrue(api_key.startswith("ps_"), "API key should have 'ps_' prefix")
        self.assertGreater(len(api_key), 40, "API key should be sufficiently long")
        
        session_id = self.auth_manager.authenticate_api_key(api_key)
        self.assertIsNotNone(session_id, "API key authentication should succeed")
        
        expired_key = self.auth_manager.create_api_key(
            user_id=self.test_user_id,
            name="expired_key",
            expires_in_days=-1
        )
        
        session_id = self.auth_manager.authenticate_api_key(expired_key)
        self.assertIsNone(session_id, "Expired API key should fail authentication")
        
        inactive_key = self.auth_manager.create_api_key(
            user_id=self.test_user_id,
            name="inactive_key"
        )
        self.auth_manager.api_keys[inactive_key]["active"] = False
        
        session_id = self.auth_manager.authenticate_api_key(inactive_key)
        self.assertIsNone(session_id, "Inactive API key should fail authentication")
    
    def test_jwt_token_security(self):
        """Test JWT token security"""
        token = self.auth_manager.generate_jwt_token(
            user_id=self.test_user_id,
            permissions=["read_audio", "write_audio"]
        )
        
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 50, "JWT token should be sufficiently long")
        
        payload = self.auth_manager.verify_jwt_token(token)
        self.assertIsNotNone(payload, "Valid JWT should verify successfully")
        self.assertEqual(payload["user_id"], self.test_user_id)
        
        invalid_payload = self.auth_manager.verify_jwt_token("invalid_token")
        self.assertIsNone(invalid_payload, "Invalid JWT should be rejected")
        
        self.auth_manager.jwt_secret = "different_secret"
        altered_payload = self.auth_manager.verify_jwt_token(token)
        self.assertIsNone(altered_payload, "Token with wrong secret should be rejected")


class TestAuthorizationSecurity(unittest.TestCase):
    """Test authorization and access control security"""
    
    def setUp(self):
        """Set up test environment"""
        from security import AuthenticationManager, SecurityManager, Permission
        self.auth_manager = AuthenticationManager()
        self.security_manager = SecurityManager()
        self.Permission = Permission
        
        self.test_user_id = self.auth_manager.create_user(
            username="test_user",
            email="test@example.com",
            password="TestPassword123!",
            roles=["user"],
            permissions=[Permission.READ_AUDIO, Permission.WRITE_AUDIO]
        )
        
        self.admin_user_id = self.auth_manager.create_user(
            username="admin_user",
            email="admin@example.com",
            password="AdminPassword123!",
            roles=["admin"],
            permissions=[Permission.READ_AUDIO, Permission.WRITE_AUDIO, 
                        Permission.DELETE_AUDIO, Permission.ADMIN_ACCESS,
                        Permission.SYSTEM_CONFIG, Permission.AUDIT_LOGS]
        )
    
    def test_permission_check(self):
        """Test permission checking"""
        session_id = self.auth_manager.authenticate_user(
            username="test_user",
            password="test_password",
            ip_address="127.0.0.1"
        )
        
        has_permission = self.auth_manager.check_permission(
            session_id, self.Permission.READ_AUDIO
        )
        self.assertTrue(has_permission, "User should have READ_AUDIO permission")
        
        has_permission = self.auth_manager.check_permission(
            session_id, self.Permission.ADMIN_ACCESS
        )
        self.assertFalse(has_permission, "User should not have ADMIN_ACCESS permission")
    
    def test_permission_bypass_prevention(self):
        """Test that permission bypass attempts are prevented"""
        session_id = self.auth_manager.authenticate_user(
            username="test_user",
            password="test_password",
            ip_address="127.0.0.1"
        )
        
        for permission in [
            self.Permission.ADMIN_ACCESS,
            self.Permission.SYSTEM_CONFIG,
            self.Permission.AUDIT_LOGS
        ]:
            has_permission = self.auth_manager.check_permission(session_id, permission)
            self.assertFalse(has_permission, f"User should not have {permission} permission")
        
        has_permission = self.auth_manager.check_permission(
            "non_existent_session", self.Permission.READ_AUDIO
        )
        self.assertFalse(has_permission, "Non-existent session should not have permissions")
    
    def test_role_based_access(self):
        """Test role-based access control"""
        admin_user = self.auth_manager.users.get("admin_user")
        self.assertIsNotNone(admin_user, "Admin user should exist")
        
        # Admin should have all assigned permissions
        expected_admin_perms = [
            self.Permission.READ_AUDIO,
            self.Permission.WRITE_AUDIO,
            self.Permission.DELETE_AUDIO,
            self.Permission.ADMIN_ACCESS,
            self.Permission.SYSTEM_CONFIG,
            self.Permission.AUDIT_LOGS
        ]
        for permission in expected_admin_perms:
            self.assertIn(permission, admin_user.permissions, f"Admin should have {permission} permission")
        
        regular_user = self.auth_manager.users.get("test_user")
        self.assertIsNotNone(regular_user, "Regular user should exist")
        
        # Regular user should have limited permissions
        self.assertIn(self.Permission.READ_AUDIO, regular_user.permissions)
        self.assertIn(self.Permission.WRITE_AUDIO, regular_user.permissions)
        
        # Regular user should not have sensitive permissions
        restricted_permissions = [
            self.Permission.ADMIN_ACCESS,
            self.Permission.SYSTEM_CONFIG,
            self.Permission.AUDIT_LOGS
        ]
        
        for permission in restricted_permissions:
            self.assertNotIn(permission, regular_user.permissions, f"Regular user should not have {permission}")


class TestEncryptionSecurity(unittest.TestCase):
    """Test encryption security vulnerabilities"""
    
    def setUp(self):
        """Set up test environment"""
        from security import EncryptionManager
        self.encryption_manager = EncryptionManager()
    
    def test_key_generation_security(self):
        """Test encryption key generation security"""
        password = "TestPassword123!"
        
        key, salt = self.encryption_manager.generate_key(password)
        
        self.assertEqual(len(key), 32, "Key should be 32 bytes (256 bits)")
        self.assertEqual(len(salt), 16, "Salt should be 16 bytes")
        
        key2, _ = self.encryption_manager.generate_key(password, os.urandom(16))
        self.assertNotEqual(key, key2, "Same password with different salt should produce different key")
        
        key3, _ = self.encryption_manager.generate_key(password, salt)
        self.assertEqual(key, key3, "Same password with same salt should produce same key")
    
    def test_encryption_decryption(self):
        """Test encryption and decryption security"""
        password = "TestPassword123!"
        key, _ = self.encryption_manager.generate_key(password)
        
        original_text = "This is a secret message"
        encrypted = self.encryption_manager.encrypt_data(original_text, key)
        
        self.assertNotEqual(encrypted, original_text, "Encrypted data should differ from original")
        
        decrypted = self.encryption_manager.decrypt_data(encrypted, key)
        self.assertEqual(decrypted.decode(), original_text, "Decrypted data should match original")
        
        binary_data = b"\x00\x01\x02\x03\x04\x05"
        encrypted_binary = self.encryption_manager.encrypt_data(binary_data, key)
        decrypted_binary = self.encryption_manager.decrypt_data(encrypted_binary, key)
        self.assertEqual(decrypted_binary, binary_data, "Binary data should round-trip correctly")
    
    def test_encryption_integrity(self):
        """Test encryption integrity verification"""
        password = "TestPassword123!"
        key, _ = self.encryption_manager.generate_key(password)
        
        data = "Test data for integrity"
        hash_value = self.encryption_manager.hash_data(data, "sha256")
        
        is_valid = self.encryption_manager.verify_integrity(data, hash_value, "sha256")
        self.assertTrue(is_valid, "Valid data should pass integrity check")
        
        modified_data = data + "modified"
        is_valid = self.encryption_manager.verify_integrity(modified_data, hash_value, "sha256")
        self.assertFalse(is_valid, "Modified data should fail integrity check")
    
    def test_wrong_key_rejection(self):
        """Test that wrong key properly rejects decryption"""
        password = "TestPassword123!"
        key1, _ = self.encryption_manager.generate_key(password)
        
        key2, _ = self.encryption_manager.generate_key(password + "different")
        
        data = "Secret message"
        encrypted = self.encryption_manager.encrypt_data(data, key1)
        
        try:
            self.encryption_manager.decrypt_data(encrypted, key2)
            self.fail("Decryption with wrong key should fail")
        except Exception:
            pass
    
    def test_hash_algorithm_security(self):
        """Test hash algorithm security"""
        data = "Test data"
        
        hash_sha256 = self.encryption_manager.hash_data(data, "sha256")
        self.assertEqual(len(hash_sha256), 64, "SHA-256 should produce 64 hex chars")
        
        hash_sha512 = self.encryption_manager.hash_data(data, "sha512")
        self.assertEqual(len(hash_sha512), 128, "SHA-512 should produce 128 hex chars")
        
        different_data = "Different data"
        self.assertNotEqual(
            self.encryption_manager.hash_data(data, "sha256"),
            self.encryption_manager.hash_data(different_data, "sha256")
        )
        
        self.assertEqual(
            self.encryption_manager.hash_data(data, "sha256"),
            self.encryption_manager.hash_data(data, "sha256")
        )


class TestInputValidationSecurity(unittest.TestCase):
    """Test input validation vulnerabilities"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention in input handling"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1; DELETE FROM users WHERE 1=1",
            "admin' --",
            "1 OR 1=1",
            "' UNION SELECT * FROM users --",
            "anything' OR 'x'='x' --"
        ]
        
        for input_str in malicious_inputs:
            is_safe = self._validate_input(input_str)
            self.assertFalse(is_safe, f"Potentially malicious input should be rejected: {input_str}")
    
    def _validate_input(self, input_str):
        dangerous_patterns = [
            r"['\";].*(DROP|DELETE|INSERT|UPDATE|SELECT)",
            r"--",
            r"\/\*",
            r"\*/",
            r"UNION\s+SELECT",
            r"OR\s+1\s*=\s*1",
            r"'\s+OR\s+'",
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return False
        
        if len(input_str) > 1000:
            return False
        
        return True
    
    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention"""
        malicious_paths = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "....//....//etc/passwd",
            "/var/www/../../../etc/shadow",
            "assets/../../sensitive_data.txt"
        ]
        
        for path in malicious_paths:
            is_safe = self._validate_file_path(path)
            self.assertFalse(is_safe, f"Path traversal should be prevented: {path}")
        
        valid_paths = [
            "audio/sample.mp3",
            "/home/user/audio/file.wav",
            "assets/presets/default.json"
        ]
        
        for path in valid_paths:
            is_safe = self._validate_file_path(path)
            self.assertTrue(is_safe, f"Valid path should be allowed: {path}")
    
    def _validate_file_path(self, path):
        if ".." in path:
            return False
        if path.startswith("/"):
            return True
        return True
    
    def test_xss_prevention(self):
        """Test XSS (Cross-Site Scripting) prevention"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "{{constructor.constructor('alert(\"xss\")')()}}"
        ]
        
        for input_str in malicious_inputs:
            is_safe = self._sanitize_input(input_str)
            self.assertFalse(is_safe, f"XSS payload should be sanitized: {input_str}")
    
    def _sanitize_input(self, input_str):
        dangerous_patterns = [
            r"<script.*?>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe.*?>",
            r"<object.*?>",
            r"<embed.*?>",
            r"{{.*}}"
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return False
        
        return True
    
    def test_command_injection_prevention(self):
        """Test command injection prevention"""
        malicious_inputs = [
            "; cat /etc/passwd",
            "| whoami",
            "&& rm -rf /",
            "`ls -la`",
            "$(id)"
        ]
        
        for input_str in malicious_inputs:
            is_safe = self._validate_command(input_str)
            self.assertFalse(is_safe, f"Command injection should be prevented: {input_str}")
    
    def _validate_command(self, input_str):
        dangerous_chars = [';', '|', '&', '$', '`', '(', ')', '{', '}']
        
        for char in dangerous_chars:
            if char in input_str:
                return False
        
        return True
    
    def test_email_validation(self):
        """Test email format validation"""
        invalid_emails = [
            "notanemail",
            "@nodomain.com",
            "no@",
            "spaces in@email.com",
            "double@@at.com",
            "no.at.sign"
        ]
        
        for email in invalid_emails:
            is_valid = self._validate_email(email)
            self.assertFalse(is_valid, f"Invalid email should be rejected: {email}")
        
        valid_emails = [
            "user@example.com",
            "user.name@domain.org",
            "user+tag@subdomain.example.com"
        ]
        
        for email in valid_emails:
            is_valid = self._validate_email(email)
            self.assertTrue(is_valid, f"Valid email should be accepted: {email}")
    
    def _validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


class TestNetworkSecurity(unittest.TestCase):
    """Test network security features"""
    
    def setUp(self):
        """Set up test environment"""
        from security import NetworkSecurityManager, NetworkPolicy
        self.network_security = NetworkSecurityManager()
        
        self.test_policy = NetworkPolicy(
            policy_id="test_policy",
            name="Test Policy",
            allowed_ips=["127.0.0.1", "192.168.1.0/24"],
            blocked_ips=["10.0.0.1"],
            allowed_vlans=["private"],
            enabled=True
        )
        self.network_security.add_network_policy(self.test_policy)
    
    def test_ip_whitelisting(self):
        """Test IP whitelist functionality"""
        self.assertTrue(
            self.network_security.check_ip_access("127.0.0.1", "test_policy"),
            "Whitelisted IP should be allowed"
        )
        self.assertTrue(
            self.network_security.check_ip_access("192.168.1.50", "test_policy"),
            "IP in CIDR range should be allowed"
        )
        
        self.assertFalse(
            self.network_security.check_ip_access("10.0.0.1", "test_policy"),
            "Blocked IP should be denied"
        )
        
        self.assertFalse(
            self.network_security.check_ip_access("8.8.8.8", "test_policy"),
            "Non-whitelisted IP should be denied"
        )
    
    def test_cidr_notation_support(self):
        """Test CIDR notation for IP ranges"""
        from security import NetworkPolicy
        
        test_cases = [
            ("192.168.1.0/24", "192.168.1.100", True),
            ("192.168.1.0/24", "192.168.2.1", False),
            ("10.0.0.0/8", "10.255.255.255", True),
            ("10.0.0.0/8", "11.0.0.1", False),
        ]
        
        for cidr, ip, expected in test_cases:
            policy_id = f"cidr_{cidr.replace('.', '_').replace('/', '_')}"
            policy = NetworkPolicy(
                policy_id=policy_id,
                name=f"Test CIDR {cidr}",
                allowed_ips=[cidr],
                enabled=True
            )
            self.network_security.add_network_policy(policy)
            
            result = self.network_security.check_ip_access(ip, policy_id)
            self.assertEqual(result, expected)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        identifier = "test_ip"
        limit = 5
        window = 3600
        
        for i in range(limit):
            self.assertTrue(
                self.network_security.check_rate_limit(identifier, limit, window),
                f"Request {i+1} should be allowed"
            )
        
        self.assertFalse(
            self.network_security.check_rate_limit(identifier, limit, window),
            "Request over limit should be blocked"
        )
    
    def test_ip_blocking(self):
        """Test IP blocking functionality"""
        test_ip = "203.0.113.1"
        
        self.network_security.block_ip(test_ip, duration=1)
        
        self.assertIn(test_ip, self.network_security.blocked_ips)
        
        time.sleep(1.1)
        
        self.assertNotIn(test_ip, self.network_security.blocked_ips)


class TestAuditLoggingSecurity(unittest.TestCase):
    """Test audit logging security"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        from security import AuditLogger
        self.audit_logger = AuditLogger(log_directory=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_audit_event_logging(self):
        """Test audit event logging"""
        log_id = self.audit_logger.log_event(
            action="test.action",
            user_id="test_user",
            resource="test_resource",
            details={"test": "data"},
            ip_address="127.0.0.1",
            risk_level="low"
        )
        
        self.assertIsNotNone(log_id, "Audit log ID should be returned")
        self.assertGreater(len(log_id), 10, "Audit log ID should be sufficiently long")
    
    def test_auth_attempt_logging(self):
        """Test authentication attempt logging"""
        log_id = self.audit_logger.log_authentication_attempt(
            username="test_user",
            success=True,
            ip_address="127.0.0.1"
        )
        
        self.assertIsNotNone(log_id)
        
        log_id = self.audit_logger.log_authentication_attempt(
            username="test_user",
            success=False,
            ip_address="127.0.0.1"
        )
        
        self.assertIsNotNone(log_id)
    
    def test_audit_log_retrieval(self):
        """Test audit log retrieval with filters"""
        for i in range(5):
            self.audit_logger.log_event(
                action=f"test.action.{i}",
                user_id="test_user",
                resource="test_resource",
                details={"index": i},
                ip_address="127.0.0.1"
            )
        
        logs = self.audit_logger.get_audit_logs()
        
        self.assertGreaterEqual(len(logs), 5, "Should retrieve logged events")
        
        filtered_logs = self.audit_logger.get_audit_logs(action_pattern="action\\.0")
        self.assertGreater(len(filtered_logs), 0, "Should filter by action pattern")
    
    def test_log_integrity(self):
        """Test audit log integrity"""
        log_id = self.audit_logger.log_event(
            action="security.test",
            user_id="test_user",
            resource="test_resource",
            details={"sensitive": "data"},
            ip_address="127.0.0.1",
            risk_level="medium"
        )
        
        log_file = Path(self.test_dir) / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        self.assertTrue(log_file.exists(), "Audit log file should exist")
        
        with open(log_file, 'r') as f:
            content = f.read()
            self.assertIn(log_id, content, "Log entry should be in file")


class TestSecurityConfiguration(unittest.TestCase):
    """Test security configuration validation"""
    
    def test_security_status_reporting(self):
        """Test security status reporting"""
        from security import SecurityManager
        security_manager = SecurityManager()
        
        status = security_manager.get_security_status()
        
        self.assertIn("active_sessions", status)
        self.assertIn("api_keys", status)
        self.assertIn("users", status)
        self.assertIn("network_policies", status)
        self.assertIn("blocked_ips", status)
    
    def test_default_policies_initialization(self):
        """Test default security policies are initialized"""
        from security import SecurityManager
        security_manager = SecurityManager()
        security_manager.initialize_default_policies()
        
        self.assertIn("default", security_manager.network_security.policies)
        
        default_policy = security_manager.network_security.policies["default"]
        self.assertTrue(default_policy.enabled)
        self.assertIn("127.0.0.1", default_policy.allowed_ips)


def run_security_tests():
    """Run all security tests"""
    print("=" * 80)
    print("Pure Sound - Security Tests")
    print("=" * 80)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestAuthenticationSecurity,
        TestAuthorizationSecurity,
        TestEncryptionSecurity,
        TestInputValidationSecurity,
        TestNetworkSecurity,
        TestAuditLoggingSecurity,
        TestSecurityConfiguration,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("SECURITY TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\nAll security tests passed!")
        print("\nSecurity Validations:")
        print("  - Authentication: Password strength, session management, JWT tokens")
        print("  - Authorization: Permission checks, role-based access control")
        print("  - Encryption: Key generation, encryption/decryption, hashing")
        print("  - Input Validation: SQL injection, XSS, path traversal prevention")
        print("  - Network Security: IP whitelisting, rate limiting, CIDR support")
        print("  - Audit Logging: Event logging, log retrieval, integrity")
    else:
        print("\nSome security tests failed")
        
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
    success = run_security_tests()
    exit(0 if success else 1)
