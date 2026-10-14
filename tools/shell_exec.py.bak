import asyncio
import os
from pathlib import Path

from tools.sandbox import WORKSPACE


TOOL = {
    "type": "function",
    "function": {
        "name": "shell_exec",
        "description": (
            "Run a shell command as the ordinary Ubuntu guest user. "
            "The command runs in the experiment workspace with a timeout. "
            "Report the purpose of the command before using this tool."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"}
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    },
}


async def execute(command: str) -> dict:
    if not command.strip():
        return {"ok": False, "error": "Empty command"}

    env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": str(Path.home()),
        "LANG": "C.UTF-8",
        "WORKSPACE": str(WORKSPACE),
    }

    try:
        process = await asyncio.create_subprocess_exec(
            "/bin/bash",
            "--noprofile",
            "--norc",
            "-c",
            command,
            cwd=str(WORKSPACE),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=15
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {"ok": False, "error": "Command timed out after 15 seconds"}

        return {
            "ok": process.returncode == 0,
            "exit_code": process.returncode,
            "stdout": stdout.decode(errors="replace")[-12000:],
            "stderr": stderr.decode(errors="replace")[-4000:],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
