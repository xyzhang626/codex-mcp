#!/usr/bin/env python3
"""Codex MCP Server - Ask OpenAI models for opinions via MCP."""

import asyncio
import json
import os
import uuid
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from openai import AsyncOpenAI

# Config via environment variables
API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEFAULT_MODEL = os.environ.get("CODEX_MODEL", "gpt-4.1")
SYSTEM_PROMPT = os.environ.get(
    "CODEX_SYSTEM_PROMPT",
    "You are Codex, a helpful coding assistant. Provide concise, practical advice.",
)

mcp = FastMCP("codex")

# Store for async tasks and conversation histories
_tasks: dict[str, dict] = {}
_conversations: dict[str, list] = {}


def _get_client() -> AsyncOpenAI:
    extra_headers = {}
    # Azure OpenAI requires api-key header
    if "azure" in API_BASE.lower():
        extra_headers["api-key"] = API_KEY
    return AsyncOpenAI(
        api_key=API_KEY,
        base_url=API_BASE,
        default_headers=extra_headers if extra_headers else None,
    )


async def _call_codex(prompt: str, model: str, conversation_id: str | None) -> tuple[str, str]:
    """Call OpenAI and return (response_text, conversation_id)."""
    client = _get_client()

    if conversation_id and conversation_id in _conversations:
        messages = _conversations[conversation_id]
    else:
        conversation_id = str(uuid.uuid4())[:8]
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
    )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    _conversations[conversation_id] = messages

    return reply, conversation_id


@mcp.tool()
async def codex_exec(prompt: str, model: str = "", conversation_id: str = "") -> str:
    """Ask Codex (OpenAI) a question and get a synchronous response.

    Args:
        prompt: The question or prompt to send to Codex.
        model: Model to use. Options: "gpt-5.1" (default, strongest), "gpt-4.1" (faster). Leave empty for default.
        conversation_id: Optional conversation ID to continue a previous discussion. Leave empty for new conversation.
    """
    use_model = model if model else DEFAULT_MODEL
    try:
        reply, conv_id = await _call_codex(prompt, use_model, conversation_id or None)
        return json.dumps({
            "status": "success",
            "model": use_model,
            "conversation_id": conv_id,
            "response": reply,
            "hint": f"Use conversation_id='{conv_id}' to continue this discussion."
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def codex_async(prompt: str, model: str = "", conversation_id: str = "") -> str:
    """Submit an async question to Codex. Returns a task_id immediately; use codex_poll to check results later.

    Args:
        prompt: The question or prompt to send to Codex.
        model: Model to use. Options: "gpt-5.1" (default), "gpt-4.1" (faster). Leave empty for default.
        conversation_id: Optional conversation ID to continue a previous discussion.
    """
    use_model = model if model else DEFAULT_MODEL
    task_id = str(uuid.uuid4())[:8]
    _tasks[task_id] = {
        "status": "running",
        "prompt": prompt,
        "model": use_model,
        "submitted_at": datetime.now().isoformat(),
        "result": None,
    }

    async def _run():
        try:
            reply, conv_id = await _call_codex(prompt, use_model, conversation_id or None)
            _tasks[task_id]["status"] = "completed"
            _tasks[task_id]["result"] = reply
            _tasks[task_id]["conversation_id"] = conv_id
        except Exception as e:
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["result"] = str(e)

    asyncio.create_task(_run())

    return json.dumps({
        "status": "submitted",
        "task_id": task_id,
        "model": use_model,
        "hint": f"Use codex_poll(task_id='{task_id}') to check results."
    }, ensure_ascii=False, indent=2)


@mcp.tool()
async def codex_poll(task_id: str) -> str:
    """Check the status/result of an async Codex task.

    Args:
        task_id: The task ID returned by codex_async.
    """
    if task_id not in _tasks:
        return json.dumps({"status": "error", "error": f"Unknown task_id: {task_id}"}, indent=2)

    task = _tasks[task_id]
    result = {
        "task_id": task_id,
        "status": task["status"],
        "model": task["model"],
        "prompt": task["prompt"][:100],
    }
    if task["status"] == "completed":
        result["response"] = task["result"]
        result["conversation_id"] = task.get("conversation_id", "")
        result["hint"] = f"Use conversation_id='{result['conversation_id']}' to continue this discussion."
    elif task["status"] == "error":
        result["error"] = task["result"]

    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def codex_list_tasks() -> str:
    """List all async Codex tasks and their statuses."""
    summary = []
    for tid, t in _tasks.items():
        summary.append({
            "task_id": tid,
            "status": t["status"],
            "model": t["model"],
            "prompt": t["prompt"][:80],
            "submitted_at": t["submitted_at"],
        })
    return json.dumps(summary, ensure_ascii=False, indent=2)


@mcp.tool()
async def codex_conversations() -> str:
    """List all active conversation IDs and their message counts."""
    convs = []
    for cid, msgs in _conversations.items():
        convs.append({
            "conversation_id": cid,
            "message_count": len(msgs),
            "last_user_msg": next((m["content"][:80] for m in reversed(msgs) if m["role"] == "user"), ""),
        })
    return json.dumps(convs, ensure_ascii=False, indent=2)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
