"""Lab 12: Safety, approval gates, audit and evaluation."""
class GovernanceController:
    def __init__(self):
        self.audit = []

    def evaluate_draft(self, draft):
        checks = {
            "recipient_present": bool(draft.get("to")),
            "subject_present": bool(draft.get("subject")),
            "body_present": bool(draft.get("body", "").strip()),
            "approval_pending": draft.get("status", "PENDING_APPROVAL") == "PENDING_APPROVAL",
            "no_auto_send_tool": True
        }
        allowed_to_queue = all(checks.values())
        event = {"email_id": draft.get("email_id"), "checks": checks,
                 "decision": "QUEUE_FOR_HUMAN_APPROVAL" if allowed_to_queue else "BLOCK"}
        self.audit.append(event)
        return event

    def report(self):
        checked = sum(1 for event in self.audit if "checks" in event)
        return {"policy": "Human approval is mandatory; this project does not send email.",
                "drafts_checked": checked, "audit": list(self.audit)}

    def rollback_draft(self, memory, draft_id, reason):
        result = memory.reject_draft(draft_id, reason)
        event = {
            "draft_id": draft_id,
            "decision": "REJECTED",
            "reason": reason
        }
        self.audit.append(event)
        return result
