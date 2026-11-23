"""House-style fingerprint: what this repo's history and neighboring code actually look like.

    python3 -I fingerprint.py <repo-root> [<path you will touch> ...]

With paths, commits are read from the history of those paths and code from their directories.
Relative paths resolve against the current directory, so run it from the repo or pass absolute
paths. Fewer than 20 commits for the paths falls back to the whole repository's history.
Without paths, the whole repository. Prints markdown, meant to be saved beside the charter and
handed to the Reviewer and the Auditor so craft (H-rules) is judged against the house, not taste.
"""
import ast
import collections
import os
import re
import statistics
import subprocess
import sys

SRC = {".py": "py", ".ts": "ts", ".tsx": "ts", ".js": "js", ".jsx": "js", ".go": "go",
       ".java": "java", ".kt": "java", ".rb": "rb", ".rs": "rs", ".c": "c", ".h": "c",
       ".cc": "c", ".cpp": "c", ".cs": "java", ".php": "php"}
SKIP = re.compile(r"(^|/)(node_modules|vendor|third_party|dist|build|\.venv|venv|migrations)/")
AREA = re.compile(r"^([\w./*{},+-]+(?: [\w./-]+)?): ")
CONV = re.compile(r"^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\([^)]*\))?!?: ")
TRAILER = re.compile(r"^([A-Z][A-Za-z-]+): ", re.M)
PAST = {"added", "fixed", "updated", "removed", "changed", "implemented", "improved", "refactored",
        "moved", "renamed", "made", "converted", "replaced", "corrected", "deleted", "created"}
IMPER = {"add", "fix", "update", "remove", "change", "implement", "improve", "refactor", "move",
         "rename", "make", "convert", "replace", "correct", "delete", "create", "use", "avoid",
         "allow", "drop", "support", "handle", "simplify", "ensure", "teach", "document", "skip",
         "split", "bump", "revert", "set", "prevent", "return", "pass", "mark", "reduce", "switch"}
MIN_PATH_COMMITS = 20
ISSUE_STYLES = [("Fixed #N --", r"^Fixed #\d+ --"), ("Fixes #N", r"\b(?:Fixes|Closes|Resolves) #\d+"),
                ("(#N) in subject", r"\(#\d+\)"), ("JIRA-style KEY-N", r"\b[A-Z][A-Z0-9]+-\d+\b"),
                ("bpo-N / gh-N", r"\b(?:bpo|gh)-\d+"), ("URL to issue", r"https?://\S+/(?:issues|pull)/\d+")]


def git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True,
                          errors="replace").stdout


def pct(n, d):
    return f"{round(100.0 * n / d)}%" if d else "n/a"


def log_messages(root, paths):
    raw = git(root, "log", "--no-merges", "-400", "--format=%B%x1e", "--", *paths)
    return [m.strip("\n") for m in raw.split("\x1e") if m.strip()]


