# Craft: write it the way the house would have

The Law ([law.md](law.md)) decides whether code is *right*: modeled, typed, honest, tested. Craft
decides whether it reads like it was written by a maintainer of *this* repository, someone with
years in the codebase, writing before AI assistants existed. Each H-rule is grounded in a finding
in [research.md](research.md), cited as (F1)…(F8).

Craft findings go in the same ledger as Law findings, with the same severities and penalties. Rule
IDs are `H1`…`H16`.

The organizing principle is **H1**. Almost every other rule here says "do what the house does, and
here is the default when the house is silent." The defaults come from the pre-2020 corpus. They
never override a convention the repo already has.

---

## The house fingerprint

Before writing in a repository, the Writer runs:

```
python3 -I <skill-dir>/scripts/fingerprint.py <repo-root> [<dir-or-file you will touch> ...]
```

It reads the last 400 non-merge commits and the source files near the change. It prints the
commit-message convention (prefix style, mood, length, body and trailer habits, issue-reference
style), comment density and comment style, docstring or doc-comment habits, TODO form, indentation,
line length, error idiom counts and the median function length in the touched area. Save the
output as `fingerprint.md` beside the charter. The Reviewer and the Auditor get the path and judge
H-rules against it, not against their own taste.

If the script can't run (no Python, not a git repo), do the same thing by hand: `git log -30
--no-merges --format='%s%n%b---'` on the touched paths, and read three neighboring files whole.
Write down what you saw. A missing fingerprint is not a reason to skip H1.

---

## MAJOR

**H1: match the house before any general rule.** The repo's own conventions beat every default in
this file, and every default in this file beats your habits. That covers naming case, error
handling idiom, comment density and voice, doc-comment format, import grouping, test layout and
naming, log style and commit format. When neighboring code and the repo overall disagree, match the
neighbors (Git's CodingGuidelines: "match the _local_ convention … even if it doesn't match the
overall style"). An inconsistency you introduce is a finding even when your version is "better."
Fix the house style only as a separate, preparatory change, and only if asked. (F1)

**H4: functions are the size and shape the house writes.** Calibrate against the fingerprint's
median and against the language baseline: median 3–9 lines in Java, Ruby, Python, Go and JS, with
p90 under about 35, and median 12–16 in C, with p90 under about 70. Cyclomatic complexity above 10
appears in under 5% of functions in the Python, Java, Ruby and most Go codebases studied. A new
function past the house's p90 length or CCN 10 needs a reason a reviewer would accept: a parser, a
state machine, a protocol switch. "It does several things" is not a reason, it's L16. Prefer guard
clauses and early returns over nesting. In C, a single `goto out`/`goto fail` cleanup label is the
idiom (3.5–12 per KLOC in Git, Redis, curl, PostgreSQL and SQLite), not a smell. (F4)

**H5: errors follow the language's idiom, narrowly, with context.**

- Python: catch the specific exception you expect. `try: x = d[k]` / `except KeyError:` is the
  house idiom when absence is a normal branch (EAFP), and it may legitimately `pass` or fall through
  *when the absent case is the intended behavior*. `except Exception` is for a process boundary
  that logs and re-raises or reports, never in library code to "be safe." Chain with `raise … from
  exc` when translating.
- Go: `if err != nil { return err }` when no context is added, `fmt.Errorf("parsing %q: %v", name,
  err)` (or `%w` where the repo's Go version and history use it) when it is. Error strings are
  lowercase with no trailing punctuation. No `panic` in library code for recoverable conditions.
- C: return codes checked at every call, cleanup by `goto`, invariants by `assert`.
- Java: precondition checks at public entry points (Guava's `checkNotNull`/`checkArgument`), and
  specific exceptions. No empty `catch {}`.
- JS/TS: no `try` around code that can't throw. No `.catch(() => {})`. Rejections are handled or
  propagated.

The message names the value and the operation, so whoever reads the log can act on it. (F6)

**H6: no speculative surface area.** Don't add parameters, flags, options, environment variables,
config keys, retry loops, timeouts, fallback chains, feature toggles, "strategy" hooks, or `try`
blocks around code that cannot raise, unless the task needs them now. AI-assisted code
characteristically carries unused constructs. Pre-2020 diffs had a median of 5–22 source lines.
This rule is L29's `yagni` aimed at the surface of a change, and L29's safety carve-out applies:
real validation, security and data-loss handling are never speculative. (F2, F8)

**H7: reuse and move, don't paste.** Before writing five or more lines that resemble something in
the repo, find the original (`rg` for a distinctive token) and call it, or move it somewhere both
callers can reach. A near-duplicate with a few names changed is a finding even if each copy is
clean. Don't over-correct into premature abstraction either: two call sites that merely look alike
but change for different reasons stay separate. (F8)

**H11: a bug fix comes with the test that would have caught it.** Write it in the repo's existing
test style and location, name it for the behavior, and confirm it fails without the fix (say in
the ledger that you saw it fail). Git's SubmittingPatches: "Make sure that you have tests for the
bug you are fixing." If the repo has no test infrastructure for that code, say so in the ledger
instead of inventing a framework. (F2)

**H14: assert invariants, validate at the edge, trust in between.** Inputs from outside the process
are validated once at the boundary (L10, L30). Conditions that can only be false if *this* code has
a bug are stated as assertions in the house form (SQLite `assert` at 38 per KLOC, PostgreSQL
`Assert`, Guava `checkState`), or not at all. Never re-validate them as runtime branches with
invented fallback behavior. (F6)

**H15: every API you call exists in the version the repo uses.** For each external function, method,
option, flag or import a change introduces, confirm it in the installed source or the lockfile's
version (`site-packages/`, `node_modules/`, `go doc`, `mvn dependency:tree`, the vendored copy), not
from memory. A plausible method that doesn't exist, or exists only in a newer major version, is a
finding. Record in the ledger what was checked and where. (F8)

**H16: no assistant artifacts.**

- **CAPITAL:** a placeholder that stands in for real code (`# ... existing code ...`, `// rest of
  implementation`, `pass  # TODO implement`, a stub returning fake data) in anything reported as
  done.
