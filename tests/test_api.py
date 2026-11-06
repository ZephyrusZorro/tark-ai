"""
Integration Tests for TarkAI FastAPI Endpoints
Tests full HTTP request/response cycle using TestClient.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "TarkAI" in data["system"]


def test_api_curriculum_list():
    res = client.get("/api/curriculum")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    assert any(c["id"] == "two_sum_sorted" for c in data)


def test_api_analyze_code():
    res = client.post("/api/analyze", json={
        "code": "def solve(nums):\n    for i in nums:\n        for j in nums:\n            pass"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["syntax_valid"] is True
    assert data["complexity"]["estimated_time"] == "O(N^2)"
    assert data["complexity"]["halstead"] is not None
    assert data["mermaid_flowchart"] is not None


def test_api_run_challenge_pass():
    solution_code = """
def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    left = 0
    right = len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []
"""
    res = client.post("/api/run", json={
        "challenge_id": "two_sum_sorted",
        "code": solution_code
    })
    assert res.status_code == 200
    data = res.json()
    assert data["overall_passed"] is True
    assert data["passed_count"] == data["total_count"]
    assert len(data["test_results"]) >= 4
    assert data["spaced_repetition_update"] is not None
    assert data["spaced_repetition_update"]["box"] >= 1


def test_api_socratic_hint():
    res = client.post("/api/socratic-hint", json={
        "challenge_id": "two_sum_sorted",
        "code": "def two_sum_sorted(numbers, target): return []",
        "hint_level": 1
    })
    assert res.status_code == 200
    data = res.json()
    assert data["hint_level"] == 1
    assert "guidance" in data
    assert "question_to_ponder" in data


def test_api_leitner_cards():
    res = client.get("/api/leitner")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_api_stats():
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_attempts" in data
    assert "problems_solved" in data
