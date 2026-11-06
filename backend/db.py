"""
TarkAI — Local SQLite Persistence Layer
Stores code submissions, execution metrics, solved problem history,
and student weakness records locally.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Set
from models import UserStats


DB_PATH = Path(__file__).parent / "tark_data.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables on startup."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id TEXT NOT NULL,
                code TEXT NOT NULL,
                passed INTEGER NOT NULL,
                passed_count INTEGER NOT NULL,
                total_count INTEGER NOT NULL,
                execution_time_ms REAL NOT NULL,
                complexity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS solved_challenges (
                challenge_id TEXT PRIMARY KEY,
                solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempts INTEGER DEFAULT 1,
                best_time_ms REAL
            )
        """)
        conn.commit()

# Ensure database is initialized on import
init_db()


def record_submission(
    challenge_id: str,
    code: str,
    passed: bool,
    passed_count: int,
    total_count: int,
    execution_time_ms: float,
    complexity: str = "O(N)"
) -> None:
    """Logs submission and updates solved problem status."""
    with get_db() as conn:
        conn.execute("""
            INSERT INTO submissions (challenge_id, code, passed, passed_count, total_count, execution_time_ms, complexity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (challenge_id, code, 1 if passed else 0, passed_count, total_count, execution_time_ms, complexity))

        if passed:
            conn.execute("""
                INSERT INTO solved_challenges (challenge_id, solved_at, attempts, best_time_ms)
                VALUES (?, CURRENT_TIMESTAMP, 1, ?)
                ON CONFLICT(challenge_id) DO UPDATE SET
                    best_time_ms = MIN(best_time_ms, excluded.best_time_ms)
            """, (challenge_id, execution_time_ms))
        else:
            conn.execute("""
                INSERT INTO solved_challenges (challenge_id, attempts, best_time_ms)
                VALUES (?, 1, NULL)
                ON CONFLICT(challenge_id) DO UPDATE SET
                    attempts = attempts + 1
            """, (challenge_id,))
        conn.commit()


def get_solved_ids() -> Set[str]:
    """Returns set of challenge IDs that have been solved."""
    with get_db() as conn:
        rows = conn.execute("SELECT challenge_id FROM solved_challenges WHERE best_time_ms IS NOT NULL").fetchall()
        return {r["challenge_id"] for r in rows}


def get_stats() -> UserStats:
    """Computes aggregate user metrics."""
    with get_db() as conn:
        total_sub = conn.execute("SELECT COUNT(*) as cnt FROM submissions").fetchone()["cnt"]
        solved_sub = conn.execute("SELECT COUNT(*) as cnt FROM solved_challenges WHERE best_time_ms IS NOT NULL").fetchone()["cnt"]

        rows = conn.execute("SELECT complexity, COUNT(*) as cnt FROM submissions GROUP BY complexity").fetchall()
        top_complexity = rows[0]["complexity"] if rows else "O(N)"

    return UserStats(
        total_attempts=total_sub,
        problems_solved=solved_sub,
        streak_days=1 if solved_sub > 0 else 0,
        average_complexity=top_complexity,
        top_anti_patterns=[]
    )
