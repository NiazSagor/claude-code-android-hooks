import json
import subprocess
import re
import sys
from pathlib import Path

print("HOOK RUNNING")

COMPOSABLE_HEADER_RE = re.compile(
    r'@Composable\s*(?:\n\s*)*(?:(?:private|internal|public|protected)\s+)?fun\s+([A-Za-z_][A-Za-z0-9_]*)\s*\('
)

def get_composables(content):
    """Return list of (name, has_params) for non-preview composables."""
    results = []
    for match in COMPOSABLE_HEADER_RE.finditer(content):
        name = match.group(1)
        if name.endswith("Preview"):
            continue

        # Walk forward to find the closing ')' of the parameter list
        start = match.end() - 1  # position of '('
        depth, end_pos = 0, None
        for i, ch in enumerate(content[start:]):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    end_pos = start + i
                    break

        has_params = bool(end_pos and content[match.end():end_pos].strip())
        results.append((name, has_params))
    return results

def has_preview(name, contents):
    pattern = re.compile(rf'@Preview[\s\S]*?\b{name}Preview\b|fun\s+{name}Preview')
    return any(pattern.search(c) for c in contents)

# 1. resolve file from hook stdin
kt_files = []
try:
    hook_input = json.loads(sys.stdin.read())
    fp = hook_input.get("tool_input", {}).get("file_path", "")
    if fp:
        if not fp.endswith(".kt"):
            sys.exit(0)
        kt_files = [fp]
except (json.JSONDecodeError, AttributeError):
    pass

# fallback: git diff (unstaged + staged) — only when stdin gave no file path
if not kt_files:
    try:
        unstaged = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
        staged   = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
        kt_files = [f for f in set(unstaged + staged) if f.endswith(".kt")]
    except subprocess.CalledProcessError:
        sys.exit(0)

if not kt_files:
    sys.exit(0)

must_fix  = []  # zero-arg composables — block, agent can generate preview safely
warnings  = []  # parameterized composables — warn only, agent needs sample data

for file in kt_files:
    path = Path(file)
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue

    composables = get_composables(content)
    if not composables:
        continue

    # search scope: same file + sibling *Preview*.kt files
    search_contents = [content]
    for sibling in path.parent.glob("*Preview*.kt"):
        if sibling.resolve() != path.resolve():
            try:
                search_contents.append(sibling.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                pass

    for name, has_params in composables:
        if not has_preview(name, search_contents):
            (warnings if has_params else must_fix).append((file, name))

if warnings:
    print("Warning — @Preview missing (parameterized composable; add sample data manually):")
    for file, name in warnings:
        print(f"  - {name} ({file})")

if must_fix:
    print("Missing @Preview for zero-arg composable(s) — please add:")
    for file, name in must_fix:
        print(f"  - {name} ({file})")
    sys.exit(2)

sys.exit(0)
