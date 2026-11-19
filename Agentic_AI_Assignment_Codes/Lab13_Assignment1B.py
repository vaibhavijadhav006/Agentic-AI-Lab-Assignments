"""Lab 13B: three consecutive rising WARNING readings trigger inspection."""
WARNING=70
ALARM=100
def analyze(readings):
    consecutive=[]
    for r in readings:
        if r>=ALARM:
            return {"recommendation":"ALARM_RESPONSE","reason":f"Reading {r} reached ALARM threshold."}
        if r>=WARNING:
            consecutive.append(r)
            if len(consecutive)>=3 and consecutive[-1]>consecutive[-2]>consecutive[-3]:
                return {"recommendation":"schedule_inspection",
                        "reason":f"Three consecutive WARNING readings rose: {consecutive[-3:]}."}
        else:
            consecutive=[]
    return {"recommendation":"continue_monitoring","reason":"No ALARM or three-reading rising WARNING trend."}
if __name__ == "__main__":
    log=[72,78,84]  # all below ALARM, rising for three consecutive readings
    print("Readings:",log)
    print("Decision:",analyze(log))
