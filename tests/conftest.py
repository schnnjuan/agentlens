import pytest

from agentlens import AuditLog


@pytest.fixture
def audit(tmp_path):
    db = str(tmp_path / "test.db")
    return AuditLog(db)


@pytest.fixture
def seeded_audit(audit):
    audit.log("billing", "fetch_invoices", "found 3 overdue", status="ok")
    audit.log("billing", "charge_card", "card declined", status="error")
    audit.log("support", "read_ticket", "ticket #1042", status="ok")
    audit.log("support", "classify_intent", "intent=refund", status="ok")
    return audit
