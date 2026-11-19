"""Lab 7A: security_scan node inserted between builder and tester."""
class Node:
    def __init__(self,name,owner,action,success,on_fail):
        self.name=name; self.owner=owner; self.action=action; self.success=success; self.on_fail=on_fail
def requirement(s): s["requirements"]=["login","events","RSVP"]; return s
def planner(s): s["tasks"]=["implement "+x for x in s["requirements"]]; return s
def builder(s): s["build_ok"]=True; s["code"]="app.py"; return s
def security_scan(s):
    s["security_scan_passed"]=not s.get("force_security_fail",False)
    s["scan_report"]="No critical vulnerabilities" if s["security_scan_passed"] else "Critical vulnerability found"
    return s
def tester(s): s["tests_passed"]=True; return s
GRAPH=[
 Node("requirement","requirements_agent",requirement,lambda s:len(s["requirements"])>=3,"escalate"),
 Node("planner","planner_agent",planner,lambda s:bool(s["tasks"]),"revise_plan"),
 Node("builder","builder_agent",builder,lambda s:s["build_ok"],"retry_build"),
 Node("security_scan","security_agent",security_scan,lambda s:s["security_scan_passed"],"block_release_and_escalate"),
 Node("tester","test_agent",tester,lambda s:s["tests_passed"],"fix_tests")
]
def simulate(force_security_fail=False):
    state={"force_security_fail":force_security_fail}
    for n in GRAPH:
        state=n.action(state); print(n.name,state)
        if not n.success(state):
            print("FAILED NODE:",n.name,"BEHAVIOR:",n.on_fail); return state
    print("Workflow completed"); return state
if __name__ == "__main__":
    print("SUCCESS PATH"); simulate()
    print("\\nSECURITY FAILURE PATH"); simulate(True)
