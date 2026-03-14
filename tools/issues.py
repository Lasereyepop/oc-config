import argparse
import glob
import os
import re
from datetime import datetime

ISSUES_DIR = "issues"
STATUS_RE = re.compile(r"^# \[(?P<status>[^\]]+)\] (?P<title>.+)$")
VALID_TYPES = ["task", "bug", "feature", "refactor"]


def ensure_dir():
    os.makedirs(ISSUES_DIR, exist_ok=True)


def issue_files():
    return sorted(glob.glob(os.path.join(ISSUES_DIR, "*.md")))


def parse_header(first_line):
    match = STATUS_RE.match(first_line.strip())
    if not match:
        return "OPEN", first_line.strip().lstrip("# ").strip()
    return match.group("status"), match.group("title")


def normalize_slug(title):
    slug = "".join(c.lower() if c.isalnum() else "-" for c in title)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "untitled"


def next_issue_id():
    max_id = 0
    for path in issue_files():
        base = os.path.basename(path)
        issue_id = base.split("-", 1)[0]
        if issue_id.isdigit():
            max_id = max(max_id, int(issue_id))
    return max_id + 1


def find_issue_path(issue_id):
    normalized = str(issue_id).zfill(3) if str(issue_id).isdigit() else str(issue_id)
    matches = glob.glob(os.path.join(ISSUES_DIR, f"{normalized}*.md"))
    return sorted(matches)[0] if matches else None


def read_issue_file(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_issue_file(path, content):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def append_section(content, heading, body):
    body = body.strip()
    if not body:
        return content
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    section = f"\n\n## {heading}\n- {stamp} - {body}\n"
    return content.rstrip() + section


def replace_field(content, field, value):
    pattern = re.compile(rf"^\*\*{re.escape(field)}:\*\* .*?$", re.MULTILINE)
    replacement = f"**{field}:** {value}"
    if pattern.search(content):
        return pattern.sub(replacement, content, count=1)
    return content.rstrip() + f"\n{replacement}\n"


def replace_status(content, new_status):
    lines = content.splitlines()
    if not lines:
        return content
    _, title = parse_header(lines[0])
    lines[0] = f"# [{new_status}] {title}"
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def field_value(line, field):
    prefix = f"**{field}:** "
    if line.startswith(prefix):
        return line[len(prefix):].strip()
    return None


def list_issues(_args):
    ensure_dir()
    files = issue_files()
    if not files:
        print("No issues found.")
        return

    print(f"{'ID':<6} {'Status':<10} {'Type':<10} {'Title'}")
    print("-" * 100)
    for path in files:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
        status, title = parse_header(lines[0] if lines else "")
        issue_type = "task"
        for line in lines:
            value = field_value(line.strip(), "Type")
            if value is not None:
                issue_type = value
                break
        issue_id = os.path.basename(path).split("-", 1)[0]
        print(f"{issue_id:<6} {status:<10} {issue_type:<10} {title}")


def summary_issues(_args):
    ensure_dir()
    files = issue_files()
    if not files:
        print("No issues found.")
        return

    for path in files:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
        status, title = parse_header(lines[0] if lines else "")
        issue_type = "task"
        assignee = "Unassigned"
        created = ""
        for line in lines:
            stripped = line.strip()
            value = field_value(stripped, "Type")
            if value is not None:
                issue_type = value
                continue
            value = field_value(stripped, "Assignee")
            if value is not None:
                assignee = value
                continue
            value = field_value(stripped, "Created")
            if value is not None:
                created = value
        issue_id = os.path.basename(path).split("-", 1)[0]
        created_part = f" | created {created}" if created else ""
        print(f"{issue_id} | {status} | {issue_type} | {assignee} | {title}{created_part}")


def new_issue(args):
    ensure_dir()
    issue_id = next_issue_id()
    filename = f"{issue_id:03d}-{normalize_slug(args.title)}.md"
    path = os.path.join(ISSUES_DIR, filename)
    content = f"""# [OPEN] {args.title}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Type:** {args.type}
**Assignee:** {args.assignee}

## Description
{args.desc}

## Acceptance Criteria
- [ ] 
"""
    write_issue_file(path, content)
    print(f"Created issue: {path}")


def read_issue(args):
    path = find_issue_path(args.id)
    if not path:
        print(f"Issue {args.id} not found.")
        return
    print(read_issue_file(path))


def close_issue(args):
    path = find_issue_path(args.id)
    if not path:
        print(f"Issue {args.id} not found.")
        return
    content = read_issue_file(path)
    content = replace_status(content, "CLOSED")
    content = replace_field(content, "Closed", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if args.note:
        content = append_section(content, "Closure Note", args.note)
    write_issue_file(path, content)
    print(f"Closed issue: {path}")


def update_issue(args):
    path = find_issue_path(args.id)
    if not path:
        print(f"Issue {args.id} not found.")
        return
    content = read_issue_file(path)
    if args.assignee:
        content = replace_field(content, "Assignee", args.assignee)
    if args.type:
        content = replace_field(content, "Type", args.type)
    if args.status:
        content = replace_status(content, args.status.upper())
    if args.note:
        content = append_section(content, "Progress Notes", args.note)
    content = replace_field(content, "Updated", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    write_issue_file(path, content)
    print(f"Updated issue: {path}")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    p_list = subparsers.add_parser("list")
    p_list.set_defaults(func=list_issues)

    p_summary = subparsers.add_parser("summary")
    p_summary.set_defaults(func=summary_issues)

    p_new = subparsers.add_parser("new")
    p_new.add_argument("title")
    p_new.add_argument("--type", default="task", choices=VALID_TYPES)
    p_new.add_argument("--assignee", default="Unassigned")
    p_new.add_argument("--desc", default="TODO")
    p_new.set_defaults(func=new_issue)

    p_read = subparsers.add_parser("read")
    p_read.add_argument("id")
    p_read.set_defaults(func=read_issue)

    p_close = subparsers.add_parser("close")
    p_close.add_argument("id")
    p_close.add_argument("--note", default="")
    p_close.set_defaults(func=close_issue)

    p_update = subparsers.add_parser("update")
    p_update.add_argument("id")
    p_update.add_argument("--note", default="")
    p_update.add_argument("--assignee")
    p_update.add_argument("--type", choices=VALID_TYPES)
    p_update.add_argument("--status", choices=["OPEN", "IN_PROGRESS", "BLOCKED", "CLOSED"])
    p_update.set_defaults(func=update_issue)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
