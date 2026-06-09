"""
examples/quickstart.py
----------------------
A realistic simulation: a billing agent processes invoices.
Run: python examples/quickstart.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agentlens import AuditLog, generate_report

# ------------------------------------------------------------------ #
#  Imagine this is your real AI agent doing real work.                #
#  You just add audit.log(...) wherever the agent takes an action.   #
# ------------------------------------------------------------------ #

audit = AuditLog("demo.db")

# Simulate a billing agent running
audit.log("billing-agent", "fetch_invoices", "found 3 overdue invoices")
audit.log("billing-agent", "send_reminder", "emailed client@acme.com", status="ok")
audit.log("billing-agent", "send_reminder", "emailed client@beta.com", status="ok")
audit.log("billing-agent", "charge_card", "charged $299 — card declined", status="error")
audit.log("billing-agent", "notify_human", "flagged for manual review", status="ok")

# Simulate a second agent
audit.log("support-agent", "read_ticket", "ticket #1042 from user João")
audit.log("support-agent", "classify_intent", "intent=refund, confidence=0.91")
audit.log("support-agent", "draft_reply", "draft ready, pending approval")

# ------------------------------------------------------------------ #
#  Now generate a report — this is what you send to your client       #
#  or attach to a compliance audit.                                   #
# ------------------------------------------------------------------ #

print(generate_report(audit))

# Clean up demo db
os.remove("demo.db")
