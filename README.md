# better-coding

Claude Code skills that make an AI agent write code the way a long-time maintainer of *your*
repository would have written it before AI assistants existed, and that stop the agent from grading
its own work.

Ask an agent to write code, then ask the same agent whether the code is good, and one train of
thought is checking itself. Whatever reasoning led to a shortcut is still there when you ask about
the shortcut. So `better-coding` splits the job across exactly three agents that don't share
context:

| Agent | Job |
| --- | --- |
| **Writer** | Your Claude Code session. Plans, writes, fixes, verifies, commits, and talks to you. |
| **Reviewer** | Reviews each small slice as it's written, against the rules. Can't edit anything. |
| **Auditor** | Spawned fresh at the end. Re-runs every test the Writer claims passed, checks the acceptance criteria, reviews the whole change cold, and confirms every new API call exists. Can't edit anything. Only its verdict means "done". |

New here? [GUIDE.md](GUIDE.md) walks through every feature: install, modes, resuming, the
ledger, the standalone scripts and troubleshooting.

## Two standards

**The Law** decides whether code is *right*. You write the domain model down before writing code.
Behavior lives with the data it belongs to. Typing is strict: no `any`. Errors aren't swallowed,
tests aren't gutted, verification isn't faked. And there's a laziness ladder against
over-engineering, borrowed from [ponytail](https://github.com/DietrichGebert/ponytail): does this
need to exist, is it already here, does the standard library do it, before anything new gets
written.

**Craft** decides whether code reads as *human-written and production-grade*. It comes from
measuring real pre-AI code, not from opinion:

- **756,498 commits** made before 2020 across 22 long-lived production projects: Linux, Git, Go,
  CPython, Rust, PostgreSQL, SQLite, Redis, curl, nginx, Kubernetes, Terraform, Prometheus, Django,
  Rails, Flask, Requests, NumPy, React, Express, Guava, Spring.
- **3.1M lines of production code** from pre-2020 release snapshots of 20 of them, with tests,
  vendored code and generated files excluded. Function size and complexity were measured with
  `lizard`. Comments, error handling and markers were measured with a purpose-built scanner, and a
  sample of comments was read by hand.
- The projects' own written guidelines (Git's `SubmittingPatches` and `CodingGuidelines`, Django's
  coding and committing guides), plus published studies of how AI-assisted code differs.

The headline finding: **there's no universal human style. There's a house style.** Comment density
ranges from 4 to 58 lines per 100 lines of code. Django mandates past-tense commit messages and Git
mandates imperative ones. So the first Craft rule is "match the house". A `fingerprint` script
measures your repo's own conventions before any code is written, and the Reviewer and Auditor judge
style against that, not against taste.

Some of what the corpus showed:

| What pre-2020 production code did | What that makes the rule |
| --- | --- |
| Median commit changed 5–22 source lines in 1–2 files | Small slices, nothing reformatted that the change didn't need |
| Conventional Commits (`feat:`) in 0–4% of commits, in every project | Commit format copies the repo's own history; `feat:` only if the repo already uses it |
| 3+ bullet lists in under 2% of commits in most projects; emoji ~0% | Commit bodies are prose: what was wrong, why this fixes it |
| "comprehensive", "seamless", "leverage", "delve": under 0.2 per 1,000 commits | That register is a tell |
| Median function 3–9 lines (Python, Java, Ruby, Go, JS), 12–16 (C); CCN > 10 in under 5% outside C | Function shape calibrated per language and per repo |
| Comments carry units, invariants, ordering assumptions, RFC and issue refs; narration about 1 per KLOC | Comment for surprise; narration is judged by density |
| Python `except …: pass` only on specific expected exceptions (`KeyError`, `ImportError`), never `Exception` | Narrow EAFP is fine; broad swallowing is a capital offense |
| Guava's `@SuppressWarnings` always names one warning, and 52% carry a same-line reason | Suppressions stay banned for the agent unless you ask |

The full method, tables, caveats and sources are in
[`better-coding/references/research.md`](better-coding/references/research.md).

## The skills

