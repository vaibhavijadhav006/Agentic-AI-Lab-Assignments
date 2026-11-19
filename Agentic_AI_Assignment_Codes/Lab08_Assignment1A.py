"""Lab 8A: add marketing role and enforce shared budget cap."""
from concurrent.futures import ThreadPoolExecutor
def research_agent(goal): return {"role":"research","format":"24-hour themed hackathon"}
def logistics_agent(goal): return {"role":"logistics","venue":"Grand Hall","venue_cost":22000}
def budget_agent(goal): return {"role":"budget","total_cap":30000}
def judging_agent(goal): return {"role":"judging","criteria":["innovation","depth","demo"]}
def marketing_agent(goal): return {"role":"marketing","campaign":"posters + social media","marketing_cost":12000}
def run_swarm(goal):
    funcs=[research_agent,logistics_agent,budget_agent,judging_agent,marketing_agent]
    with ThreadPoolExecutor(max_workers=5) as pool:
        return {f.__name__.replace("_agent",""):r for f,r in zip(funcs,pool.map(lambda f:f(goal),funcs))}
def critique(draft):
    conflicts=[]
    total=draft["venue_cost"]+draft["marketing_cost"]
    if total>draft["budget_cap"]:
        conflicts.append({"conflict":"combined costs exceed budget","total":total,"cap":draft["budget_cap"]})
    return conflicts
def resolve(conflict):
    return {"rule_applied":"budget_over_preference","resolution":"Reduce marketing spend or choose a lower-cost venue."}
if __name__ == "__main__":
    roles=run_swarm("Plan college AI hackathon")
    draft={"venue":roles["logistics"]["venue"],"venue_cost":roles["logistics"]["venue_cost"],
           "marketing":roles["marketing"]["campaign"],"marketing_cost":roles["marketing"]["marketing_cost"],
           "budget_cap":roles["budget"]["total_cap"]}
    print("Role outputs:",roles); print("Draft:",draft)
    for c in critique(draft): print("Conflict:",c,"Resolution:",resolve(c))
