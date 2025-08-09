#!/usr/bin/env python3
"""
Script to run tests in integration mode (with Docker).
This script ensures Docker Compose is running and executes tests in the container.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed with exit code {result.returncode}")
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def check_docker_running():
    """Check if Docker is running."""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests in integration mode")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--auth", action="store_true", help="Run authentication tests")
    parser.add_argument("--authors", action="store_true", help="Run author tests")
    parser.add_argument("--books", action="store_true", help="Run book tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--show-help", action="store_true", help="Show pytest help")

    args = parser.parse_args()

    # Check if Docker is running
    if not check_docker_running():
        print("❌ Docker is not running. Please start Docker and try again.")
        return 1

    # Start Docker Compose if not running
    print("🚀 Starting Integration Tests")
    print("==================================================")
    print("✅ Docker Compose required")
    print("✅ MySQL database")
    print("✅ Full integration testing")
    print("✅ Production-like environment")
    print("==================================================")

    # Start Docker Compose
    if not run_command(["docker-compose", "up", "-d"], "Starting Docker Compose"):
        return 1

    # Wait for services to be ready
    if not run_command(["docker-compose", "exec", "-T", "api", "sleep", "5"], "Waiting for services"):
        return 1

    # Build pytest command
    cmd = ["docker-compose", "exec", "-T", "api", "python", "-m", "pytest"]
    
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

    # Run the tests
    success = run_command(cmd, "Running integration tests")

    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
