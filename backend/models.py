"""
TarkAI — Data Models & Schemas (Pydantic v2)
Defines type-safe contracts for AST analysis, sandboxed execution,
curriculum challenges, and Socratic pedagogical responses.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class CodeSubmission(BaseModel):
    code: str = Field(..., description="Python source code submitted by the student")
    challenge_id: Optional[str] = Field(None, description="Optional ID of curriculum challenge")


class AntiPatternReport(BaseModel):
    pattern_type: str
    message: str
    line: int
    severity: Literal["info", "warning", "error"]
    suggestion: str


class ComplexityEstimate(BaseModel):
    estimated_time: str = Field(..., description="e.g. O(1), O(N), O(N log N), O(N^2), O(2^N)")
    max_loop_nesting: int
    recursion_detected: bool
    cyclomatic_complexity: int
    reason: str


class SymbolInfo(BaseModel):
    functions: List[Dict[str, Any]] = Field(default_factory=list)
    classes: List[Dict[str, Any]] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)


class ASTAnalysisResult(BaseModel):
    syntax_valid: bool
    syntax_error: Optional[str] = None
    syntax_line: Optional[int] = None
    complexity: Optional[ComplexityEstimate] = None
    anti_patterns: List[AntiPatternReport] = Field(default_factory=list)
    symbol_table: Optional[SymbolInfo] = None
    tree_hierarchy: Optional[Dict[str, Any]] = None


class TestCase(BaseModel):
    __test__ = False  # Prevent pytest from treating this as a test class
    description: str
    call: str
    expected: Any
    is_hidden: bool = False


class TestCaseResult(BaseModel):
    __test__ = False
    test_index: int
    description: str
    call: str
    expected_repr: str
    actual_repr: str
    passed: bool
    execution_time_ms: float
    error_message: Optional[str] = None


class ExecutionResult(BaseModel):
    overall_passed: bool
    passed_count: int
    total_count: int
    execution_time_ms: float
    memory_kb: float
    stdout: str
    stderr: str
    test_results: List[TestCaseResult] = Field(default_factory=list)


class SocraticHintRequest(BaseModel):
    code: str
    challenge_id: str
    hint_level: Literal[1, 2, 3] = Field(1, description="1=Conceptual Nudge, 2=Algorithmic Guidance, 3=Pseudocode Scaffold")
    student_question: Optional[str] = None
    failed_test: Optional[TestCaseResult] = None


class SocraticHintResponse(BaseModel):
    hint_level: int
    level_name: str
    title: str
    guidance: str
    question_to_ponder: str
    code_anchor_line: Optional[int] = None


class ChallengeMetadata(BaseModel):
    id: str
    title: str
    track: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    summary: str
    description: str
    constraints: List[str]
    starter_code: str
    test_count: int
    solved: bool = False


class UserStats(BaseModel):
    total_attempts: int
    problems_solved: int
    streak_days: int
    average_complexity: str
    top_anti_patterns: List[Dict[str, Any]]
