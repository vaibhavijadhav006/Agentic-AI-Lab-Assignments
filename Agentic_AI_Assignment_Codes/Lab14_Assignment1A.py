"""Lab 14A: route between reusable triage and password-reset skills."""
def triage_skill(issue):
    return {"skill":"triage_skill","instructions":"Classify issue, request safe diagnostics, escalate urgent incidents.",
            "response":"Please share the exact error and when it began. Do not share passwords or tokens."}
def password_reset_skill(issue):
    return {"skill":"password_reset_guidance","instructions":"Give safe self-service reset steps; never request credentials.",
            "response":"Use the official password-reset page, verify the domain, follow the recovery steps, and enable MFA. Never share your password or OTP."}
def route_skill(issue):
    text=issue.lower()
    if any(k in text for k in ["forgot password","reset password","locked out"]):
        return password_reset_skill(issue)
    return triage_skill(issue)
if __name__ == "__main__":
    for issue in ["I forgot my password","The application crashes on login"]:
        print(issue,"=>",route_skill(issue))
