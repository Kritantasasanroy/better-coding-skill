"""Mechanical triage for better-coding: Law and Craft patterns, no model involved.

    python3 -I triage.py <repo-root>                      whole repo (tests/docs/generated excluded)
    python3 -I triage.py <repo-root> --diff <base-ref>    only lines added since <base-ref>
    python3 -I triage.py <repo-root> --files a.py b.ts    only these files
    python3 -I triage.py <repo-root> --commit HEAD        also check that commit's message
    options: --include-tests  --max-lines N (default 50)  --max-branches N (default 10)

Prints markdown. Near-verdicts are close to findings on their own; leads need judgment.
Exit status is 0 whether or not anything was found: triage informs, it doesn't gate.
"""
import argparse
import ast
import os
import re
import shutil
import subprocess
import sys

SOURCE_EXT = {".py": "py", ".ts": "ts", ".tsx": "ts", ".js": "js", ".jsx": "js", ".mjs": "js",
              ".go": "go", ".java": "java", ".kt": "java", ".rb": "rb", ".rs": "rs",
              ".c": "c", ".h": "c", ".cc": "c", ".cpp": "c", ".cs": "java", ".php": "php"}
EXCLUDE = re.compile(
    r"(^|/)(tests?|__tests__|spec|testdata|fixtures|docs?|node_modules|vendor|third_party|"
    r"dist|build|\.venv|venv|__pycache__|migrations|generated)/"
    r"|(^|/)(test_[^/]*\.py|[^/]*_test\.(py|go)|[^/]*\.(test|spec)\.[jt]sx?|[^/]*Tests?\.java)$"
    r"|\.min\.js$|\.d\.ts$|\.pb\.go$|_pb2\.py$")
HASH_LANGS = {"py", "rb"}


class Pattern:
    def __init__(self, rule, tier, label, regex, langs=None, flags=0, comment_only=False,
                 code_only=False):
        self.rule = rule
        self.tier = tier
        self.label = label
        self.regex = re.compile(regex, flags)
        self.langs = langs
        self.comment_only = comment_only
        self.code_only = code_only


COMMENT_PREFIX = r"(?:#|//|/?\*)\s*"
NARRATION = (r"(?:step \d+\s*[:.-]|initiali[sz]e (?:the |a )?\w+|loop (?:through|over)|iterate "
             r"(?:through|over)|return (?:the )?result|check (?:if|whether)|create (?:a|an|the) "
             r"\w+$|define (?:the|a) |import (?:the )?(?:necessary|required)|call the |increment "
             r"(?:the )?\w+$|set (?:the )?\w+ to |get the \w+$)")

