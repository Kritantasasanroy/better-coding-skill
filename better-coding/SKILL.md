---
name: better-coding
description: >
  Write production-grade code that reads as if a long-time maintainer of the repository wrote it,
  under continuous enforcement by exactly three agents: the Writer (you) builds in small slices, an
  independent Reviewer checks each slice, and a fresh Auditor gives the final verdict by re-running
  every claimed test and reviewing the whole change cold. Enforces the Law (domain model first,
  object-oriented design, strict typing, no swallowed errors, the laziness ladder against
  over-engineering) and Craft (H-rules drawn from a study of 756k pre-2020 commits and 3.1M lines of
  pre-AI production code: match the house style, small diffs, sparse why-comments, idiomatic errors,
  no speculative options, no pasted duplicates, verified APIs, house-style commit messages, no
  assistant artifacts). Measures the repo's own conventions first with a fingerprint script, so
  "human-written" means this house, not a generic style. Mechanical triage script, lite/full/deep
  modes, penalty ledger, resumable checkpoints. Use for any feature, fix or refactor where quality
  matters, or to resume an interrupted one. Pairs with better-coding-review (audits an existing
  codebase) and domain-modelling (designs the model before code).
argument-hint: "[lite|full|deep]"
---

# better-coding

Code doesn't get written here on trust. It gets written, triaged mechanically, reviewed by an agent
that didn't write it, penalized wherever it breaks the rules, reworked, and finally audited by a
second agent that has never seen the session. That cycle repeats until the goal is met and the
ledger is empty.

There are two standards, enforced together:

- **The Law** ([references/law.md](references/law.md)): is the code *right*? Modeled, typed, honest,
  tested, not over-engineered.
- **Craft** ([references/craft.md](references/craft.md)): does it read as if a maintainer of *this*
  repository wrote it, the way production code was written before AI assistants? Grounded in
  measurements of 22 production projects' pre-2020 history and code
  ([references/research.md](references/research.md)).

Read each reference when the phase that needs it begins, not before:

| File | Used by | When |
| --- | --- | --- |
| [law.md](references/law.md), [craft.md](references/craft.md) | all three | Phase 2 onward |
| [triage.md](references/triage.md) + `scripts/triage.py` | Writer, Auditor | every slice, and the gate |
| `scripts/fingerprint.py` | Writer | Phase 1 |
| [reviewer.md](references/reviewer.md), [cheatsheet.md](references/cheatsheet.md) | Reviewer | Phase 4 |
| [auditor.md](references/auditor.md) | Auditor | Phase 8 |
| [ledger.md](references/ledger.md) | Writer | Phase 5 onward |
| [research.md](references/research.md) | anyone | only when a rule's reason is in question |

`domain-modelling` is the canonical way Phase 2 is satisfied for anything non-trivial. Its rules are
folded into L25/L26/L27/L8/L29, so the standard holds even when a full session isn't run.

## Exactly three agents

| Agent | Who | Job | Never |
| --- | --- | --- | --- |
| **Writer** | You, this session | Charter, fingerprint, model, slices, code, triage, fixes, verification, commit, and every conversation with the user | Judges its own work as CLEAN |
| **Reviewer** | Subagent `better-coding-reviewer` | Reviews each slice against the Law and Craft, judged against the fingerprint | Edits anything, or gives the final verdict |
| **Auditor** | Subagent `better-coding-auditor`, always fresh | The final gate: re-runs every verification claim, checks acceptance criteria, reviews the whole diff cold, checks APIs exist, applies the human-read test | Sees the Reviewer's verdicts or the Writer's reasoning; edits anything |

No other agents are spawned. If the `better-coding-reviewer` / `better-coding-auditor` subagent
types aren't installed (`~/.claude/agents/`), spawn `general-purpose` with the same brief. The brief
opens by having the agent read its role file, so the behavior is the same, only the tool
restriction is lost. Say so once to the user.

The Reviewer sees the code, the rules, the fingerprint, triage's leads and the charter. The Auditor
sees the same, plus the Writer's verification *claims* (commands and reported results) so it can
reproduce them. Neither ever sees the Writer's reasoning about why the code is fine, a summary of
what the code "does", or a hint of the expected verdict.

## Mode: how much independent review, and when