**`better-coding`** runs while you build. It writes a charter with checkable acceptance criteria,
fingerprints the house, writes the domain model, then builds in small slices. Each slice goes
through triage, a Reviewer pass, sentencing in a penalty ledger, fixes and verification. At the end,
a fresh Auditor gates the whole change. Checkpoints let an interrupted session resume where it
stopped.

**`better-coding-review`** audits code that already exists. It scopes the repo, runs triage, and has
cheap Reviewer instances read every important file exactly once. The Auditor then confirms
everything they flagged or weren't sure about. You get a full compliance report, including where
the code departs from its own house and where it shows AI-generated tells. Nothing gets fixed
unless you say yes, and fixes go through the same three-agent loop.

**`domain-modelling`** runs an interview-driven modelling session before any code is written. Its
design document is what `better-coding` builds from.

Modes: `/better-coding lite|full|deep` and `/better-coding-review lite|full|deep`. The mode changes
how much the Reviewer does. The Auditor's final gate runs in every mode, at full rigor.

## Install

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.sh | bash
```

### Windows

```powershell
irm https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.ps1 | iex
```

This installs the three skills into `~/.claude/skills/` and the Reviewer and Auditor subagents into
`~/.claude/agents/`, once per machine. After that, `/better-coding` and `/better-coding-review` work
in every repo.

By hand: copy `better-coding`, `better-coding-review` and `domain-modelling` into
`~/.claude/skills/`, and `agents/*.md` into `~/.claude/agents/`. Keep the folder names. If the agent
files are missing, the skills fall back to general-purpose subagents with the same briefs, but you
lose the tool restriction that keeps the Reviewer and Auditor read-only.

The scripts need Python 3.8+ and use only the standard library. `lizard` (`pip install lizard`) is
optional and adds function-shape measurement for non-Python languages.

### Cursor, Windsurf, Cline, Devin, Kiro, and AGENTS.md-aware tools

```bash
curl -fsSL https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.sh -o install.sh
bash install.sh --project --skip-claude
```

Run this from inside the project. It drops each tool's own rule file into the repo. Those files carry
the condensed Law and Craft as always-on instructions, without the agents, the triage scripts or the
loop. Those need Claude Code.

## Your project's rules come first

If the repo has an `AGENTS.md`, `CLAUDE.md` or its own doctrine, you're asked once per session how
the two relate: your file wins, the Law wins, or both apply and conflicts get raised. Separately,
Craft's first rule always defers to the house's actual *style*, measured from its history and code.

## What's inside

| File | What it's for |
| --- | --- |
| `GUIDE.md` | How to use every feature. |
| `better-coding/SKILL.md` | The build loop: charter, fingerprint, domain model, slices, review, sentencing, verification, the Auditor's gate. |
| `better-coding-review/SKILL.md` | The whole-repository audit pipeline. |
| `better-coding/references/law.md` | The Law: correctness, design and honesty rules, one stable ID each. |
| `better-coding/references/craft.md` | Craft: the H-rules for human-written, production-grade code. |
| `better-coding/references/research.md` | The pre-2020 corpus study behind Craft: method, tables, caveats, sources. |
| `better-coding/references/reviewer.md` | The Reviewer's brief. |
| `better-coding/references/auditor.md` | The Auditor's brief. |
| `better-coding/references/cheatsheet.md` | Condensed Law and Craft for cheap Reviewer passes. |
| `better-coding/references/triage.md` | What triage checks, scoping and chunking, and a corrected `rg` fallback. |
| `better-coding/references/ledger.md` | Penalties, Standing Orders, and the evidence records the Auditor re-checks. |
| `better-coding/scripts/triage.py` | Mechanical checks for Law and Craft, diff-aware, standard library only. |
| `better-coding/scripts/fingerprint.py` | Measures a repo's house conventions from its history and code. |
| `agents/better-coding-reviewer.md`, `agents/better-coding-auditor.md` | The read-only subagent definitions. |
| `domain-modelling/SKILL.md` | The modelling session. |
| `AGENTS.md`, `.cursor/`, `.windsurf/`, `.clinerules/`, `.kiro/`, `.devin-plugin/` | Condensed rules for other tools. |
| `install.sh`, `install.ps1` | Installers. |

## License

MIT. See [LICENSE](LICENSE).
