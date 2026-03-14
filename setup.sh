#!/usr/bin/env bash
set -euo pipefail

echo "Installing OpenCode plugin dependencies..."
bun install

echo "Installing global skills for OpenCode..."
npx skills add vercel-labs/agent-skills -g -y --agent opencode --skill web-design-guidelines
npx skills add anthropics/skills -g -y --agent opencode --skill frontend-design
npx skills add nextlevelbuilder/ui-ux-pro-max-skill -g -y --agent opencode --skill ui-ux-pro-max
npx skills add obra/superpowers -g -y --agent opencode --skill systematic-debugging
npx skills add supercent-io/skills-template -g -y --agent opencode --skill security-best-practices database-schema-design performance-optimization code-review
npx skills add wshobson/agents -g -y --agent opencode --skill architecture-patterns api-design-principles python-performance-optimization nodejs-backend-patterns tailwind-design-system
npx skills add supabase/agent-skills -g -y --agent opencode --skill supabase-postgres-best-practices

echo "Setup complete."
