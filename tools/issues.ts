import os from "node:os"
import path from "node:path"
import { tool } from "@opencode-ai/plugin"

const script = path.join(os.homedir(), ".config/opencode/tools/issues.py")

async function runIssues(context: { directory: string }, args: string[]) {
  const proc = Bun.spawn(["python3", script, ...args], {
    cwd: context.directory,
    stdout: "pipe",
    stderr: "pipe",
  })

  const [stdout, stderr, exitCode] = await Promise.all([
    new Response(proc.stdout).text(),
    new Response(proc.stderr).text(),
    proc.exited,
  ])

  if (exitCode !== 0) {
    throw new Error(stderr.trim() || stdout.trim() || `issues tool failed with exit code ${exitCode}`)
  }

  return stdout.trim()
}

export const list = tool({
  description:
    "List all project issues with ID, status, type, and title. Use when you need the full tracker view.",
  args: {},
  async execute(_args, context) {
    return runIssues(context, ["list"])
  },
})

export const summary = tool({
  description:
    "Get a compact one-line summary of all project issues. Prefer this when you only need current context.",
  args: {},
  async execute(_args, context) {
    return runIssues(context, ["summary"])
  },
})

export const read = tool({
  description: "Read a project issue by numeric ID.",
  args: {
    id: tool.schema.string().describe("Issue ID, for example 001"),
  },
  async execute(args, context) {
    return runIssues(context, ["read", args.id])
  },
})

export const create = tool({
  description:
    "Create a new project issue for a bug, task, feature, or refactor item.",
  args: {
    title: tool.schema.string().describe("Short issue title"),
    type: tool.schema
      .enum(["task", "bug", "feature", "refactor"])
      .describe("Issue type"),
    desc: tool.schema.string().describe("Issue description"),
    assignee: tool.schema
      .string()
      .optional()
      .describe("Optional assignee name"),
  },
  async execute(args, context) {
    return runIssues(context, [
      "new",
      args.title,
      "--type",
      args.type,
      "--desc",
      args.desc,
      "--assignee",
      args.assignee ?? "Unassigned",
    ])
  },
})

export const close = tool({
  description: "Close an existing project issue by ID.",
  args: {
    id: tool.schema.string().describe("Issue ID to close"),
    note: tool.schema
      .string()
      .optional()
      .describe("Optional closure note"),
  },
  async execute(args, context) {
    const command = ["close", args.id]
    if (args.note) {
      command.push("--note", args.note)
    }
    return runIssues(context, command)
  },
})

export const update = tool({
  description:
    "Update an existing project issue with a note, assignee, type, or status.",
  args: {
    id: tool.schema.string().describe("Issue ID to update"),
    note: tool.schema
      .string()
      .optional()
      .describe("Progress note to append"),
    assignee: tool.schema
      .string()
      .optional()
      .describe("New assignee"),
    type: tool.schema
      .enum(["task", "bug", "feature", "refactor"])
      .optional()
      .describe("Updated issue type"),
    status: tool.schema
      .enum(["OPEN", "IN_PROGRESS", "BLOCKED", "CLOSED"])
      .optional()
      .describe("Updated issue status"),
  },
  async execute(args, context) {
    const command = ["update", args.id]
    if (args.note) {
      command.push("--note", args.note)
    }
    if (args.assignee) {
      command.push("--assignee", args.assignee)
    }
    if (args.type) {
      command.push("--type", args.type)
    }
    if (args.status) {
      command.push("--status", args.status)
    }
    return runIssues(context, command)
  },
})
