---
name: better-coding-review
description: >
  Audit an entire existing codebase, at any size, against the same standards better-coding enforces
  while writing: the Law (domain modeling, object-oriented design, strict typing, error honesty,
  over-engineering) and Craft (does the code read like the house's own production code, per a study
  of pre-2020 human-written code: house conventions, function shape, idiomatic errors, sparse
  why-comments, no duplication, no assistant artifacts). Uses exactly three agents: the Writer (you)
  scopes, triages and compiles; Reviewers read every important file exactly once on a cheap model;
  the Auditor confirms what the Reviewers flagged or couldn't settle. Produces a full compliance
  report, then asks before fixing anything; fixes run through better-coding's own Writer, Reviewer
  and Auditor loop. lite/full/deep modes, resumable per chunk. Use when the user wants a codebase
  audited, reviewed for compliance or AI-generated code smells, checked for over-engineering, or
  asks "how compliant is this repo" / "audit this codebase" / "what's not following our standards".
argument-hint: "[lite|full|deep]"
---

# better-coding-review

`better-coding` enforces the Law and Craft while code is being written. This skill enforces them
against code that already exists: code from before the loop existed, from other contributors, or
from AI assistants, at whatever size the repository is.

It does two things, in order, and never skips the gap between them. It reports, in full, before it
touches anything. Fixing starts only on the user's explicit word.

Everything it uses lives in the sibling `better-coding` skill. Read each file when the phase that
needs it begins:

- `../better-coding/references/law.md` and `craft.md`: the rules.
- `../better-coding/references/triage.md` and `../better-coding/scripts/triage.py`: the mechanical
  pass, scoping and chunking.
- `../better-coding/scripts/fingerprint.py`: the house conventions Craft is judged against.
- `../better-coding/references/reviewer.md` and `cheatsheet.md`: the Reviewer's brief and the
  condensed rules.
- `../better-coding/references/auditor.md`: the Auditor's brief.
- `../better-coding/references/ledger.md`: the fixing pass only.
- `../domain-modelling/SKILL.md`: where L25 findings go in the fixing pass.

If `better-coding` isn't installed alongside this skill, stop and tell the user.

## Exactly three agents

| Agent | Job here |
| --- | --- |
| **Writer** (you) | Scope, fingerprint, triage, chunk, dispatch, compile the report, ask the user, and, if approved, fix through `better-coding`'s loop |
| **Reviewer** (`better-coding-reviewer`) | The exhaustive base pass: one instance per chunk, cheapest model, reads every file in its chunk in full, returns a row per file per applicable rule |
| **Auditor** (`better-coding-auditor`) | Confirmation: resolves every row a Reviewer marked Ambiguous or flagged MAJOR/CAPITAL; in `deep` mode, also re-checks a sample of Clean rows; strongest model |

Running several Reviewer instances at once, one per chunk, is still one agent role: same brief, same
rules, different scope. No other kind of agent is spawned. If the named subagent types aren't
installed, use `general-purpose` with the same brief, and say so once.

You don't soften, drop or pre-filter a finding before it reaches the user.

## The pipeline: read once, confirm the uncertain part, then fix

Every mode starts the same way: scope, fingerprint, triage, then one exhaustive Reviewer pass that
reads every important file exactly once and produces one master table. Modes differ only in what
happens after that table exists:

- **`lite`**: the table is the deliverable. Rows the Reviewers marked Ambiguous stay Ambiguous, and
  the report says so.
- **`full`** (default): the Auditor confirms every Ambiguous row and every MAJOR/CAPITAL Finding.
  Clean rows are trusted as read.
- **`deep`**: everything in `full`, plus the Auditor re-checks a random ~10% of Clean rows to catch
  cheap-model false negatives.

`full` and `deep` never re-read the repository from scratch. Their cost scales with how uncertain
the base pass was, not with repository size.

## Precedence is negotiated, not assumed

Same as `better-coding`: check for `AGENTS.md`, `CLAUDE.md`, a doctrine file, `.cursorrules`,
`CONTRIBUTING.md`. If any exist, ask once with `AskUserQuestion` (project wins / Law wins / hand in
hand). Record it at the top of the report, for this session only.

## State and checkpoints

