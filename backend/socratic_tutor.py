"""
TarkAI — Socratic Pedagogical Guidance Engine
Provides tiered conceptual questions and targeted hints based on
AST inspection and failed assertion differentials.
"""

from typing import Dict, Any, Optional
from models import SocraticHintRequest, SocraticHintResponse, TestCaseResult
from curriculum import get_challenge_by_id
from ast_analyzer import analyze_code_ast


LEVEL_NAMES = {
    1: "Level 1: Conceptual Invariant",
    2: "Level 2: Algorithmic Strategy",
    3: "Level 3: Structural Scaffold"
}


def generate_socratic_guidance(request: SocraticHintRequest) -> SocraticHintResponse:
    """Generates tiered Socratic hints without giving away the full solution."""
    challenge = get_challenge_by_id(request.challenge_id)
    if not challenge:
        return SocraticHintResponse(
            hint_level=request.hint_level,
            level_name=LEVEL_NAMES.get(request.hint_level, "Custom Hint"),
            title="General Code Review",
            guidance="Review your function signature and ensure return values match the requested data types.",
            question_to_ponder="What is the expected output type for an empty or boundary input?"
        )

    hints_dict = challenge.get("hints", {})
    tier_hint = hints_dict.get(request.hint_level, {})

    # 1. Analyze student code for anti-patterns or complexity
    ast_res = analyze_code_ast(request.code)

    title = tier_hint.get("title", f"Hint for {challenge['title']}")
    guidance = tier_hint.get("guidance", "Consider the mathematical invariant of your current loop.")
    question = tier_hint.get("question", "What happens on an edge case with minimal input length?")

    # 2. If student has anti-patterns, prepend pedagogical advice
    if ast_res.anti_patterns:
        top_warning = ast_res.anti_patterns[0]
        if top_warning.severity in ("warning", "error"):
            guidance = f"[Note: {top_warning.message}] {guidance}"

    # 3. If there is a failed test, contextualize the question
    if request.failed_test:
        test = request.failed_test
        if test.error_message and "TimeLimitExceeded" in test.error_message:
            title = "Algorithmic Complexity & Infinite Loop"
            guidance = "Your submission timed out. Check your loop exit condition (e.g., does your `while` loop increment/decrement its pointers on every path?)."
            question = "Are your pointers moving toward each other on every iteration?"
        elif test.error_message and "IndexError" in test.error_message:
            title = "Boundary & Index Range Check"
            guidance = f"An IndexError occurred when executing `{test.call}`. Check if your loop traverses past `len(array) - 1` or accesses negative indices."
            question = "Is your right pointer initialized to `len(numbers) - 1` rather than `len(numbers)`?"
        elif test.expected_repr and test.actual_repr:
            guidance = f"{guidance}\n\nNotice that on test `{test.call}`, the expected result was `{test.expected_repr}`, but your function returned `{test.actual_repr}`."

    # 4. If student asked a direct natural language question
    if request.student_question and request.student_question.strip():
        q_lower = request.student_question.lower()
        if "time complexity" in q_lower or "o(n)" in q_lower or "big o" in q_lower:
            guidance = f"Regarding your question: {request.student_question}\n\nYour current code has estimated time complexity of {ast_res.complexity.estimated_time if ast_res.complexity else 'unknown'}. {ast_res.complexity.reason if ast_res.complexity else ''}\n\n{guidance}"
        elif "edge case" in q_lower:
            guidance = f"Regarding edge cases: Think about minimal bounds: empty arrays `[]`, single elements `[1]`, duplicate values, or all negative numbers. How does your code handle these?"

    return SocraticHintResponse(
        hint_level=request.hint_level,
        level_name=LEVEL_NAMES.get(request.hint_level, f"Level {request.hint_level}"),
        title=title,
        guidance=guidance,
        question_to_ponder=question,
        code_anchor_line=ast_res.anti_patterns[0].line if ast_res.anti_patterns else None
    )
