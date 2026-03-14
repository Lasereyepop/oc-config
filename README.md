# OpenCode Config

Personal global OpenCode configuration for fullstack development, study sessions,
UI review, backend design, and local markdown-based issue tracking.

## Setup

Clone this repo into the OpenCode config directory and run the bootstrap script:

```bash
git clone <repo-url> ~/.config/opencode
cd ~/.config/opencode
bash setup.sh
```

`setup.sh` installs plugin dependencies and the global skills used by the custom
agents.

## Structure

```text
.
├── AGENTS.md         # Global rules and issue-tracking behavior
├── agents/           # Custom primary and subagent definitions
├── prompts/          # Prompt files for built-in agents
├── tools/            # Global custom tools, including issue tracker integration
├── opencode.json     # Main OpenCode config
├── package.json      # Tool/plugin dependency manifest
├── bun.lock          # Locked dependency versions
├── setup.sh          # Reinstalls dependencies and skills on a new machine
└── README.md
```

## Agents

- `build` - primary coding agent with full tool access and a stack-aware prompt
- `plan` - read-only planning and analysis agent
- `study` - primary exam-prep mode focused on teaching, not implementing
- `reviewer` - code review across JS/TS, Python, C++, Java, and Rust
- `designer` - UI and UX design review with accessibility and visual feedback
- `backend` - database, API, and systems-focused analysis
- `tutor` - concept explanation and guided learning support

## Skills

Installed globally by `setup.sh`:

- `web-design-guidelines`
- `frontend-design`
- `ui-ux-pro-max`
- `systematic-debugging`
- `code-review`
- `database-schema-design`
- `performance-optimization`
- `security-best-practices`
- `api-design-principles`
- `architecture-patterns`
- `tailwind-design-system`
- `python-performance-optimization`
- `nodejs-backend-patterns`
- `supabase-postgres-best-practices`

These live in `~/.agents/skills/` and are used selectively through agent skill
permissions.

## Issue Tracker

This config includes a global issue tracker tool built around local `issues/*.md`
files in each project.

- Python script: `tools/issues.py`
- OpenCode custom tool wrapper: `tools/issues.ts`
- Exposed tools: `issues_list`, `issues_summary`, `issues_read`,
  `issues_create`, `issues_update`, `issues_close`

Global rules in `AGENTS.md` tell agents to use `issues_summary` at session start
when an `issues/` directory exists. `opencode.json` also includes
`instructions: ["issues/*.md"]` so issue files can be pulled into context.

## Notes

- `node_modules/` is intentionally ignored; run `bash setup.sh` after cloning
- Keep secrets out of `opencode.json`; prefer environment variables if you add
  MCP servers or other integrations later
