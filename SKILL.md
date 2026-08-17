---
name: better_coding
description: Write code under enforcement. A Warden agent audits every change against a fixed rule set (the Law), penalises violations, and forces rework until the goal is 100% met with zero open violations. Use for any feature, fix, or refactor where quality matters — and whenever the user asks for strict, compliant, or reviewed coding.
---

# better_coding

Code is not written here on trust. It is written, audited by an independent **Warden**, penalised
where it breaks the Law, reworked, and re-audited — until the goal is fully met and the ledger is
empty.

Three files carry the detail. Read them when the phase that needs them begins, not before:

- [references/law.md](references/law.md) — the enforceable rules, each with a stable ID.
- [references/warden.md](references/warden.md) — the auditor's brief. Handed to the Warden verbatim.
- [references/ledger.md](references/ledger.md) — the penalty schedule and the ledger format.

## The two roles

You are the **Builder**. You plan, write, and fix.

The **Warden** is a separate agent with its own context. It sees the diff and the Law, never your
reasoning about why the code is fine. It is the only authority on compliance. You do not audit your
own work, you do not argue a verdict into submission, and you do not declare yourself done — the
Warden's report and the command output do that.

## Precedence

The project's `AGENTS.md` and `CLAUDE.md` outrank the Law. Read them in the recon phase.

- Where the project is stricter, the project rule replaces the Law's version.
- Where the project is silent, the Law applies.
- The Law is never used to loosen a project rule. If this repo bans all comments, "comments that
  explain why" are still banned.

## State

Loop state lives in your session scratchpad under `better_coding/` — `charter.md` and `ledger.md`.
Never in the repository. Writing loop bookkeeping into the user's project is itself a scope
violation (L13).

---

# The loop

## Phase 0 — Charter

Do not write a line of code until the charter exists.

Write `charter.md`: the goal in one sentence, then the **acceptance criteria** as a numbered list of
statements that are individually checkable by running something — a test, a command, a request, an
observed behaviour. "Login works" is not a criterion. "`POST /sessions` with a valid password
returns 201 and a session cookie; with a wrong password returns 401" is.

Record the baseline: current branch, `git rev-parse HEAD`, and whether the working tree was dirty at
start. **Pre-existing uncommitted changes are the user's, not yours** — list them, never revert them,
and ask before touching them.

Acceptance criteria are frozen. If one turns out to be wrong or impossible, you stop and say so to
the user. You never quietly narrow them to make the loop terminate.

## Phase 1 — Recon

- Read the project's `AGENTS.md` / `CLAUDE.md` and any directory-level guidance near the files you
  will touch.
- Search the repo for an existing solution before you plan a new abstraction, helper, or dependency
  (L11). Read the neighbouring code and match its idiom.
- Identify what already owns this responsibility. Most work belongs on an existing type.

## Phase 2 — Design

Before code: name the entities involved, the state each owns, and the behaviour that belongs to
each (L16). Say where the logic lives and why that is the right owner. If your plan is a long
function, the plan is wrong — find the entity it belongs to.

Then cut the work into slices. One slice is one coherent change (L18).

## Phase 3 — Build one slice

Write the smallest coherent slice. Do not batch three slices to save an audit round — a large diff
buries violations and makes the revert penalty expensive.

While writing, the Law is a constraint, not a later checklist. The Standing Orders section of the
ledger (rules you have already broken once) is re-read before every slice.

## Phase 4 — Audit

Spawn the Warden. Blocking — the next step depends on the verdict:

```
Agent(
  subagent_type: "general-purpose",
  run_in_background: false,
  description: "Warden audit",
  prompt: <the brief below>
)
```

