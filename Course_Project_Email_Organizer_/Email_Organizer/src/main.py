
from pathlib import Path
import argparse
import json
from dotenv import load_dotenv

from .agent import EmailOrganizerAgent
from .connectors.json_connector import JSONEmailConnector
from .connectors.mcp_style_adapter import MCPStyleEmailAdapter
from .llm import LLMClient
from .skills import EmailSkills
from .storage import MemoryStore
from .tools import ToolRegistry


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def collect_optional_email(email_file):
    answer = input(
        "Would you like to add an email to this lab run? (y/N): "
    ).strip().lower()
    if answer not in {"y", "yes"}:
        return []

    sample_emails = JSONEmailConnector(email_file).list_emails()
    existing_ids = {str(email["id"]) for email in sample_emails}
    while True:
        email_id = input("Email ID (must be unique): ").strip()
        if email_id and email_id not in existing_ids:
            break
        print("Enter a non-empty ID that is not already in the sample inbox.")

    sender = input("Sender email: ").strip()
    subject = input("Subject: ").strip()
    body = input("Email body: ").strip()
    received_at = input(
        "Received at (optional; press Enter for current time): "
    ).strip()
    if not received_at:
        from datetime import datetime
        received_at = datetime.now().isoformat(timespec="seconds")

    if not all([sender, subject, body]):
        raise ValueError("Sender, subject, and body are required.")

    print(
        "Email content is processed locally unless an OpenAI API key is "
        "configured; with a key, text may be sent to that provider."
    )
    return [{
        "id": email_id,
        "sender": sender,
        "subject": subject,
        "body": body,
        "received_at": received_at
    }]


def show_agent_execution(result):

    print_section("1. AGENT EXECUTION")

    print("Goal: Intelligent Email Organization")
    print("Process: Observe -> Plan -> Act -> Observe -> Revise")

    print("\nLAB 1 AGENT LOOP TRACE")
    lab1 = result["lab1_agent_loop"]
    print(f"Cycle: {lab1['cycle']}")
    for step in lab1["trace"]:
        print(f"Cycle {step['cycle']} [{step['step']}] {step['detail']}")
    print(f"\nChatbot difference: {lab1['chatbot_difference']}")

    print("\nTRIAGED INBOX")

    for item in result["triaged_inbox"]:
        print(
            f"[{item['priority']}] "
            f"{item['subject']} | "
            f"{item['category']} | "
            f"Urgency: {item['urgency_score']}"
        )
        print(f"Reason: {item['reason']}")

    print("\nDRAFT-REPLY QUEUE")

    if not result["draft_reply_queue"]:
        print("No drafts generated.")

    for draft in result["draft_reply_queue"]:
        print(f"To: {draft['to']}")
        print(f"Subject: {draft['subject']}")
        print(f"Body: {draft['body']}")
        print(f"Status: {draft['status']}")
        print("-" * 50)

    print("\nACTION-ITEM LIST")

    if not result["action_item_list"]:
        print("No action items.")

    for item in result["action_item_list"]:
        print(f"[{item['email_id']}] {item['action']}")

    print("\nFOLLOW-UP DIGEST")

    if not result["follow_up_digest"]:
        print("No follow-ups.")

    for item in result["follow_up_digest"]:
        print(item)

    print("\nAPPROVAL RULE")
    print(result["approval_rule"])


def show_tool_execution(result):

    print_section("2. TOOL EXECUTION")

    print("Registered tools:")

    for tool in result["tool_calls"]:
        print(f"- {tool['name']}: {tool['description']}")

    print("\nThe agent uses these tools to:")
    print("- Retrieve emails")
    print("- Search relevant memory")
    print("- Save reply drafts")
    print("- Save memory notes")


def show_skill_execution(result):

    print_section("3. SKILL EXECUTION")

    print("Reusable skills executed:")

    summary = result["skill_summary"]

    print(f"Emails classified: {summary['emails_classified']}")
    print(f"Priorities scored: {summary['priorities_scored']}")
    print(f"Action items extracted: {summary['action_items_extracted']}")
    print(f"Reply drafts generated: {summary['drafts_generated']}")
    print(f"Follow-ups generated: {summary['followups_generated']}")

    print("\nSkills used:")
    print("- Email classification")
    print("- Priority scoring")
    print("- Action-item extraction")
    print("- Reply drafting")
    print("- Follow-up digest")


