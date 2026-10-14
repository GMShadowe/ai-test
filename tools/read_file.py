from tools.sandbox import resolve_path


TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a UTF-8 text file inside the experiment workspace.",
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
        file_path = resolve_path(path)
        if not file_path.is_file():
            return {"ok": False, "error": "Not a regular file"}
        if file_path.stat().st_size > 100_000:
            return {"ok": False, "error": "File exceeds 100 KB limit"}

        return {"ok": True, "content": file_path.read_text(encoding="utf-8")}
    except (OSError, ValueError, UnicodeError) as exc:
        return {"ok": False, "error": str(exc)}
