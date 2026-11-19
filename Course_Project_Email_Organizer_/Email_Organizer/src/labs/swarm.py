"""Lab 8: Parallel specialist agents with deterministic result merging."""
from concurrent.futures import ThreadPoolExecutor, as_completed

class SpecialistAgent:
    def __init__(self, name, fn):
        self.name, self.fn = name, fn
    def run(self, email):
        return {"agent": self.name, "email_id": email.get("id"),
                "result": self.fn(email)}

class EmailSwarm:
    def __init__(self, specialists=None, max_workers=4):
        self.specialists = specialists or []
        self.max_workers = max_workers

    def run(self, emails):
        jobs = []
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            for email in emails:
                for specialist in self.specialists:
                    jobs.append((email, specialist, pool.submit(specialist.run, email)))
            for email, specialist, future in jobs:
                try:
                    results.append(future.result())
                except Exception as exc:
                    results.append({"agent": specialist.name, "email_id": email.get("id"),
                                    "error": str(exc)})
        return self.merge(results, jobs)

    def merge(self, results, jobs):
        failed = [item for item in results if "error" in item]
        successful = [item for item in results if "error" not in item]
        return {"specialist_count": len(self.specialists),
                "task_count": len(jobs), "successful_tasks": len(successful),
                "failed_tasks": len(failed), "fault_tolerant_merge": "complete",
                "results": results}
