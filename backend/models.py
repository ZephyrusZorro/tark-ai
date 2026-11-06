"""
TarkAI (तर्क) — Advanced Domain Models & Schemas (Pydantic v2)
Covers AST static metrics, Control Flow Graphs (CFG), Basic Blocks,
Spectrum-Based Fault Localization (SBFL), Halstead software complexity,
sandboxed execution telemetry, and FSRS spaced repetition.
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
    recursion_type: Optional[str] = None
    cyclomatic_complexity: int
    cognitive_complexity: int
    halstead: Optional[HalsteadMetrics] = None
    reason: str


class SymbolInfo(BaseModel):
    functions: List[Dict[str, Any]] = Field(default_factory=list)
    classes: List[Dict[str, Any]] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    global_variables: List[str] = Field(default_factory=list)


# --- Control Flow Graph (CFG) Models ---
class BasicBlock(BaseModel):
    id: str
    block_type: str
    start_line: int
    end_line: int
    statements: List[str] = Field(default_factory=list)
    predecessors: List[str] = Field(default_factory=list)
    successors: List[str] = Field(default_factory=list)
    is_reachable: bool = True


class CFGEdge(BaseModel):
    source: str
    target: str
    condition: Optional[str] = None


class CFGAnalysisResult(BaseModel):
    total_blocks: int
    total_edges: int
    cyclomatic_complexity: int
    unreachable_blocks: List[str] = Field(default_factory=list)
    blocks: List[BasicBlock] = Field(default_factory=list)
    edges: List[CFGEdge] = Field(default_factory=list)
    mermaid_cfg: str = ""


# --- Spectrum-Based Fault Localization Models ---
class LineSuspiciousness(BaseModel):
    line: int
    source_snippet: str
    tarantula_score: float
    ochiai_score: float
    executed_in_failed: int
    executed_in_passed: int
    verdict: str


class FaultLocalizationReport(BaseModel):
    has_failures: bool
    total_passed_tests: int
    total_failed_tests: int
    most_suspicious_line: Optional[int] = None
    max_suspiciousness: float = 0.0
    line_scores: List[LineSuspiciousness] = Field(default_factory=list)
    pedagogical_diagnosis: str


# --- Property-Based Fuzzing Models ---
class FuzzCaseResult(BaseModel):
    fuzz_index: int
    property_name: str
    input_repr: str
    output_repr: str
    invariant_held: bool
    latency_ms: float
    error_message: Optional[str] = None


class FuzzSessionReport(BaseModel):
    challenge_id: str
    total_fuzz_tests: int
    passed_fuzz_tests: int
    failed_fuzz_tests: int
    all_invariants_held: bool
    fuzz_results: List[FuzzCaseResult] = Field(default_factory=list)
    boundary_diagnosis: str


class ASTAnalysisResult(BaseModel):
    syntax_valid: bool
    syntax_error: Optional[str] = None
    syntax_line: Optional[int] = None
    complexity: Optional[ComplexityEstimate] = None
    anti_patterns: List[AntiPatternReport] = Field(default_factory=list)
    symbol_table: Optional[SymbolInfo] = None
    tree_hierarchy: Optional[Dict[str, Any]] = None
    mermaid_flowchart: Optional[str] = None
    cfg_analysis: Optional[CFGAnalysisResult] = None


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
    fault_localization: Optional[FaultLocalizationReport] = None


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
    box: int = 1
    interval_days: int = 1
    stability_days: float = 1.0
    retrievability_pct: float = 100.0
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
