"""Lab 10: Cloud-operations-style health checks for local services."""
from pathlib import Path
import sqlite3, json

class OperationsMonitor:
    def __init__(self, email_file, db_file):
        self.email_file, self.db_file = Path(email_file), Path(db_file)

    def check(self):
        checks = []
        checks.append(self._file_check("email_dataset", self.email_file))
        checks.append(self._sqlite_check())
        checks.append({"name": "llm_api", "status": "OPTIONAL",
                       "detail": "Local rule-based fallback is available; no API call made."})
        failed = [check for check in checks if check["status"] == "ERROR"]
        return {
            "overall": "HEALTHY" if not failed else "DEGRADED",
            "checks": checks,
            "diagnostics": [
                {
                    "check": check["name"],
                    "detail": check["detail"],
                    "remediation": check["remediation"]
                }
                for check in failed
            ]
        }

    @staticmethod
    def _file_check(name, path):
        exists = path.exists()
        result = {"name": name, "status": "OK" if exists else "ERROR",
                  "detail": str(path)}
        if not exists:
            result["remediation"] = "Restore the expected file or correct the configured path."
        return result

    def _sqlite_check(self):
        connection = None
        try:
            connection = sqlite3.connect(self.db_file)
            connection.execute("SELECT 1").fetchone()
            return {"name": "sqlite_memory", "status": "OK", "detail": str(self.db_file)}
        except Exception as exc:
            return {
                "name": "sqlite_memory",
                "status": "ERROR",
                "detail": str(exc),
                "remediation": "Check database path permissions and SQLite file integrity."
            }
        finally:
            if connection is not None:
                connection.close()