def show_memory_retrieval(memory):

    print_section("4. MEMORY AND RETRIEVAL")

    query = "project review"

    print(f"Search query: {query}")

    rows = memory.search(query, limit=5)

    if rows:
        for row in rows:
            print(
                f"\nID: {row['id']}"
                f"\nSubject/Key: {row['subject']}"
                f"\nContent: {row['body'][:200]}"
                f"\nSource: {row['source']}"
            )
    else:
        print("No matching records found.")


def show_connector(raw_connector, email_connector):

    print_section("5. MCP-STYLE CONNECTOR")

    print("Connector: JSONEmailConnector")
    print("Adapter: MCPStyleEmailAdapter")

    print("\nAvailable connector operations:")

    for tool in raw_connector.list_tools():
        print(f"- {tool['name']}: {tool['description']}")

    print("\nRetrieving emails through the adapter...")

    emails = email_connector.list_emails()

    print(f"Total emails retrieved: {len(emails)}")

    for email in emails:
        print(f"[{email['id']}] {email['subject']}")


def tool_demo(tools, memory, agent):

    while True:

        print_section("INTERACTIVE EMAIL ORGANIZER")

        print("1. List Emails")
        print("2. Get Email")
        print("3. Save Draft")
        print("4. Search Memory")
        print("5. Save Memory")
        print("6. View Calendar/Task Sync")
        print("7. Archive Email")
        print("8. Exit")
        print("9. Enter and Process a New Email")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":

            print_section("LIST EMAILS")

            try:
                emails = tools.call("list_emails")

                for email in emails:
                    print(f"[{email['id']}] {email['subject']}")

            except Exception as e:
                print(f"Error: {e}")

        elif choice == "2":

            print_section("GET EMAIL")

            email_id = input("Enter Email ID (example: E004): ").strip()

            try:
                email = tools.call("get_email", email_id=email_id)

                if email:
                    print(f"ID: {email['id']}")
                    print(f"From: {email.get('from', 'N/A')}")
                    print(f"To: {email.get('to', 'N/A')}")
                    print(f"Subject: {email['subject']}")
                    print(f"Body: {email['body']}")
                else:
                    print("Email not found.")

            except Exception as e:
                print(f"Error: {e}")

        elif choice == "3":

            print_section("SAVE DRAFT")

            email_id = input("Enter Email ID: ").strip()
            to = input("Enter recipient email: ").strip()
            subject = input("Enter subject: ").strip()
            body = input("Enter draft body: ").strip()

            if not all([email_id, to, subject, body]):
                print("All fields are required.")
                continue

            draft = {
                "email_id": email_id,
                "to": to,
                "subject": subject,
                "body": body,
                "status": "PENDING_APPROVAL"
            }

            try:
                result = tools.call("save_draft", draft=draft)

                print("Draft saved successfully.")
                print("Human approval required.")
                print("Email has NOT been sent.")
                print(result)

            except Exception as e:
                print(f"Error: {e}")

        elif choice == "4":

            print_section("SEARCH MEMORY")

            query = input("Enter search term: ").strip()

            if not query:
                print("Search term cannot be empty.")
                continue

            try:
                rows = tools.call(
                    "search_memory",
                    query=query,
                    limit=5
                )

                if rows:
                    for row in rows:
                        print(
                            f"\n[{row['id']}] "
                            f"{row['subject']}"
                        )
                        print(f"Content: {row['body']}")
                        print(f"Source: {row['source']}")
                else:
                    print("No matching records found.")

            except Exception as e:
                print(f"Error: {e}")

        elif choice == "5":

            print_section("SAVE MEMORY")

            key = input("Enter memory key: ").strip()
            value = input("Enter memory value: ").strip()

            if not key or not value:
                print("Memory key and value cannot be empty.")
                continue

            try:
                result = tools.call(
                    "save_memory",
                    key=key,
                    value=value
                )

                print("Memory saved successfully.")
                print(result)

            except Exception as e:
                print(f"Error: {e}")

        elif choice == "6":

            print_section("CALENDAR AND TASK SYNC")
            tasks = memory.calendar_tasks()
            if not tasks:
                print("No synchronized tasks.")
            for task in tasks:
                print(
                    f"[{task['email_id']}] {task['task']}"
                    f"\nDue: {task['due_date'] or 'Not specified'}"
                    f"\nStatus: {task['status']}"
                    "\n"
                )

        elif choice == "7":

            print_section("ARCHIVE EMAIL")
            email_id = input("Enter Email ID: ").strip()
            reason = input("Archive reason (optional): ").strip()

            if not email_id:
                print("Email ID is required.")
                continue

            try:
                print(tools.call(
                    "archive_email",
                    email_id=email_id,
                    reason=reason
                ))
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "8":

            print("\nExiting Email Organizer.")
            break

        elif choice == "9":

            print_section("ENTER AND PROCESS A NEW EMAIL")
            email_id = input("Email ID: ").strip()
            sender = input("Sender email: ").strip()
            subject = input("Subject: ").strip()
            body = input("Email body: ").strip()
            received_at = input(
                "Received at (optional; press Enter for current time): "
            ).strip()

            if not all([email_id, sender, subject, body]):
                print("Email ID, sender, subject, and body are required.")
                continue

            if not received_at:
                from datetime import datetime
                received_at = datetime.now().isoformat(timespec="seconds")

            try:
                result = agent.run([{
                    "id": email_id,
                    "sender": sender,
                    "subject": subject,
                    "body": body,
                    "received_at": received_at
                }])
                show_agent_execution(result)
                print(
                    "\nThis email was processed locally. Its analysis and any "
                    "draft are stored in SQLite; the sample JSON file was not changed."
                )
            except Exception as e:
                print(f"Error processing email: {e}")

        else:
            print("Invalid choice. Select 1-9.")


