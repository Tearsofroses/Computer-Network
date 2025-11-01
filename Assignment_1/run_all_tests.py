"""
Run All Tests - P2P File Sharing System
Executes all unit tests and generates summary report
"""

import unittest
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def run_all_tests():
    """Discover and run all tests in the tests directory"""
    
    print("=" * 70)
    print("P2P FILE SHARING SYSTEM - TEST SUITE")
    print("=" * 70)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Discover all tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests Run:  {result.testsRun}")
    print(f"Successes:        {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:         {len(result.failures)}")
    print(f"Errors:           {len(result.errors)}")
    print(f"Skipped:          {len(result.skipped)}")
    print("=" * 70)
    
    # Calculate success rate
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"Success Rate:     {success_rate:.1f}%")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
