"""Run one worklet lab and print its concept, stack, implementation and evidence."""
from .runtime import AgentRuntime
from .graph import EmailAgentGraph
from .swarm import EmailSwarm, SpecialistAgent
from .research import EmailResearchAgent
from .cloud_ops import OperationsMonitor
from .sdlc import SDLCAgent
from .governance import GovernanceController
from .domain_agents import AcademicDomainAgents


LAB_INFO = {
    1: ("Agent vs Chatbot", "Agent loop: plan, act, observe and revise.",
        "Python, local email connector, reusable skills, SQLite.",
        "The organizer observes incoming emails, plans analysis, classifies and scores them, observes extracted actions, revises priority when needed, then persists the final triage and drafts."),
    2: ("Tool-Using Agent", "Tool registration and function-style execution.",
        "Python, ToolRegistry, JSON email connector, SQLite.",
        "ToolRegistry exposes named email and memory functions. The demo lists emails, retrieves one by ID, saves a draft behind approval, and searches memory."),
    3: ("Skill Creation", "Reusable email classification, scoring, extraction and drafting.",
        "Python, EmailSkills, optional LLM API with local fallback.",
        "EmailSkills provides reusable classification, priority scoring, action extraction, reply drafting, and follow-up digest methods; rule-based behavior works without an API key."),
    4: ("Memory & Retrieval", "Short-term state with persistent retrieval.",
        "Python, SQLite, keyword retrieval; no vector database.",
        "A run-local state dictionary represents short-term context; analyses and notes are stored in SQLite and retrieved with keyword matching. This is not vector RAG."),
    5: ("MCP-Style Connector", "Named tools/resources behind a connector adapter.",
        "Python, JSON file connector, SQLite memory, in-process adapter; no network MCP server.",
        "The adapter exposes named email, memory, and health operations with input schemas, hiding storage details from its caller."),
    6: ("OpenCLA / OpenClaw Runtime", "Runtime executes skills/tools and records an audit trace.",
        "Python, AgentRuntime, ToolRegistry, SQLite.",
        "AgentRuntime wraps email retrieval, skill execution, and persistence calls, recording UTC start/success/failure events and re-raising errors."),
    7: ("Agentic Node Graph", "State passes through ingest, analyse and summarize nodes.",
        "Python, LangGraph StateGraph.",
        "The graph loads emails into state, analyzes each email, captures per-email errors, and returns a summary with results."),
    8: ("Parallel Swarm", "Specialist agents execute concurrently and merge results.",
        "Python concurrent.futures, deterministic merge.",
        "Three specialist functions inspect each email concurrently; results are merged in submission order and report success and failure counts."),
    9: ("Deep Research Agent", "Retrieve local evidence and produce an auditable summary.",
        "Python, local email corpus, keyword evidence retrieval; no web search.",
        "The research agent ranks local emails against query terms, returns source email IDs and quoted evidence, and states its retrieval limitations."),
    10: ("Cloud Operations Agent", "Check service health and report degraded dependencies.",
         "Python, filesystem and SQLite health checks; local simulation, no cloud deployment.",
         "The monitor checks the dataset and SQLite service, reports health, and includes a simulated missing-dataset incident with a remediation hint."),
    11: ("Agentic SDLC Factory", "Check requirements, source syntax and project tests.",
         "Python AST and unittest; local pipeline.",
         "The SDLC check lists project requirements, parses every source file with Python AST, and runs the unit-test suite."),
    12: ("Safety & Governance", "Validate drafts and require human approval before action.",
         "Python, governance checks, SQLite review state; no email sending.",
         "The controller blocks incomplete drafts, queues complete drafts for human approval, records decisions, and can reject a pending draft while retaining the reason."),
    13: ("Discipline-Specific Agents", "Route academic emails to relevant specialist domains.",
         "Python keyword-based academic, placement, coursework and meeting agents.",
         "Placement, project/research, coursework, and meeting agents independently match domain signals and return routing evidence."),
    14: ("Capstone Project Studio", "Integrate the worklet modules into one end-to-end pipeline.",
         "Python, SQLite, local connectors, labs 1-13; no automatic sending.",
         "The capstone runs the organizer foundation and Labs 6-13 against the same sample dataset, summarizes results, and keeps sending disabled.")
}


def _emails(tools):
    return tools.call("list_emails")


