"""Lab 2A: Notification tool only drafts; it never sends."""
import csv, io
CSV = "event,signups\nAI Club Talk,12\nHackathon,9\nRobotics Demo,15\nGenAI Workshop,7\n"
THRESHOLD = 11
trace = []

def read_csv():
    rows = list(csv.DictReader(io.StringIO(CSV)))
    trace.append({"tool":"read_csv","reason":"signup data is stored in CSV","output":rows})
    return rows

def calculator(values):
    result = sum(values)/len(values)
    trace.append({"tool":"calculator","reason":"calculate average sign-ups","input":values,"output":result})
    return result

def send_notification(message):
    draft = {"status":"DRAFT ONLY - NOT SENT","message":message}
    trace.append({"tool":"send_notification","reason":f"average below threshold {THRESHOLD}","output":draft})
    return draft

if __name__ == "__main__":
    rows = read_csv()
    average = calculator([int(r["signups"]) for r in rows])
    print("Average:", round(average, 2))
    if average < THRESHOLD:
        print("Notification:", send_notification(f"Low turnout alert: average sign-ups are {average:.1f}."))
    print("Trace:", trace)
