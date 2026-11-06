"""
TarkAI — Local SQLite Persistence Layer
Stores code submissions, execution telemetry, solved challenge state,
and Leitner spaced repetition review schedules.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Set, Optional
from models import UserStats, SpacedRepetitionCard


DB_PATH = Path(__file__).parent / "tark_data.db"

INTERVAL_MAP = {
    1: 1,    # Box 1: review daily
    2: 3,    # Box 2: review every 3 days
    3: 7,    # Box 3: review every 7 days
    4: 14,   # Box 4: review every 14 days
    5: 30    # Box 5: review every 30 days (mastered)
}


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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leitner_cards (
                challenge_id TEXT PRIMARY KEY,
                box INTEGER DEFAULT 1,
                interval_days INTEGER DEFAULT 1,
                next_due TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                failures INTEGER DEFAULT 0,
                last_reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


# Ensure database is initialized on import
init_db()


def update_leitner_card(challenge_id: str, passed: bool) -> Dict[str, Any]:
    """Updates Leitner spaced repetition interval for a challenge."""
    now = datetime.now(timezone.utc)
    with get_db() as conn:
        row = conn.execute(
            "SELECT box, interval_days, attempts, failures FROM leitner_cards WHERE challenge_id = ?",
            (challenge_id,)
        ).fetchone()

        if row is None:
            new_box = 2 if passed else 1
            interval = INTERVAL_MAP[new_box]
            next_due = now + timedelta(days=interval)
            conn.execute("""
                INSERT INTO leitner_cards (challenge_id, box, interval_days, next_due, attempts, failures, last_reviewed_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (challenge_id, new_box, interval, next_due.isoformat(), 0 if passed else 1, now.isoformat()))
        else:
            current_box = row["box"]
            attempts = row["attempts"] + 1
            failures = row["failures"] + (0 if passed else 1)

            if passed:
                new_box = min(5, current_box + 1)
            else:
                new_box = 1  # Reset on failure to reinforce recall

            interval = INTERVAL_MAP[new_box]
            next_due = now + timedelta(days=interval)
            conn.execute("""
                UPDATE leitner_cards
                SET box = ?, interval_days = ?, next_due = ?, attempts = ?, failures = ?, last_reviewed_at = ?
                WHERE challenge_id = ?
            """, (new_box, interval, next_due.isoformat(), attempts, failures, now.isoformat(), challenge_id))

        conn.commit()

        return {
            "challenge_id": challenge_id,
            "box": new_box,
            "interval_days": interval,
            "next_due": next_due.isoformat(),
            "passed": passed
        }


def get_all_leitner_cards() -> List[Dict[str, Any]]:
    """Retrieves all spaced repetition cards with due status."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        rows = conn.execute("""
            SELECT challenge_id, box, interval_days, next_due, attempts, failures, last_reviewed_at,
                   (next_due <= ?) as is_due
            FROM leitner_cards
            ORDER BY box ASC, next_due ASC
        """, (now_iso,)).fetchall()

        return [dict(r) for r in rows]


def record_submission(
    challenge_id: str,
    code: str,
    passed: bool,
    passed_count: int,
    total_count: int,
    execution_time_ms: float,
    complexity: str = "O(N)"
) -> Dict[str, Any]:
    """Logs submission, updates solved problem status, and advances Leitner schedule."""
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

    leitner_info = update_leitner_card(challenge_id, passed)
    return leitner_info


def get_solved_ids() -> Set[str]:
    """Returns set of challenge IDs that have been solved."""
    with get_db() as conn:
        rows = conn.execute("SELECT challenge_id FROM solved_challenges WHERE best_time_ms IS NOT NULL").fetchall()
        return {r["challenge_id"] for r in rows}


def get_stats() -> UserStats:
    """Computes aggregate user metrics, lines analyzed, and Leitner mastery."""
    with get_db() as conn:
        total_sub = conn.execute("SELECT COUNT(*) as cnt FROM submissions").fetchone()["cnt"]
        solved_sub = conn.execute("SELECT COUNT(*) as cnt FROM solved_challenges WHERE best_time_ms IS NOT NULL").fetchone()["cnt"]

        rows = conn.execute("SELECT complexity, COUNT(*) as cnt FROM submissions GROUP BY complexity ORDER BY cnt DESC").fetchall()
        top_complexity = rows[0]["complexity"] if rows else "O(1)"

        # Calculate estimated lines of code submitted
        sub_codes = conn.execute("SELECT code FROM submissions").fetchall()
        total_lines = sum(len(r["code"].splitlines()) for r in sub_codes)

        # Leitner breakdown by box
        leitner_breakdown = {f"box_{i}": 0 for i in range(1, 6)}
        l_rows = conn.execute("SELECT box, COUNT(*) as cnt FROM leitner_cards GROUP BY box").fetchall()
        for lr in l_rows:
            key = f"box_{lr['box']}"
            if key in leitner_breakdown:
                leitner_breakdown[key] = lr["cnt"]

        # Weakness matrix (challenges with highest failure counts)
        weak_rows = conn.execute("""
            SELECT challenge_id, COUNT(*) as fail_count
            FROM submissions
            WHERE passed = 0
            GROUP BY challenge_id
            ORDER BY fail_count DESC
            LIMIT 5
        """).fetchall()
        weakness_matrix = [{"challenge_id": w["challenge_id"], "failures": w["fail_count"]} for w in weak_rows]

    mastery_pct = round((solved_sub / 10.0) * 100.0, 1)

    return UserStats(
        total_attempts=total_sub,
        problems_solved=solved_sub,
        mastery_percentage=mastery_pct,
        streak_days=1 if solved_sub > 0 else 0,
        average_complexity=top_complexity,
        total_loc_analyzed=total_lines,
        leitner_breakdown=leitner_breakdown,
        weakness_matrix=weakness_matrix
    )
