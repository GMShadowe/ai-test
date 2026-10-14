import shlex

from tools.sandbox import run_remote, validate_path


def read_file(path: str) -> dict:
    try:
        safe_path = validate_path(path)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}

    return run_remote(
        "cat -- " + shlex.quote(safe_path),
        timeout=10,
    )


TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a file inside the permitted VM workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"}
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
}
