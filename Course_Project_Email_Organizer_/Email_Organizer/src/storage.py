
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "email_memory.db"
)


class MemoryStore:
    """Persistent email analysis, drafts and memory retrieval."""

    def __init__(self, db_path: Path = DB_PATH):

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        self._create_tables()

    def _create_tables(self):

        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            sender TEXT,
            subject TEXT,
            body TEXT,
            received_at TEXT,
            category TEXT,
            priority TEXT,
            urgency_score INTEGER,
            action_items TEXT,
            follow_up_date TEXT,
            reply_required INTEGER,
            reason TEXT
        );

        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            recipient TEXT,
            subject TEXT,
            body TEXT,
            status TEXT,
            review_note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS memory_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS calendar_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            task TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'PLANNED',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS archive_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            action TEXT,
            reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        draft_columns = {
            row["name"] for row in self.conn.execute("PRAGMA table_info(drafts)")
        }
        if "review_note" not in draft_columns:
            self.conn.execute("ALTER TABLE drafts ADD COLUMN review_note TEXT")

        self.conn.commit()

    def save_analysis(
        self,
        email: Dict[str, Any],
        analysis: Dict[str, Any]
    ):

        self.conn.execute("""
        INSERT OR REPLACE INTO emails
        (id, sender, subject, body, received_at, category, priority,
         urgency_score, action_items, follow_up_date, reply_required, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email["id"],
            email["sender"],
            email["subject"],
            email["body"],
            email["received_at"],
            analysis["category"],
            analysis["priority"],
            analysis["urgency_score"],
            json.dumps(analysis["action_items"]),
            analysis.get("follow_up_date"),
            int(analysis["reply_required"]),
            analysis.get("reason", "")
        ))

        self.conn.commit()

    def save_draft(self, draft: Dict[str, Any]):

        self.conn.execute("""
        INSERT INTO drafts
        (email_id, recipient, subject, body, status)
        VALUES (?, ?, ?, ?, ?)
        """, (
            draft["email_id"],
            draft["to"],
            draft["subject"],
            draft["body"],
            draft.get("status", "PENDING_APPROVAL")
        ))

        self.conn.commit()

        return {
            "status": "saved",
            "email_id": draft["email_id"]
        }

    def save_memory(self, key: str, value: str):

        self.conn.execute(
            "INSERT INTO memory_notes (key, value) VALUES (?, ?)",
            (key, value)
        )

        self.conn.commit()

        return {
            "key": key,
            "value": value,
            "status": "saved"
        }

    def search(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search analysed emails and saved memory notes."""

        terms = [
            term.lower()
            for term in query.split()
            if len(term) >= 3
        ]

        if not terms or limit <= 0:
            return []

        # Search analysed emails
        email_clauses = []
        email_params = []

        for term in terms:

            email_clauses.append("""
                (
                    LOWER(subject) LIKE ?
                    OR LOWER(body) LIKE ?
                    OR LOWER(sender) LIKE ?
                )
            """)

            like = f"%{term}%"
            email_params.extend([like, like, like])

        email_sql = f"""
        SELECT id, sender, subject, body, received_at, category,
               priority, urgency_score, action_items, follow_up_date,
               reply_required, reason
        FROM emails
        WHERE {" OR ".join(email_clauses)}
        ORDER BY received_at DESC
        LIMIT ?
        """

        email_params.append(limit)

        email_rows = self.conn.execute(
            email_sql,
            email_params
        ).fetchall()

        results = []

        for row in email_rows:

            item = dict(row)
            item["source"] = "email"

            results.append(item)

        # Search saved memory notes
        note_clauses = []
        note_params = []

        for term in terms:

            note_clauses.append(
                "(LOWER(key) LIKE ? OR LOWER(value) LIKE ?)"
            )

            like = f"%{term}%"
            note_params.extend([like, like])

        note_sql = f"""
        SELECT id, key, value, created_at
        FROM memory_notes
        WHERE {" OR ".join(note_clauses)}
        ORDER BY created_at DESC
        LIMIT ?
        """

        note_params.append(limit)

        note_rows = self.conn.execute(
            note_sql,
            note_params
        ).fetchall()

        for row in note_rows:

            note = dict(row)

            results.append({
                "id": f"MEM-{note['id']}",
                "sender": "Saved Memory",
                "subject": note["key"],
                "body": note["value"],
                "note": note["value"],
                "priority": "MEMORY",
                "source": "memory_note",
                "created_at": note["created_at"]
            })

        return results[:limit]

    def pending_drafts(self) -> List[Dict[str, Any]]:

        rows = self.conn.execute("""
            SELECT * FROM drafts
            WHERE status = 'PENDING_APPROVAL'
            ORDER BY created_at DESC
        """).fetchall()

        return [dict(row) for row in rows]

    def reject_draft(self, draft_id: int, reason: str) -> Dict[str, Any]:
        cursor = self.conn.execute("""
            UPDATE drafts
            SET status = 'REJECTED', review_note = ?
            WHERE id = ? AND status = 'PENDING_APPROVAL'
        """, (reason, draft_id))
        if cursor.rowcount != 1:
            self.conn.rollback()
            raise ValueError(
                f"Pending draft {draft_id} was not found or was already reviewed."
            )
        self.conn.commit()
        return {
            "draft_id": draft_id,
            "status": "REJECTED",
            "review_note": reason
        }

    def save_calendar_task(
        self,
        email_id: str,
        task: str,
        due_date: str
    ) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT INTO calendar_tasks (email_id, task, due_date, status)
            VALUES (?, ?, ?, 'PLANNED')
        """, (email_id, task, due_date))
        self.conn.commit()
        return {
            "status": "saved",
            "email_id": email_id,
            "task": task,
            "due_date": due_date
        }

    def calendar_tasks(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT * FROM calendar_tasks
            ORDER BY created_at DESC
        """).fetchall()
        return [dict(row) for row in rows]

    def archive_email(self, email_id: str, reason: str = "") -> Dict[str, Any]:
        self.conn.execute("""
            INSERT INTO archive_log (email_id, action, reason)
            VALUES (?, 'ARCHIVED', ?)
        """, (email_id, reason))
        self.conn.commit()
        return {
            "status": "archived",
            "email_id": email_id,
            "reason": reason
        }

    def archive_log(self) -> List[Dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT * FROM archive_log
            ORDER BY created_at DESC
        """).fetchall()
        return [dict(row) for row in rows]

    def close(self):

        self.conn.close()
