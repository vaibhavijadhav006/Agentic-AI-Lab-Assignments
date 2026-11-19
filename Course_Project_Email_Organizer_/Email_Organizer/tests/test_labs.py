import unittest
from pathlib import Path
import tempfile
import json
from src.labs.runtime import AgentRuntime
from src.labs.governance import GovernanceController
from src.labs.domain_agents import AcademicDomainAgents
from src.labs.research import EmailResearchAgent
from src.storage import MemoryStore
from src.tools import ToolRegistry
from src.agent import EmailOrganizerAgent
from src.skills import EmailSkills
from src.connectors.json_connector import JSONEmailConnector
from src.connectors.mcp_style_adapter import MCPStyleEmailAdapter
from src.labs.cloud_ops import OperationsMonitor
from src.labs.graph import EmailAgentGraph


class FakeMemoryConnector:
    def list_emails(self):
        return [{"id":"T1","sender":"prof.ai@college.edu",
                 "subject":"Project review",
                 "body":"Please submit the project report before Friday.",
                 "received_at":"2026-10-01T08:30:00"}]

    def get_email(self, email_id):
        return None

class FakeConnector:
    def list_emails(self):
        return [{"id":"T1","sender":"x@y.com","subject":"Project review",
                 "body":"Please submit the project report before Friday."}]

class LabExtensionTests(unittest.TestCase):
    def test_agent_loop_records_plan_act_observe_revise(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemoryStore(Path(temp_dir) / "memory.db")
            tools = ToolRegistry(FakeMemoryConnector(), memory)
            agent = EmailOrganizerAgent(tools, EmailSkills(), memory)
            result = agent.run()
            trace = result["lab1_agent_loop"]["trace"]
            steps = [event["step"] for event in trace]
            self.assertIn("PLAN", steps)
            self.assertIn("ACT", steps)
            self.assertIn("OBSERVE", steps)
            self.assertIn("REVISE", steps)
            self.assertEqual(result["triaged_inbox"][0]["priority"], "HIGH")
            stored = memory.search("project review", limit=1)
            self.assertEqual(stored[0]["priority"], "HIGH")
            memory.close()

    def test_agent_processes_user_supplied_email(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemoryStore(Path(temp_dir) / "memory.db")
            tools = ToolRegistry(FakeMemoryConnector(), memory)
            agent = EmailOrganizerAgent(tools, EmailSkills(), memory)
            result = agent.run([{
                "id": "USER-1",
                "sender": "student@example.edu",
                "subject": "Please confirm meeting",
                "body": "Please confirm the meeting time by Friday.",
                "received_at": "2026-11-19T10:00:00"
            }])
            self.assertEqual(result["triaged_inbox"][0]["email_id"], "USER-1")
            self.assertTrue(result["draft_reply_queue"])
            memory.close()

    def test_runtime_records_success(self):
        runtime = AgentRuntime()
        self.assertEqual(runtime.execute("sum", lambda: 2+3), 5)
        self.assertEqual(runtime.audit_report()["event_count"], 2)

    def test_langgraph_runs_ingest_analyse_summarize(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemoryStore(Path(temp_dir) / "memory.db")
            tools = ToolRegistry(FakeMemoryConnector(), memory)
            result = EmailAgentGraph(tools, EmailSkills()).run()
            self.assertEqual(
                result["node_sequence"],
                ["ingest", "analyse", "summarize"]
            )
            self.assertEqual(result["emails_ingested"], 1)
            self.assertEqual(result["emails_analysed"], 1)
            self.assertEqual(result["errors"], [])
            memory.close()

    def test_governance_blocks_incomplete_draft(self):
        result = GovernanceController().evaluate_draft({"to":"x@y.com"})
        self.assertEqual(result["decision"], "BLOCK")

    def test_governance_queues_complete_draft(self):
        result = GovernanceController().evaluate_draft({
            "email_id":"T1","to":"x@y.com","subject":"Re: Hello",
            "body":"Thank you.","status":"PENDING_APPROVAL"})
        self.assertEqual(result["decision"], "QUEUE_FOR_HUMAN_APPROVAL")

    def test_domain_router(self):
        result = AcademicDomainAgents().route(FakeConnector().list_emails())
        self.assertIn("project_research", result[0]["domains"])

    def test_research_evidence(self):
        result = EmailResearchAgent(FakeConnector()).research("project report")
        self.assertEqual(result["evidence"][0]["email_id"], "T1")

    def test_calendar_and_archive_tools(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemoryStore(Path(temp_dir) / "memory.db")
            tools = ToolRegistry(FakeMemoryConnector(), memory)
            task = tools.call(
                "sync_calendar_task",
                email_id="T1",
                task="Submit project report",
                due_date="2026-11-20"
            )
            archive = tools.call(
                "archive_email",
                email_id="T1",
                reason="No action needed"
            )
            self.assertEqual(task["status"], "saved")
            self.assertEqual(archive["status"], "archived")
            self.assertEqual(len(memory.calendar_tasks()), 1)
            self.assertEqual(len(memory.archive_log()), 1)
            memory.close()

    def test_connector_exposes_email_sqlite_and_health_tools(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            email_file = root / "emails.json"
            email_file.write_text(json.dumps(FakeMemoryConnector().list_emails()))
            memory = MemoryStore(root / "memory.db")
            adapter = MCPStyleEmailAdapter(JSONEmailConnector(email_file), memory)
            names = {tool["name"] for tool in adapter.list_tools()}
            self.assertIn("email.list", names)
            self.assertIn("memory.search", names)
            self.assertIn("system.health", names)
            adapter.call("memory.save", {"key": "topic", "value": "project review"})
            self.assertTrue(adapter.call("memory.search", {"query": "project"}))
            self.assertEqual(adapter.call("system.health", {})["status"], "OK")
            memory.close()

    def test_connector_includes_run_specific_email_without_file_change(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            email_file = Path(temp_dir) / "emails.json"
            original = FakeMemoryConnector().list_emails()
            email_file.write_text(json.dumps(original))
            extra_email = {
                "id": "USER-2",
                "sender": "student@example.edu",
                "subject": "Custom email",
                "body": "Please review this.",
                "received_at": "2026-11-19T10:00:00"
            }
            connector = JSONEmailConnector(email_file, [extra_email])
            self.assertEqual(len(connector.list_emails()), 2)
            self.assertEqual(connector.get_email("USER-2"), extra_email)
            self.assertEqual(json.loads(email_file.read_text()), original)

    def test_governance_rollback_rejects_pending_draft(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory = MemoryStore(Path(temp_dir) / "memory.db")
            memory.save_draft({
                "email_id": "T1",
                "to": "x@y.com",
                "subject": "Re: Hello",
                "body": "Draft body",
                "status": "PENDING_APPROVAL"
            })
            draft_id = memory.pending_drafts()[0]["id"]
            result = GovernanceController().rollback_draft(
                memory, draft_id, "Reviewer rejected."
            )
            self.assertEqual(result["status"], "REJECTED")
            self.assertEqual(memory.pending_drafts(), [])
            memory.close()

    def test_operations_monitor_diagnoses_missing_dataset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            result = OperationsMonitor(
                root / "missing.json",
                root / "memory.db"
            ).check()
            self.assertEqual(result["overall"], "DEGRADED")
            self.assertEqual(result["diagnostics"][0]["check"], "email_dataset")
            self.assertTrue(result["diagnostics"][0]["remediation"])

if __name__ == "__main__":
    unittest.main()
