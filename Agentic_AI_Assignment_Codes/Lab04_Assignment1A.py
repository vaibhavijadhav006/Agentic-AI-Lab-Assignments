"""Lab 4A: Topic-scoped memory prevents cross-topic leakage."""
from dataclasses import dataclass
@dataclass
class MemoryRecord:
    topic: str
    fact: str
    date: str
class ProjectMemory:
    def __init__(self): self.records=[]
    def write(self, record): self.records.append(record)
    def retrieve(self, topic): return [r for r in self.records if r.topic == topic]
class Assistant:
    def __init__(self, memory): self.memory=memory
    def answer(self, topic):
        hits=self.memory.retrieve(topic)
        return hits[-1].fact if hits else f"No stored decision for {topic}."
if __name__ == "__main__":
    m=ProjectMemory()
    m.write(MemoryRecord("database","PostgreSQL selected","2026-07-03"))
    m.write(MemoryRecord("hosting","Use campus cloud hosting","2026-07-04"))
    a=Assistant(m)
    print("Database:",a.answer("database"))
    print("Hosting:",a.answer("hosting"))
    assert "hosting" not in a.answer("database").lower()
    assert "postgresql" not in a.answer("hosting").lower()
