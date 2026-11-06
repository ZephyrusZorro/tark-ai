"""
TarkAI (तर्क) — Advanced Abstract Syntax Tree (AST) Semantic Engine
Performs safe static code introspection to extract:
1. Algorithmic Time & Space Complexity bounds
2. McCabe Cyclomatic Complexity & Cognitive Complexity
3. Software Engineering Halstead Metrics (Volume, Difficulty, Effort)
4. Comprehensive Anti-Pattern & Static Linter Rules
5. Dead / Unreachable Code Detection
6. Mermaid Flowchart graph generation
"""

import ast
import math
from typing import Dict, Any, List, Set, Optional, Tuple
from models import (
    ASTAnalysisResult,
    ComplexityEstimate,
    HalsteadMetrics,
    AntiPatternReport,
    SymbolInfo
)

BUILTIN_NAMES = {
    "list", "dict", "set", "tuple", "str", "int", "float", "bool",
    "len", "sum", "min", "max", "id", "type", "map", "filter",
    "range", "enumerate", "zip", "all", "any", "sorted", "reversed", "open"
}


class AdvancedMetricVisitor(ast.NodeVisitor):
    """Computes Cyclomatic, Cognitive, and Halstead software engineering metrics."""

    def __init__(self):
        # Cyclomatic & Nesting
        self.cyclomatic = 1
        self.cognitive = 0
        self.current_nesting = 0
        self.max_nesting = 0

        # Recursion
        self.current_function: Optional[str] = None
        self.function_calls: Dict[str, int] = {}
        self.recursive_functions: Set[str] = set()

        # Halstead Operators & Operands
        self.operators: List[str] = []
        self.operands: List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.operators.append("def")
        self.operands.append(node.name)
        prev_func = self.current_function
        self.current_function = node.name
        self.function_calls[node.name] = 0

        self.generic_visit(node)

        if self.function_calls.get(node.name, 0) > 0:
            self.recursive_functions.add(node.name)

        self.current_function = prev_func

    def visit_Call(self, node: ast.Call):
        self.operators.append("call")
        if self.current_function and isinstance(node.func, ast.Name):
            if node.func.id == self.current_function:
                self.function_calls[self.current_function] = self.function_calls.get(self.current_function, 0) + 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.operators.append("for")
        self.cyclomatic += 1
        self.cognitive += 1 + self.current_nesting
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)

        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_While(self, node: ast.While):
        self.operators.append("while")
        self.cyclomatic += 1
        self.cognitive += 1 + self.current_nesting
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)

        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_If(self, node: ast.If):
        self.operators.append("if")
        self.cyclomatic += 1
        self.cognitive += 1 + self.current_nesting

        # Check else
        if node.orelse:
            self.operators.append("else")
            if not isinstance(node.orelse[0], ast.If):  # elif already handled
                self.cognitive += 1

        self.current_nesting += 1
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_BoolOp(self, node: ast.BoolOp):
        self.operators.append(type(node.op).__name__)
        self.cyclomatic += len(node.values) - 1
        self.cognitive += 1
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        self.operators.append(type(node.op).__name__)
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        self.operators.append(type(node.op).__name__)
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        for op in node.ops:
            self.operators.append(type(op).__name__)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        self.operands.append(node.id)
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        self.operands.append(repr(node.value))
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return):
        self.operators.append("return")
        self.generic_visit(node)

    def calculate_halstead(self) -> HalsteadMetrics:
        distinct_ops = set(self.operators)
        distinct_operands = set(self.operands)

        eta1 = len(distinct_ops) or 1
        eta2 = len(distinct_operands) or 1
        n1 = len(self.operators) or 1
        n2 = len(self.operands) or 1

        vocab = eta1 + eta2
        length = n1 + n2
        volume = length * math.log2(vocab) if vocab > 1 else 0.0
        difficulty = (eta1 / 2.0) * (n2 / eta2) if eta2 > 0 else 0.0
        effort = difficulty * volume

        return HalsteadMetrics(
            distinct_operators=eta1,
            distinct_operands=eta2,
            total_operators=n1,
            total_operands=n2,
            program_length=length,
            vocabulary=vocab,
            volume=round(volume, 2),
            difficulty=round(difficulty, 2),
            effort=round(effort, 2)
        )


