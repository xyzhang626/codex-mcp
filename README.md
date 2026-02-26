# codex-mcp

An MCP server that lets you query OpenAI models (Codex) directly from Claude Code — with sync calls, async tasks, and multi-turn conversations.

## Quick Install

```bash
claude mcp add codex -s user -- uvx --from git+https://github.com/xyzhang626/codex-mcp codex-mcp
```

Then create `~/.codex-mcp/config.toml` with your API credentials and restart Claude Code.

## Configuration

Config is loaded in this order (later overrides earlier):

1. **`~/.codex-mcp/config.toml`** (recommended)
2. **Environment variables** (fallback)
3. **Built-in defaults**

### Config File (`~/.codex-mcp/config.toml`)

```toml
api_key = "sk-xxx"
api_base = "https://api.openai.com/v1"
model = "gpt-4.1"
# system_prompt = "You are Codex, a helpful coding assistant. Provide concise, practical advice."
```

#### Azure OpenAI Example

```toml
api_key = "your-azure-key"
api_base = "https://your-resource.openai.azure.com/openai/v1"
model = "gpt-4.1"
```

### Environment Variables (fallback)

| Variable | Config key | Default |
|---|---|---|
| `OPENAI_API_KEY` | `api_key` | `""` |
| `OPENAI_API_BASE` | `api_base` | `https://api.openai.com/v1` |
| `CODEX_MODEL` | `model` | `gpt-4.1` |
| `CODEX_SYSTEM_PROMPT` | `system_prompt` | `"You are Codex, a helpful coding assistant..."` |

Environment variables override config file values when both are set.

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
