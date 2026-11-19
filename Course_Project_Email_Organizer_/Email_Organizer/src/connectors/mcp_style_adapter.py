class MCPStyleEmailAdapter:
    """
    Adapter used by the agent's ToolRegistry.

    The important Lab-5 idea is that the agent does not directly know
    where email data comes from. It talks to a connector interface.
    """

    def __init__(self, connector, memory=None):
        self.connector = connector
        self.memory = memory

    def list_emails(self):
        return self.connector.call("email.list", {})

    def get_email(self, email_id):
        return self.connector.call("email.get", {"email_id": email_id})

    def list_tools(self):
        tools = self.connector.list_tools()
        if self.memory is not None:
            tools.extend([
                {
                    "name": "memory.search",
                    "description": "Search persisted SQLite email and memory records.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "memory.save",
                    "description": "Save a note to the SQLite memory store.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "value": {"type": "string"}
                        },
                        "required": ["key", "value"]
                    }
                },
                {
                    "name": "system.health",
                    "description": "Return local connector and memory availability.",
                    "input_schema": {"type": "object", "properties": {}}
                }
            ])
        return tools

    def call(self, tool_name, arguments):
        if tool_name.startswith("email."):
            return self.connector.call(tool_name, arguments)
        if self.memory is None:
            raise ValueError(f"Unknown connector tool: {tool_name}")
        if tool_name == "memory.search":
            return self.memory.search(
                arguments["query"], limit=arguments.get("limit", 5)
            )
        if tool_name == "memory.save":
            return self.memory.save_memory(arguments["key"], arguments["value"])
        if tool_name == "system.health":
            return {"status": "OK", "transport": "in-process MCP-style adapter"}
        raise ValueError(f"Unknown connector tool: {tool_name}")
