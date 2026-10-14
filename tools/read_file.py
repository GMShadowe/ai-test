import asyncio
import json

from tools.sandbox import resolve_path

TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a UTF-8 text file inside /workspace.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
}


async def execute(path: str) -> dict:
    try:
        # Validate the path before sending it to the helper.
        target = resolve_path(path)
        payload = json.dumps({
            "op": "read",
            "path": str(target.relative_to("/workspace")),
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
