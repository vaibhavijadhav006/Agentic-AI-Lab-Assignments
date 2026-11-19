"""Lab 7: LangGraph workflow for email ingestion, analysis and summary."""
from typing import TypedDict
from langgraph.graph import END, START, StateGraph


class GraphState(TypedDict):
    emails: list
    analyses: list
    errors: list
    node_sequence: list
    output: dict

class EmailAgentGraph:
    """LangGraph state graph: ingest -> analyse -> summarize."""
    def __init__(self, tools, skills):
        self.tools, self.skills = tools, skills
        self.nodes = ["ingest", "analyse", "summarize"]
        builder = StateGraph(GraphState)
        builder.add_node("ingest", self._ingest)
        builder.add_node("analyse", self._analyse)
        builder.add_node("summarize", self._summarize)
        builder.add_edge(START, "ingest")
        builder.add_edge("ingest", "analyse")
        builder.add_edge("analyse", "summarize")
        builder.add_edge("summarize", END)
        self.graph = builder.compile()

    def run(self):
        state = self.graph.invoke({
            "emails": [],
            "analyses": [],
            "errors": [],
            "node_sequence": [],
            "output": {}
        })
        return state["output"]

    def _ingest(self, state: GraphState):
        return {
            "emails": self.tools.call("list_emails"),
            "node_sequence": state["node_sequence"] + ["ingest"]
        }

    def _analyse(self, state: GraphState):
        analyses = []
        errors = []
        for raw in state["emails"]:
            try:
                from ..models import Email
                email = Email(**raw)
                analysis = self.skills.classify_email(email)
                analysis = self.skills.score_priority(email, analysis)
                analyses.append({
                    "email": email.to_dict(),
                    "analysis": analysis.to_dict()
                })
            except Exception as exc:
                errors.append({"email_id": raw.get("id"), "error": str(exc)})
        return {
            "analyses": analyses,
            "errors": errors,
            "node_sequence": state["node_sequence"] + ["analyse"]
        }

    def _summarize(self, state: GraphState):
        node_sequence = state["node_sequence"] + ["summarize"]
        return {
            "node_sequence": node_sequence,
            "output": {
                "node_sequence": node_sequence,
                "emails_ingested": len(state["emails"]),
                "emails_analysed": len(state["analyses"]),
                "errors": state["errors"],
                "results": state["analyses"]
            }
        }
