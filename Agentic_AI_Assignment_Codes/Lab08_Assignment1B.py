"""Lab 8B: each role independently critiques merged plan."""
def role_critique(role,draft):
    objections=[]
    if role=="logistics" and draft["venue_cost"]>25000:
        objections.append("Venue cost exceeds logistics constraint (₹25,000).")
    if role=="budget" and draft["venue_cost"]+draft["marketing_cost"]>30000:
        objections.append("Combined cost exceeds total budget cap (₹30,000).")
    if role=="judging" and len(draft["criteria"])<3:
        objections.append("Judging criteria must contain at least three dimensions.")
    if role=="marketing" and draft["marketing_cost"]>5000:
        objections.append("Marketing cost exceeds marketing allocation (₹5,000).")
    return [{"raised_by":role,"objection":x} for x in objections]
if __name__ == "__main__":
    draft={"venue_cost":28000,"marketing_cost":8000,"criteria":["innovation"]}
    log=[]
    for role in ["logistics","budget","judging","marketing"]:
        log.extend(role_critique(role,draft))
    print("Distributed conflict log:")
    for item in log: print(item)