Set with the skill argument (`/better-coding lite|full|deep`) or by the user; default `full`. Mode
controls the Reviewer only. Triage always runs in full, and **the Auditor's gate runs in every mode,
at full rigor, on the strongest model.**

- **`lite`**: no Reviewer during the loop. Triage near-verdicts get fixed directly. Leads and
  judgment-only rules get a self-check by the Writer, labeled **SELF-CHECKED**, never CLEAN. It's
  cheapest, and honestly weaker on exactly the failure this system exists to catch: a Writer
  rationalizing its own shortcut. The Auditor still gates the end.
- **`full`** (default): one Reviewer for the whole session, spawned once with `model: "haiku"` and
  `cheatsheet.md`, then continued round after round with `SendMessage`. The rules are read once per
  feature, not once per slice.
- **`deep`**: a fresh Reviewer every slice, default model, full `law.md` + `craft.md` +
  `reviewer.md`, no persistence. A Reviewer that remembers agreeing with you earlier is slightly
  more likely to agree again, and `deep` trades that efficiency away on purpose.

## Precedence is negotiated, not assumed

The first time this skill runs in a repository this session, check for instruction files
(`AGENTS.md`, `CLAUDE.md`, a doctrine file, `.cursorrules`, `CONTRIBUTING.md`). If none exist, the
Law and Craft apply on their own; say so and move on. If any exist, ask once with `AskUserQuestion`:

- **Project wins.** The project's file is authoritative. The Law fills only what it leaves unstated
  and never loosens what it locked down.
- **Law wins.** The Law is authoritative; the project's file fills gaps.
- **Hand in hand.** Both apply. A genuine conflict is surfaced to the user when found.

Record it in the charter, for this session only. Don't ask again this session.

H1 is not a precedence question. Matching the house's *style* (comment voice, commit format, error
idiom, naming case) is a Craft rule in every precedence mode. Precedence decides conflicts between
*written rules*.

## State

State lives outside the repository (writing loop bookkeeping into the user's project is an L13
scope violation), and not in the session scratchpad, which a new session can't reach. It lives at a
fixed, repo-keyed location:

```
~/.claude/better-coding/state/<repo-slug>/charter.md
~/.claude/better-coding/state/<repo-slug>/fingerprint.md
~/.claude/better-coding/state/<repo-slug>/ledger.md
~/.claude/better-coding/state/<repo-slug>/progress.md
```

`<repo-slug>` is `git rev-parse --show-toplevel` (or the working directory) lowercased, with every
character that isn't a letter, digit or dash turned into a dash, and runs of dashes collapsed:
`… | tr 'A-Z' 'a-z' | sed 's/[^a-z0-9-]/-/g; s/--*/-/g'`. Compute it once, at the start of Phase 0.

## Progress checkpoints, for resuming after a stop

The next invocation remembers nothing but what's on disk. Write `progress.md` first thing in Phase
0, with the full goal and agenda in it:

```markdown
# Progress — better-coding

## Goal
<one sentence, verbatim>

## Agenda
<the slice breakdown: the first slice for certain, later ones "to be determined" until Phase 2 fills them>

## Mode / Precedence
<settings, once resolved>

## Domain model
Path A (domain-modelling) | Path B (self-authored) — <path to the design doc, or "in charter.md">

## Agents
Reviewer: <name/id from the first spawn, full mode only> | Auditor runs: <count>

## Status: NOT STARTED | IN PROGRESS | BLOCKED | DONE
Last updated: <phase, slice, timestamp>

## Completed
- [x] Recon + fingerprint
- [x] Domain model + design
- [x] Slice 1: <one line> — committed <sha>

## In progress right now
<exact phase and slice, specific enough to act on, e.g. "Slice 3: Phase 4, Reviewer round sent, awaiting verdict">

## Remaining
- [ ] Slice 3: <one line>
```

Update it at every phase transition, and mid-phase when a phase runs long. On starting Phase 0,
check for a `progress.md` whose status isn't `DONE`. If there is one, cross-check its `Completed`
slices against `git log`, confirm in one line with the user that it's the same goal, and resume at
`In progress right now`. A different goal is a new task: start fresh, and don't overwrite the old
file until the new charter exists. A persisted Reviewer ID from a previous session is dead, so spawn
a new one and hand it the Standing Orders.

Mark `DONE` only when Phase 8's gate passes and the ledger has been reported.

---

# The loop

## Phase 0: Charter, mode and precedence

