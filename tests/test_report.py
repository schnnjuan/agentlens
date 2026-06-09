from agentlens import generate_markdown_report, generate_report


class TestPlainTextReport:
    def test_empty_db(self, audit):
        text = generate_report(audit)
        assert "No agents found" in text
        assert "AGENTLENS" in text

    def test_shows_all_agents(self, seeded_audit):
        text = generate_report(seeded_audit)
        assert "billing" in text
        assert "support" in text
        assert "AUDIT REPORT" in text

    def test_filter_by_agent(self, seeded_audit):
        text = generate_report(seeded_audit, agent="billing")
        assert "billing" in text
        assert "support" not in text

    def test_shows_error_rate(self, seeded_audit):
        text = generate_report(seeded_audit)
        assert "50.0%" in text or "25.0%" in text

    def test_shows_last_events_table(self, seeded_audit):
        text = generate_report(seeded_audit)
        assert "Last" in text
        assert "fetch_invoices" in text
        assert "charge_card" in text
        assert "Timestamp" in text
        assert "Status" in text
        assert "Action" in text

    def test_single_agent_no_events(self, audit):
        text = generate_report(audit)
        assert "No agents found" in text

    def test_report_round_trip_clean(self, audit):
        audit.log("a", "act")
        text = generate_report(audit)
        assert text.endswith("=" * 60)

    def test_empty_string_agent_still_shows(self, audit):
        audit.log("", "act")
        text = generate_report(audit)
        assert "AGENT:" in text


class TestMarkdownReport:
    def test_empty_db_returns_header(self, audit):
        text = generate_markdown_report(audit)
        assert text.startswith("# ")
        assert "Audit Report" in text

    def test_shows_all_agents(self, seeded_audit):
        text = generate_markdown_report(seeded_audit)
        assert "billing" in text
        assert "support" in text

    def test_filter_by_agent(self, seeded_audit):
        text = generate_markdown_report(seeded_audit, agent="billing")
        assert "billing" in text
        assert "support" not in text

    def test_contains_metric_table(self, seeded_audit):
        text = generate_markdown_report(seeded_audit)
        assert "| Metric | Value |" in text
        assert "| Total actions |" in text

    def test_contains_recent_events_table(self, seeded_audit):
        text = generate_markdown_report(seeded_audit)
        assert "### Recent Events" in text
        assert "| Timestamp | Status | Action | Result |" in text
        assert "fetch_invoices" in text

    def test_shows_success_rate(self, seeded_audit):
        text = generate_markdown_report(seeded_audit)
        assert "%" in text
