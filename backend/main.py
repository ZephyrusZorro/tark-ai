"""
TarkAI — FastAPI Application Server
Provides RESTful APIs for AST analysis, sandboxed execution,
curriculum retrieval, Socratic mentoring, and serves the static frontend UI.
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from models import (
    CodeSubmission,
    ASTAnalysisResult,
    ExecutionResult,
    SocraticHintRequest,
    SocraticHintResponse,
    UserStats
)
from ast_analyzer import analyze_code_ast
from sandbox import execute_sandboxed
from curriculum import get_all_challenges, get_challenge_by_id
from socratic_tutor import generate_socratic_guidance
from db import init_db, record_submission, get_solved_ids, get_stats

app = FastAPI(
    title="TarkAI (तर्क) — Local-First Code Auditor & AST Tutor",
    version="1.0.0",
    description="Intelligent code inspection, complexity analysis, and Socratic guidance."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "system": "TarkAI (तर्क)",
        "version": "1.0.0",
        "engine": "Python AST + Subprocess Sandbox"
    }


@app.get("/api/curriculum")
def list_curriculum():
    challenges = get_all_challenges()
    solved = get_solved_ids()
    for c in challenges:
        c.solved = c.id in solved
    return challenges


@app.get("/api/challenge/{challenge_id}")
def get_challenge(challenge_id: str):
    chal = get_challenge_by_id(challenge_id)
    if not chal:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    
    # Return challenge without exposing solution
    return {
        "id": chal["id"],
        "title": chal["title"],
        "track": chal["track"],
        "difficulty": chal["difficulty"],
        "summary": chal["summary"],
        "description": chal["description"],
        "constraints": chal["constraints"],
        "starter_code": chal["starter_code"],
        "test_cases": [
            {"description": t.description, "call": t.call, "expected": repr(t.expected)}
            for t in chal["test_cases"]
        ]
    }


@app.post("/api/analyze", response_model=ASTAnalysisResult)
def analyze_code(submission: CodeSubmission):
    return analyze_code_ast(submission.code)


@app.post("/api/run", response_model=ExecutionResult)
def run_code(submission: CodeSubmission):
    if not submission.challenge_id:
        raise HTTPException(status_code=400, detail="Challenge ID required for test evaluation.")

    chal = get_challenge_by_id(submission.challenge_id)
    if not chal:
        raise HTTPException(status_code=404, detail="Challenge not found.")

    # 1. AST pre-check to detect syntax errors
    ast_res = analyze_code_ast(submission.code)
    if not ast_res.syntax_valid:
        return ExecutionResult(
            overall_passed=False,
            passed_count=0,
            total_count=len(chal["test_cases"]),
            execution_time_ms=0.0,
            memory_kb=0.0,
            stdout="",
            stderr=f"{ast_res.syntax_error} (line {ast_res.syntax_line})",
            test_results=[]
        )

    # 2. Execute against test cases
    exec_res = execute_sandboxed(submission.code, chal["test_cases"])

    # 3. Record in DB
    complexity_str = ast_res.complexity.estimated_time if ast_res.complexity else "O(N)"
    record_submission(
        challenge_id=submission.challenge_id,
        code=submission.code,
        passed=exec_res.overall_passed,
        passed_count=exec_res.passed_count,
        total_count=exec_res.total_count,
        execution_time_ms=exec_res.execution_time_ms,
        complexity=complexity_str
    )

    return exec_res


@app.post("/api/socratic-hint", response_model=SocraticHintResponse)
def get_socratic_hint(request: SocraticHintRequest):
    return generate_socratic_guidance(request)


@app.get("/api/stats", response_model=UserStats)
def get_user_statistics():
    return get_stats()


# Mount static frontend
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