- **MAJOR:** text addressed to a chat rather than a codebase ("as requested", "here's the updated",
  "now we", "this fixes the issue you mentioned"), changelog notes inside code ("changed from X to
  Y", "previously this was…", "new:" / "updated:" prefixes), invented example values shipped as
  real config (`example.com`, `your-api-key`, `foo@bar.com`, lorem ipsum), and hardcoded debugging
  output.

(F5, F8)

## MINOR

**H2: comment only where a careful reader would otherwise be surprised.** Comments in pre-2020
production code carry what the code can't: units and sentinel values on fields ("timeout in
seconds", "-1 if unset", "or nil"), invariants and ordering assumptions ("we rely on the child XID
following its parent's"), why the obvious approach is wrong, design rationale for a structure, the
RFC section, the issue number, and open questions with the trade-off spelled out. They rarely
narrate. So:

- Narration is judged by **density, not by instance**. Human code does contain the occasional
  section label: Django 3.0 has about 48 "# Check if …" / "# Loop over …" comments in 55 KLOC,
  roughly 1 per KLOC, mostly heading a long block. The tell is narration as a *habit*: a label on
  most blocks of a short function, `# Step 1:` / `# Step 2:` sequences, `# Initialize the counter`
  above `count = 0`, `# Return the result` above `return result`, or a comment that restates a name.
  Flag a change whose narration comments run past about 1 per 25 new code lines, or that labels
  consecutive trivial statements. Don't flag a lone section label heading a long block in a house
  that does the same.
- Density lands inside the house band from the fingerprint, which varies from about 4 comment lines
  per 100 code lines (nginx) to about 58 (Rails). Too many is as foreign as too few.
- Voice matches the house. Django's style guide bans "we" in comments; Redis and PostgreSQL use "we"
  freely.
- Where the project bans comments outright (L2), there are none, and this rule's job is done.

(F1, F5)

**H3: doc comments follow the house rule, not a template.** Go: every exported identifier gets a
comment that begins with its name ("Len returns …"). Java libraries: Javadoc on public API. Python:
the house docstring style (reST, Google or NumPy) where the module already uses docstrings, PEP 257
form, and Django's "state the expected behavior; don't start with 'Tests that'" for tests. Never
pad a private three-line helper with an Args/Returns block that restates its signature unless the
whole house does exactly that. (F5)

**H8: names are idiomatic and sized to their scope.** Short conventional names in tight scopes
(`i`, `n`, `err`, `ctx`, `buf`, a one- or two-letter Go receiver), domain words in wider ones (L9,
L26). Never version or hype words in an identifier (`process_v2`, `newHandler`, `ImprovedParser`,
`enhanced_`, `final_`, `_fixed`, `smart`, `robust`), and never a meaningless placeholder in a wide
scope (`data`, `result`, `item`, `obj`, `temp`, `info`) where a domain word exists. (F7)

**H9: the diff contains the change and nothing else.** No reformatting, re-wrapping, import
reordering or quote-style changes on lines you didn't otherwise need to touch. Preserve the file's
line endings, final newline, indentation character and encoding. `git diff --check` is clean. If
the formatter the repo uses would reformat your lines, run the repo's formatter config, not your
default. (F2)

**H12: output goes through the house channel, in the house voice.** Use the repo's logger and its
level conventions. No `print`/`console.log` left in library code. No emoji, ASCII banners, "✅
Success!" lines or exclamation marks in logs, CLI output or errors, unless the project already
does exactly that. (F3, F8)

**H13: markers in the house form, with a condition.** `TODO(owner):` where the house marks owners
(Go stdlib 52%, Guava 81%, Prometheus 66%), `XXX` for an open question where the house does that
(PostgreSQL). Every marker says what would have to be true to resolve it. Never leave a marker for
work in the current change (L21). (F7)

## PROCESS: checked at the commit gate

**H10: the commit message reads like the house's history.** Rewrites L19's default. From the
fingerprint, match the prefix convention (`area: `, `BUG:`/`ENH:`, `Fixed #123 -- `, Conventional
Commits *only if the history already uses them*: they appear in 0–4% of pre-2020 commits in all 22
projects studied), the mood (imperative in Git and Linux, past tense in Django), the capitalization,
trailing period habit, issue-reference style and trailers. When the history gives no signal: `area:
imperative summary`, at most 50 characters (hard limit 72), no trailing period. Then a blank line,
then a body wrapped at 72 that says what was wrong, why this fixes it, and any alternative rejected.

What the body is not: a bulleted inventory of every file touched (3+ bullet lists appear in under
2% of commits in most projects), headings, bold text, emoji (0.0–0.3%), or vocabulary like
*comprehensive*, *robust*, *seamless*, *leverage*, *enhance*, *delve*, *streamline*, *crucial*
(each under 2 per 1,000 human commits). Keep any trailers the user's own configuration requires.
(F3)

---

## The human-read test

The Auditor ends every gate with one question, asked of the whole diff and the commit message as
they would appear in `git log -p`: *would a long-time maintainer of this repository, reading this
cold, find anything that marks it as written by a tool rather than by a colleague?* Anything
specific that fails that test is reported under the H-rule it breaks. If nothing specific fails it,
nothing gets reported. "Feels AI-ish" with no location is not a finding.
