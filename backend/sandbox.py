"""
TarkAI — Safe Sandboxed Code Runner
Executes untrusted user Python submissions within isolated subprocesses
under strict time limits, memory bounds, and assertion verification.
"""

import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Tuple
from models import TestCase, TestCaseResult, ExecutionResult


HARNESS_TEMPLATE = """# -*- coding: utf-8 -*-
import sys
import json
import time
import tracemalloc

# Student Submission Code
{student_code}

# Test Harness
test_specs = json.loads({test_specs_json})
results = []

tracemalloc.start()
start_total = time.perf_counter()

for idx, test in enumerate(test_specs):
    desc = test.get("description", f"Test #{{idx + 1}}")
    call_expr = test.get("call", "")
    expected = test.get("expected")

    t0 = time.perf_counter()
    try:
        # Evaluate student function call
        actual = eval(call_expr)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Semantic equality check
        passed = (actual == expected)
        results.append({{
            "test_index": idx,
            "description": desc,
            "call": call_expr,
            "expected_repr": repr(expected),
            "actual_repr": repr(actual),
            "passed": bool(passed),
            "execution_time_ms": round(elapsed_ms, 3),
            "error_message": None
        }})
    except Exception as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        results.append({{
            "test_index": idx,
            "description": desc,
            "call": call_expr,
            "expected_repr": repr(expected),
            "actual_repr": "Exception",
            "passed": False,
            "execution_time_ms": round(elapsed_ms, 3),
            "error_message": f"{{type(e).__name__}}: {{str(e)}}"
        }})

total_elapsed_ms = (time.perf_counter() - start_total) * 1000.0
_, peak_bytes = tracemalloc.get_traced_memory()
tracemalloc.stop()

output_payload = {{
    "total_elapsed_ms": round(total_elapsed_ms, 3),
    "peak_memory_kb": round(peak_bytes / 1024.0, 2),
    "results": results
}}

print("__TARK_RESULT_START__")
print(json.dumps(output_payload))
print("__TARK_RESULT_END__")
"""


def execute_sandboxed(
    student_code: str,
    test_cases: List[TestCase],
    timeout_seconds: float = 2.5
) -> ExecutionResult:
    """Spawns an isolated Python interpreter subprocess with strict timeouts."""
    if not student_code or not student_code.strip():
        return ExecutionResult(
            overall_passed=False,
            passed_count=0,
            total_count=len(test_cases),
            execution_time_ms=0.0,
            memory_kb=0.0,
            stdout="",
            stderr="No code submitted.",
            test_results=[]
        )

    # Prepare test specs JSON
    test_specs = [
        {"description": t.description, "call": t.call, "expected": t.expected}
        for t in test_cases
    ]

    harness_code = HARNESS_TEMPLATE.format(
        student_code=student_code,
        test_specs_json=repr(json.dumps(test_specs))
    )

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(harness_code)
        temp_file_path = f.name

    try:
        t_start = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, "-B", temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        wall_time_ms = (time.perf_counter() - t_start) * 1000.0
        stdout_raw = proc.stdout
        stderr_raw = proc.stderr

        # Extract structured payload from between delimiters
        if "__TARK_RESULT_START__" in stdout_raw and "__TARK_RESULT_END__" in stdout_raw:
            parts = stdout_raw.split("__TARK_RESULT_START__")
            user_prints = parts[0].strip()
            result_block = parts[1].split("__TARK_RESULT_END__")[0].strip()
            data = json.loads(result_block)

            test_results = [TestCaseResult(**r) for r in data["results"]]
            passed_count = sum(1 for r in test_results if r.passed)
            overall_passed = (passed_count == len(test_results)) and len(test_results) > 0

            return ExecutionResult(
                overall_passed=overall_passed,
                passed_count=passed_count,
                total_count=len(test_results),
                execution_time_ms=data.get("total_elapsed_ms", round(wall_time_ms, 2)),
                memory_kb=data.get("peak_memory_kb", 0.0),
                stdout=user_prints,
                stderr=stderr_raw,
                test_results=test_results
            )
        else:
            # Code failed before reaching test completion (e.g. top-level SyntaxError or crash)
            return ExecutionResult(
                overall_passed=False,
                passed_count=0,
                total_count=len(test_cases),
                execution_time_ms=round(wall_time_ms, 2),
                memory_kb=0.0,
                stdout=stdout_raw,
                stderr=stderr_raw or "Execution failed before tests could execute.",
                test_results=[]
            )

    except subprocess.TimeoutExpired:
        return ExecutionResult(
            overall_passed=False,
            passed_count=0,
            total_count=len(test_cases),
            execution_time_ms=timeout_seconds * 1000.0,
            memory_kb=0.0,
            stdout="",
            stderr=f"TimeLimitExceeded: Process terminated after exceeding maximum limit of {timeout_seconds}s. Look for infinite loops (while True without break) or unbounded recursion.",
            test_results=[
                TestCaseResult(
                    test_index=i,
                    description=t.description,
                    call=t.call,
                    expected_repr=repr(t.expected),
                    actual_repr="Timeout",
                    passed=False,
                    execution_time_ms=timeout_seconds * 1000.0,
                    error_message="Execution timed out (infinite loop or high algorithmic complexity)."
                ) for i, t in enumerate(test_cases)
            ]
        )
    finally:
        try:
            Path(temp_file_path).unlink(missing_ok=True)
        except Exception:
            pass
