"""
Tests for TarkAI AST Semantic Analyzer
Verifies complexity calculation, anti-pattern detection, and syntax error handling.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from ast_analyzer import analyze_code_ast


def test_syntax_error_detection():
    bad_code = "def broken(\n  return 42"
    result = analyze_code_ast(bad_code)
    assert result.syntax_valid is False
    assert result.syntax_error is not None
    assert "SyntaxError" in result.syntax_error


def test_linear_complexity_detection():
    code = """
def find_item(items, target):
    for x in items:
        if x == target:
            return True
    return False
"""
    result = analyze_code_ast(code)
    assert result.syntax_valid is True
    assert result.complexity.max_loop_nesting == 1
    assert result.complexity.estimated_time == "O(N)"
    assert result.complexity.recursion_detected is False


def test_quadratic_complexity_detection():
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    result = analyze_code_ast(code)
    assert result.syntax_valid is True
    assert result.complexity.max_loop_nesting == 2
    assert result.complexity.estimated_time == "O(N^2)"


def test_mutable_default_anti_pattern():
    code = """
def append_item(x, buffer=[]):
    buffer.append(x)
    return buffer
"""
    result = analyze_code_ast(code)
    assert result.syntax_valid is True
    assert len(result.anti_patterns) >= 1
    pattern = next(p for p in result.anti_patterns if p.pattern_type == "mutable_default")
    assert pattern.severity == "warning"
    assert "mutable default" in pattern.message


def test_bare_except_anti_pattern():
    code = """
def risky_operation():
    try:
        val = 1 / 0
    except:
        pass
"""
    result = analyze_code_ast(code)
    assert result.syntax_valid is True
    assert any(p.pattern_type == "bare_except" for p in result.anti_patterns)


def test_builtin_shadowing():
    code = """
def process(data):
    list = [1, 2, 3]
    return len(list)
"""
    result = analyze_code_ast(code)
    assert result.syntax_valid is True
    assert any(p.pattern_type == "shadow_builtin" for p in result.anti_patterns)


def test_tree_recursion_detection():
    code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
"""
    result = analyze_code_ast(code)
    assert result.syntax_valid is True
    assert result.complexity.recursion_detected is True
    assert result.complexity.estimated_time == "O(2^N)"
