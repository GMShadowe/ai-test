from tools.sandbox import resolve_path


TOOL = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write UTF-8 text to a file inside the experiment workspace.",
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
    if len(content.encode("utf-8")) > 100_000:
        return {"ok": False, "error": "Content exceeds 100 KB limit"}

    try:
        file_path = resolve_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return {"ok": True, "path": str(file_path)}
    except (OSError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
