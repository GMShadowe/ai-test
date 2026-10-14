import os
import shlex
import subprocess
from pathlib import PurePosixPath

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("SANDBOX_HOST", "")
USER = os.getenv("SANDBOX_USER", "")
WORKDIR = PurePosixPath(
    os.getenv("SANDBOX_WORKDIR", "/workspace")
)
SSH_KEY = os.getenv("SSH_KEY_PATH", "")


def validate_config():
    if not HOST or HOST == "YOUR_VM_IP" or not USER:
        raise RuntimeError("Sandbox SSH configuration is incomplete")

    if not SSH_KEY or not os.path.isfile(SSH_KEY):
        raise RuntimeError("Configure SSH_KEY_PATH in .env")

    if not WORKDIR.is_absolute():
        raise RuntimeError("Sandbox workdir must be absolute")


def validate_path(path: str) -> str:
    requested = PurePosixPath(path)

    if not requested.is_absolute():
        requested = WORKDIR / requested

    if ".." in requested.parts:
        raise ValueError("Parent-directory traversal is not allowed")

    normalized = PurePosixPath(os.path.normpath(str(requested)))

    if normalized != WORKDIR and WORKDIR not in normalized.parents:
        raise ValueError("Path is outside the permitted workspace")

    return str(normalized)


def run_remote(command: str, timeout: int = 15) -> dict:
    validate_config()

    remote_command = "bash -lc " + shlex.quote(command)

    try:
        result = subprocess.run(
            [
                "ssh",
                "-i", SSH_KEY,
                "-o", "BatchMode=yes",
                "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=yes",
                f"{USER}@{HOST}",
                remote_command,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Execution timed out"}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}

    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-4000:],
    }
