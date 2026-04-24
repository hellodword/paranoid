# paranoid

## Why this exists

The current LLM agent ecosystem makes me uneasy. Too much of it relies on unsafe defaults, and some of those defaults have become widely accepted as normal.

A simple example: the official documentation for many popular MCP tools recommends running commands like `npx -y foo@latest`. That may be convenient, but it also means executing whatever happens to be published as `latest` at that moment. For security-sensitive workflows, especially those involving agents, this is not a tradeoff I am comfortable with. At the same time, solutions like [toolhive](https://github.com/stacklok/toolhive) feel too heavyweight for my use case, for reasons I may explain in the future.

I looked into whether `npm` or `npx` could lock both the package version and the package hash in a single command. As far as I can tell, they cannot. I found a workaround.

This is only one small part of a much broader concern I have about the agent tooling ecosystem. I plan to keep documenting issues, mitigations, and safer patterns as I continue digging.

## npm / npx workaround

1. Add an audited package:

```shell
npm run add-cli "@upstash/context7-mcp@2.1.8"
```

2. Replace `npx` with a repo-local `npm run` entry:

Original:

```toml
[mcp_servers.context7]
command = "npx"
args = [
  "-y",
  "@upstash/context7-mcp"
]

[mcp_servers.playwright]
command = "npx"
args = [
  "-y",
  "@playwright/mcp",
  "--cdp-endpoint", "http://1.2.3.4:9222"
]
```

Now:

```toml
[mcp_servers.context7]
command = "npm"
args = [
  "-C", "/path/to/paranoid",
  "run", "--silent",
  "@upstash/context7-mcp"
]

[mcp_servers.playwright]
command = "npm"
args = [
  "-C", "/path/to/paranoid",
  "run", "--silent",
  "@playwright/mcp",
  "--",
  "--cdp-endpoint", "http://1.2.3.4:9222"
]
```

## uv / uvx workaround

This repo also includes a `uvx` replacement based on `pyproject.toml` and `uv.lock`.
The lockfile remains the source of truth, but Python tools are installed into a repo-local
vendor directory instead of `.venv`. That avoids copied-venv breakage when the whole directory
is moved to a different path.

1. Add an audited Python CLI package with an exact pin:

```shell
uv --directory /path/to/paranoid run --no-project python scripts/add_uv_cli.py mcp-server-time==2026.1.26
```

2. Build or refresh the vendored tool directory:

```shell
uv --directory /path/to/paranoid run --no-project python scripts/sync_uv_tools.py
```

3. Replace `uvx ...` with `uv --directory ... run --no-project --offline python scripts/run_uv_tool.py ...`:

Original:

```toml
[mcp_servers.mcp-server-time]
command = "uvx"
args = [
  "mcp-server-time"
]
```

Now:

```toml
[mcp_servers.mcp-server-time]
command = "uv"
args = [
  "--directory", "/path/to/paranoid",
  "run",
  "--no-project",
  "--offline",
  "python",
  "scripts/run_uv_tool.py",
  "mcp-server-time"
]
```

If the package name and executable name differ, add the package name but run the executable name.
For example, add `httpie==3.2.4`, then run `http`:

```shell
uv --directory /path/to/paranoid run --no-project --offline python scripts/run_uv_tool.py http --version
```

`scripts/add_uv_cli.py` only accepts exact pins in the form `package==version`.
That is intentional. Allowing floating specs such as `package`, `>=1.0`, or `@latest`
would defeat the point of this repository.

The repo-local `.uv-tools` directory is the runnable artifact. Copying `repo + .uv-tools`
to a new path is enough to keep commands working. If you also copy `.uv-cache`, then the target
environment can rebuild `.uv-tools` offline:

```shell
uv --directory /path/to/paranoid run --no-project --offline python scripts/sync_uv_tools.py --offline
```

The vendored artifacts are platform and Python-version specific. This repo pins Python `3.13`
via `.python-version`, and expects the target environment to provide a compatible interpreter.
