"""Lab 2B: read CSV -> filter category -> calculate average, validating each stage."""
import csv, io
CSV = """event,signups,category
AI Club Talk,12,technical
Hackathon,9,technical
Robotics Demo,15,technical
Cultural Night,30,social
Career Panel,11,social
"""
trace = []
def read_csv():
    rows = list(csv.DictReader(io.StringIO(CSV)))
    trace.append({"tool":"read_csv","output":rows})
    return rows
def filter_category(rows, category):
    filtered = [r for r in rows if r["category"].lower() == category.lower()]
    trace.append({"step":"filter","category":category,"output":filtered})
    if not filtered:
        raise ValueError(f"No rows found for category: {category}")
    return filtered
def calculator(values):
    result = sum(values)/len(values)
    trace.append({"tool":"calculator","input":values,"output":result})
    return result
if __name__ == "__main__":
    technical = filter_category(read_csv(), "technical")
    print("Technical average:", calculator([int(r["signups"]) for r in technical]))
    print("Trace:", trace)
