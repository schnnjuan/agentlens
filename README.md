# 🔍 agentlens

**Zero-dependency audit trail for AI agents.**

Most teams deploy AI agents with no idea what they're actually doing. When something goes wrong — a wrong email sent, a card charged twice, a GDPR violation — there's no record.

agentlens fixes that in 3 lines of code.

```python
from agentlens import AuditLog

audit = AuditLog()
audit.log("billing-agent", "charge_card", "charged $49 to user@example.com")
```

No setup. No cloud. No API key. Just a local SQLite file that knows everything your agents did.

---

## Why this exists

The [MCP protocol](https://modelcontextprotocol.io/) has no built-in audit layer. Frameworks like LangChain and AutoGen give you powerful agents — but no answer to "what did that agent do yesterday at 3pm?"

When the EU AI Act, LGPD, or your enterprise client's security team asks for a compliance report, you need this.

agentlens is the minimal, composable piece you bolt onto whatever agent stack you already have.

---

## Install

```bash
pip install agentlens
```

Or from source:

```bash
git clone https://github.com/schnnjuan/agentlens
cd agentlens
pip install -e .
```

---

## Quick start

```python
from agentlens import AuditLog, generate_report

audit = AuditLog()  # creates agentlens.db in current directory

# Log any action your agent takes
audit.log("email-agent",   "send_email",    "sent to ceo@company.com",     status="ok")
audit.log("email-agent",   "send_email",    "SMTP timeout — retry queued", status="error")
audit.log("billing-agent", "charge_card",   "charged $299",                status="ok")

# Get a summary
print(audit.summary("email-agent"))
# {'agent': 'email-agent', 'total_actions': 2, 'errors': 1, 'success_rate': '50.0%', 'last_seen': '...'}

# Print a full report
print(generate_report(audit))

# Or get Markdown (for Notion, GitHub Issues, etc.)
from agentlens import generate_markdown_report
print(generate_markdown_report(audit, agent="billing-agent"))
```

---

## API reference

### `AuditLog(db_path="agentlens.db")`

Creates (or opens) a SQLite audit database.

| Method | Description |
|--------|-------------|
| `log(agent, action, result, status, metadata)` | Record one agent action |
| `history(agent=None, limit=100)` | Return recent events as a list of dicts |
| `summary(agent)` | Return error rate and totals for one agent |
| `agents()` | List all agent IDs in the database |
| `clear(agent=None)` | Delete logs for one agent (or all) |

### `generate_report(audit, agent=None)`

Returns a plain-text report. Pass `agent` to filter to one agent.

### `generate_markdown_report(audit, agent=None)`

Same but in Markdown. Paste into Notion, GitHub Issues, or a Slack message.

---

## Works with everything

agentlens doesn't care what framework you use. Just add `.log()` wherever your agent takes an action:

```python
# LangChain
from langchain.agents import AgentExecutor
# ... your agent code ...
audit.log("research-agent", tool_name, tool_output)

# OpenAI function calls
response = openai.chat.completions.create(...)
audit.log("gpt-agent", response.choices[0].message.function_call.name, ...)

# AutoGen
# ... after each agent message ...
audit.log(agent.name, "send_message", message.content)

# Raw Claude API
audit.log("claude-agent", "tool_use", result)
```

---

## Roadmap

- [ ] CLI: `agentlens report --agent billing-agent`  
- [ ] TypeScript/Node.js port  
- [ ] Streaming export (CSV, JSON)  
- [ ] Webhook on error threshold  
- [ ] Cloud-hosted version (agentlens.dev)  

PRs welcome. This is intentionally minimal — contributions that keep it simple are favored over ones that add complexity.

---

## Contributing

```bash
git clone https://github.com/schnnjuan/agentlens
cd agentlens
python examples/quickstart.py  # should print a report and exit cleanly
```

There are no external dependencies and no build step. If `python examples/quickstart.py` works, your change is probably fine.

---

## License

MIT