Don't write a line of code until all three exist.

Resolve the mode, run the precedence negotiation, then write `charter.md`: the goal in one sentence,
the mode, the precedence mode, and the **acceptance criteria** as a numbered list. Each one must be
checkable by running something. "Login works" isn't a criterion. "`POST /sessions` with a valid
password returns 201 and a session cookie; with a wrong password, 401" is. Copy the criteria to a
`## Criteria as first written` section too. The Auditor compares the two (C5).

Record the baseline: branch, `git rev-parse HEAD`, and whether the tree was dirty. Pre-existing
uncommitted changes belong to the user. List them, never revert them, and ask before touching them.

Acceptance criteria are frozen. If one turns out wrong or impossible, stop and tell the user.

## Phase 1: Recon and the house fingerprint

- Read the project's instruction files per the negotiated precedence, and any guidance near the
  files you'll touch.
- **Fingerprint the house** (H1):

  ```
  python3 -I <skill-dir>/scripts/fingerprint.py <repo-root> <paths you expect to touch> > ~/.claude/better-coding/state/<repo-slug>/fingerprint.md
  ```

  It reports this repo's commit convention, comment density and voice, doc-comment habit, function
  sizes, indentation, quote style, logging habit and TODO form. Then read three neighboring files
  whole, and add one line to the fingerprint for anything the script can't see, such as how errors
  are wrapped or how tests are named. If the script can't run, do it by hand (craft.md explains how)
  and write what you saw. No fingerprint means no H1, and H1 is the organizing rule of Craft.
- Search the repo for an existing solution before planning a new abstraction, helper or dependency
  (L11, H7). Figure out what already owns this responsibility.

## Phase 2: Domain model, then design

L25 is not optional for any non-trivial feature. Choose one path at the start of this phase.

**Path A, run `domain-modelling` (default for anything non-trivial).** Invoke it in this session and
let its interview, silent build and walkthrough finish. Its design document (usually
`docs/designs/<feature>.md`) *is* this phase's deliverable. Record its path in the charter. If the
engineer wants it raised as its own PR first, let that land before cutting slices.

**Path B, a self-authored model, only for small work** (a narrow fix, a one-file change with no new
concept). Write down the important domain objects, their properties and behavior, their
relationships, their states, the invariants, and what the API resources should look like. It must
still survive L25's checks: durable nouns, general / ours / plumbing, real layering, CRUD decided per
entity, and a cut pass. If a `FooManager`/`FooHandler`/`FooBuilder` appears, ask what real thing
it's standing in for (L26). When in doubt, take Path A.

Then design: the entities involved, the state each owns, the behavior that belongs to each (L16),
and where logic lives and why (L27, within its language scope). A plan that reads like a long
function or a pipeline of transforms is wrong. Prefer polymorphism over branching on a tag (L28).

Cut the work into slices, one coherent change each (L18). Aim for the size the house commits at. The
corpus median is 5–22 source lines and 1–2 files per commit (F2). If Path A produced an
implementation order, that order is the slice breakdown.

## Phase 3: Write one slice

Before writing, walk the laziness ladder (L29): does this need to exist; is it already in the
codebase; does the standard library, the platform or an installed dependency do it; is it one line;
only then the minimum that works. Validation, error handling, security and accessibility are never
cut to climb the ladder faster.

While writing, the Law and Craft are constraints, not a checklist for later. Reread the ledger's
Standing Orders before every slice. Specifically:

- **Write like the neighbors** (H1): their naming, error idiom (H5), comment density and voice (H2,
  H3), log channel (H12) and test layout.
- **Only what the task needs** (H6): no options, flags, retries, fallbacks or `try` blocks nobody
  asked for.
- **Reuse, don't paste** (H7).
- **Bug fix? Test first** (H11): write the test that reproduces it, run it, see it fail, record the
  failure in the ledger, then fix.
- **Every new external API call** (H15): confirm it in the installed source or docs for the locked
  version, and record where under "APIs checked" in the ledger.
- **Touch only what the change needs** (H9): no reformatting of other lines.
- **No assistant artifacts** (H16): no placeholders, no chat-addressed comments, no changelog notes
  in code, no invented example values.

Write the smallest coherent slice you can. Don't batch slices to save a review round.

## Phase 3.5: Triage

```
python3 -I <skill-dir>/scripts/triage.py <repo-root> --diff HEAD
```

