#!/usr/bin/env python3
"""
Script to run tests in isolated mode (without Docker).
This script sets up the environment for isolated testing and runs pytest.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(cmd, description, env=None):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, env=env, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests in isolated mode")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--auth", action="store_true", help="Run authentication tests")
    parser.add_argument("--authors", action="store_true", help="Run author tests")
    parser.add_argument("--books", action="store_true", help="Run book tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--show-help", action="store_true", help="Show pytest help")

    args = parser.parse_args()

    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test selection
    if args.auth:
        cmd.extend(["tests/test_auth.py"])
    elif args.authors:
        cmd.extend(["tests/test_authors.py"])
    elif args.books:
        cmd.extend(["tests/test_books.py"])
    else:
        # Run all tests except performance tests by default
        cmd.extend(["tests/", "-m", "not slow"])

    # Add options
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html:htmlcov"])
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    if args.debug:
        cmd.extend(["-v", "-s"])
    else:
        cmd.extend(["-v"])
    
    if args.show_help:
        cmd.extend(["--help"])

    # Set environment for isolated testing
    env = os.environ.copy()
    env["TESTING_MODE"] = "isolated"
    env["DATABASE_URL"] = "sqlite:///./test_isolated.db"
    env["DEBUG"] = "True"
    env["SECRET_KEY"] = "test-secret-key-for-isolated-testing"

    print("🚀 Starting Isolated Tests")
    print("==================================================")
    print("✅ No Docker required")
    print("✅ SQLite in-memory database")
    print("✅ Fast execution")
    print("✅ Isolated test environment")
    print("==================================================")

    # Run the tests
    success = run_command(cmd, "Running isolated tests", env)

    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
