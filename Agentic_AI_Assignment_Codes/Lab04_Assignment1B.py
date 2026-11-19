"""Lab 4B: Warn before using records older than retention_days."""
from dataclasses import dataclass
from datetime import date, timedelta
@dataclass
class MemoryRecord:
    topic:str; fact:str; recorded_on:date
class ProjectMemory:
    def __init__(self, retention_days=30):
        self.retention_days=retention_days; self.records=[]
    def add(self, record): self.records.append(record)
    def answer(self, topic, today=None):
        today=today or date.today()
        hits=[r for r in self.records if r.topic==topic]
        if not hits: return "No stored decision."
        r=hits[-1]; age=(today-r.recorded_on).days
        warning=(f"WARNING: this decision is from {age} days ago and may be out of date. "
                 if age>self.retention_days else "")
        return warning + r.fact
if __name__ == "__main__":
    today=date(2026,11,16); m=ProjectMemory(retention_days=30)
    m.add(MemoryRecord("fresh","Use PostgreSQL",today-timedelta(days=5)))
    m.add(MemoryRecord("old","Use legacy database",today-timedelta(days=90)))
    print("Fresh:",m.answer("fresh",today))
    print("Old:",m.answer("old",today))
