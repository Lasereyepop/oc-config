## Issue Tracking

Projects may include an `issues/` directory managed by a local markdown issue
tracker.

- At session start, if an `issues/` directory exists in the current project,
  call `issues_summary` to get a compact view of active work before doing other
  planning.
- Use `issues_read` when you need the full detail for a specific issue.
- Use `issues_create` when you discover a bug, identify a task, or plan a
  follow-up feature.
- Use `issues_update` to append progress notes, change assignees, or adjust
  issue status while work is in progress.
- Use `issues_close` when work tied to an issue is complete.
- Prefer `issues_summary` over `issues_list` when a compact context view is
  enough.
