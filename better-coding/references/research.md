# Research: how production code was written before AI assistants

This file is the evidence behind [craft.md](craft.md). Every H-rule there points back to a finding
here. Read it when a rule's reason is in question. You don't need it to apply the rules.

## Method

Everything here comes from code and history written before 1 January 2020, before AI coding
assistants were in general use. Copilot's technical preview opened in mid-2021.

**Commit history.** 756,498 non-merge commits authored before 2020 across 22 long-lived production
projects: CPython, curl, Django, Express, Flask, Git, Go, Guava, Kubernetes, the Linux kernel
(2018–2019 window only, 148,772 commits), nginx, NumPy, PostgreSQL, Prometheus, Rails, React,
Redis, Requests, Rust, Spring Framework, SQLite, Terraform. Measured per commit: subject length,
mood, prefix style, body presence and wrapping, "why" language, trailers, issue references,
bullet lists, emoji, and a set of words that are common in AI-generated prose.

**Diff size.** Every pre-2020 commit in 7 repos small enough to clone in full (Redis, curl,
Requests, Flask, Click, Express, Prometheus), measured with `--numstat` and with tests and docs
separated from source.

**Code.** Source snapshots at the last release tag before 2020: Redis 5.0.7, Git 2.24.0, Django 3.0,
Requests 2.22.0, Flask 1.1.1, Express 4.17.1, React 16.12.0, curl 7.67.0, PostgreSQL 12.1, Guava 28.1,
Spring 5.2.2, Terraform 0.12.18, Prometheus 2.14.0, Go 1.13.5, Rails 6.0.2, Kubernetes 1.17.0, lodash
4.17.15, NumPy 1.17.4, nginx 1.17.6, SQLite 3.30.1. Tests, vendored dependencies, generated files,
docs and examples were excluded, so this is production code only: about 3.1M lines of code
(comments and blank lines not counted) across C, Go, Python, Java, JavaScript and Ruby. Function
length, cyclomatic complexity (CCN) and parameter counts come from `lizard`. Comment density,
comment kinds, error-handling idioms and TODO conventions come from a purpose-built scanner. A
random sample of inline comments was saved per repo, and the Redis, PostgreSQL, Django and Go
samples were read by hand to check what the automatic classifier was counting.

**Primary sources read in full or in part:** Git's `Documentation/SubmittingPatches` and
`Documentation/CodingGuidelines`, and Django's `committing-code.txt` and `coding-style.txt`, all from
the pre-2020 snapshots.

**Contrast with the AI era:** GitClear's 2024 and 2025 code-quality reports (153M and 211M changed
lines, 2020–2024). GitClear sells code analytics, so treat these as directional. Cotroneo, Improta
and Liguori, *Human-Written vs. AI-Generated Code* (ISSRE 2025, arXiv 2508.21634). Ghosh Paul et
al., *Investigating the Smells of LLM Generated Code* (arXiv 2510.03029).

Heuristics are heuristics. The comment classifier treats a comment containing "because", "so
that", "otherwise", "note", "workaround" and similar words as a "why" comment. That undercounts
real reasoning comments that don't use those words. Read the percentages as orders of magnitude
and as differences between projects, not as precise constants.

---

## Finding 1: there is no universal style. The house is the authority.

The strongest result is how much the projects disagree with each other, each one consistently.

| Measure | Lowest | Highest |
| --- | --- | --- |
| Non-license comment lines per 100 code lines | nginx 4 | lodash 121 (JSDoc on every export) |
| Inline (non-doc) comment lines per 100 code lines | Spring 2.6 | Rails 58 |
| Commit subject median length | Requests 24 chars | SQLite 71 chars |
| Commits with a body | Express 11% | Linux 98%, Guava 99% |
| Subjects with an `area:` prefix | Django 0.5% | Linux 97%, Go 82%, Git 71% |
| Imperative mood (of commits with a classifiable first verb) | Django 4% (past tense is policy) | Linux 99.5%, Git 99% |
| Trailers (`Signed-off-by`, `Reviewed-by`, …) | most < 5% | Linux 99.9%, Git 97%, Go 50% |

