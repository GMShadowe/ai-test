import asyncio
import json

async def run_file_operation(operation: dict) -> dict:
    # Purpose: serialize the request so paths and content are passed safely.
    payload = json.dumps(operation)

    # Purpose: invoke a fixed helper as subject; no model-supplied shell code.
    script = r'''
import json, sys
from pathlib import Path

root = Path("/workspace").resolve()
data = json.load(sys.stdin)
path = (root / data["path"]).resolve()

if path != root and root not in path.parents:
    print(json.dumps({"ok": False, "error": "Path outside workspace"}))
    raise SystemExit(0)

try:
    if data["op"] == "read":
        if not path.is_file():
            result = {"ok": False, "error": "Not a regular file"}
        elif path.stat().st_size > 100_000:
            result = {"ok": False, "error": "File exceeds 100 KB limit"}
        else:
            result = {"ok": True, "content": path.read_text(encoding="utf-8")}
    elif data["op"] == "write":
        content = data["content"]
        if len(content.encode("utf-8")) > 100_000:
            result = {"ok": False, "error": "Content exceeds 100 KB limit"}
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            result = {"ok": True, "path": str(path)}
    else:
        result = {"ok": False, "error": "Unknown operation"}
except (OSError, ValueError, UnicodeError) as exc:
    result = {"ok": False, "error": str(exc)}

print(json.dumps(result))
'''

    process = await asyncio.create_subprocess_exec(
        "sudo", "-n", "/usr/local/bin/subject-shell",
        "python3 -c " + repr(script) + " <<'SUBJECT_INPUT'\n" + payload + "\nSUBJECT_INPUT",
        cwd="/home/ai",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        return {"ok": False, "error": stderr.decode(errors="replace")[-2000:]}
    try:
        return json.loads(stdout.decode())
    except json.JSONDecodeError:
        return {"ok": False, "error": "Invalid helper response"}
