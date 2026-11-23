# Guide: using better-coding in every project

This covers every feature. For why the rules exist, see
[`better-coding/references/research.md`](better-coding/references/research.md).

## 1. Install once, use everywhere

```bash
curl -fsSL https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.sh | bash
```

(Windows: `irm https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.ps1 | iex`)

This puts three skills in `~/.claude/skills/` and two subagents in `~/.claude/agents/`. Both folders
are user-level, so Claude Code sees them in every repo. There's nothing to set up per project.
Restart Claude Code (or open a new session) after installing.

To update later, run the same command again. It replaces the installed copies.

Check it worked: in any repo, type `/better-coding` and the skill should be offered.

Optional: `pip install lizard` adds function-size measurement for non-Python languages. Without it,
triage says plainly that shape was not measured for those languages.

## 2. The three skills

| You want to… | Run |
| --- | --- |
| Build a feature, fix a bug, or refactor with enforcement | `/better-coding` |
| Audit a codebase that already exists | `/better-coding-review` |
| Design the domain model before any code | `/domain-modelling` |

You don't have to call `/domain-modelling` yourself: `/better-coding` runs it for non-trivial
features.

### Modes

Add a mode as an argument: `/better-coding lite`, `full`, or `deep`. Default is `full`.

| Mode | `/better-coding` | `/better-coding-review` |
| --- | --- | --- |
| `lite` | No Reviewer during the loop. You self-check, labeled SELF-CHECKED. Cheapest. | One cheap exhaustive read, no confirmation. Rows it was unsure about stay "Ambiguous". |
| `full` | One Reviewer for the session (cheap model), continued each round. | Cheap read of everything, then the Auditor confirms only what was flagged or unsure. |
| `deep` | A fresh Reviewer every slice, strongest model. | As `full`, plus the Auditor re-checks ~10% of rows the cheap pass called clean. |

In every mode of `/better-coding`, the Auditor's final gate runs at full rigor. `lite` can't skip it.

Pick `lite` for throwaway or exploratory work, `full` for normal work, `deep` for code you can't
afford to get wrong (payments, auth, migrations).

## 3. Building something: `/better-coding`

Example prompts:

```
/better-coding add a remove() method to Cart that rejects removing more than is held
/better-coding deep  migrate the invoice totals to integer cents
/better-coding lite  quick script to dedupe the CSV exports
```

What happens, in order:

1. **Charter.** Your goal becomes a numbered list of acceptance criteria, each checkable by running
   something. They're frozen: if one is wrong, it stops and tells you rather than quietly narrowing it.
2. **Precedence.** If the repo has an `AGENTS.md`, `CLAUDE.md`, `.cursorrules` or `CONTRIBUTING.md`,
   you're asked once: project wins, the Law wins, or both apply and conflicts get raised.
3. **House fingerprint.** `fingerprint.py` measures the repo's own conventions: commit format,
   comment density, doc style, function sizes, indentation, logging, TODO form. Everything stylistic
   is judged against this, so output matches *your* repo, not a generic style.
4. **Domain model.** Non-trivial features run the `/domain-modelling` interview first (a short list
   of business questions, then a walkthrough). Small fixes get a short self-written model.
5. **Slices.** Work is cut into small changes, sized like the house's own commits.
6. **For each slice:** write it, run triage, the Reviewer checks it, fixes happen, verification
   runs, then it's committed in the repo's own message style.
7. **The Auditor's gate.** A fresh agent re-runs every test the Writer claimed passed, checks every
   acceptance criterion against the original wording, reviews the whole change cold, and confirms
   every external API call exists in your installed version. Only its CLEAN means done.
8. **Report.** You get what was built, the model, the commits, the evidence, and the full penalty
   ledger, including everything that went wrong along the way, even on a clean run.

### Resuming

State is saved to `~/.claude/better-coding/state/<repo-slug>/`. If a session stops (context limit,
crash, closed terminal), run `/better-coding` again in the same repo. It finds `progress.md`, checks
it against `git log`, confirms in one line that it's the same goal, and continues from the exact
phase. A different goal starts fresh.

### The penalty ledger

Findings are recorded with points:

| Severity | Points | Consequence |
| --- | --- | --- |
| CAPITAL | 10 | The slice is stashed (never deleted) and rewritten from the clean base |
| MAJOR | 5 | Fixed before anything else is written |
| MINOR | 2 | Fixed, or contested once in writing (an upheld contest counts double) |

A rule broken twice doubles and becomes a Standing Order, re-read before every slice. Broken three
times, or 15+ points in one round, escalates or sends the slice back to design.

## 4. Auditing existing code: `/better-coding-review`

```
/better-coding-review
/better-coding-review lite
/better-coding-review deep
```

What happens:

1. **Scope.** First line of the report states `N files -> n important -> L lines to review`.
   Tests, docs, generated code, vendored code and migrations are excluded by default. Say so if
   you want tests included.
2. **Fingerprint and triage.** Free, script-based, across everything.
3. **Exhaustive read.** The repo is split into ~3,000-line chunks. A cheap Reviewer reads every file
   in a chunk, and returns a row per file per rule: Clean, Finding, or Ambiguous.
