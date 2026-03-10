#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/xyzhang626/codex-mcp"
SKILL_DIR="$HOME/.claude/skills/discuss-with-multi-codex"
SKILL_RAW_URL="https://raw.githubusercontent.com/xyzhang626/codex-mcp/main/skills/discuss-with-multi-codex/SKILL.md"

echo "==> Installing codex-mcp server and skills..."

# 1. Register codex MCP server in Claude Code
echo "==> Registering codex MCP server..."
claude mcp add codex -s user -- uvx --from "git+${REPO_URL}" codex-mcp

# 2. Install discuss-with-multi-codex skill
echo "==> Installing discuss-with-multi-codex skill..."
mkdir -p "$SKILL_DIR"
curl -sSL "$SKILL_RAW_URL" -o "$SKILL_DIR/SKILL.md"

echo ""
echo "Done! Restart Claude Code to use:"
echo "  - codex MCP tools (codex_exec, codex_async, codex_poll)"
echo "  - /discuss-with-multi-codex skill"
