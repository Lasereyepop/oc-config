import argparse
import glob
import os
import re
from datetime import datetime

ISSUES_DIR = "issues"
STATUS_RE = re.compile(r"^# \[(?P<status>[^\]]+)\] (?P<title>.+)$")
VALID_TYPES = ["task", "bug", "feature", "refactor"]
ISSUE_ID_RE = re.compile(r"^\d+$")
SECTION_RE_TEMPLATE = r"\n## {heading}\n"


def ensure_dir() -> None:
    os.makedirs(ISSUES_DIR, exist_ok=True)


def issue_files() -> list[str]:
    return sorted(glob.glob(os.path.join(ISSUES_DIR, "*.md")))


def parse_header(first_line: str) -> tuple[str, str]:
    match = STATUS_RE.match(first_line.strip())
    if not match:
        title = first_line.strip()
        if title.startswith("# "):
            title = title[2:]
        return "OPEN", title.strip()
    return match.group("status"), match.group("title")


def normalize_slug(title: str) -> str:
    slug = "".join(c.lower() if c.isalnum() else "-" for c in title)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "untitled"


def sanitize_title(title: str) -> str:
    collapsed = " ".join(title.splitlines()).strip()
    return collapsed or "Untitled issue"


def sanitize_description(description: str) -> str:
    return description.strip() or "TODO"


def next_issue_id() -> int:
    max_id = 0
    for path in issue_files():
        base = os.path.basename(path)
        issue_id = base.split("-", 1)[0]
        if ISSUE_ID_RE.fullmatch(issue_id):
            max_id = max(max_id, int(issue_id))
    return max_id + 1


def normalize_issue_id(issue_id: str | int) -> str | None:
    issue_id_str = str(issue_id).strip()
    if not ISSUE_ID_RE.fullmatch(issue_id_str):
        return None
    return issue_id_str.zfill(3)


def find_issue_path(issue_id: str | int) -> str | None:
    normalized = normalize_issue_id(issue_id)
    if normalized is None:
        return None
    matches = glob.glob(os.path.join(ISSUES_DIR, f"{normalized}*.md"))
    safe_matches = [
        path
        for path in matches
        if os.path.abspath(path).startswith(os.path.abspath(ISSUES_DIR) + os.sep)
    ]
    return sorted(safe_matches)[0] if safe_matches else None


def read_issue_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_issue_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def create_issue_file(path: str, content: str) -> bool:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        return False

    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(content)
    return True


def append_section(content: str, heading: str, body: str) -> str:
    body = body.strip()
    if not body:
        return content

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"- {stamp} - {body}\n"
    header = f"\n## {heading}\n"
    pattern = re.compile(SECTION_RE_TEMPLATE.format(heading=re.escape(heading)))
    match = pattern.search(content)
    if not match:
        return content.rstrip() + f"{header}{entry}"

    insert_at = content.find("\n## ", match.end())
    if insert_at == -1:
        insert_at = len(content)

    prefix = content[:insert_at].rstrip("\n")
    suffix = content[insert_at:]
    return f"{prefix}\n{entry}{suffix}"


def replace_field(content: str, field: str, value: str) -> str:
    pattern = re.compile(rf"^\*\*{re.escape(field)}:\*\* .*?$", re.MULTILINE)
    replacement = f"**{field}:** {value}"
    if pattern.search(content):
        return pattern.sub(replacement, content, count=1)

    first_section_index = content.find("\n## ")
    if first_section_index == -1:
        return content.rstrip() + f"\n\n{replacement}\n"

    prefix = content[:first_section_index].rstrip("\n")
    suffix = content[first_section_index:]
    return f"{prefix}\n{replacement}\n{suffix}"


def replace_status(content: str, new_status: str) -> str:
    lines = content.splitlines()
    if not lines:
        return content
    _, title = parse_header(lines[0])
    lines[0] = f"# [{new_status}] {title}"
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def field_value(line: str, field: str) -> str | None:
    prefix = f"**{field}:** "
    if line.startswith(prefix):
        return line[len(prefix):].strip()
    return None


def parse_issue_meta(path: str) -> dict[str, str]:
    lines = read_issue_file(path).splitlines()
    status, title = parse_header(lines[0] if lines else "")
    meta = {
        "id": os.path.basename(path).split("-", 1)[0],
        "status": status,
        "title": title,
        "type": "task",
        "assignee": "Unassigned",
        "created": "",
    }
    for line in lines:
        stripped = line.strip()
        for field in ("Type", "Assignee", "Created"):
            value = field_value(stripped, field)
            if value is not None:
                meta[field.lower()] = value
    return meta


def list_issues(_args: argparse.Namespace) -> None:
    ensure_dir()
    files = issue_files()
    if not files:
        print("No issues found.")
        return

    print(f"{'ID':<6} {'Status':<10} {'Type':<10} {'Title'}")
    print("-" * 100)
    for path in files:
        meta = parse_issue_meta(path)
        print(f"{meta['id']:<6} {meta['status']:<10} {meta['type']:<10} {meta['title']}")


def summary_issues(_args: argparse.Namespace) -> None:
    ensure_dir()
    files = issue_files()
    if not files:
        print("No issues found.")
        return

    for path in files:
        meta = parse_issue_meta(path)
        created_part = f" | created {meta['created']}" if meta["created"] else ""
        print(
            f"{meta['id']} | {meta['status']} | {meta['type']} | {meta['assignee']} | {meta['title']}{created_part}"
        )


def build_issue_content(title: str, issue_type: str, assignee: str, description: str) -> str:
    return f"""# [OPEN] {title}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Type:** {issue_type}
**Assignee:** {assignee}

## Description
{description}

## Acceptance Criteria
- [ ] 
"""


def new_issue(args: argparse.Namespace) -> None:
    ensure_dir()
    title = sanitize_title(args.title)
    description = sanitize_description(args.desc)
    slug = normalize_slug(title)
    issue_id = next_issue_id()

    while True:
        filename = f"{issue_id:03d}-{slug}.md"
        path = os.path.join(ISSUES_DIR, filename)
        content = build_issue_content(title, args.type, args.assignee, description)
        if create_issue_file(path, content):
            print(f"Created issue: {path}")
            return
        issue_id += 1


def read_issue(args: argparse.Namespace) -> None:
    path = find_issue_path(args.id)
    if not path:
        print(f"Issue {args.id} not found.")
        return
    print(read_issue_file(path))


def close_issue(args: argparse.Namespace) -> None:
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


def update_issue(args: argparse.Namespace) -> None:
    path = find_issue_path(args.id)
    if not path:
        print(f"Issue {args.id} not found.")
        return
    content = read_issue_file(path)
    changed = False
    if args.assignee:
        content = replace_field(content, "Assignee", args.assignee)
        changed = True
    if args.type:
        content = replace_field(content, "Type", args.type)
        changed = True
    if args.status:
        content = replace_status(content, args.status.upper())
        changed = True
    if args.note:
        content = append_section(content, "Progress Notes", args.note)
        changed = True
    if not changed:
        print(f"No changes provided for issue {args.id}.")
        return
    content = replace_field(content, "Updated", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    write_issue_file(path, content)
    print(f"Updated issue: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage markdown issues in the current project.")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

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
    args.func(args)


if __name__ == "__main__":
    main()
