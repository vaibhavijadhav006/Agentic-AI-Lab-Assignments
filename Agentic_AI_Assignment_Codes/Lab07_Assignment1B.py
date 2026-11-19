"""Lab 7B: builder gets exactly one retry, then escalates."""
def run_builder(outcomes):
    attempts=0
    for outcome in outcomes:
        attempts+=1
        print(f"Builder attempt {attempts}: {'SUCCESS' if outcome else 'FAIL'}")
        if outcome: return {"status":"success","attempts":attempts}
        if attempts==2:
            return {"status":"escalated_to_human","attempts":attempts,
                    "message":"Builder failed twice; retry limit reached."}
        print("Retrying builder once...")
    return {"status":"failed","attempts":attempts}
if __name__ == "__main__":
    print("Scenario A:",run_builder([False,True]))
    print("Scenario B:",run_builder([False,False,True]))
