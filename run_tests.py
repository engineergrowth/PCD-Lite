#!/usr/bin/env python3
"""
Test runner for PCD-Lite
Runs all unit tests and provides coverage report
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running PCD-Lite Unit Tests...")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests with coverage
    cmd = [
        "python", "-m", "pytest", 
        "tests/", 
        "-v", 
        "--cov=app", 
        "--cov-report=html", 
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
