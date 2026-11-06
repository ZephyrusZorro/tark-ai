"""
TarkAI — Abstract Syntax Tree (AST) Semantic Analyzer
Performs safe, static code introspection to extract algorithmic complexity,
detect anti-patterns, calculate cyclomatic complexity, and generate visual hierarchy.
"""

import ast
from typing import Dict, Any, List, Set, Optional
from models import (
    ASTAnalysisResult,
    ComplexityEstimate,
    AntiPatternReport,
    SymbolInfo
)

BUILTIN_NAMES = {
    "list", "dict", "set", "tuple", "str", "int", "float", "bool",
    "len", "sum", "min", "max", "id", "type", "map", "filter",
    "range", "enumerate", "zip", "all", "any", "sorted", "reversed", "open"
}


class AntiPatternVisitor(ast.NodeVisitor):
    def __init__(self):
        self.reports: List[AntiPatternReport] = []
        self.in_loop_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # 1. Mutable Default Arguments
        for default in node.args.defaults + node.args.kw_defaults:
            if default is not None and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.reports.append(AntiPatternReport(
                    pattern_type="mutable_default",
                    message=f"Function '{node.name}' uses a mutable default argument (list/dict/set).",
                    line=node.lineno,
                    severity="warning",
                    suggestion="Default arguments are evaluated once at definition time. Use `None` as default and initialize inside the function."
                ))
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        # 2. Bare except clause
        if node.type is None:
            self.reports.append(AntiPatternReport(
                pattern_type="bare_except",
                message="Bare `except:` catch-all detected without specifying an exception class.",
                line=node.lineno,
                severity="warning",
                suggestion="Catch explicit exceptions like `except ValueError:` or at minimum `except Exception:` to avoid intercepting SystemExit and KeyboardInterrupt."
            ))
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # 3. Built-in shadowing
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in BUILTIN_NAMES:
                self.reports.append(AntiPatternReport(
                    pattern_type="shadow_builtin",
                    message=f"Variable name '{target.id}' shadows a standard Python built-in function or type.",
                    line=node.lineno,
                    severity="warning",
                    suggestion=f"Rename '{target.id}' to something domain-specific (e.g. `items_list`, `{target.id}_val`) to prevent masking built-in behavior."
                ))

            # 4. Inefficient string concatenation in loop
            if self.in_loop_depth > 0 and isinstance(target, ast.Name):
                if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
                    if (isinstance(node.value.left, ast.Name) and node.value.left.id == target.id) or \
                       (isinstance(node.value.right, ast.Name) and node.value.right.id == target.id):
                        self.reports.append(AntiPatternReport(
                            pattern_type="loop_string_concat",
                            message=f"String/sequence accumulator `+=` inside a loop at line {node.lineno}.",
                            line=node.lineno,
                            severity="info",
                            suggestion="Repeated string concatenation creates O(N^2) memory reallocations. Accumulate in a list and use `''.join(chars)` instead."
                        ))
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global):
        # 5. Global state mutation
        self.reports.append(AntiPatternReport(
            pattern_type="global_variable",
            message=f"Global statement modifying variables: {', '.join(node.names)}.",
            line=node.lineno,
            severity="warning",
            suggestion="Global state creates coupling and breaks thread-safety. Pass state via function parameters or class encapsulation."
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
                    suggestion="Use truthiness directly: `if condition:` or `if not condition:` for cleaner Pythonic idiom."
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


class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.current_nesting = 0
        self.max_nesting = 0
        self.cyclomatic = 1
        self.current_function = None
        self.function_calls: Dict[str, int] = {}
        self.recursive_functions: Set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        prev_func = self.current_function
        self.current_function = node.name
        self.function_calls[node.name] = 0

        self.generic_visit(node)

        if self.function_calls.get(node.name, 0) > 0:
            self.recursive_functions.add(node.name)

        self.current_function = prev_func

    def visit_Call(self, node: ast.Call):
        if self.current_function and isinstance(node.func, ast.Name):
            if node.func.id == self.current_function:
                self.function_calls[self.current_function] = self.function_calls.get(self.current_function, 0) + 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.cyclomatic += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_While(self, node: ast.While):
        self.cyclomatic += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_If(self, node: ast.If):
        self.cyclomatic += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        self.cyclomatic += len(node.values) - 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.cyclomatic += 1
        self.generic_visit(node)


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
        data["label"] = "Loop"
    elif isinstance(node, ast.If):
        data["label"] = "If"
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
        data["children"] = children[:20]  # Limit breadth per node for clean visual rendering

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

    # 1. Anti-patterns
    anti_visitor = AntiPatternVisitor()
    anti_visitor.visit(tree)

    # 2. Complexity
    comp_visitor = ComplexityVisitor()
    comp_visitor.visit(tree)

    is_recursive = len(comp_visitor.recursive_functions) > 0
    nesting = comp_visitor.max_nesting

    if is_recursive:
        # Check recursive calls per function
        max_branching = max(comp_visitor.function_calls.values()) if comp_visitor.function_calls else 1
        if max_branching >= 2:
            est_time = "O(2^N)"
            reason = "Tree recursion with multiple branches per stack frame without detected memoization."
        else:
            est_time = "O(N)" if nesting == 0 else f"O(N^{nesting + 1})"
            reason = "Linear recursion detected."
    elif nesting == 0:
        est_time = "O(1)"
        reason = "Constant time operations with no loops detected."
    elif nesting == 1:
        est_time = "O(N)"
        reason = "Single-level iteration over input."
    elif nesting == 2:
        est_time = "O(N^2)"
        reason = "Two nested loop levels detected (quadratic scaling)."
    else:
        est_time = f"O(N^{nesting})"
        reason = f"{nesting} levels of nested iteration detected."

    complexity = ComplexityEstimate(
        estimated_time=est_time,
        max_loop_nesting=nesting,
        recursion_detected=is_recursive,
        cyclomatic_complexity=comp_visitor.cyclomatic,
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

    # 4. Tree representation
    tree_hierarchy = ast_to_dict(tree)

    return ASTAnalysisResult(
        syntax_valid=True,
        complexity=complexity,
        anti_patterns=anti_visitor.reports,
        symbol_table=symbols,
        tree_hierarchy=tree_hierarchy
    )