PATTERNS = [
    # near-verdicts
    Pattern("C1", "near", "checker suppression",
            r"#\s*noqa|#\s*type:\s*ignore|eslint-disable|@ts-ignore|@ts-nocheck|//\s*nolint|"
            r"#\s*pylint:\s*disable|@SuppressWarnings\((?![^)]*\)\s*//)"),
    Pattern("C1", "near", "bare any/Any",
            r"(?:->|:|\[|,)\s*Any\b|\bimport\b[^\n]*\bAny\b|:\s*any\b|<any>|\bas any\b|\bany\[\]",
            {"py", "ts"}, code_only=True),
    Pattern("C3", "near", "swallowed error",
            r"^\s*except\s*(?:(?:Base)?Exception(?:\s+as\s+\w+)?)?\s*:\s*\n\s*(?:pass|\.\.\.|"
            r"return\s*(?:None)?|continue)\s*$", {"py"}, re.M),
    Pattern("C3", "near", "empty catch",
            r"catch\s*(?:\([^)]*\))?\s*\{\s*\}|\.catch\(\s*\(?\s*\w*\s*\)?\s*=>\s*\{?\s*\}?\s*\)",
            {"ts", "js", "java"}),
    Pattern("H16", "near", "placeholder standing in for code",
            r"(?:#|//|/\*)\s*\.\.\.\s*(?:existing|rest of|remaining|other|previous|same as)\b|"
            r"(?:#|//)\s*(?:rest of (?:the )?(?:code|implementation)|implementation (?:goes )?here|"
            r"your (?:code|logic) here)|raise NotImplementedError\(\s*\)\s*#\s*TODO", None, re.I),
    Pattern("H16", "near", "text addressed to a chat, or a changelog in code",
            r"(?:#|//|/?\*)\s*(?:as requested|here'?s the (?:updated|new|fixed|complete)|this (?:fixes|"
            r"resolves) the (?:issue|bug|problem) you|updated to (?:fix|use|handle)|changed from "
            r"\w+ to|previously,? (?:this|we|it)|\b(?:NEW|UPDATED|FIXED|ADDED):)", None, re.I),
    # leads
    Pattern("H2", "lead", "narration comment", COMMENT_PREFIX + NARRATION, None, re.I,
            comment_only=True),
    Pattern("H5", "lead", "broad catch",
            r"^\s*except\s+(?:Base)?Exception\b|catch\s*\(\s*(?:final\s+)?(?:Exception|Throwable)"
            r"\b", {"py", "java"}, re.M),
    Pattern("H8", "lead", "versioned or hype identifier",
            r"\b(?:def|class|function|const|let|var|func|type|interface)\s+\w*(?:_v\d+|V\d+\b|"
            r"_new\b|New[A-Z]?\w*Impl|Improved|Enhanced|Advanced|Smart|Robust|_final\b|Final[A-Z]|"
            r"_fixed\b|_updated\b|_better\b)"),
    Pattern("H12", "lead", "emoji in source",
            "[\U0001F300-\U0001FAFF✅❌✨⚠⭐❗]"),
    Pattern("H16", "lead", "invented example value in code",
            r"example\.(?:com|org)|your[_-]?api[_-]?key|lorem ipsum|foo@bar|john\.?doe|"
            r"(?:api_?key|secret|password|token)\s*=\s*[\"'](?:sk-|xxx|changeme|secret|test)", None,
            re.I, code_only=True),
    Pattern("L5", "lead", "Optional / nullable",
            r"Optional\[|:\s*\w+(?:\[[^\]]*\])?\s*\|\s*None\b|\?\s*:\s*\w", {"py", "ts"}),
    Pattern("L26", "lead", "generic-suffix class",
            r"\b(?:class|interface|struct|type)\s+\w*(?:Manager|Helper|Utils?|Processor|Generator|"
            r"Handler|Builder|Engine|Coordinator|Data|Info)\b"),
    Pattern("L26", "lead", "adjective-as-state class",
            r"\b(?:class|interface|struct|type)\s+(?:Connected|Active|Verified|Paid|Cancelled|"
            r"Expired|Enabled|Disabled|Pending|Valid|Invalid)[A-Z]\w*"),
    Pattern("L27", "lead", "verb-named class",
            r"\bclass\s+(?:Process|Generate|Validate|Check|Handle|Fetch|Parse|Calculate|Compute|"
            r"Create|Update|Send)[A-Z]\w*"),
    Pattern("L27", "lead", "module-level function", r"^def \w+", {"py"}, re.M),
    Pattern("L21", "lead", "debug leftover / unowned marker",
            r"\bconsole\.(?:log|debug)\(|^\s*print\((?!.*file=)|\bdebugger;|\bpdb\.set_trace|"
            r"\bbreakpoint\(\)|\bfmt\.Print(?:ln|f)?\(|System\.out\.print|\bTODO\b(?!\()|\bFIXME\b(?!\()",
            None, re.M),
]

AI_WORDS = re.compile(r"\b(comprehensive|robust|seamless(?:ly)?|leverag(?:e|es|ing)|enhanc(?:e|ed|es|"
                      r"ement)|delve|streamlin(?:e|ed|es)|crucial|holistic|showcase|utiliz(?:e|es|ing)|"
                      r"elevate|furthermore|additionally)\b", re.I)


def git(root, *args):
    return subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True,
                          errors="replace")


def list_files(root, include_tests):
    proc = git(root, "ls-files")
    if proc.returncode == 0:
        paths = proc.stdout.splitlines()
    else:
        paths = []
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if not x.startswith(".") and x != "node_modules"]
            paths += [os.path.relpath(os.path.join(d, f), root) for f in fs]
    out = []
    for p in paths:
        if os.path.splitext(p)[1] not in SOURCE_EXT:
            continue
        if not include_tests and EXCLUDE.search(p):
            continue
        out.append(p)
    return out


def added_lines(root, base):
    """{path: set(line numbers added since base)}, including untracked files."""
    proc = git(root, "diff", "-U0", "--no-color", base, "--")
    if proc.returncode != 0:
        sys.exit("git diff failed: " + proc.stderr.strip())
    result, path = {}, None
    for line in proc.stdout.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
            if path:
                result.setdefault(path, set())
        elif line.startswith("@@") and path:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            result[path].update(range(start, start + count))
    for p in git(root, "ls-files", "--others", "--exclude-standard").stdout.splitlines():
        result[p] = None
    return result


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def is_comment_line(line, lang):
    s = line.strip()
    if lang in HASH_LANGS:
        return s.startswith("#")
    return s.startswith("//") or s.startswith("/*") or s.startswith("*")


