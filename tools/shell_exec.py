from tools.sandbox import run_remote


def execute(command: str) -> dict:
    if not command.strip():
        return {"ok": False, "error": "Command is empty"}

    return run_remote(command, timeout=15)


TOOL = {
    "type": "function",
    "function": {
        "name": "shell_exec",
        "description": (
            "Execute a shell command inside the isolated Ubuntu VM. "
            "Commands are subject to VM permissions and a 15-second timeout. "
            "Use only for the assigned experiment."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute inside the VM",
                }
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    },
}
