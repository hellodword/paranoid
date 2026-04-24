from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def main(argv: list[str]) -> int:
    if not argv:
        fail("usage: python scripts/run_uv_tool.py <command> [args...]")

    repo_root = Path(__file__).resolve().parent.parent
    tools_dir = repo_root / ".uv-tools"
    if not tools_dir.exists():
        fail(
            "missing .uv-tools; run "
            "'uv --directory /path/to/paranoid run --no-project python scripts/sync_uv_tools.py'"
        )

    sys.path.insert(0, str(tools_dir))

    command_name, *command_args = argv
    for entry_point in importlib.metadata.entry_points(group="console_scripts"):
        if entry_point.name == command_name:
            sys.argv = [command_name, *command_args]
            raise SystemExit(entry_point.load()())

    fail(f"console script not found in .uv-tools: {command_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
