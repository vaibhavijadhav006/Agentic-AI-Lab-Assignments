
from typing import Dict, Any

from .models import Email
from .skills import EmailSkills
from .storage import MemoryStore
from .tools import ToolRegistry


class EmailOrganizerAgent:
    """Goal-driven email organization agent."""

    def __init__(
        self,
        tools: ToolRegistry,
        skills: EmailSkills,
        memory: MemoryStore
    ):
        self.tools = tools
        self.skills = skills
        self.memory = memory

    def run(self, raw_emails=None) -> Dict[str, Any]:

        # OBSERVE: Retrieve emails
        if raw_emails is None:
            raw_emails = self.tools.call("list_emails")
        loop_trace = [{
            "cycle": 1,
            "step": "OBSERVE",
            "detail": f"Retrieved {len(raw_emails)} emails from the configured connector."
        }]

        triaged = []
        drafts = []
        action_items = []
        analyses = []
        loop_trace.append({
            "cycle": 2,
            "step": "PLAN",
            "detail": (
                "For each email, plan classification, priority scoring, "
                "action extraction, and conditional reply drafting."
            )
        })

        # PLAN + ACT
        for raw in raw_emails:

            email = Email(**raw)

            # Retrieve relevant memory
            context_rows = self.tools.call(
                "search_memory",
                query=f"{email.sender} {email.subject}",
                limit=3
            )

            context_parts = []

            for row in context_rows:
                if str(row.get("id", "")) == str(email.id):
                    continue

                subject = row.get(
                    "subject",
                    row.get("key", "Memory")
                )

                body = row.get(
                    "body",
                    row.get("value", "")
                )

                context_parts.append(
                    f"{subject}: {str(body)[:200]}"
                )

            context = "\n".join(context_parts)

            # Execute reusable skills
            analysis = self.skills.classify_email(email)

            analysis = self.skills.score_priority(
                email,
                analysis
            )

            loop_trace.append({
                "cycle": len(loop_trace) + 1,
                "step": "ACT",
                "detail": (
                    f"Processed {email.id}: classified as {analysis.category}, "
                    f"initial priority {analysis.priority}, found "
                    f"{len(analysis.action_items)} action item(s)."
                )
            })
            loop_trace.append({
                "cycle": len(loop_trace) + 1,
                "step": "OBSERVE",
                "detail": f"Observed urgency={analysis.urgency_score} and "
                          f"{len(analysis.action_items)} action item(s) for {email.id}."
            })

            original_priority = analysis.priority
            revised = analysis.priority == "MEDIUM" and bool(analysis.action_items)
            if revised:
                analysis.priority = "HIGH"
                analysis.urgency_score = max(analysis.urgency_score, 85)
            loop_trace.append({
                "cycle": len(loop_trace) + 1,
                "step": "REVISE",
                "detail": (
                    f"Re-evaluated {email.id}: priority "
                    f"{original_priority} -> {analysis.priority}; revised={revised}."
                )
            })

            analyses.append(analysis)
            self.memory.save_analysis(email.to_dict(), analysis.to_dict())
            triaged.append({
                "email_id": email.id,
                "subject": email.subject,
                "category": analysis.category,
                "priority": analysis.priority,
                "urgency_score": analysis.urgency_score,
                "reason": analysis.reason
            })

            for item in analysis.action_items:
                action_items.append({
                    "email_id": email.id,
                    "subject": email.subject,
                    "action": item
                })
                self.tools.call(
                    "sync_calendar_task",
                    email_id=email.id,
                    task=item,
                    due_date=analysis.follow_up_date or ""
                )

            if analysis.reply_required:
                draft = self.skills.draft_reply(email, analysis, context)
                draft_data = draft.to_dict()
                draft_data["email_id"] = email.id
                self.tools.call("save_draft", draft=draft_data)
                drafts.append(draft_data)

        # Generate follow-up digest
        followups = self.skills.build_followup_digest(
            analyses
        )

        # Save run summary
        self.tools.call(
            "save_memory",
            key="last_run_summary",
            value=(
                f"Processed {len(raw_emails)} emails; "
                f"generated {len(drafts)} drafts."
            )
        )

        # Skill execution summary
        skill_summary = {
            "emails_classified": len(analyses),
            "priorities_scored": len(analyses),
            "emails_checked_for_action_items": len(analyses),
            "action_items_extracted": len(action_items),
            "drafts_generated": len(drafts),
            "followups_generated": len(followups)
        }

        return {
            "lab1_agent_loop": {
                "goal": "Intelligent Email Organization",
                "cycle": "OBSERVE -> PLAN -> ACT -> OBSERVE -> REVISE",
                "trace": loop_trace,
                "chatbot_difference": (
                    "The agent repeatedly evaluates state and adjusts outputs; "
                    "it is not a one-request/one-response chatbot."
                )
            },
            "triaged_inbox": triaged,
            "draft_reply_queue": drafts,
            "action_item_list": action_items,
            "follow_up_digest": followups,
            "tool_calls": self.tools.describe(),
            "skill_summary": skill_summary,
            "approval_rule": (
                "No email is sent automatically. "
                "Human approval is required."
            )
        }
