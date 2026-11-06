"""
TarkAI (तर्क) — Advanced Domain Models & Schemas (Pydantic v2)
Covers AST static metrics, Halstead complexity, Cognitive complexity,
sandboxed execution telemetry, spaced repetition (FSRS/Leitner),
and multi-turn Socratic mentoring.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class CodeSubmission(BaseModel):
    code: str = Field(..., description="Python source code submitted by the student")
    challenge_id: Optional[str] = Field(None, description="Curriculum challenge ID")
    used_hint_level: Optional[int] = Field(0, description="Highest hint level accessed (0=None)")


class AntiPatternReport(BaseModel):
    pattern_type: str
    message: str
    line: int
    severity: Literal["info", "warning", "error"]
    suggestion: str
    code_snippet: Optional[str] = None


class HalsteadMetrics(BaseModel):
    distinct_operators: int
    distinct_operands: int
    total_operators: int
    total_operands: int
    program_length: int
    vocabulary: int
    volume: float
    difficulty: float
    effort: float


class ComplexityEstimate(BaseModel):
    estimated_time: str = Field(..., description="e.g. O(1), O(N), O(N log N), O(N^2), O(2^N)")
    max_loop_nesting: int
    recursion_detected: bool
    recursion_type: Optional[str] = None  # "tail", "linear", "binary_tree", "exponential"
    cyclomatic_complexity: int
    cognitive_complexity: int
    halstead: Optional[HalsteadMetrics] = None
    reason: str


class SymbolInfo(BaseModel):
    functions: List[Dict[str, Any]] = Field(default_factory=list)
    classes: List[Dict[str, Any]] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    global_variables: List[str] = Field(default_factory=list)


class ASTAnalysisResult(BaseModel):
    syntax_valid: bool
    syntax_error: Optional[str] = None
    syntax_line: Optional[int] = None
    complexity: Optional[ComplexityEstimate] = None
    anti_patterns: List[AntiPatternReport] = Field(default_factory=list)
    symbol_table: Optional[SymbolInfo] = None
    tree_hierarchy: Optional[Dict[str, Any]] = None
    mermaid_flowchart: Optional[str] = None


class TestCase(BaseModel):
    __test__ = False
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
    is_timeout: bool = False
    spaced_repetition_update: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    role: Literal["student", "tutor", "system"]
    content: str
    timestamp: Optional[float] = None


class SocraticHintRequest(BaseModel):
    code: str
    challenge_id: str
    hint_level: Literal[1, 2, 3] = Field(1, description="1=Conceptual, 2=Algorithmic, 3=Scaffold")
    student_question: Optional[str] = None
    chat_history: List[ChatMessage] = Field(default_factory=list)
    failed_test: Optional[TestCaseResult] = None
    use_local_llm: bool = False


class SocraticHintResponse(BaseModel):
    hint_level: int
    level_name: str
    title: str
    guidance: str
    question_to_ponder: str
    code_anchor_line: Optional[int] = None
    chat_reply: Optional[str] = None


class SpacedRepetitionCard(BaseModel):
    challenge_id: str
    box: int = 1  # Leitner box 1 through 5
    interval_days: int = 1
    due_date: str
    attempts_count: int = 0
    failure_count: int = 0
    last_solved_at: Optional[str] = None


class ChallengeMetadata(BaseModel):
    id: str
    title: str
    track: str
    track_code: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    summary: str
    description: str
    constraints: List[str]
    starter_code: str
    test_count: int
    solved: bool = False
    leitner_box: int = 1
    due_status: Literal["New", "Due", "Learned", "Mastered"] = "New"


class UserStats(BaseModel):
    total_attempts: int
    problems_solved: int
    mastery_percentage: float
    streak_days: int
    average_complexity: str
    total_loc_analyzed: int
    leitner_breakdown: Dict[str, int]
    weakness_matrix: List[Dict[str, Any]]
