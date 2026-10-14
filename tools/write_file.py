import asyncio
import json

from tools.sandbox import resolve_path

TOOL = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write UTF-8 text to a file inside /workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
}


async def execute(path: str, content: str) -> dict:
    try:
        target = resolve_path(path)
        payload = json.dumps({
            "op": "write",
            "path": str(target.relative_to("/workspace")),
            "content": content,
        })

        process = await asyncio.create_subprocess_exec(
            "sudo", "-n", "-u", "subject",
            "/usr/local/bin/subject-file",
            cwd="/home/ai",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate(payload.encode())

        if process.returncode != 0:
            return {"ok": False, "error": stderr.decode(errors="replace")[-2000:]}
        return json.loads(stdout.decode())
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