def main():

    parser = argparse.ArgumentParser(description="Agentic Email Organizer")
    parser.add_argument(
        "--lab",
        type=int,
        choices=range(1, 15),
        metavar="1-14",
        help="Run one worklet lab and print its implementation evidence."
    )
    parser.add_argument(
        "--all-labs",
        "--labs",
        dest="all_labs",
        action="store_true",
        help="Run and display Labs 1–14 sequentially."
    )
    args = parser.parse_args()
    load_dotenv()

    base = Path(__file__).resolve().parent.parent
    email_file = base / "data" / "emails.json"

    additional_emails = []
    if args.all_labs or args.lab is not None:
        additional_emails = collect_optional_email(email_file)

    # Connector and adapter.
    raw_connector = JSONEmailConnector(email_file, additional_emails)

    # Memory.
    memory = MemoryStore()

    try:
        email_connector = MCPStyleEmailAdapter(raw_connector, memory)

        # Skills.
        skills = EmailSkills(LLMClient())

        # Tools.
        tools = ToolRegistry(email_connector, memory)
        agent = EmailOrganizerAgent(tools, skills, memory)

        if args.lab is not None:
            from .labs.demo import run_lab_demo
            result = run_lab_demo(
                args.lab, tools, skills, email_connector, memory, base
            )
            print_section(f"LAB {args.lab}: {result['title']}")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        if args.all_labs:
            from .labs.demo import run_lab_demo
            for lab_number in range(1, 15):
                result = run_lab_demo(
                    lab_number, tools, skills, email_connector, memory, base
                )
                print_section(f"LAB {lab_number}: {result['title']}")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            print_section("ALL LABS COMPLETE")
            print("Labs completed: 14")
            print("Capstone report file: not generated")
            tool_demo(tools, memory, agent)
            return

        print_section("AGENTIC EMAIL ORGANIZER")
        print("Starting automatic email processing...")

        result = agent.run()

        # Display five evidence sections.
        show_agent_execution(result)
        show_tool_execution(result)
        show_skill_execution(result)
        show_memory_retrieval(memory)
        show_connector(raw_connector, email_connector)

        # Interactive demonstration.
        tool_demo(tools, memory, agent)

    finally:
        memory.close()


if __name__ == "__main__":
    main()
