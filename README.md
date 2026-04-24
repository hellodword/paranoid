# paranoid

## Why this exists

The current LLM agent ecosystem makes me uneasy. Too much of it relies on unsafe defaults, and some of those defaults have become widely accepted as normal.

A simple example: the official documentation for many popular MCP tools recommends running commands like `npx -y foo@latest`. That may be convenient, but it also means executing whatever happens to be published as `latest` at that moment. For security-sensitive workflows, especially those involving agents, this is not a tradeoff I am comfortable with.

I looked into whether `npm` or `npx` could lock both the package version and the package hash in a single command. As far as I can tell, they cannot. I found a workaround.

This is only one small part of a much broader concern I have about the agent tooling ecosystem. I plan to keep documenting issues, mitigations, and safer patterns as I continue digging.

## Usage

1. add audited package

```shell
npm run add-cli "@upstash/context7-mcp@2.1.8"
```

2. codex config:

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
  "-C","/path/to/paranoid",
  "run" ,"--silent",
  "@upstash/context7-mcp"
]

[mcp_servers.playwright]
command = "npm"
args = [
  "-C","/path/to/paranoid",
  "run" ,"--silent",
  "@playwright/mcp",
  "--",
  "--cdp-endpoint", "http://1.2.3.4:9222"
]
```
