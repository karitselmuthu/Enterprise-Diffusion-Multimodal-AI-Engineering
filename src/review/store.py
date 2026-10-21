"""SQLite-backed, append-once decisions for incident review."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ReviewStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS reviews (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                status TEXT NOT NULL, analysis_json TEXT NOT NULL, decision_json TEXT
            )""")
            connection.execute("CREATE INDEX IF NOT EXISTS reviews_status_idx ON reviews(status, created_at)")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _decode(row: sqlite3.Row) -> dict:
        return {"id": row["id"], "created_at": row["created_at"], "updated_at": row["updated_at"],
                "status": row["status"], "analysis": json.loads(row["analysis_json"]),
                "decision": json.loads(row["decision_json"]) if row["decision_json"] else None}

    def create(self, analysis: dict) -> dict:
        identifier, now = uuid4().hex, _now()
        with self._connect() as connection:
            connection.execute("INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?)",
                               (identifier, now, now, "pending", json.dumps(analysis), None))
        return self.get(identifier)

    def get(self, identifier: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM reviews WHERE id = ?", (identifier,)).fetchone()
        return self._decode(row) if row else None

    def list(self, *, status: str = "pending", limit: int = 50) -> list[dict]:
        if status not in {"pending", "approved", "rejected"} or not 1 <= limit <= 100:
            raise ValueError("invalid status or limit")
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM reviews WHERE status = ? ORDER BY created_at ASC LIMIT ?",
                                      (status, limit)).fetchall()
        return [self._decode(row) for row in rows]

    def decide(self, identifier: str, *, status: str, reviewer: str, summary: str,
               recommendation: str, cited_sources: list[str]) -> dict:
        current = self.get(identifier)
        if current is None:
            raise KeyError(identifier)
        if current["status"] != "pending":
            raise RuntimeError("review is already decided")
        if status not in {"approved", "rejected"} or not reviewer.strip():
            raise ValueError("status must be approved or rejected and reviewer is required")
        available = {item["source"] for item in current["analysis"]["evidence"]}
        if not set(cited_sources) <= available:
            raise ValueError("all cited_sources must exist in the incident evidence")
        if status == "approved" and (not summary.strip() or not recommendation.strip() or not cited_sources):
            raise ValueError("approval requires summary, recommendation and cited evidence")
        if status == "rejected" and not summary.strip():
            raise ValueError("rejection requires a reason in summary")
        decision = {"reviewer": reviewer.strip(), "summary": summary.strip(),
                    "recommendation": recommendation.strip(), "cited_sources": sorted(set(cited_sources)),
                    "decided_at": _now()}
        with self._connect() as connection:
            cursor = connection.execute("UPDATE reviews SET status = ?, updated_at = ?, decision_json = ? "
                                        "WHERE id = ? AND status = 'pending'",
                                        (status, decision["decided_at"], json.dumps(decision), identifier))
            if cursor.rowcount != 1:
                raise RuntimeError("review was decided concurrently")
        return self.get(identifier)
