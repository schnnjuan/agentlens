from agentlens import AuditLog


class TestLog:
    def test_returns_int_id(self, audit):
        id_ = audit.log("agent", "action")
        assert isinstance(id_, int)
        assert id_ > 0

    def test_stores_all_fields(self, audit):
        audit.log("a1", "act", "res", "error", '{"key":"val"}')
        (e,) = audit.history()
        assert e == {
            "ts": e["ts"],
            "agent": "a1",
            "action": "act",
            "result": "res",
            "status": "error",
            "metadata": '{"key":"val"}',
        }

    def test_default_status(self, audit):
        audit.log("a", "act")
        assert audit.history()[0]["status"] == "ok"

    def test_default_result_and_metadata(self, audit):
        audit.log("a", "act")
        e = audit.history()[0]
        assert e["result"] == ""
        assert e["metadata"] == ""

    def test_timestamp_iso8601(self, audit):
        audit.log("a", "act")
        ts = audit.history()[0]["ts"]
        assert "T" in ts
        parts = ts.split("T")
        assert len(parts) == 2
        assert len(parts[0]) == 10
        assert len(parts[1]) >= 8

    def test_unicode_content(self, audit):
        audit.log("agênte", "ação", "resultado: 100% concluído ✓")
        assert audit.history()[0]["result"] == "resultado: 100% concluído ✓"

    def test_long_strings(self, audit):
        long = "x" * 10000
        audit.log("a", action=long, result=long, metadata=long)
        e = audit.history()[0]
        assert e["action"] == long
        assert e["result"] == long
        assert e["metadata"] == long

    def test_special_chars_in_agent_name(self, audit):
        audit.log("billing-agent-v2.1", "act")
        assert "billing-agent-v2.1" in audit.agents()

    def test_multiple_logs_increment_id(self, audit):
        id1 = audit.log("a", "first")
        id2 = audit.log("a", "second")
        assert id2 > id1


class TestHistory:
    def test_newest_first(self, audit):
        audit.log("a", "first")
        audit.log("a", "second")
        audit.log("a", "third")
        assert [e["action"] for e in audit.history()] == ["third", "second", "first"]

    def test_filter_by_agent(self, audit):
        audit.log("a1", "act1")
        audit.log("a2", "act2")
        h = audit.history(agent="a1")
        assert len(h) == 1
        assert h[0]["agent"] == "a1"

    def test_limit(self, audit):
        for i in range(10):
            audit.log("a", f"act{i}")
        assert len(audit.history(limit=3)) == 3

    def test_limit_default_is_100(self, audit):
        for i in range(200):
            audit.log("a", f"act{i}")
        assert len(audit.history()) == 100

    def test_empty_db(self, audit):
        assert audit.history() == []

    def test_empty_for_nonexistent_agent(self, audit):
        audit.log("a1", "act")
        assert audit.history(agent="nonexistent") == []

    def test_agent_none_returns_all(self, audit):
        audit.log("a1", "act")
        audit.log("a2", "act")
        assert len(audit.history()) == 2

    def test_seeded_returns_agent_count(self, seeded_audit):
        assert len(seeded_audit.history()) == 4

    def test_seeded_filter(self, seeded_audit):
        h = seeded_audit.history(agent="billing")
        assert len(h) == 2
        assert all(e["agent"] == "billing" for e in h)