Pass **absolute** paths — the Warden is a fresh agent with no conversation context, so its `Read`
cannot expand `~` or resolve anything relative to this file. Resolve this skill's own directory to
a concrete absolute path first: it is wherever this SKILL.md actually loaded from — a user-level
install (`~/.claude/skills/better_coding/`, e.g. `C:\Users\<you>\.claude\skills\better_coding\` on
Windows) or a project-level one checked into the repo (`<repo-root>/.claude/skills/better_coding/`).
If it isn't already obvious, check both for `references/law.md` and use whichever exists.

The brief must contain, and nothing else that colours the judgement:

- `Read <skill-dir>/references/warden.md and follow it exactly.`
- `Read <skill-dir>/references/law.md — that is the rule set.`
- The repo path, the baseline ref, and the changed files.
- The project guidance files to read (`AGENTS.md`, `CLAUDE.md`) and the precedence rule.
- The charter's goal and acceptance criteria.
- The Standing Orders (repeat-offence rules), if any.

Never include your justification for a choice, a summary of what the code "does", or any framing of
what you expect the verdict to be. The Warden reads the code.

## Phase 5 — Sentencing

Apply [references/ledger.md](references/ledger.md). Record every finding with its rule ID, severity,
and points. Then:

- **Any open violation** → you may not commit, and you may not call the work done.
- **Any CAPITAL finding** → the slice is not patched. Stash it (`git stash push -m "better_coding
  penalty <n>" -- <files this iteration touched>`) and rewrite from the clean base. Stash, never
  discard, and only files this loop wrote.
- **15+ points in one round** → the whole slice goes back to Phase 2. The design was wrong, not the
  code.
- **A rule broken twice** → its points double and it is promoted into Standing Orders.
- **A rule broken three times** → stop the loop and escalate to the user with the ledger. Something
  about the approach is wrong and another iteration will not find it.

## Phase 6 — Remediate

Fix every finding. MINOR findings may be contested exactly once, in writing, with a reason grounded
in the code or a project rule — "it reads better" is not one. A contested finding goes back to the
Warden in the next round; if it is upheld, it is fixed and it counts double.

Fixing means removing the cause. Silencing the check is a CAPITAL offence, every time.

## Phase 7 — Verify

Run the real thing and paste the real output: the project's test command, linter, type checker, and
build. Then walk the charter and mark each acceptance criterion against evidence you actually
produced.

A criterion is met when a command says so. Not when the code looks correct, not when you reason
that it should work. If you could not run something, that criterion is **unverified**, and
unverified is not met.

## Phase 8 — Gate

Loop back to Phase 3 unless **all** of these hold:

- Every acceptance criterion in the charter is met, with evidence.
- The Warden's latest audit — a fresh one, over the full diff, after your last edit — returns CLEAN.
- The ledger has zero open violations.
- Tests, lint, type check, and build all pass on the current tree.

The last audit must run *after* the last change. A CLEAN verdict on a stale diff proves nothing.

When the gate opens, commit per L19 and report to the user: what was built, the evidence, and the
final ledger including everything that was penalised along the way. The ledger is reported even
when the outcome is clean — especially then.

## Circuit breaker

The loop runs until the goal is met, but it does not spin. Stop and escalate — with the ledger, the
blocker, and what you would need — when:

- The same rule has been broken three times.
- An acceptance criterion needs a decision only the user can make.
- Something external blocks you: missing credentials, a broken dependency, an unavailable service.
- Two consecutive rounds produce no reduction in open violations.

Escalating with a clear blocker is a correct outcome. Declaring victory on unverified work is not.

## Never

These are not shortcuts, they are the CAPITAL offences in [references/law.md](references/law.md):

- Deleting, skipping, or weakening a test to turn a build green.
- `# noqa`, `# type: ignore`, `eslint-disable`, `any`, or a blind cast to silence a checker.
- `except X: pass`, or catching an error only to hide it.
- Claiming a command passed without running it, or reporting a verdict the Warden did not give.
- Editing the charter's acceptance criteria to fit what you built.

## After the loop

For work that becomes a pull request, hand off to the repo's own `pr-conventions` and
`pr-review-loop` skills if they exist. This skill governs how the code is written; those govern how
it ships.
