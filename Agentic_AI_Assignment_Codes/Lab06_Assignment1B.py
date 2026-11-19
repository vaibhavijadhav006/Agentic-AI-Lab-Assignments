"""Lab 6B: third same-skill failure attempt escalates, using audit log only."""
class Audit:
    def __init__(self): self.entries=[]
    def log(self,user,skill,error=None,result=None):
        self.entries.append({"user":user,"skill":skill,"error":error,"result":result})
def receive_task(user,skill,audit,should_fail=True):
    prior=sum(1 for e in audit.entries if e["user"]==user and e["skill"]==skill and e["error"])
    if prior>=2:
        return {"status":"ESCALATED_TO_HUMAN","reason":"Same skill failed twice; no third execution attempted."}
    if should_fail:
        audit.log(user,skill,error="simulated failure")
        return {"status":"FAILED","attempt":prior+1}
    audit.log(user,skill,result="success")
    return {"status":"SUCCESS"}
if __name__ == "__main__":
    a=Audit()
    print(receive_task("u1","draft_email",a))
    print(receive_task("u1","draft_email",a))
    print(receive_task("u1","draft_email",a))
    print("Audit:",a.entries)
