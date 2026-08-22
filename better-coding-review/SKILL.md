---
name: better-coding-review
description: >
  Audit an entire existing codebase, at any size, against the same rule set better-coding enforces
  while writing new code: domain modeling, object-oriented design, strict typing, and
  over-engineering. Scopes the repository first, files then lines then the important subset (code,
  not tests or docs), runs a free mechanical triage across all of it, then a single exhaustive lite
  pass reads every important file once, on the cheapest model, and produces one master requirements
  table. full/deep modes never re-scan the repository, they spend independent review only on
  confirming what lite flagged as ambiguous, then fix. Produces a detailed compliance report, then
  asks the user whether to launch a fixing pass. Negotiates precedence against the project's own
  AGENTS.md/CLAUDE.md instead of assuming it. Use when the user wants a codebase audited, reviewed
  for compliance, checked for over-engineering, or asks "how compliant is this repo" / "audit this
  codebase" / "what's not following our standards."
argument-hint: "[lite|full|deep]"
---

# better-coding-review

`better-coding` enforces the Law while code is being written. This skill enforces it against code
that already exists, code nobody wrote under that loop, code from before it existed, code from
another contributor, a whole repository nobody has audited yet, at whatever size that repository
actually is.

It does two things, in order, and never skips the gap between them: it reports, in full, before it
touches anything. Fixing only starts on the user's explicit word.

Read the shared rule set from the paired skill when the phase that needs it begins:

- `../better-coding/references/law.md`: the enforceable rules, each with a stable ID.
- `../better-coding/references/triage.md`: the mechanical pass, the scoping/exclusion rules, the
  chunking algorithm, and the coverage map, this is what makes a repository's size a non-issue.
- `../better-coding/references/cheatsheet.md`: the condensed rule set the exhaustive `lite` pass
  reads instead of the full files.
- `../better-coding/references/warden.md`: the auditor's brief, handed to the Warden verbatim.
- `../better-coding/references/ledger.md`: used only in the fixing pass, never in the audit itself.

If `better-coding` isn't installed alongside this skill, stop and tell the user, this skill depends
on it for the rule set, the triage patterns, and the fixing loop.

## The roles

You are the **Builder** during the fixing pass, same as in `better-coding`. During the audit itself
you are closer to a dispatcher: you scope, triage, run the base pass, spawn confirmation Wardens
only where the base pass couldn't settle something, and compile what they report. You still do not
soften, drop, or pre-filter a finding before it reaches the user.

## The pipeline: read once, confirm the ambiguous part, then fix

Every mode starts the same way: scope the repository, triage it, then run one exhaustive `lite`
pass that reads every important file exactly once and produces a single master table. Modes differ
only in what happens *after* that table exists, not in how the repository gets read:

- **`lite`** (base pass, always runs first, in every mode): no mode-specific work beyond it. The
  table itself, with the coverage tier and a real, cheap-model judgment call on every row, is the
  deliverable. Cheapest, and honest about what a cheap model's judgment is worth, rows it marks
  ambiguous are exactly the ones it wasn't confident enough to call.
- **`full`** (default): takes `lite`'s table as input, never re-reads the repository from scratch.
  Spawns targeted, stronger, independent Warden confirmation passes only on the rows `lite` marked
  **Ambiguous** or **Flagged**, using the full `law.md`/`warden.md` now that the scope is a small,
  specific set of locations rather than the whole codebase. Confirmed findings get offered for
  fixing.
- **`deep`**: everything `full` does, plus a spot-check: an independent Warden re-verifies a sample
  of `lite`'s **Clean** rows too, since a cheap model's confident "nothing here" is exactly the kind
  of false negative worth catching before calling anything exhaustive. This is the only mode that
  spends tokens re-looking at what the base pass already called clean.

This is the whole point of doing the exhaustive read exactly once: `full` and `deep` cost scales
with how much `lite` was actually unsure about, not with repository size, because they're never
re-deriving their own view of the codebase, they're resolving `lite`'s.

## Precedence is negotiated, not assumed

Same mechanism as `better-coding`, run it here too since this skill may be the first thing invoked
in a session. Check for the project's own instruction files (`AGENTS.md`, `CLAUDE.md`, a doctrine
file, `.cursorrules`). If any exist, ask the user once, with `AskUserQuestion`: project wins, Law
wins, or hand in hand. Record the answer for this session only, nothing is written to disk, and
don't ask again once it's decided, including on a later conflict, that's resolved by the standing
choice.

## State

Working state lives in your session scratchpad, under `better-coding-review/`: `report.md` (the
master table, updated in place as confirmation resolves rows, never rewritten from scratch) and,
only if the user approves fixing, `charter.md` and `ledger.md` in the same location `better-coding`
would use. Never in the repository.

