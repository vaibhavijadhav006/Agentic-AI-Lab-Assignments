"""Lab 11: Agentic SDLC factory — requirements, implementation checks and tests."""
import ast
from pathlib import Path
import unittest

class SDLCAgent:
    def __init__(self, project_root):
        self.root = Path(project_root)

    def inspect(self):
        source_files = sorted((self.root / "src").rglob("*.py"))
        syntax = []
        for path in source_files:
            try:
                ast.parse(path.read_text(encoding="utf-8"))
                syntax.append({"file": str(path.relative_to(self.root)), "status": "PASS"})
            except SyntaxError as exc:
                syntax.append({"file": str(path.relative_to(self.root)), "status": "FAIL",
                               "error": str(exc)})
        return {"requirements": [
                    "Read email data through a connector",
                    "Classify and prioritize emails",
                    "Persist analyses and drafts",
                    "Require human approval before sending",
                    "Keep an execution/audit trace"
                ],
                "source_file_count": len(source_files),
                "syntax_checks": syntax,
                "syntax_status": "PASS" if all(x["status"] == "PASS" for x in syntax) else "FAIL"}

    def run_tests(self):
        suite = unittest.defaultTestLoader.discover(str(self.root / "tests"))
        result = unittest.TestResult()
        suite.run(result)
        return {"tests_run": result.testsRun, "failures": len(result.failures),
                "errors": len(result.errors),
                "details": [str(x[1]) for x in result.failures + result.errors],
                "status": "PASS" if result.wasSuccessful() else "FAIL"}