`--diff HEAD` covers this slice's uncommitted work (earlier slices are already committed). Pass
`--max-lines` set to the fingerprint's p90 function size if the house differs much from 50. It
costs nothing, so run it every slice, in every mode.

Fix every near-verdict yourself before going on. Carry every lead forward to Phase 4 as a pointer,
not a pre-judged finding.

## Phase 4: Review

**`lite`**: no spawn. Self-check against the judgment-heavy rules (L3, L7, L16, L25, L26, L28, L31,
H1, H4, H6, H7) and every triage lead. List what you checked and what you concluded, label it
SELF-CHECKED, and treat anything you find as a finding against yourself.

**`full`**: on the first Phase 4 of the session, spawn the Reviewer:

```
Agent(
  subagent_type: "better-coding-reviewer",   # or "general-purpose" if not installed
  model: "haiku",
  description: "Reviewer (session)",
  prompt: <the brief below, with "Review mode: diff, round 1 of a persistent session. Keep the rules,
           fingerprint and Standing Orders in mind for every future message on this thread.">
)
```

Record its name or ID in `progress.md`. On every later Phase 4, continue the same agent with
`SendMessage(to: <name>, message: <this round's brief, minus the rule-reading line>)`. Wait for the
reply. If a continued Reviewer seems to have lost context, spawn a fresh one for that round, because
an unreliable verdict costs more than a spawn. Retire it and spawn fresh after about 10 slices.
Standing Orders travel with the ledger, not with the agent.

**`deep`**: a fresh Reviewer every slice, no `model` override, full rule files.

Pass **absolute** paths. A subagent has no conversation context and can't expand `~`. Resolve this
skill's directory from where this SKILL.md loaded (`~/.claude/skills/better-coding/` or
`<repo>/.claude/skills/better-coding/`).

The Reviewer's brief contains this, and nothing that colors the judgment:

- `Read <skill-dir>/references/reviewer.md and follow it exactly.` Then, in `full` mode on the first
  spawn: `Read <skill-dir>/references/cheatsheet.md, that's the rule set.` In `deep` mode: `Read
  <skill-dir>/references/law.md and <skill-dir>/references/craft.md, that's the rule set.`
- `Review mode: diff.` The repo path, `git diff HEAD` as the slice, and the changed files.
- `Read <state-dir>/fingerprint.md: judge Craft against this house.`
- Triage's leads for this slice (file:line, rule, label). In `deep` mode, also the near-verdicts you
  already fixed, so the Reviewer confirms the fix rather than taking your word for it.
- The precedence mode and the project instruction files to read under it.
- The charter's goal and acceptance criteria, and the domain model (path or text).
- The Standing Orders, every round, even to a continued Reviewer.

## Phase 5: Sentencing

Apply [references/ledger.md](references/ledger.md). Record every finding with its rule ID (L, C, H or
Q), severity, points, and source (`reviewer`, `self-check` or `auditor`). Then:

