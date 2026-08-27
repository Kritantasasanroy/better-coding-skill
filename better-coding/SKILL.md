---
name: better-coding
description: >
  Write code under continuous enforcement from project start. A cheap mechanical triage pass runs on
  everything, then a Warden agent independently audits what triage flagged and what it couldn't
  check, against a fixed rule set (the Law) covering domain modeling, object-oriented design,
  typing, and over-engineering, penalizes violations, and forces rework until the goal is fully met
  with zero open violations. Scales to any codebase size via triage-first, chunked audits, and a
  lite/full/deep mode so cost matches how much independent verification you actually need mid-loop,
  never at the final gate. Negotiates precedence against the project's own AGENTS.md/CLAUDE.md
  instead of assuming it. Checkpoints the goal, agenda, and current position to disk after every
  phase, so a session that stops from a context limit or interruption resumes from exactly where it
  left off instead of restarting. Use for any feature, fix, or refactor where quality matters, or to
  resume an interrupted one. Pairs with better-coding-review, which audits a whole existing codebase
  and can hand fixes to this loop, and with domain-modelling, which this loop's Phase 2 runs for any
  non-trivial feature to produce the domain model before code gets written.
argument-hint: "[lite|full|deep]"
---

# better-coding

Code doesn't get written here on trust. It gets written, triaged mechanically, audited by an
independent **Warden** wherever mechanics alone can't settle it, penalized wherever it breaks the
Law, reworked, and audited again. That cycle repeats until the goal is fully met and the ledger comes
back empty.

This is one of two paired skills. `better-coding` runs while code is being written, from the start
of a project or task. Its sibling, `better-coding-review`, audits code that already exists, produces
a report, and, only with the user's go-ahead, hands violations to this loop to fix. Both share the
same rule set and the same triage.

Four files carry the detail. Read each one when the phase that needs it begins, not before:

- [references/law.md](references/law.md): the enforceable rules, each with a stable ID.
- [references/triage.md](references/triage.md): the mechanical pass, patterns and chunking, that
  runs before any agent gets spawned.
- [references/warden.md](references/warden.md): the auditor's brief, handed to the Warden verbatim.
- [references/ledger.md](references/ledger.md): the penalty schedule and the ledger format.

A fifth skill, `domain-modelling`, is the canonical way Phase 2 below gets satisfied for anything
non-trivial: a full interactive session (interview, silent build, walkthrough) that ends in a design
document and, if the engineer wants it, a PR putting the model in front of the team before any
implementation starts. It is not optional polish, it is what "strictly follow the domain model before
writing code" means in practice, and its rules are folded into L25/L26/L27/L8/L29 below so the same
standard applies even when a full session wasn't run for this particular change.

## The two roles

You are the **Builder**. You plan, you write, you fix, and you run triage yourself, it's `grep`, not
judgment.

The **Warden** is a separate agent with its own context, spawned only when triage can't settle the
question on its own. It sees the code, the Law, and triage's leads, never your reasoning about why
the code is fine. It's the only authority on the judgment-heavy rules. You don't audit those
yourself, you don't argue a verdict into submission, and you don't get to declare yourself done on
anything the Warden hasn't actually seen.

## Mode: how much independent verification, and when

Set with the skill argument (`/better-coding lite|full|deep`) or by the user saying so; default
`full`. Mode controls the **judgment tier** only, triage always runs in full, on everything,
regardless of mode, since it's nearly free.

- **`lite`**: no Warden spawn during the loop. Triage's near-verdicts (C1/C2/C3-class findings) get
  fixed directly. Triage's leads and every judgment-only rule (L3 reachability, L7 responsibility
  depth, L25 domain-model quality, L28 branch shape, L31 orphan relationships, and anything not
  pattern-matchable) get a self-check by the Builder against the Law, explicitly labeled
  **SELF-CHECKED**, never CLEAN, those words mean different things and the ledger keeps them
  separate. Cheapest, and honestly weaker on exactly the failure mode this system exists to catch:
  a Builder rationalizing its own shortcut. Good for low-stakes, throwaway, or exploratory work.
