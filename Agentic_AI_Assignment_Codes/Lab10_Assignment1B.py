"""Lab 10B: low-risk restart may auto-execute; rollback always requires approval."""
def propose_action(severity,action,risk_level):
    if "rollback" in action.lower():
        return {"status":"APPROVAL_REQUIRED","action":action,"reason":"Rollback-class actions always require human approval."}
    if severity=="WARNING" and action=="restart_single_pod" and risk_level=="low":
        return {"status":"AUTO_EXECUTED","action":action,"reason":"Low-risk WARNING remediation is permitted."}
    return {"status":"APPROVAL_REQUIRED","action":action,"reason":"Action is not eligible for automatic execution."}
if __name__ == "__main__":
    print("WARNING restart:",propose_action("WARNING","restart_single_pod","low"))
    print("Rollback:",propose_action("WARNING","rollback_deployment","low"))
    print("Critical restart:",propose_action("ALARM","restart_single_pod","low"))
