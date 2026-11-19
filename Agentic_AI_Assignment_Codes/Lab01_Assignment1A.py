"""Lab 1A: Two independent revisions mutate the same plan object."""
import json

class StudyPlannerAgent:
    def __init__(self):
        self.plan = {"Monday": {"subject": "DSA", "hours": 2},
                     "Tuesday": {"subject": "OS", "hours": 2},
                     "Friday": {"subject": "AI", "hours": 2}}
        self.log = []

    def revise(self, feedback):
        before_id = id(self.plan)
        f = feedback.lower()
        if "tuesday" in f and "evening" in f:
            self.plan["Tuesday"]["time"] = "20:00-22:00"
        if "friday" in f and ("shorter" in f or "one hour" in f):
            self.plan["Friday"]["hours"] = 1
        self.log.append({"iteration": len(self.log)+1, "feedback": feedback,
                         "plan_object_id": before_id, "plan": self.plan.copy()})
        assert id(self.plan) == before_id
        return self.plan

if __name__ == "__main__":
    agent = StudyPlannerAgent()
    original_id = id(agent.plan)
    print("Initial:", json.dumps(agent.plan, indent=2))
    agent.revise("Move Tuesday's session to the evening.")
    agent.revise("Also make Friday's session shorter, only one hour.")
    print("Same plan object:", id(agent.plan) == original_id)
    print("Revisions:", json.dumps(agent.log, indent=2))
    print("Final:", json.dumps(agent.plan, indent=2))