- **`full`** (default): triage narrows the Warden's job, then a real independent Warden pass runs
  per slice, spawned with a lighter model (pass `model: "haiku"` to the `Agent` call) since a
  triage-narrowed, per-slice diff is well within a smaller model's judgment. Independent, just
  cheaper than defaulting to the strongest model for every routine round.
- **`deep`**: same independence, no shortcuts. Full `law.md` and `warden.md`, default/strongest
  model, no sampling, no triage-narrowing of what gets read in full.

**The one rule mode never overrides:** Phase 8's gate audit, the last one before anything is called
done, always runs as a genuine independent Warden pass, at `full` rigor or better, even in a `lite`
session. `lite` mode buys speed in the iterative middle of the loop. It does not buy a way to skip
independent verification entirely before commit, that would just be C4 with extra steps.

## Precedence is negotiated, not assumed

Most projects already have their own standard: `AGENTS.md`, `CLAUDE.md`, a doctrine file, a
`.cursorrules`. The Law does not silently outrank or silently defer to any of them.

The first time this skill runs in a repository this session, check for such files. If none exist,
the Law applies on its own, say so, and move on. If any exist, ask the user, once, with
`AskUserQuestion`:

- **Project wins.** The project's file is authoritative; the Law fills only what it leaves unstated,
  and never loosens what it locked down.
- **Law wins.** This Law is authoritative; the project's file fills gaps instead.
- **Hand in hand.** Both apply. A genuine conflict gets surfaced to the user the moment it's found,
  instead of resolved by assumption.

Record the answer in the charter. It holds for the rest of *this session only*, nothing about
precedence is written to disk, and it is not asked again in this session once decided, including on
a later conflict, that gets resolved by the standing choice, not a repeat question. A new session
starts the negotiation fresh.

## State

Loop state lives outside the repository (L13, writing loop bookkeeping into the user's project is a
scope violation), but it does **not** live in the session scratchpad. A session scratchpad is
scoped to the session that created it, a new terminal, a relaunch after a crash, a fresh `claude`
process all get a different one, so anything written there becomes unreachable the moment the
session that wrote it ends. That's exactly the case resumability has to survive.

Instead, state lives at a fixed, repo-keyed location under the user's home directory, the same on
every session, every terminal, every day, for as long as the repo stays at the same path:

```
~/.claude/better-coding/state/<repo-slug>/charter.md
~/.claude/better-coding/state/<repo-slug>/ledger.md
~/.claude/better-coding/state/<repo-slug>/progress.md
```

`<repo-slug>` is the repository's absolute path, lowercased, with every character that isn't a
letter, digit, or dash turned into a dash, repeated dashes collapsed to one: `git rev-parse
--show-toplevel` (or the current working directory if that fails) piped through something like
`tr 'A-Z' 'a-z' | sed 's/[^a-z0-9]/-/g; s/-\+/-/g'`. Compute it once, at the very start of Phase 0,
before checking for existing state, and reuse the same value for the rest of the session, it's what
lets a different repo's in-progress work coexist without collision and lets the *same* repo's work
be found again from any future session.

Precedence, per the section above, stays session-only on purpose, deliberately, it was decided that
way, don't move it here.

## Progress checkpoints, for resuming after a stop

A session can end mid-task: the agent stops, the context runs out, the connection drops. When that
happens, the next invocation remembers none of this conversation, only what's actually on disk.
`progress.md` exists so that next invocation picks up exactly where this one left off instead of
starting the whole loop over.

Write it immediately, before any real work begins, as the first thing Phase 0 does, with the full
goal and the full agenda already in it:

```markdown
# Progress — better-coding

## Goal
<one sentence, verbatim>

## Agenda
<the planned slice breakdown: the first slice for certain, later ones as "to be determined once
prior slices land" if the full breakdown isn't known yet, filled in as Phase 2 identifies them>

## Mode / Precedence
<settings, once resolved>

## Domain model
Path A (domain-modelling) | Path B (self-authored) — <path to the design doc, or "inline below">

## Status: NOT STARTED | IN PROGRESS | BLOCKED | DONE
Last updated: <phase, slice, timestamp>

## Completed
- [x] Recon
- [x] Domain model + design
- [x] Slice 1: <one line> — committed <sha>

## In progress right now
<the exact phase and slice, specific enough that reading only this one line says what to do next,
e.g. "Slice 3: Phase 4 audit, Warden spawned, awaiting verdict">

## Remaining
- [ ] Slice 3: <one line>
- [ ] Slice 4: <one line, if already known>
```