class TestSummary:
    def test_success_rate(self, audit):
        audit.log("a", "ok1", status="ok")
        audit.log("a", "ok2", status="ok")
        audit.log("a", "err", status="error")
        s = audit.summary("a")
        assert s["total_actions"] == 3
        assert s["errors"] == 1
        assert s["success_rate"] == "66.7%"

    def test_all_errors(self, audit):
        audit.log("a", "e1", status="error")
        audit.log("a", "e2", status="error")
        s = audit.summary("a")
        assert s["errors"] == 2
        assert s["success_rate"] == "0.0%"

    def test_no_events(self, audit):
        s = audit.summary("nonexistent")
        assert s["total_actions"] == 0
        assert s["errors"] == 0
        assert s["success_rate"] == "0%"
        assert s["last_seen"] is None

    def test_includes_agent_name(self, audit):
        audit.log("my-agent", "act")
        assert audit.summary("my-agent")["agent"] == "my-agent"

    def test_last_seen_is_iso(self, audit):
        audit.log("a", "act")
        s = audit.summary("a")
        assert s["last_seen"] is not None
        assert "T" in s["last_seen"]

    def test_zero_errors(self, audit):
        audit.log("a", "act", status="ok")
        s = audit.summary("a")
        assert s["errors"] == 0
        assert s["success_rate"] == "100.0%"

    def test_multiple_agents_isolated(self, audit):
        audit.log("a1", "act", status="ok")
        audit.log("a2", "act", status="error")
        assert audit.summary("a1")["errors"] == 0
        assert audit.summary("a2")["errors"] == 1


class TestAgents:
    def test_distinct(self, audit):
        audit.log("a1", "act")
        audit.log("a2", "act")
        audit.log("a1", "act")
        assert sorted(audit.agents()) == ["a1", "a2"]

    def test_empty_db(self, audit):
        assert audit.agents() == []

    def test_seeded(self, seeded_audit):
        assert sorted(seeded_audit.agents()) == ["billing", "support"]


class TestClear:
    def test_clear_all(self, audit):
        audit.log("a1", "act")
        audit.log("a2", "act")
        assert audit.clear() == 2
        assert audit.history() == []

    def test_clear_by_agent(self, audit):
        audit.log("a1", "act")
        audit.log("a2", "act")
        assert audit.clear(agent="a1") == 1
        assert len(audit.history()) == 1
        assert audit.history()[0]["agent"] == "a2"

    def test_clear_nonexistent(self, audit):
        audit.log("a1", "act")
        assert audit.clear(agent="nonexistent") == 0

    def test_clear_then_log(self, audit):
        audit.log("a", "before")
        audit.clear()
        audit.log("a", "after")
        assert len(audit.history()) == 1
        assert audit.history()[0]["action"] == "after"

    def test_clear_one_agent_keeps_others(self, seeded_audit):
        seeded_audit.clear(agent="billing")
        assert sorted(seeded_audit.agents()) == ["support"]


class TestEdgeCases:
    def test_empty_agent_name(self, audit):
        audit.log("", "act")
        assert "" in audit.agents()

    def test_role_em_agent_name(self, audit):
        audit.log("agente de cobrança", "processar")
        assert "agente de cobrança" in audit.agents()
        assert audit.summary("agente de cobrança")["total_actions"] == 1

    def test_mixed_statuses_in_history(self, audit):
        audit.log("a", "ok", status="ok")
        audit.log("a", "warn", status="warn")
        audit.log("a", "error", status="error")
        statuses = [e["status"] for e in audit.history()]
        assert statuses == ["error", "warn", "ok"]

    def test_log_with_only_required_args(self, audit):
        id_ = audit.log("agent", "action")
        assert id_ > 0
        e = audit.history()[0]
        assert e["agent"] == "agent"
        assert e["action"] == "action"
        assert e["result"] == ""
        assert e["status"] == "ok"
        assert e["metadata"] == ""

    def test_timestamps_monotonic(self, audit):
        audit.log("a", "first")
        audit.log("a", "second")
        h = audit.history()
        assert h[0]["ts"] >= h[1]["ts"]


class TestMultipleInstances:
    def test_isolated_databases(self, tmp_path):
        db1 = str(tmp_path / "team_a.db")
        db2 = str(tmp_path / "team_b.db")
        a1 = AuditLog(db1)
        a2 = AuditLog(db2)
        a1.log("agent-x", "act")
        a2.log("agent-y", "act")
        assert a1.agents() == ["agent-x"]
        assert a2.agents() == ["agent-y"]

    def test_reopened_database_persists(self, tmp_path):
        db = str(tmp_path / "persist.db")
        AuditLog(db).log("a", "first")
        AuditLog(db).log("a", "second")
        log = AuditLog(db)
        assert len(log.history()) == 2
