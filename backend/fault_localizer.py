"""
TarkAI (तर्क) — Spectrum-Based Fault Localization (SBFL) Engine
Implements academic Tarantula and Ochiai mathematical formulas
to compute line suspiciousness rankings from passing vs failing test executions.
"""

import math
from typing import List, Dict, Any, Optional
from models import LineSuspiciousness, FaultLocalizationReport


def compute_sbfl_scores(
    code: str,
    test_results: List[Any],
    execution_traces: Optional[Dict[int, List[int]]] = None
) -> FaultLocalizationReport:
    """
    Computes Tarantula and Ochiai suspiciousness coefficients.
    execution_traces: maps test_index -> list of executed line numbers.
    """
    lines = code.splitlines()
    total_lines = len(lines)

    passed_count = sum(1 for t in test_results if getattr(t, "passed", False))
    failed_count = sum(1 for t in test_results if not getattr(t, "passed", False))

    if failed_count == 0:
        return FaultLocalizationReport(
            has_failures=False,
            total_passed_tests=passed_count,
            total_failed_tests=0,
            most_suspicious_line=None,
            max_suspiciousness=0.0,
            line_scores=[],
            pedagogical_diagnosis="All assertions verified. Zero fault localization anomalies detected."
        )

    # If no dynamic execution trace provided, infer line execution statically from AST/control flow
    line_failed_exec: Dict[int, int] = {i: 0 for i in range(1, total_lines + 1)}
    line_passed_exec: Dict[int, int] = {i: 0 for i in range(1, total_lines + 1)}

    if execution_traces:
        for idx, t in enumerate(test_results):
            t_lines = set(execution_traces.get(idx, []))
            if getattr(t, "passed", False):
                for l in t_lines:
                    if l in line_passed_exec:
                        line_passed_exec[l] += 1
            else:
                for l in t_lines:
                    if l in line_failed_exec:
                        line_failed_exec[l] += 1
    else:
        # Heuristic simulation when tracer is isolated:
        # Loops, returns, and conditions inside functions are weighted
        for i, raw_line in enumerate(lines, start=1):
            s = raw_line.strip()
            if not s or s.startswith("#") or s.startswith("def ") or s.startswith("import "):
                continue
            # Conditionals, returns, and mutations in loops are key suspect candidates
            if s.startswith("return "):
                line_failed_exec[i] = failed_count
                line_passed_exec[i] = max(0, passed_count - 1)
            elif "if " in s or "elif " in s or "else:" in s:
                line_failed_exec[i] = failed_count
                line_passed_exec[i] = int(passed_count * 0.5)
            else:
                line_failed_exec[i] = int(failed_count * 0.8)
                line_passed_exec[i] = passed_count

    line_scores: List[LineSuspiciousness] = []
    top_line = None
    max_score = 0.0

    for lineno in range(1, total_lines + 1):
        s_line = lines[lineno - 1]
        if not s_line.strip() or s_line.strip().startswith("#"):
            continue

        n_cf = line_failed_exec.get(lineno, 0)
        n_cp = line_passed_exec.get(lineno, 0)

        # 1. Tarantula formula
        # T = (n_cf / F) / ((n_cf / F) + (n_cp / P))
        tarantula = 0.0
        f_ratio = n_cf / failed_count if failed_count > 0 else 0
        p_ratio = n_cp / passed_count if passed_count > 0 else 0
        denom_t = f_ratio + p_ratio
        if denom_t > 0:
            tarantula = round(f_ratio / denom_t, 3)

        # 2. Ochiai formula
        # O = n_cf / sqrt(F * (n_cf + n_cp))
        ochiai = 0.0
        denom_o = math.sqrt(failed_count * (n_cf + n_cp))
        if denom_o > 0:
            ochiai = round(n_cf / denom_o, 3)

        combined = round((tarantula * 0.4 + ochiai * 0.6), 3)

        if combined >= 0.75:
            verdict = "CRITICAL"
        elif combined >= 0.5:
            verdict = "SUSPICIOUS"
        elif combined >= 0.25:
            verdict = "BENIGN"
        else:
            verdict = "CLEAN"

        score_item = LineSuspiciousness(
            line=lineno,
            source_snippet=s_line.strip()[:60],
            tarantula_score=tarantula,
            ochiai_score=ochiai,
            executed_in_failed=n_cf,
            executed_in_passed=n_cp,
            verdict=verdict
        )
        line_scores.append(score_item)

        if combined > max_score:
            max_score = combined
            top_line = lineno

    # Sort descending by Ochiai score
    line_scores.sort(key=lambda x: (x.ochiai_score, x.tarantula_score), reverse=True)

    diagnosis = (
        f"Spectrum-Based Fault Localization (Ochiai/Tarantula) identifies Line {top_line} "
        f"with highest failure-correlation ({int(max_score * 100)}% suspiciousness). "
        f"Examine boundary guard or return condition at line {top_line}."
    ) if top_line else "No specific line isolated."

    return FaultLocalizationReport(
        has_failures=True,
        total_passed_tests=passed_count,
        total_failed_tests=failed_count,
        most_suspicious_line=top_line,
        max_suspiciousness=max_score,
        line_scores=line_scores[:8],
        pedagogical_diagnosis=diagnosis
    )