The goal and agenda have to be complete even in round one, before anything else gets written, a
resume with a missing or vague goal can't finish the job correctly no matter how good its record of
what already happened is.

After that, update it at every phase transition, not on a timer: after Recon, after Design, after
each slice is built, after each audit verdict, after each sentencing decision, after each
remediation, after each verify, after each gate check. A phase transition is the checkpoint unit,
not a clock. If a single phase is running long, for instance reading a lot of surrounding code
during Recon, that's exactly when an extra mid-phase update earns its cost, don't wait for the
phase to finish if it's taking a while.

**On starting Phase 0**, before writing a new charter: check whether `progress.md` already exists
with `Status` other than `DONE`. If it does, read it, cross-check its `Completed` slices against
real git history (`git log`, the commits it claims actually exist), and confirm in one line with the
user that this is the same goal before resuming, a goal that doesn't match what's being asked now is
a different task, not a resume, in that case start fresh and don't overwrite the old file until the
new charter is actually written. When it does match, resume at exactly the phase and slice named
under `In progress right now`, not from Phase 0 again. If no file exists, or `Status` is already
`DONE`, start fresh normally.

Mark `Status: DONE` only once Phase 8's gate actually passes and the ledger is reported per L19,
the same finish line the loop already has, this file just makes the path there resumable.

---

# The loop

## Phase 0: Charter, mode, and precedence

Don't write a line of code until all three exist.

Resolve the mode and run the precedence negotiation above. Then write `charter.md`: the goal in one
sentence, the mode, the precedence mode, and the **acceptance criteria** as a numbered list. Each one
has to be individually checkable by running something: a test, a command, a request, an observed
behavior. "Login works" isn't a criterion. "`POST /sessions` with a valid password returns 201 and a
session cookie; with a wrong password, 401" is.

Record the baseline too: current branch, `git rev-parse HEAD`, and whether the working tree was
dirty at the start. Pre-existing uncommitted changes belong to the user, not you. List them, never
revert them, and ask before touching them.

Acceptance criteria are frozen once written. If one turns out to be wrong or impossible, stop and
say so to the user. Don't quietly narrow them just to make the loop terminate.

## Phase 1: Recon

- Read the project's instruction files per the negotiated precedence, and any directory-level
  guidance near the files you'll touch.
- Search the repo for an existing solution before planning a new abstraction, helper, or dependency
  (L11). Read the neighboring code and match its idiom.
- Figure out what already owns this responsibility. Most work belongs on an existing type, not a new
  one.

## Phase 2: Domain model, then design

L25 is not optional for any non-trivial feature, and it's satisfied properly, not with a paragraph
guessed at speed. Two paths, chosen once, at the start of this phase:

