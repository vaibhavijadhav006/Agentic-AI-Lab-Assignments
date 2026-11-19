"""Lab 12A: reject over-budget proposals and missing cost unless finance approves."""
class GovernanceAgent:
    def __init__(self,budget_limit):
        self.budget_limit=budget_limit; self.audit=[]
    def propose(self,action,cost=None,finance_approved=False):
        if cost is None:
            result={"rejected":True,"reason":"Cost estimate is mandatory; missing cost cannot bypass policy."}
        elif cost>self.budget_limit and not finance_approved:
            result={"rejected":True,"reason":"Estimated cost exceeds budget; finance approval required."}
        else:
            result={"rejected":False,"approved_for_review":True,"reason":"Cost policy satisfied."}
        self.audit.append({"action":action,"cost":cost,"finance_approved":finance_approved,"result":result})
        return result
if __name__ == "__main__":
    a=GovernanceAgent(10000)
    print("Within budget:",a.propose("restart service",500))
    print("Over budget:",a.propose("replace cluster",15000))
    print("Adversarial missing cost:",a.propose("unknown action"))
    print("Finance approved:",a.propose("replace cluster",15000,True))
    print("Audit:",a.audit)
