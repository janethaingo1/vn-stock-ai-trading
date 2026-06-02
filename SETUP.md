# vn-stock-ai-trading — Claude Code Setup

This adds a Buffett-style fundamental analyzer for Vietnamese stocks (`/vn-buffett`) and a `vn-stock-agent` subagent to your Claude Code project.

## File layout (additions)

```
vn-stock-ai-trading/
├── .claude/
│   ├── commands/
│   │   └── vn-buffett.md         # slash command — invoked as /vn-buffett VCB
│   └── agents/
│       └── vn-stock-agent.md     # subagent — autonomous mode
├── scripts/
│   └── vn_buffett.py             # the analyzer (vnstock + rubric)
├── out/                          # auto-created at runtime
└── .mcp.json                     # Obsidian MCP wiring (optional)
```

## One-time setup

```bash
# From repo root
cd ~/Desktop/Antigravity/vn-stock-ai-trading

# Install Python deps (uses the system python3 — venv recommended but optional)
pip install -U vnstock pandas

# Smoke test the script directly (no Claude Code needed)
python3 scripts/vn_buffett.py VCB
```

If the smoke test prints a report and writes to `out/buffett-VCB-<today>.md`, the core works. The Claude Code wrapper just orchestrates it.

## Optional — Obsidian MCP

If you want analyses written directly to your Obsidian vault (path `02-Areas/Investments/<TICKER> Buffett Analysis.md`):

1. Install the Obsidian Local REST API plugin in your vault (community plugin).
2. Copy your API key from the plugin settings.
3. Export it before starting Claude Code:
   ```bash
   export OBSIDIAN_API_KEY="your-key-here"
   ```
4. The `.mcp.json` at repo root will auto-load when you run `claude` from this directory.

Confirm the MCP loaded after starting `claude`:
```
/mcp
```
You should see `obsidian` listed and connected.

## Usage

```bash
cd ~/Desktop/Antigravity/vn-stock-ai-trading
claude
```

Then in the Claude Code session:

| Command | What it does |
|---------|--------------|
| `/vn-buffett VCB`          | Run Buffett analysis on Vietcombank |
| `/vn-buffett FPT`          | Run on FPT (non-bank rubric) |
| `/vn-buffett HPG`          | Run on Hoa Phat (non-bank, manufacturing) |
| "screen Buffett banks for me" | Triggers `vn-stock-agent` autonomously — runs the rubric across all known VN banks |

## Verify the slash command is registered

After `claude` starts, type `/` — `vn-buffett` should appear in the completion list. If it doesn't:

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `/vn-buffett` not in completion list | File is not at `.claude/commands/vn-buffett.md` or has wrong frontmatter | Verify path; ensure YAML frontmatter has `---` delimiters |
| Command runs but says "command not found" | Wrong CWD when invoking `claude` | `cd ~/Desktop/Antigravity/vn-stock-ai-trading` first |
| `vnstock` ImportError | Python deps missing | `pip install -U vnstock pandas` |
| `ratio data not available` | Ticker not on HOSE/HNX/UPCOM, or vnstock source rate-limited | Try a different ticker; rerun (rate limit resets in ~60s) |
| Numbers look wildly off | vnstock data column rename | Update column mapping in `_safe(...)` calls in `vn_buffett.py` |

## What this is NOT

- Not a trading system. Read-only fundamental analysis.
- Not connected to any brokerage. The agent has no order-placement capability.
- Not investment advice. Verify every figure against primary filings before allocating capital.

## Governance

The `vn-stock-agent` is aligned with OWASP Agentic Top 10 (AAI01–AAI10) per Jane's `agent-governance` skill §11. See the agent definition for the full mapping.
