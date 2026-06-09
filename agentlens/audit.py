"""
agentlens/audit.py
------------------
Core audit logging for AI agents. Zero external dependencies.
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager
from typing import Optional


class AuditLog:
    """
    A lightweight audit trail for AI agents.

    Usage:
        audit = AuditLog()
        audit.log("billing-agent", "charge_card", "charged $49.00", status="ok")
        print(audit.summary("billing-agent"))
    """

    def __init__(self, db_path: str = "agentlens.db"):
        self.db = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts       TEXT    NOT NULL,
                    agent    TEXT    NOT NULL,
                    action   TEXT    NOT NULL,
                    result   TEXT    DEFAULT '',
                    status   TEXT    DEFAULT 'ok',
                    metadata TEXT    DEFAULT ''
                )
            """)

    # ---------------------------------------------------------------
    # Write
    # ---------------------------------------------------------------

    def log(
        self,
        agent: str,
        action: str,
        result: str = "",
        status: str = "ok",
        metadata: str = "",
    ) -> int:
        """
        Record one action taken by an agent.

        Args:
            agent    : unique agent identifier  (e.g. "email-agent-v2")
            action   : what the agent did       (e.g. "send_email")
            result   : outcome or return value  (e.g. "sent to user@email.com")
            status   : "ok" | "error" | "warn"
            metadata : any extra JSON string you want to attach

        Returns:
            The row id of the inserted event.
        """
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO events (ts, agent, action, result, status, metadata) "
                "VALUES (?,?,?,?,?,?)",
                (datetime.utcnow().isoformat(), agent, action, result, status, metadata),
            )
            return cur.lastrowid

    # ---------------------------------------------------------------
    # Read
    # ---------------------------------------------------------------

    def history(self, agent: Optional[str] = None, limit: int = 100) -> list[dict]:
        """Return recent events, newest first."""
        with self._conn() as c:
            if agent:
                rows = c.execute(
                    "SELECT ts, agent, action, result, status, metadata "
                    "FROM events WHERE agent=? ORDER BY id DESC LIMIT ?",
                    (agent, limit),
                ).fetchall()
            else:
                rows = c.execute(
                    "SELECT ts, agent, action, result, status, metadata "
                    "FROM events ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        keys = ("ts", "agent", "action", "result", "status", "metadata")
        return [dict(zip(keys, r)) for r in rows]

    def summary(self, agent: str) -> dict:
        """Return a quick health summary for one agent."""
        with self._conn() as c:
            total  = c.execute("SELECT COUNT(*) FROM events WHERE agent=?", (agent,)).fetchone()[0]
            errors = c.execute(
                "SELECT COUNT(*) FROM events WHERE agent=? AND status='error'", (agent,)
            ).fetchone()[0]
            last_ts = c.execute(
                "SELECT ts FROM events WHERE agent=? ORDER BY id DESC LIMIT 1", (agent,)
            ).fetchone()

        return {
            "agent":        agent,
            "total_actions": total,
            "errors":        errors,
            "success_rate":  f"{(total - errors) / total * 100:.1f}%" if total else "0%",
            "last_seen":     last_ts[0] if last_ts else None,
        }

    def agents(self) -> list[str]:
        """List all agent IDs that have ever logged an event."""
        with self._conn() as c:
            rows = c.execute("SELECT DISTINCT agent FROM events").fetchall()
        return [r[0] for r in rows]

    def clear(self, agent: Optional[str] = None) -> int:
        """Delete logs. Pass agent name to delete only that agent. Returns rows deleted."""
        with self._conn() as c:
            if agent:
                cur = c.execute("DELETE FROM events WHERE agent=?", (agent,))
            else:
                cur = c.execute("DELETE FROM events")
            return cur.rowcount
