"""Lab 6A: maximum three tasks per user per session; runtime signature unchanged."""
class Memory:
    def scope(self,user): return {}
class Audit:
    def __init__(self): self.entries=[]
    def log(self,task,skill,calls,result=None,error=None,user=None):
        self.entries.append({"user":user,"task":task,"skill":skill,"result":result,"error":error})
def run_task(task,user,memory,audit):
    skill=task["skill"]; result=f"Executed {skill}"
    audit.log(task,skill,[],result=result,user=user)
    return result
def receive_task(task,user,memory,audit):
    completed=sum(1 for e in audit.entries if e["user"]==user)
    if completed>=3:
        return f"REJECTED: {user} has reached the 3-task session limit."
    return run_task(task,user,memory,audit)
if __name__ == "__main__":
    m,a=Memory(),Audit()
    for i in range(1,5):
        print(i,receive_task({"skill":"summarize_notes"}, "student1",m,a))
