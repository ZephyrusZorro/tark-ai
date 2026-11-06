"""
TarkAI (तर्क) — Socratic Pedagogical Mentoring Engine
Provides multi-tier conceptual guidance, conversational Socratic tutoring,
and local LLM bridging with strict anti-spoiler guards.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List
from models import (
    SocraticHintRequest,
    SocraticHintResponse,
    ChatMessage
)
from curriculum import get_challenge_by_id
from ast_analyzer import analyze_code_ast

SOCRATIC_SYSTEM_PROMPT = """You are TarkAI, an expert Socratic Code Tutor.
Your objective is to guide the student toward understanding without giving away code solutions.
1. NEVER output working code or complete algorithms.
2. Formulate 1-2 targeted questions about the invariant, data structure, or edge case.
3. Point out subtle conceptual gaps (e.g. why greedy fails, boundary index overflows, or quadratic nesting).
4. Keep answers concise, direct, and pedagogical. Use high-contrast ASCII or brief conceptual analogies."""

LEVEL_NAMES = {
    1: "Level 1: Conceptual Invariant",
    2: "Level 2: Algorithmic Strategy",
    3: "Level 3: Structural Scaffold"
}


def query_local_ollama(
    prompt: str,
    chat_history: List[ChatMessage],
    endpoint: str = "http://localhost:11434/api/generate",
    model: str = "qwen2.5-coder:7b"
) -> Optional[str]:
    """Attempts to query a local Ollama instance if running, otherwise returns None."""
    history_text = "\n".join([f"{m.role.upper()}: {m.content}" for m in chat_history[-4:]])
    full_prompt = f"{SOCRATIC_SYSTEM_PROMPT}\n\nRecent Conversation:\n{history_text}\n\nStudent Asks: {prompt}\n\nTutor:"

    payload = json.dumps({
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 250}
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=3.0) as res:
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                return data.get("response", "").strip()
    except Exception:
        # Offline or Ollama not running; fallback to deterministic engine
        return None

    return None


def generate_socratic_guidance(request: SocraticHintRequest) -> SocraticHintResponse:
    """Generates tiered Socratic hints and conversational mentoring."""
    challenge = get_challenge_by_id(request.challenge_id)
    ast_res = analyze_code_ast(request.code)

    tier_hint = {}
    if challenge:
        hints_dict = challenge.get("hints", {})
        tier_hint = hints_dict.get(request.hint_level, {})

    title = tier_hint.get("title", f"Hint (Level {request.hint_level})")
    guidance = tier_hint.get("guidance", "Examine the invariant of your loop boundaries.")
    question = tier_hint.get("question", "What is the expected state when the input array is at minimum size?")

    # 1. Check for severe anti-patterns
    if ast_res.anti_patterns:
        warning = next((p for p in ast_res.anti_patterns if p.severity in ("warning", "error")), None)
        if warning:
            guidance = f"[Static Linter Warning: Line {warning.line} - {warning.message}]\n\n{guidance}"

    # 2. Contextualize with failed assertions
    if request.failed_test:
        ft = request.failed_test
        if ft.error_message and "TimeLimitExceeded" in ft.error_message:
            title = "Algorithmic Timeout Guard"
            guidance = "Your code exceeded the 2.5-second execution limit. Look for loops whose step condition does not advance toward termination."
            question = "Are your pointers guaranteed to converge on every single branch?"
        elif ft.error_message and "IndexError" in ft.error_message:
            title = "Array Boundary Overrun"
            guidance = f"An IndexError was raised when running `{ft.call}`. Check if your loop accesses index `i + 1` without guarding `len(array) - 1`."
            question = "Is your right pointer initialized to `len(numbers) - 1` or `len(numbers)`?"
        elif ft.expected_repr and ft.actual_repr:
            guidance = f"{guidance}\n\nNotice the difference on input `{ft.call}`:\nExpected: {ft.expected_repr}\nReceived: {ft.actual_repr}"

    # 3. Handle interactive natural language queries
    chat_reply = None
    if request.student_question and request.student_question.strip():
        q_text = request.student_question.strip()

        # Try local Ollama first if requested
        if request.use_local_llm:
            chat_reply = query_local_ollama(q_text, request.chat_history)

        # Fallback to local rule engine if no LLM reply
        if not chat_reply:
            q_lower = q_text.lower()
            if "complexity" in q_lower or "o(n)" in q_lower or "time" in q_lower:
                chat_reply = (
                    f"Your code currently has an estimated complexity of {ast_res.complexity.estimated_time if ast_res.complexity else 'O(N)'}. "
                    f"{ast_res.complexity.reason if ast_res.complexity else ''} "
                    f"To optimize further, ask yourself: Can you prune branches before iterating over them?"
                )
            elif "fail" in q_lower or "test" in q_lower or "wrong" in q_lower:
                if request.failed_test:
                    chat_reply = (
                        f"Test '{request.failed_test.description}' failed on `{request.failed_test.call}`. "
                        f"Your function returned `{request.failed_test.actual_repr}`, but expected `{request.failed_test.expected_repr}`. "
                        f"Step through your pointer updates on paper for that exact input."
                    )
                else:
                    chat_reply = "All current public test cases passed! Try testing edge cases like negative numbers, duplicates, or empty lists."
            elif "edge case" in q_lower:
                chat_reply = (
                    "Standard edge cases to test: (1) Empty collection `[]`, (2) Single-element `[1]`, "
                    "(3) Duplicate values, (4) All negative values, and (5) Max boundary limits. "
                    "Which of these does your current code assume will never happen?"
                )
            else:
                chat_reply = (
                    f"Consider the core invariant: what property must remain true after each iteration? "
                    f"For '{challenge.get('title', 'this challenge')}', review: {question}"
                )

    return SocraticHintResponse(
        hint_level=request.hint_level,
        level_name=LEVEL_NAMES.get(request.hint_level, f"Level {request.hint_level}"),
        title=title,
        guidance=guidance,
        question_to_ponder=question,
        code_anchor_line=ast_res.anti_patterns[0].line if ast_res.anti_patterns else None,
        chat_reply=chat_reply
    )
