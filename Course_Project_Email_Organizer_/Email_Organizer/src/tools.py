
from typing import Callable, Dict, Any, List

from .storage import MemoryStore


class ToolRegistry:
    """Central registry for email and memory tools."""

    def __init__(self, connector, memory: MemoryStore):
        self.connector = connector
        self.memory = memory

        self.tools: Dict[str, Callable] = {
            "list_emails": self.connector.list_emails,
            "get_email": self.connector.get_email,
            "save_draft": self._save_draft,
            "search_memory": self._search_memory,
            "save_memory": self._save_memory,
            "sync_calendar_task": self._sync_calendar_task,
            "archive_email": self._archive_email,
            "reject_draft": self._reject_draft
        }

    def call(self, name: str, **kwargs) -> Any:

        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")

        print(f"\n[TOOL EXECUTED] {name}")

        return self.tools[name](**kwargs)

    def describe(self) -> List[Dict[str, Any]]:

        return [
            {
                "name": "list_emails",
                "description": "List emails from the connector."
            },
            {
                "name": "get_email",
                "description": "Retrieve an email using its ID."
            },
            {
                "name": "save_draft",
                "description": "Save a reply draft for human approval."
            },
            {
                "name": "search_memory",
                "description": "Search emails and saved memory notes."
            },
            {
                "name": "save_memory",
                "description": "Store a persistent memory note."
            },
            {
                "name": "sync_calendar_task",
                "description": "Save an extracted action item as a planned calendar/task item."
            },
            {
                "name": "archive_email",
                "description": "Record an archive decision in the audit log."
            },
            {
                "name": "reject_draft",
                "description": "Reject a pending draft and retain the human review reason."
            }
        ]

    def _save_draft(self, draft: dict):

        self.memory.save_draft(draft)

        return {
            "status": "saved",
            "approval_required": True,
            "draft": draft
        }

    def _search_memory(
        self,
        query: str,
        limit: int = 5
    ):

        return self.memory.search(
            query,
            limit=limit
        )

    def _save_memory(self, key: str, value: str):

        return self.memory.save_memory(
            key,
            value
        )

    def _sync_calendar_task(
        self,
        email_id: str,
        task: str,
        due_date: str = ""
    ):
        return self.memory.save_calendar_task(email_id, task, due_date)

    def _archive_email(self, email_id: str, reason: str = ""):
        return self.memory.archive_email(email_id, reason)

    def _reject_draft(self, draft_id: int, reason: str):
        return self.memory.reject_draft(draft_id, reason)
