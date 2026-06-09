from agentlens import AuditLog


def test_log_and_history(audit):
    audit.log("billing", "charge_card", "charged $99", status="ok")
    audit.log("billing", "charge_card", "card declined", status="error")
    h = audit.history()
    assert len(h) == 2
    assert h[0]["status"] == "error"
    assert h[0]["agent"] == "billing"


def test_history_filter_by_agent(audit):
    audit.log("support", "read_ticket", "ticket #1")
    audit.log("billing", "charge_card", "charged $99")
    h = audit.history(agent="billing")
    assert len(h) == 1
    assert h[0]["agent"] == "billing"


def test_history_limit(audit):
    for i in range(10):
        audit.log("a", f"act{i}")
    assert len(audit.history(limit=3)) == 3


def test_history_empty_db(audit):
    assert audit.history() == []


def test_summary(audit):
    audit.log("a", "ok1", status="ok")
    audit.log("a", "ok2", status="ok")
    audit.log("a", "err", status="error")
    s = audit.summary("a")
    assert s["total_actions"] == 3
    assert s["errors"] == 1
    assert s["success_rate"] == "66.7%"
    assert s["agent"] == "a"
    assert "T" in s["last_seen"]


def test_summary_no_events(audit):
    s = audit.summary("nonexistent")
    assert s["total_actions"] == 0
    assert s["errors"] == 0
    assert s["last_seen"] is None


def test_agents(audit):
    audit.log("a1", "act")
    audit.log("a2", "act")
    assert sorted(audit.agents()) == ["a1", "a2"]


def test_agents_empty_db(audit):
    assert audit.agents() == []


def test_clear_all(audit):
    audit.log("a1", "act")
    audit.log("a2", "act")
    assert audit.clear() == 2
    assert audit.history() == []


def test_clear_by_agent(audit):
    audit.log("a1", "act")
    audit.log("a2", "act")
    assert audit.clear(agent="a1") == 1
    assert len(audit.history()) == 1


def test_log_defaults(audit):
    aid = audit.log("agent", "action")
    assert isinstance(aid, int)
    e = audit.history()[0]
    assert e["result"] == ""
    assert e["status"] == "ok"
    assert e["metadata"] == ""


def test_persistence(tmp_path):
    db = str(tmp_path / "persist.db")
    AuditLog(db).log("a", "first")
    AuditLog(db).log("a", "second")
    assert len(AuditLog(db).history()) == 2


def test_unicode(audit):
    audit.log("agente", "ação", "100% concluído ✓")
    assert audit.history()[0]["result"] == "100% concluído ✓"