class AdvancedAntiPatternVisitor(ast.NodeVisitor):
    def __init__(self, raw_lines: List[str]):
        self.raw_lines = raw_lines
        self.reports: List[AntiPatternReport] = []
        self.in_loop_depth = 0

    def _snippet(self, lineno: int) -> Optional[str]:
        if 1 <= lineno <= len(self.raw_lines):
            return self.raw_lines[lineno - 1].strip()
        return None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # 1. Mutable default args
        for default in node.args.defaults + node.args.kw_defaults:
            if default is not None and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.reports.append(AntiPatternReport(
                    pattern_type="mutable_default",
                    message=f"Function '{node.name}' uses a mutable default argument (list/dict/set).",
                    line=node.lineno,
                    severity="warning",
                    suggestion="Mutable defaults persist state across function calls. Use `None` as default and initialize inside body.",
                    code_snippet=self._snippet(node.lineno)
                ))

        # Check dead code after return
        for i, stmt in enumerate(node.body[:-1]):
            if isinstance(stmt, (ast.Return, ast.Raise)):
                next_stmt = node.body[i + 1]
                self.reports.append(AntiPatternReport(
                    pattern_type="dead_code",
                    message=f"Unreachable code detected at line {next_stmt.lineno} following terminal '{type(stmt).__name__}'.",
                    line=next_stmt.lineno,
                    severity="warning",
                    suggestion="Statements placed after `return` or `raise` will never be executed. Remove or restructure branching.",
                    code_snippet=self._snippet(next_stmt.lineno)
                ))

        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # 2. Bare except
        if node.type is None:
            self.reports.append(AntiPatternReport(
                pattern_type="bare_except",
                message="Bare `except:` catches BaseException, swallowing SystemExit and KeyboardInterrupt.",
                line=node.lineno,
                severity="warning",
                suggestion="Specify explicit exceptions (e.g. `except ValueError:`) or at minimum `except Exception:`.",
                code_snippet=self._snippet(node.lineno)
            ))
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # 3. Built-in shadowing
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in BUILTIN_NAMES:
                self.reports.append(AntiPatternReport(
                    pattern_type="shadow_builtin",
                    message=f"Variable '{target.id}' shadows a standard Python built-in function or type.",
                    line=node.lineno,
                    severity="warning",
                    suggestion=f"Rename '{target.id}' to domain-specific identifier (e.g. `items_{target.id}`) to avoid masking built-in functionality.",
                    code_snippet=self._snippet(node.lineno)
                ))

            # 4. Inefficient string concatenation accumulator in loop
            if self.in_loop_depth > 0 and isinstance(target, ast.Name):
                if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
                    if (isinstance(node.value.left, ast.Name) and node.value.left.id == target.id) or \
                       (isinstance(node.value.right, ast.Name) and node.value.right.id == target.id):
                        self.reports.append(AntiPatternReport(
                            pattern_type="loop_string_concat",
                            message=f"String accumulator `+=` inside loop at line {node.lineno}.",
                            line=node.lineno,
                            severity="info",
                            suggestion="Repeated string concatenation incurs O(N^2) memory reallocation overhead. Collect items in a list and use `''.join(items)`.",
                            code_snippet=self._snippet(node.lineno)
                        ))
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global):
        # 5. Global variable pollution
        self.reports.append(AntiPatternReport(
            pattern_type="global_variable",
            message=f"Global statement modifying variables: {', '.join(node.names)}.",
            line=node.lineno,
            severity="warning",
            suggestion="Global state creates race conditions and tightly coupled modules. Pass arguments or encapsulate in class state.",
            code_snippet=self._snippet(node.lineno)
        ))
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        # 6. Redundant boolean check (e.g. if x == True)
        for comp in node.comparators:
            if isinstance(comp, ast.Constant) and isinstance(comp.value, bool):
                self.reports.append(AntiPatternReport(
                    pattern_type="redundant_bool_compare",
                    message="Redundant comparison to boolean literal (`== True` or `== False`).",
                    line=node.lineno,
                    severity="info",
                    suggestion="Simplify to Pythonic truthiness check: `if condition:` or `if not condition:`.",
                    code_snippet=self._snippet(node.lineno)
                ))
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.in_loop_depth += 1
        self.generic_visit(node)
        self.in_loop_depth -= 1

    def visit_While(self, node: ast.While):
        self.in_loop_depth += 1
        self.generic_visit(node)
        self.in_loop_depth -= 1


def generate_mermaid_flowchart(tree: ast.AST) -> str:
    """Generates clean Mermaid graph TD syntax representing execution flow."""
    lines = ["graph TD", "  Start([Start]) --> Entry"]
    node_counter = 0

    def node_id(prefix="node"):
        nonlocal node_counter
        node_counter += 1
        return f"{prefix}_{node_counter}"

    for item in getattr(tree, "body", []):
        if isinstance(item, ast.FunctionDef):
            fn_id = f"fn_{item.name}"
            lines.append(f'  Entry["def {item.name}()"] --> {fn_id}')
            prev = fn_id
            for stmt in item.body[:6]:  # Limit top nodes
                curr_id = node_id("stmt")
                if isinstance(stmt, ast.For):
                    lines.append(f'  {prev} --> {curr_id}{{"Loop: for"}}')
                elif isinstance(stmt, ast.While):
                    lines.append(f'  {prev} --> {curr_id}{{"Loop: while"}}')
                elif isinstance(stmt, ast.If):
                    lines.append(f'  {prev} --> {curr_id}{{"Branch: if"}}')
                elif isinstance(stmt, ast.Return):
                    lines.append(f'  {prev} --> {curr_id}["Return"]')
                else:
                    lines.append(f'  {prev} --> {curr_id}["{type(stmt).__name__}"]')
                prev = curr_id
            lines.append(f'  {prev} --> End([End])')
            break
    else:
        lines.append("  Entry[Script Body] --> End([End])")

    return "\n".join(lines)