---

# The loop

## Phase 0: Precedence and mode

Run the precedence negotiation above and resolve the mode (skill argument, or the user saying so;
default `full`). Both get recorded at the top of `report.md`.

## Phase 1: Scope

Two counts, always, reported to the user before anything else: total tracked files, then the
important subset after applying [triage.md](../better-coding/references/triage.md)'s default
exclusions (tests, docs, generated output, lockfiles, migrations), then the line count of that
filtered set specifically, using the safe single-call method, not a per-file loop. State the
exclusion list explicitly, and that it's overridable if the user wants tests or docs in scope.

This is the first line of `report.md`, in every mode: `<total> files -> <n> important
(<excluded categories>) -> <lines> lines to review.` A report that never states this is a report
whose completeness can't be checked by anyone reading it.

## Phase 2: Triage

Run every pattern in [triage.md](../better-coding/references/triage.md) against the important file
set from Phase 1. One pass, every mode, no agent tokens. The result is near-verdicts (already
findings) and leads (locations worth a closer look), attached to specific files and lines.

## Phase 3: The exhaustive lite pass

This runs regardless of mode, it's not something `full`/`deep` skip past, it's what they build on.

Chunk the important file set per [triage.md](../better-coding/references/triage.md)'s algorithm,
target **~3000 lines per chunk**: large enough to keep spawn count reasonable, small enough that a
cheap model reads every file in its chunk in full, not a sample. Unlike `full` mode's old
triage-narrowed chunks, every chunk here gets completely read, that's what makes this pass
exhaustive rather than another partial one. On the reference 730-file, 27,181-line filtered set,
that's roughly 9 to 10 chunks.

Spawn one Warden per chunk, cheapest available model, [cheatsheet.md](../better-coding/references/cheatsheet.md)
instead of the full `law.md`/`warden.md`:

```
Agent(
  subagent_type: "general-purpose",
  model: "haiku",
  run_in_background: false,
  description: "Lite pass: <chunk>",
  prompt: <the brief below>
)
```

Spawn a wave of up to 6 to 8 chunks together; more chunks than that runs in additional waves.

Pass **absolute** paths, resolved the same way `better-coding`'s Phase 4 resolves them: wherever
this SKILL.md actually loaded from, sibling to `better-coding` at the same level. If it isn't
obvious, check both `~/.claude/skills/` and `<repo-root>/.claude/skills/` for
`better-coding/references/law.md`.

The brief:

- `Read <better-coding-dir>/references/cheatsheet.md and follow it exactly, that's the rule set and
  the standing position.`
- `Audit mode: whole repository, exhaustive base pass. Scope: <this chunk's full file list>.`
- Triage's near-verdicts and leads within this chunk, so confirmed mechanical findings don't need
  rediscovering, only judging.
- `For every rule that applies to every file in scope, return one row: file, line (if applicable),
  rule ID, and a status of Clean, Finding, or Ambiguous. Ambiguous means you could not confidently
  call it either way on this pass, not that you skipped it, every file gets a row for every
  applicable rule, there is no "not reached."`
- The negotiated precedence mode, and the project's instruction files to read under it.

Compile every chunk's rows into one master table at `report.md`. This table is the deliverable in
`lite` mode, and the starting point for everything after it in `full`/`deep`.

## Phase 4: Confirm (full / deep only)

`lite` mode stops at Phase 3, skip to Phase 6.

Pull every row marked **Ambiguous** or **Finding** with a MAJOR/CAPITAL severity from the master
table. Group by proximity (same file or same module first) into batches sized for careful reading,
not for chunk-size economics, this set is already small because `lite` did the expensive part.
Spawn one Warden per batch, full rigor:

```
Agent(
  subagent_type: "general-purpose",
  model: <"haiku" in full mode; omit (inherit default) in deep mode>,
  run_in_background: false,
  description: "Confirm: <batch>",
  prompt: <the brief below>
)
```

The brief:

- `Read <better-coding-dir>/references/warden.md and follow it exactly. Read
  <better-coding-dir>/references/law.md, that's the rule set.` Full files here, not the cheat sheet,
  this is the confirmation step and it needs the real rationale, not just the trigger line.
- `Audit mode: confirmation. You are resolving specific rows an earlier cheap-model pass marked
  Ambiguous or Finding, not scanning fresh. Confirm, overturn, or refine each one with a real
  verdict, citing the rule and the evidence.`
- The specific rows assigned to this batch: file, line, rule ID, lite's original call.
- The negotiated precedence mode, and the project's instruction files to read under it.

