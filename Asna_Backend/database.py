"""SQLite Database Module for Logging Prompt Inspection Requests.

Developer: Asna
Module: Backend Database & Auditing
"""

import sqlite3
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firewall_logs.db")


def get_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory configured."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the prompt_logs table if it does not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                prompt TEXT NOT NULL,
                decision TEXT NOT NULL,
                is_blocked INTEGER NOT NULL,
                reason TEXT,
                severity TEXT NOT NULL,
                risk_score REAL NOT NULL,
                latency_ms REAL NOT NULL
            )
        """)
        conn.commit()


def log_request(
    prompt: str,
    decision: str,
    is_blocked: bool,
    reason: Optional[str],
    severity: str,
    risk_score: float,
    latency_ms: float
) -> int:
    """Inserts a new prompt inspection event into the database."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prompt_logs 
            (timestamp, prompt, decision, is_blocked, reason, severity, risk_score, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_iso,
            prompt,
            decision,
            1 if is_blocked else 0,
            reason,
            severity,
            float(risk_score),
            float(latency_ms)
        ))
        conn.commit()
        return cursor.lastrowid


def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves recent prompt inspection logs ordered by latest first."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, prompt, decision, is_blocked, reason, severity, risk_score, latency_ms
            FROM prompt_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# Auto-initialize table on import
init_db()