def _demo_output(lab_number, tools, skills, connector, memory, project_root):
    if lab_number == 1:
        from ..agent import EmailOrganizerAgent
        return EmailOrganizerAgent(tools, skills, memory).run()

    if lab_number == 2:
        emails = _emails(tools)
        first = emails[0]
        draft = {
            "email_id": first["id"],
            "to": first["sender"],
            "subject": "Re: " + first["subject"],
            "body": "Thank you for your email. I will review the details.",
            "status": "PENDING_APPROVAL"
        }
        return {
            "registered_tools": tools.describe(),
            "list_emails_result_count": len(emails),
            "get_email_result": tools.call("get_email", email_id=first["id"]),
            "save_draft_result": tools.call("save_draft", draft=draft),
            "search_memory_result": tools.call(
                "search_memory", query=first["subject"], limit=3
            )
        }

    if lab_number == 3:
        email = _email_model(_emails(tools)[0])
        analysis = skills.score_priority(email, skills.classify_email(email))
        draft = skills.draft_reply(email, analysis)
        return {
            "email_id": email.id,
            "classification_and_priority": analysis.to_dict(),
            "draft": draft.to_dict(),
            "follow_up_digest": skills.build_followup_digest([analysis])
        }

    if lab_number == 4:
        from ..models import Email
        raw = _emails(tools)[0]
        email = Email(**raw)
        analysis = skills.score_priority(email, skills.classify_email(email))
        memory.save_analysis(email.to_dict(), analysis.to_dict())
        memory.save_memory("lab4_reference", "Persisted email: " + email.subject)
        short_term_state = {"run_id": "lab4-demo", "current_email_id": email.id}
        return {
            "short_term_state": short_term_state,
            "long_term_record_saved": email.id,
            "retrieved_records": memory.search(email.subject, limit=3),
            "retrieval_method": "SQLite keyword matching (not vector/semantic RAG)"
        }

    if lab_number == 5:
        tool_specs = connector.list_tools()
        return {
            "connector_tool_specs": tool_specs,
            "email_list_result": connector.call("email.list", {}),
            "memory_search_result": connector.call(
                "memory.search", {"query": "project", "limit": 3}
            ),
            "mock_api_health_result": connector.call("system.health", {})
        }

    if lab_number == 6:
        runtime = AgentRuntime()
        emails = runtime.execute("list_emails", tools.call, "list_emails")
        from ..models import Email
        email = Email(**emails[0])
        analysis = runtime.execute("classify_email", skills.classify_email, email)
        runtime.execute(
            "save_analysis",
            memory.save_analysis,
            email.to_dict(),
            analysis.to_dict()
        )
        runtime.execute(
            "save_run_note", tools.call, "save_memory",
            key="lab6_runtime_demo", value="Runtime completed email analysis."
        )
        return {
            "email_processed": email.id,
            "audit_report": runtime.audit_report()
        }

    if lab_number == 7:
        return EmailAgentGraph(tools, skills).run()

    if lab_number == 8:
        specialists = [
            SpecialistAgent("action_agent", lambda email: {
                "has_action": any(
                    word in email.get("body", "").lower()
                    for word in ("please", "must", "submit", "reply")
                )
            }),
            SpecialistAgent("reply_agent", lambda email: {
                "may_need_reply": any(
                    word in email.get("body", "").lower()
                    for word in ("reply", "respond", "clarify", "confirm")
                )
            }),
            SpecialistAgent("academic_domain_agent", lambda email: {
                "academic": any(
                    word in (email.get("subject", "") + " " + email.get("body", "")).lower()
                    for word in ("assignment", "project", "research", "exam")
                )
            })
        ]
        return EmailSwarm(specialists).run(_emails(tools))

    if lab_number == 9:
        return EmailResearchAgent(connector).research(
            "project review assignment placement"
        )

    if lab_number == 10:
        root = project_root
        healthy = OperationsMonitor(
            root / "data" / "emails.json",
            root / "data" / "email_memory.db"
        ).check()
        simulated_failure = OperationsMonitor(
            root / "data" / "missing_demo_dataset.json",
            root / "data" / "email_memory.db"
        ).check()
        return {"current_health": healthy, "simulated_failure_diagnosis": simulated_failure}

    if lab_number == 11:
        sdlc = SDLCAgent(project_root)
        return {"inspection": sdlc.inspect(), "test_run": sdlc.run_tests()}

    if lab_number == 12:
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from ..storage import MemoryStore
        governance = GovernanceController()
        valid_draft = {
            "email_id": "DEMO-OK",
            "to": "faculty@example.edu",
            "subject": "Re: Review meeting",
            "body": "Thank you. I will review the meeting details.",
            "status": "PENDING_APPROVAL"
        }
        invalid_draft = {"email_id": "DEMO-BLOCK", "to": ""}
        decisions = [
            governance.evaluate_draft(valid_draft),
            governance.evaluate_draft(invalid_draft)
        ]
        with TemporaryDirectory() as temp_dir:
            review_memory = MemoryStore(Path(temp_dir) / "governance.db")
            review_memory.save_draft({
                **valid_draft,
                "email_id": "DEMO-ROLLBACK"
            })
            draft_id = review_memory.pending_drafts()[0]["id"]
            rollback = governance.rollback_draft(
                review_memory, draft_id, "Reviewer rejected this draft."
            )
            review_memory.close()
        return {
            "decisions": decisions,
            "rollback_demo": rollback,
            "rollback_plan": "Reject before send and retain the human review reason.",
            "audit_report": governance.report()
        }

    if lab_number == 13:
        return AcademicDomainAgents().route(_emails(tools))

    if lab_number == 14:
        from .capstone import run_capstone
        return run_capstone(tools, skills, connector, memory, project_root)

    raise ValueError(f"Unknown lab number: {lab_number}")


def _email_model(raw):
    from ..models import Email
    return Email(**raw)


def run_lab_demo(lab_number, tools, skills, connector, memory, project_root):
    """Return one lab's worksheet details plus its live execution evidence."""
    title, concept, stack, implementation = LAB_INFO[lab_number]
    return {
        "lab": lab_number,
        "title": title,
        "concept": concept,
        "technical_stack": stack,
        "implementation": implementation,
        "evidence": _demo_output(
            lab_number, tools, skills, connector, memory, project_root
        )
    }
