"""
Tests for TarkAI Subprocess Sandbox Runner
Verifies process isolation, assertion testing, exception reporting, and infinite loop timeout enforcement.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from models import TestCase
from sandbox import execute_sandboxed


def test_sandbox_passing_execution():
    code = """
def add(a, b):
    return a + b
"""
    tests = [
        TestCase(description="Add positive", call="add(2, 3)", expected=5),
        TestCase(description="Add negative", call="add(-5, 5)", expected=0),
    ]
    result = execute_sandboxed(code, tests)
    assert result.overall_passed is True
    assert result.passed_count == 2
    assert result.total_count == 2
    assert len(result.test_results) == 2
    assert result.test_results[0].passed is True


def test_sandbox_failing_assertion():
    code = """
def multiply(a, b):
    return a + b  # Bug: returns addition instead of multiplication
"""
    tests = [
        TestCase(description="Multiply 2x3", call="multiply(2, 3)", expected=6),
    ]
    result = execute_sandboxed(code, tests)
    assert result.overall_passed is False
    assert result.passed_count == 0
    assert result.test_results[0].passed is False
    assert result.test_results[0].actual_repr == "5"


def test_sandbox_runtime_exception():
    code = """
def divide(a, b):
    return a / b
"""
    tests = [
        TestCase(description="Zero Division", call="divide(10, 0)", expected=0),
    ]
    result = execute_sandboxed(code, tests)
    assert result.overall_passed is False
    assert "ZeroDivisionError" in result.test_results[0].error_message


def test_sandbox_infinite_loop_timeout():
    code = """
def hang(x):
    while True:
        x += 1
    return x
"""
    tests = [
        TestCase(description="Hang test", call="hang(1)", expected=1),
    ]
    # Set short timeout of 1.0 second
    result = execute_sandboxed(code, tests, timeout_seconds=1.0)
    assert result.overall_passed is False
    assert "TimeLimitExceeded" in result.stderr
    assert result.test_results[0].passed is False
