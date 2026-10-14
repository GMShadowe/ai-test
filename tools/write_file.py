import base64
import shlex

from tools.sandbox import run_remote, validate_path


def write_file(path: str, content: str) -> dict:
    try:
        safe_path = validate_path(path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    encoded = base64.b64encode(content.encode()).decode()

    command = (
        "mkdir -p -- "
        + shlex.quote(str(__import__("posixpath").dirname(safe_path)))
        + " && printf %s "
        + shlex.quote(encoded)
        + " | base64 -d > "
        + shlex.quote(safe_path)
    )

    return run_remote(command, timeout=10)


TOOL = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": (
            "Write text to a file inside the permitted VM workspace. "
            "Creates parent directories if necessary."
        ),
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
