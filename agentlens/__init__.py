"""
agentlens
~~~~~~~~~
A zero-dependency audit trail for AI agents.

Quick start:
    from agentlens import AuditLog
    audit = AuditLog()
    audit.log("my-agent", "send_email", "sent to user@example.com")
    print(audit.summary("my-agent"))
"""

from .audit  import AuditLog
from .report import generate_report, generate_markdown_report

__version__ = "0.1.0"
__all__     = ["AuditLog", "generate_report", "generate_markdown_report"]