State lives at `~/.claude/better-coding/state/<repo-slug>/` (slug computed as in `better-coding`):
`report.md`, updated in place and never rewritten from scratch, plus `fingerprint.md`. If fixing is
approved, `charter.md`, `ledger.md` and `progress.md` live there too, exactly where `better-coding`
looks for them.

At the very top of `report.md`, written in Phase 0 before any real work:

```markdown
# Progress — better-coding-review

## Goal
Audit <repo path>. Mode: <lite | full | deep>. Precedence: <mode>.

## Agenda
<filled in at Phase 1: files -> important files -> lines -> chunk count, then every chunk by id, each "Not started">

## Status: NOT STARTED | IN PROGRESS | BLOCKED | DONE
Last updated: <phase, chunk, timestamp>
```

Mark each chunk `Done` the moment its Reviewer returns, not when the wave finishes. Do the same for
the Auditor's confirmation batches.

On starting Phase 0, look for an existing `report.md` whose status isn't `DONE`. If the goal matches
(same repo, same mode), resume at the first chunk still `Not started`. Don't re-run chunks already
`Done`. A mismatch is a new task.

---

# The loop

## Phase 0: Precedence and mode

Negotiate precedence and resolve the mode (argument or the user's word; default `full`). Write both
at the top of `report.md`.

## Phase 1: Scope and fingerprint

Report to the user before anything else: total tracked source files, then the important subset
after [triage.md](../better-coding/references/triage.md)'s default exclusions (tests, docs, generated
output, vendored code, migrations), then the line count of that subset using the single
`cat | wc -l` method. State the exclusions and that they're overridable.

This is the first line of the report, in every mode: `<total> files -> <n> important (<excluded
categories>) -> <lines> lines to review.`

Then fingerprint the house, over the whole repository:

```
python3 -I <better-coding-dir>/scripts/fingerprint.py <repo-root> > <state-dir>/fingerprint.md
```

For an audit, H1 asks a specific question: where does code depart from the repository's own
dominant convention? The fingerprint is that convention.

## Phase 2: Triage

```
python3 -I <better-coding-dir>/scripts/triage.py <repo-root> > <state-dir>/triage.md
```

One pass, every mode, no agent tokens. Near-verdicts are close to findings. Leads are locations.
Before trusting a clean triage result, confirm the script found the files you expected (the
header's file count should match Phase 1's important set).

## Phase 3: The exhaustive Reviewer pass

This runs in every mode. It's what `full` and `deep` build on.

Chunk the important file set per [triage.md](../better-coding/references/triage.md): about **3,000
lines per chunk**, same-directory files together. Report the actual chunk count from this run.

Spawn one Reviewer per chunk, cheapest model, in waves of 6–8 in a single message:

```
Agent(
  subagent_type: "better-coding-reviewer",   # or "general-purpose" if not installed
  model: "haiku",
  description: "Reviewer: <chunk id>",
  prompt: <the brief below>
)
```

Pass **absolute** paths, resolved from where this SKILL.md loaded (`~/.claude/skills/` or
`<repo>/.claude/skills/`).

The brief:

- `Read <better-coding-dir>/references/reviewer.md and follow it exactly. Read
  <better-coding-dir>/references/cheatsheet.md, that's the rule set.`
- `Review mode: whole repository, exhaustive base pass. Scope: <this chunk's full file list>.`
- `Read <state-dir>/fingerprint.md: judge Craft against this house.`
- Triage's near-verdicts and leads inside this chunk.
- `For every file in scope and every rule that applies to it, return one row: file, line (if
  applicable), rule ID, and Clean, Finding, or Ambiguous, with evidence for Finding and Ambiguous.
  Ambiguous means you couldn't call it confidently, not that you skipped it. There is no "not
  reached."`
- The precedence mode and the project's instruction files.

Compile every chunk's rows into one master table in `report.md`, sourced `reviewer`.

## Phase 4: The Auditor confirms (full / deep)

`lite` stops after Phase 3. Go to Phase 5.

Pull every row marked **Ambiguous**, and every **Finding** at MAJOR or CAPITAL. Group them by file or
module into batches sized for careful reading. Spawn one Auditor per batch, no `model` override
(strongest), fresh each time:

```
Agent(
  subagent_type: "better-coding-auditor",    # or "general-purpose" if not installed
  description: "Auditor: confirm <batch id>",
  prompt: <the brief below>
)
```