Django's written policy says "Write detailed commit messages in the past tense, not present tense.
Good: 'Fixed Unicode bug in RSS API.'" Git's says "Describe your changes in imperative mood." Both
are production-grade. Code that "looks human" in Django looks wrong in Git.

Git's CodingGuidelines says it directly: *"just imitate the existing code (this is a good
guideline, no matter which project you are contributing to). It is always preferable to match the
_local_ convention … Modifications to existing code is expected to match the style the surrounding
code already uses (even if it doesn't match the overall style of existing code)."*

→ **H1** (match the house before any general rule) and the fingerprint step in the Writer's recon.

## Finding 2: commits were small, single-purpose and boring

Source lines changed per commit, tests and docs excluded:

| Repo | Commits | Median | p75 | p90 | ≤ 50 lines | Median files |
| --- | --- | --- | --- | --- | --- | --- |
| Express | 5,154 | 5 | 16 | 42 | 92% | 2 |
| Requests | 4,431 | 6 | 17 | 52 | 90% | 1 |
| Flask | 2,798 | 7 | 26 | 66 | 87% | 1 |
| Click | 974 | 8 | 25 | 63 | 87% | 1 |
| curl | 25,084 | 10 | 31 | 96 | 83% | 1 |
| Redis | 7,597 | 10 | 35 | 89 | 82% | 1 |
| Prometheus | 5,317 | 22 | 86 | 329 | 66% | 2 |

Git's guidance: *"Make separate commits for logically separate changes … If your description starts
to get too long, that's a sign that you probably need to split up your commit."* And on style
cleanups: *"Fixing style violations while working on a real change as a preparatory clean-up step
is good, but otherwise avoid useless code churn for the sake of conforming to the style."*

→ **H9** (diff hygiene) and L18 (one logical change).

## Finding 3: commit messages were plain prose, not formatted reports

Across all 756,498 commits:

- **Conventional Commits** (`feat:`, `fix(scope):`) appear in 0–4% of commits in every one of the 22
  projects. Production history before 2020 used `area: summary` prefixes (Linux, Go, Git, curl,
  Terraform, NumPy's `BUG:`/`ENH:`), plain sentences (Rails, Requests, Flask), or ticket-prefixed
  past tense (Django's `Fixed #12345 -- …`).
- **Subjects** fit in 72 characters in 58–99% of commits (median project ~93%). Trailing periods
  are a project convention, not a norm: 2% in Linux, 68% in Django, 72% in Guava.
- **Bullet lists** of three or more items appear in 0–8% of commits (React highest at 8%; most
  projects under 2%). Bodies are paragraphs.
- **Bodies wrap** at about 72 columns in 82–97% of commits in most projects.
- **Why-language** ("because", "otherwise", "instead", "the problem", "which means") appears in
  9–39% of commit bodies. Git's guidance asks a body to explain "what is wrong with the current code
  without the change", "why the result with the change is better", and "alternate solutions
  considered but discarded".
- **Emoji**: 0.0–0.3% of commits in every project.
- **Vocabulary.** Words over-represented in AI-written prose are rare. Per 1,000 human commits:
  *comprehensive* 0.17, *leverage* 0.15, *crucial* 0.13, *seamless(ly)* 0.09, *delve* 0.04,
  *showcase* 0.02, *holistic* 0.01. *Robust* 1.4 and *enhance(d/ment)* 1.8 are higher but still
  rare. *Ensure* is the one word in common use (9.4 per 1,000).

→ **H10** (commit messages) and the rewritten **L19**.

## Finding 4: functions were small and flat, even in "big" C code

| Repo | Lang | Functions | NLOC median | NLOC p90 | > 50 NLOC | CCN median | CCN p90 | CCN > 10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Guava | Java | 12,319 | 3 | 11 | 0.1% | 1 | 3 | 0.4% |
| Rails | Ruby | 11,503 | 3 | 11 | 0.1% | 1 | 3 | 0.6% |
| Spring | Java | 31,943 | 3 | 15 | 0.8% | 1 | 4 | 1.5% |
| Flask | Py | 369 | 4 | 17 | 1.1% | 2 | 6 | 3.3% |
| Django | Py | 5,440 | 5 | 20 | 1.5% | 2 | 7 | 4.7% |
| lodash | JS | 810 | 5 | 15 | 1.2% | 2 | 6 | 3.8% |
| Kubernetes | Go | 21,212 | 6 | 23 | 2.1% | 1 | 6 | 3.0% |
| Prometheus | Go | 2,515 | 7 | 28 | 3.2% | 2 | 7 | 4.9% |
| Go stdlib | Go | 22,412 | 7 | 33 | 5.2% | 2 | 10 | 8.8% |
| React | JS | 4,048 | 8 | 33 | 5.2% | 2 | 8 | 6.3% |
| Terraform | Go | 4,305 | 9 | 40 | 6.7% | 2 | 9 | 7.4% |
| Redis | C | 2,378 | 12 | 47 | 8.6% | 3 | 13 | 14.2% |
| Git | C | 8,784 | 13 | 46 | 8.4% | 3 | 13 | 13.8% |
| SQLite | C | 4,311 | 14 | 51 | 10.4% | 3 | 13 | 13.8% |
| curl | C | 2,326 | 15 | 68 | 14.5% | 4 | 18 | 19.3% |
| PostgreSQL | C | 19,055 | 16 | 72 | 16.8% | 3 | 14 | 15.4% |
| nginx | C | 2,610 | 26 | 92 | 25.1% | 5 | 20 | 25.0% |

Parameters: more than 5 in under 5% of functions everywhere except NumPy's C API (13%).

Long, branchy functions existed, mostly in C state machines and parsers. They were the tail, not
the body. A new 80-line Python function with a CCN of 15 is far outside what any of these Python,
Java, Ruby or Go projects produced.

→ **H4** (function shape), calibrated per language and per repo.

## Finding 5: comments were sparse, asymmetric and about things the code can't say

Reading the sampled comments by hand, the inline comments that recur are:

- **Units and sentinel meanings on fields.** `int maxidletime; /* Client timeout in seconds */`,
  `FPReg int8 // register number of frame pointer, -1 if not used`, `Init Stmt // initialization
  statement; or nil`.
- **Invariants and ordering assumptions.** PostgreSQL `xact.c`: "We rely on the fact that the XID
  of a child always follows that of its parent. By copying … we ensure that the array stays
  ordered."
- **Why the obvious approach is wrong.** Redis `t_zset.c`: "we need to emit any syntax error before
  executing additions to the sorted set, as the command should either execute fully or nothing at
  all."
- **Design rationale for a structure.** Redis `sentinel.c`: "Otherwise if 5 Sentinels are monitoring
  100 masters we create 500 outgoing connections instead of 5."
- **External references.** Go `net/url`: "RFC 6874 defines that %25 … introduces the zone
  identifier". Django: "Avoid infinite loop if there's a cyclic reference (#29393)."
- **Open questions with the trade-off spelled out.** PostgreSQL `heapam.c`: "XXX Should we set
  PageSetPrunable on this page? … If you do add PageSetPrunable here, add it in heap_xlog_insert
  too."
- **Short section labels** inside long C functions ("Extract database number.", "Add pair to
  ziplist"). These are the only "what" comments that recur, and only in long functions.

Narration does occur, but sparsely. Running this skill's own triage over Django 3.0 finds about 48
narration-style comments ("# Check if srid was specified", "# Loop over the groups …") in 55 KLOC,
roughly 1 per KLOC, nearly all heading a longer block. That calibrates H2 as a density rule, not a
ban.

What's absent from the samples: comments narrating each step of a short function, comments
addressed to a reader of a chat ("as requested", "updated to fix"), changelog notes in code ("changed
from X to Y"), and docstrings that restate a signature.

Doc comments follow the house strictly. Go: every exported identifier gets a comment that starts
with its name. Guava and Spring: Javadoc on public API (57–63 comment lines per 100 code lines,
nearly all of it Javadoc), almost no inline comments (2.6–7 per 100). nginx: almost no comments at all (4%).

→ **H2** (comment where a reader would be surprised), **H3** (doc comments by house rule).

## Finding 6: error handling was idiomatic, narrow and contextual

- **Python** (Django, Flask, NumPy): bare `except:` at 0–0.5 per KLOC. `except Exception` at about
  1.4 per KLOC. `except …: pass` blocks occur (1.3–1.6 per KLOC), but in Django every one catches a
  specific, expected exception used as control flow: `KeyError` (13), `AttributeError` (12),
  `ValueError` (11), `ImportError` (8), `NoReverseMatch` (5), `LookupError` (5). There are none on
  `Exception`. EAFP (try it, catch the specific "absent" case) is the idiom. Swallowing everything
  isn't.
- **Go** (Kubernetes, Prometheus, Terraform): `if err != nil` about 20 times per KLOC, with bare
  `return err` where no context is added and `fmt.Errorf("…: %v", err)` where it is. `panic` was
  rare in libraries (0.25 per KLOC in Kubernetes).
- **C** (Git, Redis, curl, PostgreSQL, nginx, SQLite): `goto` cleanup labels at 3.5–12 per KLOC,
  which is the idiomatic single-exit cleanup and not a smell there. SQLite states invariants as
  `assert()` at 38 per KLOC. That's the opposite of re-validating inputs everywhere: assert the
  invariant once and trust it.
- **Java** (Guava): `checkNotNull`/`checkArgument`/`checkState` preconditions at 22 per KLOC, at
  public entry points. Empty `catch {}` at 0.04 per KLOC. `@SuppressWarnings` appears (508 sites),
  always naming one specific warning, and 52% carry a same-line reason: `@SuppressWarnings("unchecked")
  // reading data stored by writeObject`.

→ **H5** (errors), the refined **C3**, and **H14** (assert invariants, validate at the edge).

## Finding 7: names were idiomatic, not uniformly long

Tight scopes used short conventional names (`i`, `n`, `err`, `ctx`, `buf`, `c` for a client in
Redis, `s` for a receiver in Go). Wider scopes used domain words. TODO conventions are per house:
Go stdlib marks 52% of TODO/FIXME/XXX with an owner (`TODO(gri)`), Guava 81%, Prometheus 66%, and
PostgreSQL uses `XXX` for open questions with almost no owners.

→ **H8** (names), **H13** (markers).

## Finding 8: what changed after AI assistants arrived

These are other people's findings, included as contrast and not as this skill's own evidence:

- **More copy-paste, less refactoring.** GitClear (2025, 211M changed lines, 2020–2024) reports a
  roughly 8x rise in duplicated blocks of five or more lines during 2024. It also reports 2024 as the
  first year in which copy-pasted lines outnumbered "moved" lines, its proxy for refactoring. Its
  2024 report found churn (code reverted or rewritten within two weeks) rising from a 3–4%
  pre-assistant baseline to 5.5% in 2023.
- **Unused constructs and leftover debugging.** Cotroneo et al. (ISSRE 2025) found AI-generated code
  simpler and more repetitive than human code, but with more unused constructs, more hardcoded
  debugging artifacts and more high-risk security vulnerabilities.
- **More implementation-level smells.** Ghosh Paul et al. (2025) measured about 63% more code smells
  in LLM output than in professional reference solutions, concentrated in implementation smells
  rather than design smells.

Together with findings 1–7, these define the **AI tells** that [craft.md](craft.md)'s H-rules and
[triage.md](triage.md)'s craft patterns target: narration comments, speculative options and
fallbacks, broad catches, pasted near-duplicates, debug leftovers, invented APIs, report-style
commit messages, and generic or versioned names.

## Sources

- GitClear, *AI Copilot Code Quality: 2025 Look Back at 12 Months of Data*:
  https://www.gitclear.com/ai_assistant_code_quality_2025_research; summary at
  https://www.devclass.com/ai-ml/2025/02/20/ai-is-eroding-code-quality-states-new-in-depth-report/1626250
- GitClear 2024 report, summarized at
  https://visualstudiomagazine.com/articles/2024/01/25/copilot-research.aspx
- Cotroneo, Improta, Liguori, *Human-Written vs. AI-Generated Code: A Large-Scale Study of Defects,
  Vulnerabilities, and Complexity*: https://arxiv.org/abs/2508.21634
- Ghosh Paul et al., *Investigating The Smells of LLM Generated Code*: https://arxiv.org/abs/2510.03029
- Git `Documentation/SubmittingPatches` and `Documentation/CodingGuidelines` at v2.24.0
- Django `docs/internals/contributing/committing-code.txt` and `writing-code/coding-style.txt` at 3.0
