"""Lab 13: Discipline-specific agent personas for academic email workflows."""
class DomainAgent:
    def __init__(self, domain, keywords):
        self.domain, self.keywords = domain, tuple(k.lower() for k in keywords)

    def inspect(self, email):
        text = (email.get("subject", "") + " " + email.get("body", "")).lower()
        hits = [word for word in self.keywords if word in text]
        return {"domain": self.domain, "email_id": email.get("id"),
                "matched": bool(hits), "signals": hits}

class AcademicDomainAgents:
    def __init__(self):
        self.agents = [
            DomainAgent("placement", ["placement", "interview", "registration", "recruiter"]),
            DomainAgent("project_research", ["project", "research", "paper", "literature review"]),
            DomainAgent("coursework", ["assignment", "lab", "submission", "exam"]),
            DomainAgent("meetings", ["meeting", "review", "minutes", "schedule"])
        ]

    def route(self, emails):
        routed = []
        for email in emails:
            matches = [agent.inspect(email) for agent in self.agents]
            routed.append({"email_id": email.get("id"),
                           "domains": [m["domain"] for m in matches if m["matched"]],
                           "signals": matches})
        return routed
