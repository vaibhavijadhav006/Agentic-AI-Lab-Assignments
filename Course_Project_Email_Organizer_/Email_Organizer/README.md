# Agentic Email Organizer — Labs 1 to 14

## Project overview
A local, demonstration-ready agentic email organizer. It ingests sample emails, classifies and prioritizes them, extracts action items, drafts replies, stores memory, and provides an independent demo for each worklet lab.

## Implemented labs

| Lab | Module / implementation | Evidence produced |
|---|---|---|
| 1 — Agent vs Chatbot | `src/agent.py` | Plan-act-observe-revise trace and triaged inbox |
| 2 — Tool-Using Agent | `src/tools.py` | Registered tools and actual tool-call results |
| 3 — Skill Creation | `src/skills.py` | Reusable classification, scoring, extraction, drafting |
| 4 — Memory & Retrieval | `src/storage.py` | SQLite records and keyword search |
| 5 — MCP-Style Connector | `src/connectors/` | Named JSON, SQLite-memory and local health tools through an in-process adapter |
| 6 — Agent Runtime | `src/labs/runtime.py` | Runtime execution trace and audit events |
| 7 — Agent Node Graph | `src/labs/graph.py` | Ingest → analyse → summarize state graph |
| 8 — Parallel Swarm | `src/labs/swarm.py` | Concurrent specialist-agent results |
| 9 — Deep Research Agent | `src/labs/research.py` | Evidence report from local email corpus |
| 10 — Cloud Operations Agent | `src/labs/cloud_ops.py` | Local dataset/database health checks |
| 11 — Agentic SDLC Factory | `src/labs/sdlc.py` | Requirements and Python syntax checks |
| 12 — Safety & Governance | `src/labs/governance.py` | Draft validation and approval audit |
| 13 — Discipline-Specific Agents | `src/labs/domain_agents.py` | Academic/placement/project email routing |
| 14 — Capstone Project Studio | `src/labs/capstone.py` | Integrated Labs 6–13 terminal demonstration |

**Important scope notes:** This project uses sample emails only. Lab 5 is an in-process MCP-style adapter, not a networked MCP server. Lab 7 uses LangGraph's `StateGraph` locally. Lab 9 searches only the local email dataset, not the public internet. Lab 10 performs local health checks, not deployment to a cloud provider. Calendar tasks are stored locally; they are not sent to a calendar API. These boundaries are reported rather than represented as hosted integrations.

## Setup (Windows)
```bat
cd /d "D:\7th sem\Agentic ai\Email_Organizer_\Email_Organizer"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

To run **all 14 labs in order** with separate output for each, followed by the interactive email tools:
```bat
python -m src.main --all-labs
```
Or double-click `run_labs.bat`.
Before running, the program asks whether to add one custom email; if provided, it is included alongside the sample inbox for that run only.

To run one week's lab only (replace `7` with any number from 1 to 14):
```bat
python -m src.main --lab 7
```
Each lab output includes its concept, stack, implementation summary, and execution evidence. Lab 14 runs the integrated capstone. Afterward, use the menu to list/search emails, save drafts or memory, view tasks, archive emails, or enter and process a new email.

Run the interactive organizer without `--lab`:
```bat
python -m src.main
```

## Tests
```bat
python -m unittest discover -s tests -v
```

## Output
Lab demos print execution evidence in the terminal. SQLite data is stored in `data/email_memory.db`. No capstone report file is generated.

## Safety
The program **does not send emails**. It saves reply drafts with `PENDING_APPROVAL`; a human must review them. Do not add automatic sending without explicit authorization, secure credentials, and an approval workflow.

## Optional LLM
The default project works using local rule-based fallback. To enable OpenAI, copy `.env.example` to `.env`, add your API key, and set a model available to your account in `OPENAI_MODEL`. Never upload `.env` or API keys to GitHub.
