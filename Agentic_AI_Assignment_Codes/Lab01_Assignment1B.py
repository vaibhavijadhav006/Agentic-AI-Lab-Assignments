"""Lab 1B: Detect busy-day conflicts before finalizing a study plan."""
BUSY_DAYS = ["Wednesday", "Friday"]
UNAVAILABLE_DAYS = ["Sunday"]

def read_existing_schedule():
    return {"busy_days": BUSY_DAYS}

def build_plan(unavailable_days):
    busy = read_existing_schedule()["busy_days"]
    conflicts = [day for day in busy if day not in unavailable_days]
    if conflicts:
        return {"finalized": False, "conflict": conflicts,
                "message": "Scheduling conflict detected. Resolve these busy days first."}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return {"finalized": True, "schedule": {d: "17:00-19:00" for d in days
                                             if d not in unavailable_days and d not in busy}}

if __name__ == "__main__":
    result = build_plan(UNAVAILABLE_DAYS)
    print("Tool busy days:", read_existing_schedule())
    print("Agent response:", result)