def ast_to_dict(node: ast.AST) -> Dict[str, Any]:
    """Recursively converts an AST node to a clean JSON-serializable tree for UI visualization."""
    node_type = type(node).__name__
    data: Dict[str, Any] = {
        "type": node_type,
        "line": getattr(node, "lineno", None),
        "col": getattr(node, "col_offset", None)
    }

    if isinstance(node, ast.FunctionDef):
        data["name"] = node.name
        data["label"] = f"def {node.name}()"
    elif isinstance(node, ast.ClassDef):
        data["name"] = node.name
        data["label"] = f"class {node.name}"
    elif isinstance(node, ast.Name):
        data["id"] = node.id
        data["label"] = node.id
    elif isinstance(node, ast.Constant):
        data["value"] = repr(node.value)
        data["label"] = repr(node.value)
    elif isinstance(node, (ast.For, ast.While)):
        data["label"] = f"Loop ({node_type})"
    elif isinstance(node, ast.If):
        data["label"] = "If Condition"
    elif isinstance(node, ast.Return):
        data["label"] = "Return"
    else:
        data["label"] = node_type

    children = []
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    children.append(ast_to_dict(item))
        elif isinstance(value, ast.AST):
            children.append(ast_to_dict(value))

    if children:
        data["children"] = children[:15]

    return data


def analyze_code_ast(code: str) -> ASTAnalysisResult:
    """Entrypoint: parses Python code, evaluates complexity, and identifies anti-patterns."""
    if not code or not code.strip():
        return ASTAnalysisResult(
            syntax_valid=False,
            syntax_error="Source code is empty.",
            anti_patterns=[]
        )

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return ASTAnalysisResult(
            syntax_valid=False,
            syntax_error=f"SyntaxError: {e.msg}",
            syntax_line=e.lineno,
            anti_patterns=[]
        )

    raw_lines = code.split("\n")

    # 1. Anti-patterns & static warnings
    anti_visitor = AdvancedAntiPatternVisitor(raw_lines)
    anti_visitor.visit(tree)

    # 2. Metric calculation
    metric_visitor = AdvancedMetricVisitor()
    metric_visitor.visit(tree)

    is_recursive = len(metric_visitor.recursive_functions) > 0
    nesting = metric_visitor.max_nesting
    halstead = metric_visitor.calculate_halstead()

    # Determine time complexity & recursion typology
    recursion_type = None
    if is_recursive:
        max_branching = max(metric_visitor.function_calls.values()) if metric_visitor.function_calls else 1
        if max_branching >= 2:
            est_time = "O(2^N)"
            recursion_type = "binary_tree"
            reason = "Tree recursion with multiple branches per stack frame without detected memoization."
        else:
            est_time = "O(N)" if nesting == 0 else f"O(N^{nesting + 1})"
            recursion_type = "linear"
            reason = "Linear recursive stack traversal."
    elif nesting == 0:
        est_time = "O(1)"
        reason = "Constant time execution with zero loop structures."
    elif nesting == 1:
        est_time = "O(N)"
        reason = "Single-level iteration traversing input collection."
    elif nesting == 2:
        est_time = "O(N^2)"
        reason = "Dual nested loop levels detected (quadratic scaling)."
    else:
        est_time = f"O(N^{nesting})"
        reason = f"{nesting} nested loop layers detected."

    complexity = ComplexityEstimate(
        estimated_time=est_time,
        max_loop_nesting=nesting,
        recursion_detected=is_recursive,
        recursion_type=recursion_type,
        cyclomatic_complexity=metric_visitor.cyclomatic,
        cognitive_complexity=metric_visitor.cognitive,
        halstead=halstead,
        reason=reason
    )

    # 3. Symbol table
    symbols = SymbolInfo()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            symbols.functions.append({
                "name": node.name,
                "args": [a.arg for a in node.args.args],
                "line": node.lineno
            })
        elif isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            symbols.classes.append({
                "name": node.name,
                "methods": methods,
                "line": node.lineno
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                symbols.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            symbols.imports.append(node.module or "relative")

    # 4. Tree representation, Mermaid graph & Control Flow Graph (CFG)
    tree_hierarchy = ast_to_dict(tree)
    mermaid_chart = generate_mermaid_flowchart(tree)
    from cfg_engine import generate_control_flow_graph
    cfg_res = generate_control_flow_graph(code)

    return ASTAnalysisResult(
        syntax_valid=True,
        complexity=complexity,
        anti_patterns=anti_visitor.reports,
        symbol_table=symbols,
        tree_hierarchy=tree_hierarchy,
        mermaid_flowchart=mermaid_chart,
        cfg_analysis=cfg_res
    )
