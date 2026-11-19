"""Lab 9: Deep-research workflow over the project's own email corpus.

No web search is performed. Evidence is quoted as short snippets from source
emails so that the report remains auditable and does not invent citations.
"""
class EmailResearchAgent:
    def __init__(self, connector):
        self.connector = connector

    def research(self, question, max_evidence=5):
        terms = [w.lower() for w in question.split() if len(w) >= 3]
        emails = self.connector.list_emails()
        ranked = []
        for email in emails:
            haystack = (email.get("subject", "") + " " + email.get("body", "")).lower()
            score = sum(haystack.count(term) for term in terms)
            if score:
                ranked.append((score, email))
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        evidence = []
        for score, email in ranked[:max_evidence]:
            evidence.append({
                "email_id": email["id"], "sender": email.get("sender"),
                "subject": email.get("subject"), "relevance_score": score,
                "evidence": email.get("body", "")[:300]
            })
        return {"question": question, "method": "keyword retrieval over local email data",
                "evidence": evidence,
                "conclusion": ("Found relevant source emails; review the evidence below."
                               if evidence else "No supporting emails found in the local corpus."),
                "limitations": ["Not an internet search", "Keyword relevance is not fact verification"]}