- `Read <better-coding-dir>/references/auditor.md and follow it exactly, in confirmation mode. Read
  <better-coding-dir>/references/reviewer.md, law.md and craft.md.`
- `Confirmation mode. You are resolving specific rows an earlier pass marked Ambiguous or Finding.
  Confirm, overturn, or refine each one, citing the rule and the evidence.`
- The rows: file, line, rule ID, the Reviewer's call and evidence.
- `Read <state-dir>/fingerprint.md.` The precedence mode and the project instruction files.

`deep` only: also pull a random ~10% of **Clean** rows and confirm them the same way.

Update the master table in place. Every confirmed row gets the Auditor's verdict and is tagged
`[auditor-confirmed]`. Untouched rows stay `[reviewer]`.

## Phase 5: Compile the report

```markdown
# Compliance report — <repo>

Mode: lite | full | deep | Precedence: <mode>
Scope: <total files> -> <n important> (<excluded categories>) -> <lines> lines
Pass: Reviewer (<chunks> chunks, <model>) [-> Auditor (<batches> batches) [+ deep: N% Clean-row check]]

## Summary
CAPITAL: <n>  MAJOR: <n>  MINOR: <n>
Law findings: <n>   Craft findings: <n>
Domain models missing (L25): <n>
Laziness ladder (L29): <n> — delete/stdlib/native/yagni/shrink/cut, ~<lines and deps removable>
AI-tell findings (H2, H6, H7, H8, H12, H16): <n>

## House fingerprint
<the commit and code conventions from fingerprint.md, in a few lines, so a reader knows what
"matches the house" meant in this report>

## Requirements checklist
| File | Rule | Status | Source |
| --- | --- | --- | --- |
[one row per file × applicable rule: the literal master table, not a summary of it]

## Findings
[<ID>] <SEVERITY> — <file>:<line> (<module>) [reviewer | auditor-confirmed]
  Broken: …
  Evidence: …
  Failure: …
  Required: …

## Domain modeling gaps
<modules with no identifiable model; generic-suffix and verb-named classes and what each likely
stands in for; unmarked general/ours/plumbing; flat layering; undecided CRUD>

## Where the code departs from its own house
<H1 findings grouped by convention: error idiom, comment density, naming, logging, doc format>

## Unverified
<anything no pass could resolve, and what would resolve it>
```

In `lite` mode, say plainly in the `Pass` line that every row came from one cheap-model pass.
Presenting that as a confirmed report is C4 by another name. In `full`, Clean rows are
Reviewer-sourced and never independently re-checked. Say so.

## Phase 6: Ask before fixing anything

Present the report, then ask with `AskUserQuestion` whether to start fixing. Never start on your own
judgment, however small the first fix looks. If the user declines, stop.

## Phase 7: The fixing pass

On approval, run `better-coding`'s loop at `full` rigor or better, whatever mode produced the report.
That loop uses the same three agents: you write, a Reviewer checks each slice, and a fresh Auditor
gates the end.

- Write the charter: the acceptance criteria are the report's confirmed findings for each slice
  going to zero, plus whatever tests already cover that code.
- Group findings into slices of one coherent change each. A CAPITAL finding and its file is usually
  its own slice. Keep the house's commit size (H9, L18). A repo-wide style sweep is not one slice.
- A finding that's really a missing domain model (L25) starts with `domain-modelling`, run against
  the existing code (its Phase 3 is built for that), before any implementation changes.
- An unconfirmed Ambiguous row is a reason to look, not evidence a fix is right.
- Run `better-coding` Phases 3–8 for each slice.

## Circuit breaker

Stop and escalate, with what's fixed and what remains, when the same rule breaks three times in the
fixing pass, a fix needs a decision only the user can make (a public API or persisted data shape),
something external blocks the work, two consecutive rounds don't reduce open findings, or the
Auditor fails the gate three times.

## Never

- Start the fixing pass without the user's explicit go-ahead.
- Soften, cut or reorder a finding to make the report look better.
- Call a report final while any row is still Ambiguous in `full`/`deep`, or present a `lite` report
  without saying every row came from one cheap pass.
- Re-scan files the Reviewer pass already covered instead of working from the master table.
- Mark a finding resolved without a real command's real output, re-run by the Auditor at the gate.
