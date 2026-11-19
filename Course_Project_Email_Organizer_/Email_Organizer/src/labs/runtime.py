"""Lab 6: OpenClaw-style local runtime, execution trace and tool policy.

This is a local, transparent runtime inspired by agent-runtime concepts; it is
not the OpenClaw product or an MCP server.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

@dataclass
class RuntimeEvent:
    timestamp: str
    step: str
    status: str
    detail: str

@dataclass
class AgentRuntime:
    name: str = "EmailOrganizerRuntime"
    events: list = field(default_factory=list)

    def record(self, step: str, status: str, detail: str = ""):
        self.events.append(RuntimeEvent(
            datetime.now(timezone.utc).isoformat(), step, status, detail
        ).__dict__)

    def execute(self, step: str, action: Callable, *args, **kwargs):
        self.record(step, "STARTED")
        try:
            result = action(*args, **kwargs)
            self.record(step, "SUCCESS")
            return result
        except Exception as exc:
            self.record(step, "FAILED", f"{type(exc).__name__}: {exc}")
            raise

    def audit_report(self):
        return {"runtime": self.name, "event_count": len(self.events),
                "events": list(self.events)}
