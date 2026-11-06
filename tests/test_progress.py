"""Progress must reflect the actual submission history."""
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from tempfile import TemporaryDirectory
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
import db


@pytest.fixture(autouse=True)
def isolated_store(monkeypatch):
    with TemporaryDirectory(prefix="tark-regression-", ignore_cleanup_errors=True) as directory:
        monkeypatch.setattr(db, "DB_PATH", Path(directory) / "progress.db")
        db.init_db()
        yield


def test_success_after_failure_marks_challenge_solved():
    db.record_submission("two_sum_sorted", "return []", False, 0, 5, 0.2)
    db.record_submission("two_sum_sorted", "correct", True, 5, 5, 0.8)
    assert db.get_solved_ids() == {"two_sum_sorted"}
    assert db.get_stats().problems_solved == 1
    with db.get_db() as conn:
        row = conn.execute("SELECT attempts, best_time_ms FROM solved_challenges").fetchone()
    assert (row["attempts"], row["best_time_ms"]) == (2, 0.8)


def test_repeated_success_counts_attempts_and_keeps_best_time():
    for elapsed in [0.8, 0.3, 0.6]:
        db.record_submission("two_sum_sorted", "correct", True, 5, 5, elapsed)
    with db.get_db() as conn:
        row = conn.execute("SELECT attempts, best_time_ms FROM solved_challenges").fetchone()
    assert (row["attempts"], row["best_time_ms"]) == (3, 0.3)


def test_existing_incorrect_progress_is_rebuilt_from_submission_history():
    db.record_submission("two_sum_sorted", "attempt", False, 0, 5, 0.2)
    db.record_submission("two_sum_sorted", "correct", True, 5, 5, 0.8)
    # This is the row left by the previous fail-then-pass bug.
    with db.get_db() as conn:
        conn.execute("UPDATE solved_challenges SET best_time_ms = NULL, attempts = 1")
    db.init_db()
    db.init_db()  # Repair must be safe to repeat on startup.
    assert db.get_solved_ids() == {"two_sum_sorted"}
    with db.get_db() as conn:
        row = conn.execute("SELECT attempts, best_time_ms FROM solved_challenges").fetchone()
    assert (row["attempts"], row["best_time_ms"]) == (2, 0.8)


@pytest.mark.parametrize("days, expected", [([0, 1, 2], 3), ([1, 2], 2), ([0, 2], 1), ([2], 0)])
def test_streak_counts_consecutive_practice_days(days, expected):
    today = datetime.now(timezone.utc).date()
    with db.get_db() as conn:
        for age in days:
            timestamp = str(today - timedelta(days=age)) + " 12:00:00"
            conn.execute("INSERT INTO submissions (challenge_id, code, passed, passed_count, total_count, execution_time_ms, created_at) VALUES ('two_sum_sorted', 'pass', 0, 0, 5, 0, ?)", (timestamp,))
    assert db.get_stats().streak_days == expected
