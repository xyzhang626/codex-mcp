# codex-mcp

An MCP server that lets you query OpenAI models (Codex) directly from Claude Code — with sync calls, async tasks, and multi-turn conversations.

## Quick Install

```bash
claude mcp add codex -s user -e OPENAI_API_KEY=sk-xxx -- uvx --from git+https://github.com/xyzhang626/codex-mcp codex-mcp
```

Then restart Claude Code.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `OPENAI_API_BASE` | `https://api.openai.com/v1` | API base URL (supports Azure) |
| `CODEX_MODEL` | `gpt-4.1` | Default model |
| `CODEX_SYSTEM_PROMPT` | `"You are Codex, a helpful coding assistant..."` | System prompt |

### Azure OpenAI Example

```bash
claude mcp add codex -s user \
  -e OPENAI_API_KEY=your-azure-key \
  -e OPENAI_API_BASE=https://your-resource.openai.azure.com/openai/v1 \
  -e CODEX_MODEL=gpt-4.1 \
  -- uvx --from git+https://github.com/xyzhang626/codex-mcp codex-mcp
```

## Tools

### `codex_exec`
Synchronous call — send a prompt, wait for the response.

### `codex_async`
Submit a prompt asynchronously. Returns a `task_id` immediately.

### `codex_poll`
Poll an async task by `task_id` to get the result.

### `codex_list_tasks`
List all async tasks and their statuses.

### `codex_conversations`
List all active conversations (supports multi-turn via `conversation_id`).

## Multi-turn Conversations

Every response includes a `conversation_id`. Pass it back to continue the discussion:

```
codex_exec(prompt="What is GIL?")
# returns conversation_id="abc123"

codex_exec(prompt="How to avoid it?", conversation_id="abc123")
# continues the same conversation
```