**Path A — run `domain-modelling` (the default for anything non-trivial).** Invoke the
`domain-modelling` skill directly, in this same session, before writing a line of code. Let its
interview, silent build, and walkthrough run to completion; its output (a design document, normally
at `docs/designs/<feature>.md`, occasionally an existing GitHub issue or plan file it was pointed at
instead) *is* this phase's deliverable. Record that document's path in the charter next to the goal.
If the engineer wants the design raised as its own PR first (`domain-modelling`'s Phase 12), let that
land before returning here to cut Phase 3's slices; that PR is documentation, not the feature, and
doesn't itself go through this loop's ledger.

**Path B — a same-session self-authored model, only for work too small to justify the full
session** (a narrow bug fix, a one-file change with no new concept). Write down, in plain text:

- What are the important domain objects?
- What properties and behavior belong to each?
- How do they relate to each other?
- What states can each one be in?
- What rules or invariants must always hold?
- What should the API resources look like, given this model?

A few lines per object is enough here, but it still has to survive L25's generalized checks, not just
list nouns: is each one a durable noun rather than the feature's own question in a costume; is it
marked general, ours, or plumbing, and does that placement actually hold (a business rule doesn't
belong in `application/common` just because generalizing it was tempting); does the layering hold (every
child names its parent, no duplicated identity fields); is CRUD decided per entity, not left implicit;
and did a cut pass actually run over what got written. If a name like `FooManager`, `FooHandler`, or
`FooBuilder` shows up while doing this, stop and ask what real thing it's standing in for (L26), the
answer usually replaces it with the thing itself. If in doubt about which path this feature needs,
default to Path A, a session that turns out to be short is cheap; a feature modeled by a guessed
paragraph that turns out to need real thought is not.

Save the result beside the charter either way; the Warden checks the implementation against it, in
every mode including `lite`'s self-check.

Only once the model exists: name the entities involved, the state each owns, and the behavior that
belongs to each (L16). Say where the logic lives and why that's the right home for it — on the
concept itself by default, on a reader/writer when the decision spans concepts, never bolted onto a
domain object as orchestration it doesn't own (L27). If your plan reads like a long function, a
pipeline of transforms, or a class named for what it does rather than what it is, the plan is wrong
(L27), go find the entity it actually belongs to. Prefer polymorphism over branching on a type tag
(L28).

Then cut the work into slices. One slice is one coherent change (L18). If Path A produced an
implementation plan with its own step order, that order **is** the slice breakdown, don't re-derive
one.

## Phase 3: Build one slice

Before writing the slice, walk the laziness ladder (L29): does this need to exist, is it already in
the codebase, does the standard library do it, does the platform do it natively, does an installed
dependency cover it, is it one line, only then write the minimum that works. This never overrides
validation, error handling, security, or accessibility, those are written in full regardless of what
rung you land on.

Write the smallest coherent slice you can. Don't batch three slices together to save an audit round,
in `full`/`deep` mode a large diff still buries violations and the revert penalty gets expensive on
a pile of unrelated changes. (`lite` mode's cheapness comes from skipping the agent spawn, not from
skipping this discipline, small slices stay small regardless of mode.)

While you write, treat the Law as a constraint, not a checklist for later. Reread the Standing
Orders section of the ledger, the rules you've already broken once, before every slice.

## Phase 3.5: Triage

Run [references/triage.md](references/triage.md)'s patterns against this slice's changed files.
This costs `grep`, not tokens, do it every slice, every mode, no exception.

Fix every near-verdict (C1/C2/C3-class) hit yourself before proceeding, these don't need a second
opinion to confirm they're real. Carry every lead (Optional usage, generic-suffix names, module-level
functions, orphan-class candidates, long functions) forward into whichever audit step comes next, as
a pointer, not a pre-judged finding.

## Phase 4: Audit

What runs here depends on the mode set in Phase 0.

**`lite`**: no spawn. Self-check the slice against `law.md`'s judgment-heavy rules (L3, L7, L16,
L25, L26, L28, L31, and anything triage flagged as a lead) as rigorously as you can, list what you
checked and what you concluded, and label the result **SELF-CHECKED**, not CLEAN. Proceed to
Phase 5 treating any self-identified issue as a finding against yourself.

**`full`**: one Warden for the whole build session, not one per slice. Slices in this loop are
never parallel, you can't start slice 2 until slice 1 is audited and fixed, so there's no
concurrency to lose by keeping a single Warden alive instead of spawning fresh each round. What that
buys back is real: the rules only get read once for the entire feature instead of once per slice,
which is most of the fixed cost a fresh spawn pays every single time. On the **first** Phase 4 of
the session:

```
Agent(
  subagent_type: "general-purpose",
  model: "haiku",
  run_in_background: false,
  description: "Warden (session)",
  prompt: <the brief below, with "Audit mode: diff, round 1 of a persistent session." and an
           instruction to hold the rules and Standing Orders in mind for every future message
           on this thread, not just this round>
)
```

