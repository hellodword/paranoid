from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

EXACT_SPEC_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*(?:\[[A-Za-z0-9._,-]+\])?)==(?P<version>[A-Za-z0-9][A-Za-z0-9._+!-]*)$"
)


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def validate_spec(spec: str) -> None:
    if not EXACT_SPEC_RE.fullmatch(spec):
        fail(
            "invalid package spec: "
            f"{spec!r}\n"
            "expected exact pin in the form package==version"
        )


def main(argv: list[str]) -> int:
    if not argv:
        fail(
            "usage: uv --directory /path/to/paranoid run --no-project "
            "python scripts/add_uv_cli.py package==version [package==version ...]"
        )

    for spec in argv:
        validate_spec(spec)

    uv = shutil.which("uv")
    if uv is None:
        fail("uv not found in PATH")

    repo_root = Path(__file__).resolve().parent.parent
    command = [
        uv,
        "--directory",
        str(repo_root),
        "add",
        "--no-sync",
        "--group",
        "tools",
        *argv,
    ]
    sync_command = [
        uv,
        "--directory",
        str(repo_root),
        "run",
        "--no-project",
        "python",
        "scripts/sync_uv_tools.py",
    ]
    subprocess.run(command, check=True)
    subprocess.run(sync_command, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
