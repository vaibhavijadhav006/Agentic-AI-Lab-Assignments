"""Lab 10A: compare payments incident with database pool exhaustion."""
SCENARIOS={
"payments":{"logs":["payment timeout","HTTP 503 spike"],"deploys":["payments v4.2 deployed 10m ago"],"metrics":{"error_rate":0.18,"pool_usage":0.35,"latency_ms":2400}},
"database_pool":{"logs":["connection pool exhausted","wait queue growing"],"deploys":["database client v2.1 deployed 5m ago"],"metrics":{"error_rate":0.07,"pool_usage":1.0,"latency_ms":900}}
}
def classify_severity(s):
    m=s["metrics"]
    if m["error_rate"]>=0.15 or m["pool_usage"]>=0.95: return "ALARM"
    if m["error_rate"]>=0.05 or m["latency_ms"]>=800: return "WARNING"
    return "NORMAL"
def correlate_with_recent_changes(s):
    return {"recent_change":s["deploys"][0],"diagnosis":
            "Connection-pool exhaustion likely" if s["metrics"]["pool_usage"]>=0.95
            else "Payments service regression likely"}
if __name__ == "__main__":
    for name,s in SCENARIOS.items():
        print(name,{"severity":classify_severity(s),**correlate_with_recent_changes(s)})