Remember the agent's name or ID from that spawn. On **every subsequent** Phase 4 in this session,
don't spawn again, continue the same agent:

```
SendMessage(
  to: <the Warden's name from the first spawn>,
  message: <this round's brief, same shape as below, minus the rule-set Read instructions,
            it already has them>
)
```

Wait for the reply before moving to Phase 5, same as a fresh spawn, this is still blocking. If
continuation ever behaves unexpectedly, misses context, or you're not confident it actually carried
the prior rounds forward, fall back to a fresh spawn for that round rather than trust a doubtful
verdict, a wasted spawn costs tokens, an unreliable verdict costs correctness, and correctness wins
that trade every time. Retire the session Warden and start a fresh one if a build session runs long,
past roughly 10 slices, so its own context doesn't grow unbounded, the ledger's Standing Orders
travel with it into the new one regardless, since those live in `ledger.md`, not in the Warden's own
memory.

**`deep`**: a fresh spawn every slice, deliberately no persistence. This is the tier with no
shortcuts, and continuation, useful as it is for cost, is still a shortcut: a Warden that remembers
agreeing to something earlier in the same thread is a Warden slightly more likely to agree to
something similar again, see `warden.md`'s standing position on this. `deep` mode trades that
efficiency away on purpose.

```
Agent(
  subagent_type: "general-purpose",
  run_in_background: false,
  description: "Warden audit",
  prompt: <the brief below>
)
```

**Phase 8's gate audit, regardless of the session's mode**: always a fresh spawn, always full
rigor, never a continuation of the session Warden even if one exists. This is both the honest final
check and the backstop against the exact risk `deep` mode avoids by never persisting in the first
place, a Warden that's been agreeing with you all session is the wrong one to trust for the verdict
that decides whether the work is actually done.

