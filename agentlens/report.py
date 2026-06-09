"""
agentlens/report.py
-------------------
Generate human-readable audit reports from the log database.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .audit import AuditLog


def generate_report(audit: AuditLog, agent: str | None = None) -> str:
    """
    Generate a plain-text audit report for one agent (or all agents).

    Usage:
        audit = AuditLog()
        print(generate_report(audit, agent="email-agent"))
    """
    lines = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines.append("=" * 60)
    lines.append("  AGENTLENS — AUDIT REPORT")
    lines.append(f"  Generated: {now}")
    lines.append("=" * 60)

    agents = [agent] if agent else audit.agents()

    if not agents:
        lines.append("\n  No agents found in the log.\n")
        return "\n".join(lines)

    for ag in agents:
        summary = audit.summary(ag)
        history = audit.history(ag, limit=20)

        lines.append(f"\n  AGENT: {ag}")
        lines.append(f"  {'—' * 40}")
        lines.append(f"  Total actions : {summary['total_actions']}")
        lines.append(f"  Errors        : {summary['errors']}")
        lines.append(f"  Success rate  : {summary['success_rate']}")
        lines.append(f"  Last activity : {summary['last_seen'] or 'never'}")

        if history:
            lines.append(f"\n  Last {len(history)} events:")
            lines.append(f"  {'Timestamp':<26} {'Status':<8} {'Action':<25} Result")
            lines.append(f"  {'-' * 26} {'-' * 8} {'-' * 25} ------")
            for ev in history:
                ts = ev["ts"][:19]
                status = ev["status"].upper()
                action = ev["action"][:24]
                result = ev["result"][:50]
                lines.append(f"  {ts:<26} {status:<8} {action:<25} {result}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def generate_markdown_report(audit: AuditLog, agent: str | None = None) -> str:
    """Same as generate_report but in Markdown (useful for GitHub issues, Notion, etc.)"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    agents = [agent] if agent else audit.agents()
    lines = [f"# 🔍 AgentLens Audit Report\n_Generated: {now}_\n"]

    for ag in agents:
        summary = audit.summary(ag)
        history = audit.history(ag, limit=10)

        lines.append(f"## Agent: `{ag}`")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total actions | {summary['total_actions']} |")
        lines.append(f"| Errors | {summary['errors']} |")
        lines.append(f"| Success rate | {summary['success_rate']} |")
        lines.append(f"| Last seen | {summary['last_seen'] or 'never'} |")
        lines.append("")

        if history:
            lines.append("### Recent Events")
            lines.append("| Timestamp | Status | Action | Result |")
            lines.append("|-----------|--------|--------|--------|")
            for ev in history:
                lines.append(
                    f"| {ev['ts'][:19]} | {ev['status']} | {ev['action']} | {ev['result'][:60]} |"
                )
        lines.append("")

    return "\n".join(lines)
