"""Lab 5A: list_files is discovered from the manifest; client stays generic."""
FILES={"/safe/README.md":"Agentic AI demo","/safe/data.csv":"event,count\\nTalk,12"}
CAPABILITIES=[
 {"name":"read_file","kind":"resource","input":{"path":"str"},"output":{"content":"str"}},
 {"name":"list_files","kind":"resource","input":{"directory":"str"},"output":{"files":"list"}}
]
class MCPServer:
    def discover(self): return CAPABILITIES
    def read_file(self,path): return {"content":FILES[path]} if path in FILES else {"error":"file not found"}
    def list_files(self,directory):
        return {"files":[p for p in FILES if p.startswith(directory.rstrip("/")+"/")]}
class MCPClient:
    def __init__(self,server): self.server=server
    def discover(self): return self.server.discover()
    def call(self,name,**kwargs):
        manifest={c["name"]:c for c in self.discover()}
        if name not in manifest: raise ValueError("Unknown capability")
        return getattr(self.server,name)(**kwargs)
if __name__ == "__main__":
    c=MCPClient(MCPServer())
    print("Discovered:",c.discover())
    print("list_files:",c.call("list_files",directory="/safe"))
