"""
TarkAI (तर्क) — Control Flow Graph (CFG) & Basic Block Decomposer
Inspired by compiler intermediate representations (IR) and academic tools (Scalpel, staticfg).
Decomposes Python AST into formal basic blocks, computes edge transitions,
detects unreachable code paths, and evaluates graph cyclomatic complexity (E - V + 2P).
"""

import ast
from typing import List, Dict, Any, Optional, Set, Tuple
from models import BasicBlock, CFGEdge, CFGAnalysisResult


class CFGBuilder(ast.NodeVisitor):
    """Builds basic blocks and directed control-flow edges from a Python AST."""

    def __init__(self, source_code: str):
        self.lines = source_code.splitlines()
        self.blocks: Dict[str, BasicBlock] = {}
        self.edges: List[CFGEdge] = []
        self.block_counter = 0
        self.current_block_id: Optional[str] = None

    def _new_block_id(self, prefix: str = "B") -> str:
        bid = f"{prefix}{self.block_counter}"
        self.block_counter += 1
        return bid

    def _create_block(self, b_id: str, b_type: str, start_line: int = 1, end_line: int = 1) -> BasicBlock:
        block = BasicBlock(
            id=b_id,
            block_type=b_type,
            start_line=start_line,
            end_line=end_line,
            statements=[],
            predecessors=[],
            successors=[]
        )
        self.blocks[b_id] = block
        return block

    def _add_edge(self, src: str, dst: str, cond: Optional[str] = None):
        if src in self.blocks and dst not in self.blocks[src].successors:
            self.blocks[src].successors.append(dst)
        if dst in self.blocks and src not in self.blocks[dst].predecessors:
            self.blocks[dst].predecessors.append(src)
        self.edges.append(CFGEdge(source=src, target=dst, condition=cond))

    def build(self, tree: ast.AST) -> CFGAnalysisResult:
        entry_id = self._new_block_id("ENTRY_")
        entry_block = self._create_block(entry_id, "ENTRY", 1, 1)
        entry_block.statements.append("Entry point")

        self.current_block_id = entry_id

        # Walk through top-level nodes or functions
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._process_function(node)
            else:
                self._process_statement(node)

        # Mark reachability using BFS from entry
        reachable = set()
        queue = [entry_id]
        while queue:
            curr = queue.pop(0)
            if curr not in reachable and curr in self.blocks:
                reachable.add(curr)
                queue.extend(self.blocks[curr].successors)

        unreachable = []
        for b_id, block in self.blocks.items():
            block.is_reachable = b_id in reachable
            if not block.is_reachable:
                unreachable.append(b_id)

        # Add terminal exit node and connect dangling blocks
        exit_id = self._new_block_id("EXIT_")
        self._create_block(exit_id, "EXIT", len(self.lines) or 1, len(self.lines) or 1)
        for b_id, block in list(self.blocks.items()):
            if b_id != exit_id and len(block.successors) == 0:
                self._add_edge(b_id, exit_id, "Exit")

        # Calculate Cyclomatic Complexity: Decisions + 1
        decisions = sum(1 for b in self.blocks.values() if b.block_type in ("BRANCH", "LOOP_HEADER"))
        cyclomatic = max(1, decisions + 1)
        v_count = len(self.blocks)
        e_count = len(self.edges)

        # Build clean Mermaid CFG representation
        mermaid_code = self._generate_mermaid()

        return CFGAnalysisResult(
            total_blocks=v_count,
            total_edges=e_count,
            cyclomatic_complexity=cyclomatic,
            unreachable_blocks=unreachable,
            blocks=list(self.blocks.values()),
            edges=self.edges,
            mermaid_cfg=mermaid_code
        )

    def _process_function(self, node: ast.FunctionDef):
        fn_block_id = self._new_block_id(f"FN_{node.name}_")
        self._create_block(fn_block_id, "ENTRY", node.lineno, node.lineno)
        self.blocks[fn_block_id].statements.append(f"def {node.name}()")

        if self.current_block_id:
            self._add_edge(self.current_block_id, fn_block_id, "Call")

        prev_block = self.current_block_id
        self.current_block_id = fn_block_id

        for stmt in node.body:
            self._process_statement(stmt)

        self.current_block_id = prev_block

    def _process_statement(self, stmt: ast.AST):
        if not self.current_block_id:
            return

        lineno = getattr(stmt, "lineno", 1)
        end_lineno = getattr(stmt, "end_lineno", lineno)
        code_slice = self.lines[lineno - 1].strip() if lineno <= len(self.lines) else "stmt"

        if isinstance(stmt, ast.If):
            # Conditional Branch Block
            cond_id = self._new_block_id("BRANCH_")
            cond_block = self._create_block(cond_id, "BRANCH", lineno, lineno)
            cond_block.statements.append(f"if: {code_slice}")
            self._add_edge(self.current_block_id, cond_id, "Fallthrough")

            # Then branch
            then_id = self._new_block_id("THEN_")
            self._create_block(then_id, "STATEMENT", lineno + 1, lineno + 1)
            self._add_edge(cond_id, then_id, "True")
            self.current_block_id = then_id
            for s in stmt.body:
                self._process_statement(s)
            then_end = self.current_block_id

            # Else branch
            else_end = None
            if stmt.orelse:
                else_id = self._new_block_id("ELSE_")
                self._create_block(else_id, "STATEMENT", lineno + 1, lineno + 1)
                self._add_edge(cond_id, else_id, "False")
                self.current_block_id = else_id
                for s in stmt.orelse:
                    self._process_statement(s)
                else_end = self.current_block_id

            # Merge join block
            join_id = self._new_block_id("JOIN_")
            self._create_block(join_id, "STATEMENT", end_lineno, end_lineno)
            if then_end:
                self._add_edge(then_end, join_id, "Merge")
            if else_end:
                self._add_edge(else_end, join_id, "Merge")
            elif not stmt.orelse:
                self._add_edge(cond_id, join_id, "False")

            self.current_block_id = join_id

        elif isinstance(stmt, (ast.For, ast.While)):
            # Loop Header Block
            loop_id = self._new_block_id("LOOP_HDR_")
            loop_block = self._create_block(loop_id, "LOOP_HEADER", lineno, lineno)
            loop_block.statements.append(f"loop: {code_slice}")
            self._add_edge(self.current_block_id, loop_id, "Enter")

            # Loop Body
            body_id = self._new_block_id("LOOP_BODY_")
            self._create_block(body_id, "STATEMENT", lineno + 1, lineno + 1)
            self._add_edge(loop_id, body_id, "Next Item")
            self.current_block_id = body_id

            for s in stmt.body:
                self._process_statement(s)

            # Loop back edge
            if self.current_block_id:
                self._add_edge(self.current_block_id, loop_id, "Loopback")

            # Exit Block
            exit_id = self._new_block_id("LOOP_EXIT_")
            self._create_block(exit_id, "STATEMENT", end_lineno, end_lineno)
            self._add_edge(loop_id, exit_id, "Break / Done")
            self.current_block_id = exit_id

        elif isinstance(stmt, ast.Return):
            ret_id = self._new_block_id("RET_")
            ret_block = self._create_block(ret_id, "TERMINAL", lineno, lineno)
            ret_block.statements.append(f"return: {code_slice}")
            self._add_edge(self.current_block_id, ret_id, "Return")
            # Terminal block has no fallthrough
            self.current_block_id = None

        else:
            # Normal sequential statement
            curr = self.blocks.get(self.current_block_id)
            if curr:
                curr.statements.append(code_slice[:40])
                curr.end_line = end_lineno

    def _generate_mermaid(self) -> str:
        lines = ["flowchart TD"]
        for b_id, b in self.blocks.items():
            raw_label = " | ".join(b.statements[:2]) if b.statements else b.id
            # Clean and escape characters so Mermaid parser never crashes on operators (<, >, quotes)
            clean_label = (
                raw_label.replace('&', '&amp;')
                         .replace('<', '&lt;')
                         .replace('>', '&gt;')
                         .replace('"', '#quot;')
                         .replace("'", '#39;')
                         .replace('{', '(')
                         .replace('}', ')')
                         .replace('[', '(')
                         .replace(']', ')')
                         .replace('\\', '/')
            )
            clean_label = " ".join(clean_label.split())[:50]

            if b.block_type in ("BRANCH", "LOOP_HEADER"):
                lines.append(f'  {b_id}{{"{b_id}: {clean_label}"}}')
            elif b.block_type in ("TERMINAL", "EXIT"):
                lines.append(f'  {b_id}(["{b_id}: {clean_label}"])')
            else:
                lines.append(f'  {b_id}["{b_id}: {clean_label}"]')

        for edge in self.edges:
            cond = edge.condition
            if cond:
                safe_cond = cond.replace('"', '').replace("'", "").replace("<", "&lt;").replace(">", "&gt;")
                lines.append(f'  {edge.source} -->|"{safe_cond}"| {edge.target}')
            else:
                lines.append(f'  {edge.source} --> {edge.target}')

        return "\n".join(lines)


def generate_control_flow_graph(code: str) -> CFGAnalysisResult:
    """Parses code and constructs a complete Control Flow Graph."""
    try:
        tree = ast.parse(code)
        builder = CFGBuilder(code)
        return builder.build(tree)
    except Exception as e:
        # Fallback on syntax error
        return CFGAnalysisResult(
            total_blocks=0,
            total_edges=0,
            cyclomatic_complexity=0,
            unreachable_blocks=[],
            blocks=[],
            edges=[],
            mermaid_cfg=f"flowchart TD\n  ERR[\"Syntax error in CFG generation: {str(e)[:40]}\"]"
        )
