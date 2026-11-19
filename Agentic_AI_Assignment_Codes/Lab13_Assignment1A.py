"""Lab 13A: electrical load forecasting with threshold classification and human gate."""
READINGS=[{"time":"09:00","kw":72},{"time":"10:00","kw":88},{"time":"11:00","kw":106},{"time":"12:00","kw":121}]
WARNING_KW=90
ALARM_KW=115
def classify_load(reading):
    kw=reading["kw"]
    if kw>=ALARM_KW: return "ALARM"
    if kw>=WARNING_KW: return "WARNING"
    return "NORMAL"
def recommend(reading):
    severity=classify_load(reading)
    if severity=="ALARM":
        return {"severity":severity,"recommendation":"inspect feeder and verify load","requires_human_review":True,
                "action_status":"WAITING_FOR_HUMAN_REVIEW"}
    if severity=="WARNING":
        return {"severity":severity,"recommendation":"monitor load and check trend","requires_human_review":False}
    return {"severity":severity,"recommendation":"continue monitoring","requires_human_review":False}
if __name__ == "__main__":
    for r in READINGS: print(r,recommend(r))
