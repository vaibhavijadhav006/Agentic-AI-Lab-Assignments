"""Lab 14: Integrated capstone pipeline for Labs 6–13."""
from pathlib import Path
from .runtime import AgentRuntime
from .graph import EmailAgentGraph
from .swarm import EmailSwarm, SpecialistAgent
from .research import EmailResearchAgent
from .cloud_ops import OperationsMonitor
from .sdlc import SDLCAgent
from .governance import GovernanceController
from .domain_agents import AcademicDomainAgents
from ..agent import EmailOrganizerAgent

def run_capstone(tools, skills, connector, memory, project_root):
    root = Path(project_root)
    foundation = EmailOrganizerAgent(tools, skills, memory).run()
    runtime = AgentRuntime()
    emails = runtime.execute("ingest_emails", tools.call, "list_emails")
    graph = runtime.execute("agent_node_graph", EmailAgentGraph(tools, skills).run)
    swarm = EmailSwarm([
        SpecialistAgent("action_signal_agent", lambda e: {
            "has_action_language": any(w in (e.get("body","").lower())
                                       for w in ("please", "must", "reply", "submit"))}),
        SpecialistAgent("reply_signal_agent", lambda e: {
            "may_need_reply": any(w in (e.get("body","").lower())
                                  for w in ("reply", "respond", "clarify", "confirm"))})
    ]).run(emails)
    research = EmailResearchAgent(connector).research("project review assignment placement")
    operations = OperationsMonitor(root/"data"/"emails.json",
                                   root/"data"/"email_memory.db").check()
    sdlc_factory = SDLCAgent(root)
    sdlc = sdlc_factory.inspect()
    sdlc_tests = sdlc_factory.run_tests()
    governance = GovernanceController()
    pending = memory.pending_drafts()
    approval = [governance.evaluate_draft({
        "email_id": d.get("email_id"), "to": d.get("recipient"),
        "subject": d.get("subject"), "body": d.get("body"),
        "status": d.get("status")
    }) for d in pending]
    domains = AcademicDomainAgents().route(emails)
    result = {
        "lab1_to_5_foundation": {
            "triaged_emails": len(foundation["triaged_inbox"]),
            "drafts_queued_for_approval": len(foundation["draft_reply_queue"]),
            "action_items": len(foundation["action_item_list"]),
            "followups": len(foundation["follow_up_digest"]),
            "registered_tools": [tool["name"] for tool in foundation["tool_calls"]],
            "skill_summary": foundation["skill_summary"],
            "email_sending_enabled": False
        },
        "lab6_runtime_audit": runtime.audit_report(),
        "lab7_agent_graph": graph,
        "lab8_parallel_swarm": swarm,
        "lab9_research_report": research,
        "lab10_operations": operations,
        "lab11_sdlc": sdlc,
        "lab12_governance": {**governance.report(), "current_pending_draft_checks": approval},
        "lab13_domain_routing": domains,
        "lab14_capstone_summary": {
            "emails_ingested": len(emails),
            "graph_analysed": graph["emails_analysed"],
            "swarm_tasks": swarm["task_count"],
            "research_evidence": len(research["evidence"]),
            "operations_status": operations["overall"],
            "source_syntax_status": sdlc["syntax_status"],
            "test_status": sdlc_tests["status"],
            "tests_run": sdlc_tests["tests_run"],
            "pending_drafts": len(pending),
            "email_sending_enabled": False
        }
    }
    return result