def commits(root, paths):
    msgs = log_messages(root, paths)
    scope = " touching these paths." if paths else "."
    if paths and len(msgs) < MIN_PATH_COMMITS:
        scope = f". Only {len(msgs)} touched these paths, so this is the whole repository's history."
        msgs = log_messages(root, [])
    if not msgs:
        return ["## Commits", "", "No history found."]
    subj = [m.split("\n")[0] for m in msgs]
    n = len(msgs)
    lens = sorted(len(s) for s in subj)
    areas = collections.Counter()
    conv = period = caps = imper = past = 0
    for s in subj:
        if CONV.match(s):
            conv += 1
        elif AREA.match(s):
            areas[AREA.match(s).group(1)] += 1
        rest = CONV.sub("", AREA.sub("", s, count=1), count=1)
        rest = re.sub(r"^(\[[^\]]+\]\s*|Fixed #\d+ -- |Refs #\d+ -- )", "", rest)
        period += s.endswith(".")
        caps += rest[:1].isupper()
        w = (re.match(r"[A-Za-z']+", rest) or re.match("", "")).group(0).lower()
        imper += w in IMPER
        past += w in PAST or s.startswith("Fixed #")
    bodies = [[l for l in m.split("\n")[1:] if l.strip() and not TRAILER.match(l)] for m in msgs]
    with_body = [b for b in bodies if b]
    wrapped = sum(all(len(l) <= 76 for l in b) for b in with_body)
    bullets = sum(sum(bool(re.match(r"^\s*[-*]\s", l)) for l in b) >= 3 for b in with_body)
    trailers = collections.Counter(t for m in msgs for t in set(TRAILER.findall(m))
                                   if t.endswith("-by") or t in ("Fixes", "Closes", "Refs", "Link",
                                                                  "Change-Id", "Bug", "Reviewed-on"))
    issue = [(label, sum(bool(re.search(rx, m, re.M)) for m in msgs)) for label, rx in ISSUE_STYLES]
    issue = [(l, c) for l, c in issue if c]
    out = ["## Commits", "", f"Last {n} non-merge commits{scope}"]
    out.append(f"- Subject length: median {statistics.median(lens)}, ≤50 in {pct(sum(x <= 50 for x in lens), n)}, "
               f"≤72 in {pct(sum(x <= 72 for x in lens), n)}")
    out.append(f"- Prefix: `area: ` {pct(sum(areas.values()), n)}, Conventional Commits {pct(conv, n)}"
               + (f"; common areas: {', '.join(a for a, _ in areas.most_common(8))}" if areas else ""))
    out.append(f"- Mood: imperative {imper}, past tense {past} (of those classifiable)")
    out.append(f"- First word capitalized (after prefix): {pct(caps, n)}; trailing period: {pct(period, n)}")
    out.append(f"- Body present: {pct(len(with_body), n)}; wrapped ≤76: {pct(wrapped, len(with_body))}; "
               f"3+ bullet lists: {pct(bullets, n)}")
    out.append("- Trailers: " + (", ".join(f"{t} {pct(c, n)}" for t, c in trailers.most_common(5)) or "none"))
    out.append("- Issue references: " + (", ".join(f"{l} {pct(c, n)}" for l, c in issue) or "none"))
    out.append("")
    out.append("Recent subjects, verbatim:")
    out += [f"    {s}" for s in subj[:8]]
    return out


def comment_split(text, lang):
    hashy = lang in ("py", "rb")
    code, inline, doc, in_block, block_is_doc = 0, 0, 0, False, False
    trailing = pending = 0
    for raw in text.split("\n"):
        s = raw.strip()
        if pending and not s.startswith("//"):
            if re.match(r"(func|type|var|const|package)\b", s):
                doc += pending
            else:
                inline += pending
            pending = 0
        if in_block:
            doc += block_is_doc
            inline += not block_is_doc
            in_block = "*/" not in s
            continue
        if not s:
            continue
        if hashy and s.startswith("#") and not s.startswith("#!"):
            inline += 1
        elif not hashy and s.startswith("//"):
            if lang == "go":
                pending += 1
            else:
                inline += 1
        elif not hashy and s.startswith("/*"):
            block_is_doc = s.startswith("/**")
            doc += block_is_doc
            inline += not block_is_doc
            in_block = "*/" not in s
        else:
            code += 1
            if re.search(r"\S\s+(#|//|/\*) ?\S", raw) and raw.count('"') % 2 == 0:
                trailing += 1
    return code, inline, doc, trailing


def py_docstring_lines(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return 0
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) \
                and ast.get_docstring(node) is not None:
            first = node.body[0]
            n += getattr(first, "end_lineno", first.lineno) - first.lineno + 1
    return n


