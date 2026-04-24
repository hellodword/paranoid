from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def build_uv_command(
    uv: str,
    repo_root: Path,
    *extra: str,
    offline: bool = False,
) -> list[str]:
    command = [uv, "--directory", str(repo_root)]
    if offline:
        command.append("--offline")
    command.extend(extra)
    return command


def read_pinned_python(repo_root: Path) -> str | None:
    version_file = repo_root / ".python-version"
    if not version_file.exists():
        return None
    version = version_file.read_text(encoding="utf-8").strip()
    return version or None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Export the locked tools group and sync it into .uv-tools."
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Only use artifacts already present in .uv-cache.",
    )
    args = parser.parse_args(argv)

    uv = shutil.which("uv")
    if uv is None:
        fail("uv not found in PATH")

    repo_root = Path(__file__).resolve().parent.parent
    tools_dir = repo_root / ".uv-tools"
    pinned_python = read_pinned_python(repo_root)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".requirements.txt",
        dir=repo_root,
        delete=False,
    ) as requirements:
        requirements_path = Path(requirements.name)

    try:
        export_command = build_uv_command(
            uv,
            repo_root,
            "export",
            *(["--python", pinned_python] if pinned_python else []),
            "--frozen",
            "--only-group",
            "tools",
            "--no-header",
            "--output-file",
            str(requirements_path),
            offline=args.offline,
        )
        sync_command = build_uv_command(
            uv,
            repo_root,
            "pip",
            "sync",
            *(["--python", pinned_python] if pinned_python else []),
            str(requirements_path),
            "--require-hashes",
            "--target",
            str(tools_dir),
            offline=args.offline,
        )
        subprocess.run(export_command, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(sync_command, check=True)
    finally:
        requirements_path.unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
