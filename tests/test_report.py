from agentlens import generate_markdown_report, generate_report


def test_plain_text_empty(audit):
    assert "No agents found" in generate_report(audit)


def test_plain_text_shows_agents(audit):
    audit.log("billing", "act")
    audit.log("support", "act")
    text = generate_report(audit)
    assert "billing" in text
    assert "support" in text


def test_plain_text_filter(audit):
    audit.log("billing", "act")
    audit.log("support", "act")
    text = generate_report(audit, agent="billing")
    assert "billing" in text
    assert "support" not in text


def test_markdown_format(audit):
    audit.log("billing", "charge_card")
    text = generate_markdown_report(audit)
    assert text.startswith("# ")
    assert "| Metric | Value |" in text


def test_markdown_filter(audit):
    audit.log("billing", "act")
    audit.log("support", "act")
    text = generate_markdown_report(audit, agent="billing")
    assert "billing" in text
    assert "support" not in text