def py_functions(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return [], 0, 0
    lines = text.split("\n")
    sizes, documented, public = [], 0, 0
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = getattr(node, "end_lineno", node.lineno)
        doc = ast.get_docstring(node)
        skip = 0
        if doc is not None:
            first = node.body[0]
            skip = getattr(first, "end_lineno", first.lineno) - first.lineno + 1
        n = sum(1 for l in lines[node.lineno - 1:end] if l.strip() and not l.strip().startswith("#"))
        sizes.append(max(1, n - skip))
        if not node.name.startswith("_"):
            public += 1
            documented += doc is not None
    return sizes, documented, public


def code(root, paths):
    tracked = git(root, "ls-files").splitlines()
    if paths:
        dirs = {os.path.dirname(os.path.relpath(os.path.abspath(p), root)) if os.path.isfile(p)
                else os.path.relpath(os.path.abspath(p), root) for p in paths}
        dirs = {"" if d == "." else d for d in dirs}
        files = [f for f in tracked if any(f.startswith(d + "/") or d == "" or f == d for d in dirs)]
    else:
        files = tracked
    files = [f for f in files if os.path.splitext(f)[1] in SRC and not SKIP.search(f)][:3000]
    stats = collections.defaultdict(lambda: collections.Counter())
    widths = collections.defaultdict(list)
    fn_sizes = []
    todo = collections.Counter()
    for f in files:
        lang = SRC[os.path.splitext(f)[1]]
        try:
            with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        if "Code generated" in text[:400] or "DO NOT EDIT" in text[:400]:
            continue
        c, i, d, t = comment_split(text, lang)
        if lang == "py":
            moved = py_docstring_lines(text)
            c, d = c - moved, d + moved
        st = stats[lang]
        st["files"] += 1
        st["code"] += c
        st["inline"] += i
        st["doc"] += d
        st["trailing"] += t
        for line in text.split("\n"):
            if line.strip():
                widths[lang].append(len(line.expandtabs(4)))
                if line.startswith("\t"):
                    st["tab"] += 1
                elif line.startswith("  "):
                    st["space"] += 1
                    lead = len(line) - len(line.lstrip(" "))
                    st["space2"] += lead % 4 == 2
        st["we"] += len(re.findall(r"(?:#|//|\*)[^\n]*\bwe\b", text, re.I))
        st["dq"] += len(re.findall(r'"[^"\n]*"', text)) if lang in ("py", "js", "ts") else 0
        st["sq"] += len(re.findall(r"'[^'\n]*'", text)) if lang in ("py", "js", "ts") else 0
        st["print"] += len(re.findall(r"^\s*print\(|console\.log\(|fmt\.Print", text, re.M))
        st["logger"] += len(re.findall(r"\b(?:log|logger|logging|klog|glog|slog)\.\w+\(", text))
        for m in re.finditer(r"\b(TODO|FIXME|XXX|HACK)(\([^)]*\))?", text):
            todo[m.group(1) + ("(owner)" if m.group(2) else "")] += 1
        if lang == "py":
            sizes, documented, public = py_functions(text)
            fn_sizes += sizes
            st["pub_fn"] += public
            st["pub_fn_doc"] += documented
    out = ["## Code", "", f"{len(files)} source files" + (" in the touched directories." if paths else ".")]
    for lang, st in sorted(stats.items(), key=lambda kv: -kv[1]["code"]):
        if not st["code"]:
            continue
        w = sorted(widths[lang])
        indent = "tabs" if st["tab"] > st["space"] else ("2 spaces" if st["space2"] > st["space"] / 3 else "4 spaces")
        line = (f"- **{lang}** ({st['files']} files, {st['code']} code lines): comments per 100 code lines "
                f"— inline {round(100.0 * st['inline'] / st['code'], 1)}, doc {round(100.0 * st['doc'] / st['code'], 1)}, "
                f"trailing {round(100.0 * st['trailing'] / st['code'], 1)}; indent {indent}; "
                f"line length p95 {w[int(.95 * len(w))] if w else 0}")
        if st["dq"] + st["sq"]:
            line += f"; quotes {'double' if st['dq'] > st['sq'] else 'single'}"
        line += f"; logging calls {st['logger']} vs print/console {st['print']}"
        line += f"; 'we' in comments {st['we']}"
        if lang == "py" and st["pub_fn"]:
            line += f"; public functions with docstrings {pct(st['pub_fn_doc'], st['pub_fn'])}"
        out.append(line)
    if fn_sizes:
        s = sorted(fn_sizes)
        out.append(f"- Python function size (code lines): median {statistics.median(s)}, "
                   f"p90 {s[int(.9 * len(s))]}, max {s[-1]}")
    out.append("- Markers: " + (", ".join(f"{k} {v}" for k, v in todo.most_common()) or "none"))
    return out


def instruction_files(root):
    names = ["AGENTS.md", "CLAUDE.md", ".cursorrules", "CONTRIBUTING.md", "CONTRIBUTING",
             "docs/CONTRIBUTING.md", ".github/CONTRIBUTING.md", ".editorconfig", "setup.cfg",
             "pyproject.toml", ".flake8", ".eslintrc", ".eslintrc.js", ".eslintrc.json",
             ".prettierrc", ".golangci.yml", ".clang-format", "rustfmt.toml", ".rubocop.yml"]
    found = [n for n in names if os.path.exists(os.path.join(root, n))]
    return ["## Written conventions and tool config", "",
            ("Present, read before writing: " + ", ".join(found)) if found else "None found."]


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    paths = sys.argv[2:]
    rel = [os.path.relpath(os.path.abspath(p), root) for p in paths]
    out = [f"# House fingerprint: {os.path.basename(root)}", ""]
    out += instruction_files(root) + [""]
    out += commits(root, rel) + [""]
    out += code(root, paths)
    print("\n".join(out))


if __name__ == "__main__":
    main()