`deep` mode only, additionally: pull a random ~10% sample of rows `lite` marked **Clean**, batch and
confirm those the same way, to catch cheap-model false negatives. `full` mode trusts `lite`'s Clean
calls as-is.

Update `report.md`'s master table in place: every confirmed row's status becomes the Warden's
verdict, not `lite`'s original guess, and gets tagged `[lite]` or `[warden-confirmed]` so the report
never hides which tier actually settled it.

## Phase 5: Compile the final report

```markdown
# Compliance report — <repo>

Mode: lite | full | deep | Precedence mode: <mode>
Scope: <total files> -> <n important> (<excluded categories>) -> <lines> lines
Pass: lite (chunk count, model) [-> confirm (batch count, model), deep only: + N% clean-row spot-check]

## Summary
CAPITAL: <n>  MAJOR: <n>  MINOR: <n>
Domain models missing (L25): <n features/modules with no written model and no clear one implied by the code>
Laziness ladder findings (L29): <n>, tagged delete/stdlib/native/yagni/shrink, <est. lines and dependencies removable>

## Requirements checklist
| File | Rule | Status | Source |
| --- | --- | --- | --- |
[one row per file x applicable rule from the master table; this is the literal table Phase 3 built
and Phase 4 updated, not a re-derived summary of it]

Status is one of: **Clean**, **Finding** (see below), **Ambiguous** (lite mode only, `full`/`deep`
resolve every Ambiguous row before this report is called final). Source is `lite` or
`warden-confirmed`. In `full` mode, Clean rows stay sourced `lite`, never independently re-verified,
say so plainly rather than letting silence imply otherwise.

## Findings
[<ID>] <SEVERITY> — <file>:<line> (<module>) [lite | warden-confirmed]
  Broken: ...
  Evidence: ...
  Failure: ...
  Required: ...

## Domain modeling gaps
<modules or features with no identifiable domain model; classes named FooManager/FooHelper/FooUtils/
FooProcessor/FooGenerator (L26) and what real concept each is likely standing in for>

## Unverified
<anything neither pass could resolve, and what would be needed to>
```

A `lite`-only report keeps every row's status as `Clean`/`Finding`/`Ambiguous` from a single cheap
pass, and says so in the `Pass` line. Presenting that as equivalent to a confirmed report is C4 by
another name.

## Phase 6: Ask before fixing anything

Present the report to the user. Then, only then, ask with `AskUserQuestion` whether to start the
fixing agent. Do not start fixing on your own judgment, however small the fix looks, this is the one
step in the whole system that exists specifically to not be automatic.

If the user declines, stop. The report stands as delivered; nothing in the repository changes.

## Phase 7: Fixing pass

If the user approves, hand off to `better-coding`'s own phases, reusing its ledger mechanics
exactly, at `full` rigor or better regardless of what mode produced the report, an unconfirmed
`Ambiguous` row is a reason to look, not evidence a fix is correct once you're actually changing the
code:

- Group findings into slices the same way `better-coding` Phase 2 would, one coherent change per
  slice, a CAPITAL finding and the file it's in is usually its own slice.
- Where a finding is really a missing domain model (L25) rather than a code defect, write the model
  first, per `better-coding` Phase 2, before touching the implementation it should have guided.
- Run `better-coding` Phase 3 through 8 for each slice: triage, build the fix, audit in diff mode
  this time (not whole-repository mode, you're now working a specific change against a specific
  baseline), sentence, remediate, verify, gate.
- The charter's acceptance criteria are the report's findings for this slice going to zero, plus
  whatever tests or checks already covered that code.
- Continue until every confirmed finding is resolved, contested-and-upheld findings get fixed too,
  or escalated per the circuit breaker below.

## Circuit breaker

Stop and escalate, with whatever's been fixed so far and what remains, when:

- The same rule has been broken three times during the fixing pass.
- A finding needs a decision only the user can make, most often when fixing it would change a public
  API or a persisted data shape.
- Something external blocks the work: missing credentials, a broken dependency, an unavailable
  service.
- Two consecutive rounds produce no reduction in open findings.

## Never

- Starting the fixing pass without the user's explicit go-ahead, regardless of how confident the
  audit was or how small the first finding looks.
- Softening, cutting, or reordering a finding to make the report look better before the user sees it.
- Calling a report final while any row is still `Ambiguous` in `full`/`deep` mode, or presenting a
  `lite`-only report without stating, plainly, that every row came from one cheap-model pass.
- Re-scanning files `lite` already covered instead of working from the master table, that's the
  entire efficiency case for this pipeline, and skipping it defeats the purpose of Phase 3.
- Marking a finding resolved without the same evidence-before-done standard `better-coding` Phase 7
  requires: a real command, real output, not a description of what should now be true.
