#!/usr/bin/env python3
"""
Test runner for Story Teller Bot.
Runs comprehensive tests with detailed reporting.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run the complete test suite."""
    
    print("\n" + "=" * 80)
    print("STORY TELLER BOT - TEST SUITE RUNNER")
    print("=" * 80)
    
    # Check if pytest is available
    try:
        import pytest
        print("✓ pytest available")
    except ImportError:
        print("✗ pytest not found. Install with: pip install pytest pytest-cov pytest-mock")
        return 1
    
    # Run tests with coverage
    print("\n[1/3] Running unit tests with coverage...")
    print("-" * 80)
    
    test_args = [
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html:test_results/coverage",
    ]
    
    result = subprocess.run(test_args, cwd="/app" if os.path.exists("/app") else ".")
    
    if result.returncode != 0:
        print("\n✗ Some tests failed")
    else:
        print("\n✓ All tests passed")
    
    # Run linting if available
    print("\n[2/3] Checking code style...")
    print("-" * 80)
    
    try:
        import flake8
        lint_result = subprocess.run(
            ["flake8", "src", "tests", "--max-line-length=100", "--ignore=E501,W503"],
            cwd="/app" if os.path.exists("/app") else "."
        )
        print("✓ Linting completed" if lint_result.returncode == 0 else "⚠ Linting issues found")
    except ImportError:
        print("⚠ flake8 not available (optional)")
    
    # Check imports
    print("\n[3/3] Verifying imports...")
    print("-" * 80)
    
    try:
        print("  Checking config.settings...")
        from config.settings import settings
        print("  ✓ config.settings OK")
        
        print("  ✓ Import verification passed")
    except Exception as e:
        print(f"  ✗ Import verification failed: {e}")
        return 1
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    if result.returncode == 0:
        print("✓ ALL TESTS PASSED")
        print("\nCoverage report: test_results/coverage/index.html")
        print("=" * 80)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    try:
        exit_code = run_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n✗ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