def docstring_lines(text, lang):
    """Line numbers inside Python string-literal statements (docstrings)."""
    if lang != "py":
        return set()
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return set()
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and \
                isinstance(node.value.value, str):
            out.update(range(node.lineno, getattr(node, "end_lineno", node.lineno) + 1))
    return out


def scan_patterns(path, text, lang, allowed, hits):
    lines = text.split("\n")
    docs = docstring_lines(text, lang)
    seen = set()
    for pat in PATTERNS:
        if pat.langs and lang not in pat.langs:
            continue
        for m in pat.regex.finditer(text):
            n = line_of(text, m.start())
            if allowed is not None and n not in allowed:
                continue
            src = lines[n - 1]
            if pat.comment_only and not is_comment_line(src, lang):
                continue
            if pat.code_only and (is_comment_line(src, lang) or n in docs):
                continue
            key = (pat.rule, pat.label, n)
            if key in seen:
                continue
            seen.add(key)
            hits.append((pat.tier, pat.rule, pat.label, path, n, src.strip()[:140]))


class PyFunctionShape(ast.NodeVisitor):
    BRANCHES = (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.IfExp, ast.comprehension,
                ast.ExceptHandler, ast.Assert)

    def __init__(self, lines):
        self.lines = lines
        self.found = []

    def code_lines(self, node, start, end):
        """Non-blank, non-comment lines, docstring excluded: comparable to lizard's NLOC."""
        skip = set()
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                and isinstance(body[0].value.value, str):
            skip = set(range(body[0].lineno, getattr(body[0], "end_lineno", body[0].lineno) + 1))
        n = 0
        for i in range(start, end + 1):
            s = self.lines[i - 1].strip() if i - 1 < len(self.lines) else ""
            if s and not s.startswith("#") and i not in skip:
                n += 1
        return n

    def visit_FunctionDef(self, node):
        end = getattr(node, "end_lineno", node.lineno)
        span = end - node.lineno + 1
        length = self.code_lines(node, node.lineno, end)
        branches = 1 + sum(isinstance(n, self.BRANCHES) for n in ast.walk(node))
        branches += sum(len(n.values) - 1 for n in ast.walk(node) if isinstance(n, ast.BoolOp))
        depth = self.depth(node, 0)
        self.found.append((node.name, node.lineno, length, span, branches, depth))
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def depth(self, node, d):
        nested = (ast.If, ast.For, ast.While, ast.Try, ast.With)
        best = d
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            best = max(best, self.depth(child, d + 1 if isinstance(child, nested) else d))
        return best


def scan_shape(path, text, lang, allowed, args, hits, lizard_paths):
    if lang != "py":
        lizard_paths.append(path)
        return
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        hits.append(("lead", "H4", "could not parse (shape unmeasured)", path, 1, ""))
        return
    shape = PyFunctionShape(text.split("\n"))
    shape.visit(tree)
    for name, lineno, length, span, branches, depth in shape.found:
        if allowed is not None and not (set(range(lineno, lineno + span)) & allowed):
            continue
        reasons = []
        if length > args.max_lines:
            reasons.append(f"{length} lines")
        if branches > args.max_branches:
            reasons.append(f"complexity ~{branches}")
        if depth > 3:
            reasons.append(f"nesting depth {depth}")
        if reasons:
            hits.append(("lead", "H4/L16", "function shape: " + ", ".join(reasons), path, lineno,
                         f"def {name}"))


def scan_lizard(root, paths, args, hits):
    lizard = shutil.which("lizard")
    if not paths:
        return
    if not lizard:
        langs = sorted({SOURCE_EXT[os.path.splitext(p)[1]] for p in paths})
        hits.append(("note", "H4", "function shape not measured for " + ", ".join(langs) +
                     " (install `lizard` to measure); judge it by reading", "-", 0, ""))
        return
    proc = subprocess.run([lizard, "--csv"] + [os.path.join(root, p) for p in paths],
                          capture_output=True, text=True, errors="replace")
    for row in proc.stdout.splitlines():
        cols = [c.strip('"') for c in row.split(",")]
        try:
            nloc, ccn = int(cols[0]), int(cols[1])
        except (ValueError, IndexError):
            continue
        reasons = []
        if nloc > args.max_lines:
            reasons.append(f"{nloc} lines")
        if ccn > args.max_branches:
            reasons.append(f"CCN {ccn}")
        if reasons:
            hits.append(("lead", "H4/L16", "function shape: " + ", ".join(reasons),
                         os.path.relpath(cols[6], root), int(cols[9]), cols[7]))


