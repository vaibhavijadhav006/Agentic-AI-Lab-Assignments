"""Lab 5B: read_file is restricted to /safe/ and returns structured errors."""
from pathlib import PurePosixPath
FILES={"/safe/README.md":"Safe content","/safe/data/info.txt":"Data"}
SAFE_ROOT="/safe"
class MCPServer:
    def read_file(self,path):
        candidate=PurePosixPath(path)
        # Reject traversal, absolute paths outside root, and paths outside the safe prefix.
        normalized=str(candidate)
        if not normalized.startswith(SAFE_ROOT+"/") or ".." in candidate.parts:
            return {"error":{"code":"PATH_FORBIDDEN","message":f"Access denied: {path}"}}
        if normalized not in FILES:
            return {"error":{"code":"NOT_FOUND","message":"File not found"}}
        return {"content":FILES[normalized]}
if __name__ == "__main__":
    s=MCPServer()
    print("Allowed:",s.read_file("/safe/README.md"))
    print("Adversarial attempt:",s.read_file("/private/secrets.txt"))
    print("Traversal attempt:",s.read_file("/safe/../private/secrets.txt"))
