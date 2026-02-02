#!/usr/bin/env python3
"""
End-to-End Test Runner for Pure Sound Application

This script runs all E2E tests for the Pure Sound application:
- Login tests
- Checkout tests
- Search tests
- Profile tests
- Visual regression tests
- Cross-browser and cross-device tests

Usage:
    python tests/e2e/run_e2e_tests.py
    python tests/e2e/run_e2e_tests.py --verbose
    python tests/e2e/run_e2e_tests.py --test login
    python tests/e2e/run_e2e_tests.py --headed
"""

import sys
import os
import argparse
import subprocess
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


def print_header(title: str):
    """Print test section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def run_test_module(module_name: str, verbose: bool = False) -> bool:
    """
    Run a specific test module.
    
    Args:
        module_name: Name of the test module to run
        verbose: Whether to show verbose output
    
    Returns:
        True if tests passed, False otherwise
    """
    module_path = f"tests/e2e/{module_name}.py"
    
    if not os.path.exists(module_path):
        print(f"❌ Test module not found: {module_path}")
        return False
    
    print_header(f"Running {module_name} E2E Tests")
    
    cmd = [sys.executable, module_path]
    if verbose:
        cmd.append("--verbose")
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_all_e2e_tests(verbose: bool = False, headed: bool = False) -> dict:
    """
    Run all E2E test modules.
    
    Args:
        verbose: Whether to show verbose output
        headed: Whether to run with visible browser
    
    Returns:
        Dictionary with test results for each module
    """
    test_modules = [
        ("test_login", "Login & Authentication"),
        ("test_checkout", "Checkout & Payment"),
        ("test_search", "Search & Discovery"),
        ("test_profile", "Profile Management"),
        ("test_visual_regression", "Visual Regression"),
        ("test_cross_browser", "Cross-Browser & Cross-Device"),
    ]
    
    results = {}
    
    for module_name, description in test_modules:
        print_header(f"{description} Tests")
        
        # Run pytest for this module
        cmd = [
            sys.executable, "-m", "pytest",
            f"tests/e2e/{module_name}.py",
            "-v", "--tb=short",
        ]
        
        if verbose:
            cmd.append("-vv")
        if headed:
            cmd.append("--headed")
        
        start_time = time.time()
        result = subprocess.run(cmd, cwd=project_root)
        elapsed = time.time() - start_time
        
        passed = result.returncode == 0
        results[module_name] = {
            "passed": passed,
            "time": elapsed,
        }
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {module_name} ({elapsed:.2f}s)")
    
    return results


def run_quick_e2e_tests() -> bool:
    """
    Run quick E2E tests (essential tests only).
    
    Returns:
        True if tests passed, False otherwise
    """
    print_header("Quick E2E Tests")
    
    # Run login tests (most critical)
    login_passed = run_test_module("test_login")
    
    if not login_passed:
        print("❌ Critical: Login tests failed")
        return False
    
    print("\n✅ Quick E2E tests completed successfully")
    return True


def print_summary(results: dict):
    """
    Print test results summary.
    
    Args:
        results: Dictionary with test results
    """
    print_header("E2E Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r["passed"])
    failed_tests = total_tests - passed_tests
    
    print(f"Modules run: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    if failed_tests > 0:
        print("\nFailed modules:")
        for module, result in results.items():
            if not result["passed"]:
                print(f"  ❌ {module}")
    else:
        print("\n✅ All E2E tests passed!")
    
    # Print timing
    total_time = sum(r["time"] for r in results.values())
    print(f"\nTotal time: {total_time:.2f}s")


def main():
    """Main entry point for E2E test runner"""
    parser = argparse.ArgumentParser(
        description="Run Pure Sound E2E tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_e2e_tests.py                 # Run all E2E tests
  python run_e2e_tests.py --verbose       # Run with verbose output
  python run_e2e_tests.py --quick         # Run quick tests only
  python run_e2e_tests.py --test login    # Run specific test module
  python run_e2e_tests.py --test visual   # Run visual regression tests
  python run_e2e_tests.py --test cross    # Run cross-browser tests
  python run_e2e_tests.py --headed        # Run with visible browser
        """,
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output",
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run quick tests only (login tests)",
    )
    
    parser.add_argument(
        "--test", "-t",
        choices=["login", "checkout", "search", "profile", "visual", "cross"],
        help="Run specific test module",
    )
    
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run with visible browser (headed mode)",
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print(" Pure Sound - End-to-End (E2E) Tests")
    print("=" * 80)
    
    if args.test:
        # Run specific test module
        module_map = {
            "login": "test_login",
            "checkout": "test_checkout",
            "search": "test_search",
            "profile": "test_profile",
            "visual": "test_visual_regression",
            "cross": "test_cross_browser",
        }
        success = run_test_module(module_map[args.test], args.verbose)
    elif args.quick:
        # Run quick tests
        success = run_quick_e2e_tests()
    else:
        # Run all tests
        results = run_all_e2e_tests(args.verbose, args.headed)
        print_summary(results)
        success = all(r["passed"] for r in results.values())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