def scan_orphans(root, scope_texts, all_paths, hits):
    defined = {}
    for path, text in scope_texts.items():
        for m in re.finditer(r"^[ \t]*(?:export\s+)?(?:abstract\s+)?(?:class|struct|interface)\s+([A-Z]\w+)",
                             text, re.M):
            defined.setdefault(m.group(1), (path, line_of(text, m.start())))
    if not defined:
        return
    counts = dict.fromkeys(defined, 0)
    word = re.compile(r"\b(" + "|".join(map(re.escape, defined)) + r")\b")
    for p in all_paths:
        try:
            with open(os.path.join(root, p), encoding="utf-8", errors="replace") as fh:
                for m in word.finditer(fh.read()):
                    counts[m.group(1)] += 1
        except OSError:
            continue
    for name, n in counts.items():
        if re.match(r"Test|.*Tests?$", name):
            continue
        if n <= 1:
            path, line = defined[name]
            hits.append(("lead", "L31", "orphan-class candidate (name appears once)", path, line,
                         "class " + name))


def check_commit(root, rev, hits):
    msg = git(root, "log", "-1", "--format=%B", rev).stdout.rstrip("\n")
    if not msg:
        return
    lines = msg.split("\n")
    subject = lines[0]
    if len(subject) > 72:
        hits.append(("near", "H10", f"subject is {len(subject)} chars (> 72)", "commit " + rev, 1, subject))
    body = [l for l in lines[2:] if l.strip() and not re.match(r"^[A-Z][\w-]+: ", l)]
    if sum(bool(re.match(r"^\s*[-*•]\s", l)) for l in body) >= 3:
        hits.append(("lead", "H10", "body is a bullet list", "commit " + rev, 0, ""))
    if any(re.match(r"^#+\s|\*\*", l) for l in body):
        hits.append(("lead", "H10", "markdown headings/bold in commit body", "commit " + rev, 0, ""))
    if any(len(l) > 76 for l in body):
        hits.append(("lead", "H10", "body not wrapped at ~72", "commit " + rev, 0, ""))
    if re.search("[\U0001F300-\U0001FAFF☀-➿]", msg):
        hits.append(("near", "H10", "emoji in commit message", "commit " + rev, 0, ""))
    words = sorted({w.lower() for w in AI_WORDS.findall(msg)})
    if words:
        hits.append(("lead", "H10", "AI-register vocabulary: " + ", ".join(words), "commit " + rev, 0, ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--diff")
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--commit")
    ap.add_argument("--include-tests", action="store_true")
    ap.add_argument("--max-lines", type=int, default=50)
    ap.add_argument("--max-branches", type=int, default=10)
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    all_paths = list_files(root, include_tests=True)
    if args.diff:
        added = added_lines(root, args.diff)
        scope = {p: lines for p, lines in added.items()
                 if os.path.splitext(p)[1] in SOURCE_EXT and os.path.exists(os.path.join(root, p))}
    elif args.files:
        scope = {os.path.relpath(os.path.abspath(f), root): None for f in args.files}
    else:
        scope = {p: None for p in list_files(root, args.include_tests)}

    hits, texts, lizard_paths = [], {}, []
    for path, allowed in sorted(scope.items()):
        lang = SOURCE_EXT.get(os.path.splitext(path)[1])
        if not lang:
            continue
        try:
            with open(os.path.join(root, path), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        if "Code generated" in text[:400] or "DO NOT EDIT" in text[:400]:
            continue
        texts[path] = text
        scan_patterns(path, text, lang, allowed, hits)
        scan_shape(path, text, lang, allowed, args, hits, lizard_paths)
    scan_lizard(root, lizard_paths, args, hits)
    scan_orphans(root, texts, all_paths, hits)
    if args.commit:
        check_commit(root, args.commit, hits)

    print(f"# Triage: {len(texts)} files in scope"
          + (f" (lines added since {args.diff})" if args.diff else ""))
    for tier, title in (("near", "Near-verdicts (fix or confirm)"),
                        ("lead", "Leads (judge, don't auto-fix)"), ("note", "Not measured")):
        rows = [h for h in hits if h[0] == tier]
        print(f"\n## {title}: {len(rows)}")
        for _, rule, label, path, line, src in sorted(rows, key=lambda h: (h[1], h[3], h[4])):
            loc = f"{path}:{line}" if line else path
            print(f"- [{rule}] {loc} — {label}" + (f" — `{src}`" if src else ""))


if __name__ == "__main__":
    main()