Pass **absolute** paths on every spawn. A fresh Warden has no conversation context, so its `Read`
cannot expand `~` or resolve anything relative to this file. Resolve this skill's own directory to a
concrete absolute path first: it's wherever this SKILL.md actually loaded from, whether that's a
user-level install (`~/.claude/skills/better-coding/`, e.g.
`C:\Users\<you>\.claude\skills\better-coding\` on Windows) or a project-level one checked into the
repo (`<repo-root>/.claude/skills/better-coding/`). If it isn't already obvious, check both for
`references/law.md` and use whichever exists.

The brief must contain, and nothing else that colors the judgment:

- **`full` mode, first spawn only:** `Read <skill-dir>/references/cheatsheet.md and follow it
  exactly, that's the rule set and the standing position for this session.` The condensed rulebook,
  one line per rule instead of the full rationale, read once and carried forward by the same agent
  for every round after this one. **`deep` mode**, and **Phase 8's gate audit regardless of the
  session's mode**: `Read <skill-dir>/references/warden.md and follow it exactly. Read
  <skill-dir>/references/law.md, that's the rule set.`, the full files, no compression, every time,
  this is the tier and the check that have to be trustworthy on their own.
- `Audit mode: diff.`
- The repo path, the baseline ref, and the changed files.
- Triage's leads for this slice (file:line, which pattern), so the Warden verifies and expands
  instead of rediscovering them cold. In `full` mode, triage's near-verdicts you already fixed don't
  need to be re-included, they're resolved; in `deep` mode, include them anyway so the Warden
  confirms the fix rather than trusting your own report of it.
- The negotiated precedence mode, and the project's instruction files to read under it.
- The charter's goal, acceptance criteria, and this slice's domain model (from Phase 2).
- The Standing Orders (repeat-offense rules), if there are any yet, every round, even to a
  continued session Warden, a rule promoted to Standing Orders mid-session needs to reach it just as
  reliably as a fresh spawn would get it.

Never include your own justification for a choice, a summary of what the code "does," or any hint of
what verdict you're expecting. The Warden reads the code. That's all it gets.

## Phase 5: Sentencing

Apply [references/ledger.md](references/ledger.md). Record every finding with its rule ID, severity,
points, and whether it came from a Warden verdict or a `lite`-mode self-check, the ledger keeps those
distinct. Then work through the consequences:

- **Any open violation**: you can't commit, and you can't call the work done.
- **Any CAPITAL finding**: the slice doesn't get patched. Stash it
  (`git stash push -m "better-coding penalty <n>" -- <files this iteration touched>`) and rewrite
  from the clean base. Stash, never discard, and only the files this loop touched this iteration.
- **15+ points in one round**: the whole slice goes back to Phase 2. The design was wrong, most
  often a missed or wrong domain model, not just the code.
- **A rule broken twice**: its points double, and it gets promoted into Standing Orders.
- **A rule broken three times**: stop the loop and escalate to the user with the ledger. Two rounds
  already failed to fix it, so a third one won't either.

## Phase 6: Remediate

Fix every finding. A MINOR finding can be contested exactly once, in writing, with a reason grounded
in the code or the negotiated precedence. "It reads better" doesn't count. A contested finding goes
back to the Warden next round (in `lite` mode, back to your own self-check); if it's upheld, it gets
fixed and it counts double.

Fixing means removing the cause. Silencing the check instead is a CAPITAL offense, every single
time, and triage will likely catch you doing it on the very next slice.

## Phase 7: Verify

Run the real thing and paste the real output: the project's test command, linter, type checker,
build. Then walk the charter and mark each acceptance criterion against evidence you actually
produced yourself.

A criterion is met when a command says so, not when the code looks correct and not because you
reasoned it should work. If you couldn't run something, that criterion is **unverified**, and
unverified doesn't count as met.

## Phase 8: Gate

Loop back to Phase 3 unless all of the following hold, at the same time:

- Every acceptance criterion in the charter is met, with evidence attached.
- **A genuine independent Warden audit**, at `full` rigor or better, over the full diff, after your
  last edit, comes back CLEAN. If the session ran in `lite` mode throughout, this is the one point
  where a real agent still gets spawned, once, before commit, regardless of mode. A SELF-CHECKED
  result never satisfies this gate on its own.
- The ledger shows zero open violations.
- Tests, lint, type check, and build all pass on the current tree.

The last audit has to run after the last change. A CLEAN verdict on a stale diff proves nothing at
all.

When the gate opens, commit per L19 and report back to the user: what got built, the domain model it
was built from, the mode the session ran in, the evidence, and the final ledger, including everything
that was penalized along the way. Report the ledger even when the run is clean. Especially then.

## Circuit breaker

The loop runs until the goal is met, but it doesn't spin forever. Stop and escalate, with the
ledger, the blocker, and what you'd need to move forward, when:

- The same rule has been broken three times.
- An acceptance criterion needs a decision only the user can make.
- Something external is blocking you: missing credentials, a broken dependency, an unavailable
  service.
- Two consecutive rounds produce no reduction in open violations.

Escalating with a clear blocker is a correct outcome. Declaring victory on unverified work never is.

## Never

These aren't shortcuts. They're the CAPITAL offenses in [references/law.md](references/law.md), and
none of them are negotiable, in any mode:

- Deleting, skipping, or weakening a test to turn a build green.
- `# noqa`, `# type: ignore`, `eslint-disable`, a bare `any`/`Any`, or a blind cast used to silence a
  checker.
- `except X: pass`, or catching an error only to hide it from whoever's calling you.
- Claiming a command passed without running it, or reporting a verdict the Warden never gave, or
  reporting SELF-CHECKED as CLEAN.
- Skipping Phase 8's independent gate audit because the rest of the session ran in `lite` mode.
- Editing the charter's acceptance criteria to fit whatever you ended up building.

## After the loop

For work headed toward a pull request, hand off to the repo's own `pr-conventions` and
`pr-review-loop` skills, if they exist. This skill governs how the code gets written. Those govern
how it ships. For an existing codebase that was never built under this loop, use
`better-coding-review` first, it produces the report this skill's Phase 0 through 2 would otherwise
have no way to generate for code nobody here wrote. For the domain model specifically, `domain-
modelling` governs how it gets decided, before Phase 2 ever writes a class; this loop governs
everything from there on.
