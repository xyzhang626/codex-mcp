#!/usr/bin/env python3
"""Codex MCP Server - Call the real Codex CLI (`codex exec`) via MCP."""

import asyncio
import json
import shutil
import uuid
from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("codex")

# Store for async tasks
_tasks: dict[str, dict] = {}


def _find_codex() -> str:
    """Find the codex binary path."""
    path = shutil.which("codex")
    if not path:
        raise FileNotFoundError("codex CLI not found in PATH. Install it first: npm install -g @openai/codex")
    return path


async def _call_codex(prompt: str, model: str | None = None) -> str:
    """Run `codex exec <prompt>` and return stdout."""
    codex_bin = _find_codex()
    cmd = [codex_bin, "exec"]
    if model:
        cmd.extend(["-m", model])
    cmd.append(prompt)

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        err_msg = stderr.decode().strip() or f"codex exec exited with code {proc.returncode}"
        raise RuntimeError(err_msg)

    return stdout.decode().strip()


@mcp.tool()
async def codex_exec(prompt: str, model: str = "") -> str:
    """Ask Codex (OpenAI) a question and get a synchronous response.

    Args:
        prompt: The question or prompt to send to Codex.
        model: Model to use. Options: "gpt-5.1" (default, strongest), "gpt-4.1" (faster). Leave empty for default.
    """
    try:
        reply = await _call_codex(prompt, model or None)
        return json.dumps({
            "status": "success",
            "model": model or "(default)",
            "response": reply,
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def codex_async(prompt: str, model: str = "") -> str:
    """Submit an async question to Codex. Returns a task_id immediately; use codex_poll to check results later.

    Args:
        prompt: The question or prompt to send to Codex.
        model: Model to use. Options: "gpt-5.1" (default), "gpt-4.1" (faster). Leave empty for default.
    """
    task_id = str(uuid.uuid4())[:8]
    _tasks[task_id] = {
        "status": "running",
        "prompt": prompt,
        "model": model or "(default)",
        "submitted_at": datetime.now().isoformat(),
        "result": None,
    }

    async def _run():
        try:
            reply = await _call_codex(prompt, model or None)
            _tasks[task_id]["status"] = "completed"
            _tasks[task_id]["result"] = reply
        except Exception as e:
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["result"] = str(e)

    asyncio.create_task(_run())

    return json.dumps({
        "status": "submitted",
        "task_id": task_id,
        "model": model or "(default)",
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


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
