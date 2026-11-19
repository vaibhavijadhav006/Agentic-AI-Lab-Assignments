"""Lab 12B: block proposal six until evaluate() is called again."""
class Agent:
    def __init__(self):
        self.evaluated=False; self.proposals_since_eval=0; self.audit=[]
    def evaluate(self):
        self.evaluated=True; self.proposals_since_eval=0
        self.audit.append({"step":"evaluation","status":"passed"})
        return True
    def propose(self,description):
        if not self.evaluated:
            return {"blocked":True,"message":"Call evaluate() before proposing."}
        if self.proposals_since_eval>=5:
            self.evaluated=False
            return {"blocked":True,"message":"Five proposals reached; re-evaluation required before proposal six."}
        self.proposals_since_eval+=1
        item={"proposal":self.proposals_since_eval,"description":description}
        self.audit.append({"step":"proposal","data":item})
        return {"blocked":False,**item}
if __name__ == "__main__":
    a=Agent(); a.evaluate()
    for i in range(1,7): print(i,a.propose(f"change {i}"))
    print("Re-evaluate:",a.evaluate())
    print("After evaluation:",a.propose("change 6"))