- **Any open violation**: no commit, not done.
- **Any CAPITAL**: the slice isn't patched. `git stash push -m "better-coding penalty <n>" -- <files
  this iteration touched>`, then rewrite from the clean base. Stash, never discard, and only files
  this loop touched this iteration.
- **15+ points in one round**: the slice goes back to Phase 2. Concentrated points mean the design
  was wrong.
- **A rule broken twice**: its points double, and it's promoted to Standing Orders.
- **A rule broken three times**: stop and escalate to the user with the ledger.

## Phase 6: Remediate

Fix every finding. A MINOR can be contested once, in writing, with a reason grounded in the code,
the fingerprint, or the precedence mode. "It reads better" doesn't count. If the Reviewer upholds
it, it gets fixed and counts double. Fixing means removing the cause. Silencing the check is CAPITAL,
and triage will catch it next slice.

If a fix changes the design (a type added, a concept split, a responsibility moved), amend the
charter's domain model **before** the next review, as a dated section that says what changed and
why. Keep the original text and never touch the acceptance criteria (C5). A model that no longer
describes the code fails the Auditor's L25 check, and the Reviewer, who only sees the diff, won't
catch it.

## Phase 7: Verify, then commit the slice

Run the real things and keep the real output: tests, linter, type checker, build. Walk the charter
and mark each criterion against evidence you produced. A criterion you couldn't run is
**unverified**, and unverified isn't met.

Record every command and its exact result under **Verification claims** in the ledger. The Auditor
will re-run each one, and a claim that doesn't reproduce is C4.

When the Reviewer's verdict for this slice is CLEAN (or SELF-CHECKED in `lite`) and verification
passes, commit the slice with a message written per L19 and H10, matching the fingerprint's commit
section. Stage the files you changed **by name**, and read `git status --short` before committing.
Never `git add -A` or `git add <directory>`: your own verification can leave `__pycache__`, build
output or scratch files behind, and a binary in a commit is a finding (L21, L13). Then check the
message:

```
python3 -I <skill-dir>/scripts/triage.py <repo-root> --diff HEAD~1 --commit HEAD
```

Amend the message if triage flags it. Keep any trailers the user's own configuration requires.

## Phase 8: The Auditor's gate

When every slice is done and every acceptance criterion looks met, spawn a **fresh** Auditor. Never
continue an earlier one, and never use the Reviewer for this.

```
Agent(
  subagent_type: "better-coding-auditor",    # or "general-purpose" if not installed
  description: "Auditor gate",
  prompt: <the brief below>
)
```

No `model` override: the Auditor runs on the session's default (strongest) model in every mode. Its
brief:

- `Read <skill-dir>/references/auditor.md and follow it exactly. Read
  <skill-dir>/references/reviewer.md, <skill-dir>/references/law.md and
  <skill-dir>/references/craft.md.`
- `Gate mode.` The repo path, the baseline SHA from the charter, and `HEAD`.
- The triage command to run: `python3 -I <skill-dir>/scripts/triage.py <repo> --diff <baseline>
  --commit HEAD`.
- Paths to `fingerprint.md`, `charter.md` (with "Criteria as first written") and the domain model.
- The ledger's **Verification claims**, **Regression tests seen failing** and **APIs checked**
  sections, verbatim, and nothing else from the ledger. No findings history, no Reviewer verdicts.
  Write them to `<state-dir>/auditor_claims.md` **at spawn time**, extracted from the ledger as it
  is then, and re-extract before every later gate. A claims file written earlier goes stale when
  the code changes, and a stale claim is a false claim.
- The precedence mode and the project instruction files.

The gate opens only when the Auditor returns CLEAN. That means no findings, every verification claim
reproduced, and every criterion MET. Then the ledger shows zero open violations and tests, lint,
type check and build pass on the current tree.

If the Auditor returns VIOLATIONS, record its findings (source `auditor`) and go to Phase 5. After
remediation, the next gate is another **fresh** Auditor. The last audit has to run after the last
change, because a CLEAN verdict on a stale tree proves nothing.

When the gate opens, report to the user: what was built, the domain model it came from, the mode,
the commits, the evidence, and the final ledger, including everything penalized along the way.
Report the ledger even when the run is clean. Especially then.

## Circuit breaker

Stop and escalate, with the ledger, the blocker and what's needed, when:

- the same rule has been broken three times;
- an acceptance criterion needs a decision only the user can make;
- something external blocks the work (credentials, a broken dependency, an unavailable service);
- two consecutive rounds produce no reduction in open violations;
- the Auditor has failed the gate three times.

Escalating with a clear blocker is a correct outcome. Declaring victory on unverified work never is.

## Never

These are the CAPITAL offenses in [references/law.md](references/law.md) and
[references/craft.md](references/craft.md), in every mode:

- Deleting, skipping or weakening a test to turn a build green.
- `# noqa`, `# type: ignore`, `eslint-disable`, a bare `any`/`Any`, or a blind cast used to silence a
  checker.
- `except X: pass` or any catch that hides a real failure from the caller.
- Claiming a command passed without running it, reporting a verdict an agent never gave, or
  reporting SELF-CHECKED as CLEAN.
- Skipping the Auditor's gate, reusing a previous Auditor, or showing the Auditor the Reviewer's
  verdicts.
- Editing the charter's acceptance criteria to fit what was built.
- Leaving a placeholder where real code belongs in anything reported as done.

## After the loop

For work headed to a pull request, hand off to the repo's own PR skills if it has them. Write the PR
description in the same register as the commits (H10): what was wrong, why this fixes it, what was
rejected. Plain prose, no inventory of files. For an existing codebase never built under this loop,
run `better-coding-review` first.
