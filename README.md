# codex-mcp

An MCP server that wraps the [Codex CLI](https://github.com/openai/codex) (`codex exec`) for use in Claude Code — with sync calls and async tasks.

## Prerequisites

You need the Codex CLI installed and configured:

```bash
npm install -g @openai/codex
codex login
```

## Quick Install

```bash
claude mcp add codex -s user -- uvx --from git+https://github.com/xyzhang626/codex-mcp codex-mcp
```

Then restart Claude Code.

## Tools

### `codex_exec`
Synchronous call — send a prompt to `codex exec`, wait for the response.

### `codex_async`
Submit a prompt asynchronously. Returns a `task_id` immediately.

### `codex_poll`
Poll an async task by `task_id` to get the result.

### `codex_list_tasks`
List all async tasks and their statuses.

## Configuration

Codex CLI uses its own config at `~/.codex/config.toml`. You can override the model per-call:

```
codex_exec(prompt="How are you?", model="gpt-4.1")
```