4. **Confirmation** (`full`/`deep`). The Auditor resolves every Ambiguous row and every
   MAJOR/CAPITAL finding.
5. **Report.** A full table of every file against every applicable rule, findings with evidence, a
   section on missing domain models, and a section on where the code departs from its own house
   style (the AI-generated tells live here).
6. **It stops and asks.** Nothing is fixed until you say yes. If you do, fixing runs through the
   `/better-coding` loop, with the same Reviewer and Auditor.

It resumes per chunk too: an interrupted audit continues from the next unfinished chunk.

## 5. Modelling first: `/domain-modelling`

```
/domain-modelling subscriptions with a flat fee plus usage credits
```

An interview, not a form. It reads the repo, asks only the business questions it can't answer from
the code (one at a time, with examples), builds the model silently, then walks you through it a
concept at a time. It ends with a design document (usually `docs/designs/<feature>.md`) and, if you
want, a PR putting the design in front of your team before implementation starts.

## 6. The two rule sets

**The Law** (`better-coding/references/law.md`): is the code right?
Domain model before code (L25) · no generic `Manager`/`Helper` names (L26) · behavior lives with
its data (L27, in the languages where classes are the unit of design) · few branches (L28) · the
laziness ladder (L29): does this need to exist, is it already here, does the standard library do
it, does the platform do it, does a dependency do it, is it one line · every branch reachable (L3) ·
`Optional` presumed guilty (L5) · validate once at the boundary (L30) · no orphan classes (L31) ·
strict typing (C1: no `any`, no suppressions) · no swallowed errors (C3) · no gutted tests (C2) ·
no fabricated verification (C4) · no moved goalposts (C5).

**Craft** (`better-coding/references/craft.md`): does it read as human-written, production-grade
code from this repo? Match the house (H1) · comments for surprise only (H2) · doc comments per house
rule (H3) · function size and shape (H4) · idiomatic errors (H5) · no speculative options (H6) · no
pasted duplicates (H7) · idiomatic names (H8) · minimal diffs (H9) · house-style commit messages
(H10) · a test with every bug fix (H11) · no emoji or banners in output (H12) · markers with
conditions (H13) · assert invariants, validate at the edge (H14) · every API verified against the
installed version (H15) · no placeholders, chat text or invented values (H16).

## 7. The scripts, standalone

Both need only Python 3.8+. You can use them without Claude, from any repo:

```bash
S=~/.claude/skills/better-coding/scripts

python3 -I $S/triage.py .                              # whole repo
python3 -I $S/triage.py . --diff main                  # only lines added since main
python3 -I $S/triage.py . --diff main --commit HEAD    # also check the last commit message
python3 -I $S/triage.py . --files src/app.py           # specific files
python3 -I $S/triage.py . --include-tests              # include tests
python3 -I $S/triage.py . --max-lines 35 --max-branches 8

python3 -I $S/fingerprint.py .                         # the repo's house conventions
python3 -I $S/fingerprint.py . src/billing             # scoped to a path
```

Triage output has two tiers. **Near-verdicts** (a suppression comment, a swallowed error, a
`# ... existing code ...` placeholder) are close to findings on their own. **Leads** (an `Optional`,
a long function, a `Manager` class) are places to look, not verdicts. Triage informs and never
fails a build: it always exits 0.

## 8. Using it in other tools

Cursor, Windsurf, Cline, Devin, Kiro and anything that reads `AGENTS.md` can't run skills or
agents, but they can read the rules. From inside a project:

```bash
curl -fsSL https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.sh -o install.sh
bash install.sh --project --skip-claude
```

This adds the condensed Law and Craft as always-on instructions. Commit those files to share them
with your team. You get the rules, not the independent Reviewer and Auditor.

## 9. Tips

- **Large repos:** run `/better-coding-review lite` first to see where the problems are, then
  `full` on the areas that matter.
- **Your own rules win on style.** Put conventions in `AGENTS.md` or `CLAUDE.md`. Craft's H1 also
  follows whatever the repo's history shows.
- **Commit messages:** the repo's history decides the format. If yours uses plain sentences, you
  get plain sentences. `feat:`-style prefixes appear only if your history already uses them.
- **If an agent type is missing:** the skills fall back to `general-purpose` subagents with the same
  briefs. You lose the read-only tool restriction, so reinstall to get it back.
- **Read the ledger.** The final report lists every penalty. Repeated entries for the same rule tell
  you something about the task or the codebase.
- **It won't fake a pass.** If a command couldn't be run (no credentials, no network), the criterion
  is reported *unverified*, which doesn't count as met.

## 10. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `/better-coding` isn't offered | Re-run the installer, then start a new Claude Code session |
| "No such subagent type" | Check `~/.claude/agents/` has `better-coding-reviewer.md` and `better-coding-auditor.md`; otherwise the skill falls back to general-purpose |
| Triage says "shape not measured" | `pip install lizard`, or accept judging non-Python function size by reading |
| Fingerprint shows "Last 1 non-merge commits" | The path has little history. Run it on the repo root instead |
| Resumed the wrong task | State lives in `~/.claude/better-coding/state/<repo-slug>/`. Delete that folder to start clean |
