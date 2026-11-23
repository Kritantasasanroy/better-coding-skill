# The Ledger

The ledger is the loop's memory. Without it, the same mistake made in round four is the same mistake
made in round one, and "penalty" means nothing.

It lives at `~/.claude/better-coding/state/<repo-slug>/ledger.md`, per `SKILL.md`'s State section.
Never in the repository, and deliberately persisted past the current session, that's what lets a
Standing Order survive a stop and a resume, not just a stop and a restart of the same round.

This file governs the build loop's penalty mechanics, used directly by `better-coding`, and reused
by `better-coding-review` once the user approves fixing what its audit found. The audit-only report
`better-coding-review` produces before that point is a different artifact, not a ledger; its format
lives in that skill's own `SKILL.md`.

## SELF-CHECKED is not CLEAN

In `lite` mode, Phase 4 rounds are judged by the Writer's own self-check instead of the Reviewer.
Record the source of every round's verdict: `reviewer`, `self-check`, or `auditor`. Never let a
self-checked round be reported, summarized or remembered as CLEAN. That word is reserved for an
independent agent's verdict. A self-check that finds nothing is recorded as "SELF-CHECKED: no issues
found", which is weaker evidence than CLEAN, and the ledger should read that way. Phase 8's gate is
always `auditor`-sourced, whatever mode the rest of the session ran in. If the last verdict in the
ledger isn't the Auditor's, the loop isn't done.

## Penalty schedule

| Severity | Points | Consequence |
| --- | --- | --- |
| CAPITAL | 10 | The slice is stashed and rewritten from the clean base. Not patched. |
| MAJOR | 5 | Fixed before anything else is written. No commit while one is open. |
| MINOR | 2 | Fixed this round, or contested once in writing. |

Escalation, applied per round:

- **Any open violation**, the work can't be committed and can't be called done.
- **Repeat of the same rule ID**, points double, and the rule is promoted to Standing Orders.
- **Third offense on the same rule ID**, stop the loop, escalate to the user with the ledger. Two
  rounds already failed to teach it; a third won't either.
- **15+ points in one round**, the whole slice returns to the design phase. Points concentrated like
  that are a design failure, not a coding failure, most often a missed or wrong L25 domain model.
- **A contested MINOR the Reviewer upholds**, counts double. Contesting is not free.
- **Two consecutive rounds with no reduction in open violations**, circuit breaker, escalate.

## The revert penalty

A CAPITAL finding means the slice is not repaired, it's redone. Patching over a suppressed check or
a gutted test leaves the shape of the mistake in the code.

```
git stash push -m "better-coding penalty <n>" -- <files this iteration touched>
```

- **Stash, never discard.** The work is recoverable, it just doesn't count.
- **Only files this loop wrote in this iteration.** Never a file the user had already modified.
- If the working tree was dirty at loop start, those changes belong to the user, leave them alone
  and ask before going near them.

## Standing Orders

Any rule broken twice is copied here verbatim and **re-read before every subsequent slice**. This is
the mechanism that makes a penalty change behavior instead of just recording it, the rule stops
being one line among thirty and becomes an active constraint on the next thing written.

## Format

```markdown
# Ledger — <goal>

Baseline: <branch> @ <sha> | tree at start: clean | dirty (<files, untouchable>)
Mode: lite | full | deep | Precedence mode: <project wins | Law wins | hand in hand>
Fingerprint: ~/.claude/better-coding/state/<repo-slug>/fingerprint.md

## Standing Orders
- [L25] Non-trivial feature work starts with a written domain model, not a class. (broken R1, R2, 2x points)

## Round 2 (reviewer, full mode)
Reviewer: VIOLATIONS
| ID | Severity | Location | Points | State |
| --- | --- | --- | --- | --- |
| C1 | CAPITAL | src/billing/plan.py:19 | 10 | fixed, stashed and rewritten without `dict[str, Any]` |
| L26 | MAJOR | src/billing/plan_manager.py | 5 | fixed, PlanManager split into Plan and PlanRenewal |
| L29 | MAJOR | src/billing/plan.py:44 | 5 (yagni) | fixed, removed hand-rolled retry loop, stdlib has it |
| H6 | MAJOR | src/billing/plan.py:12 | 5 | fixed, dropped unrequested `timeout` parameter |

Round total: 25 -> slice returned to design (15+ rule)
Open: 0

## Verification claims
The Auditor re-runs every line here and compares. Write the exact command and the exact result.
- `pytest tests/` — 84 passed
- `mypy src/` — Success: no issues found in 12 source files
- Criterion 2 (renewal transitions SubscriptionStatus correctly) — `pytest tests/test_renew.py::test_renew_moves_past_due_to_active` — passed

## Regression tests seen failing (H11)
- tests/test_renew.py::test_renew_moves_past_due_to_active — failed on baseline (AssertionError: PAST_DUE != ACTIVE), passes with the fix

## APIs checked (H15)
- `stripe.Subscription.modify` — .venv/lib/python3.11/site-packages/stripe/_subscription.py:1840 (stripe 7.4.0)

## Gate (auditor, required regardless of session mode)
Auditor: VIOLATIONS (C4: `mypy src/` claimed clean, reproduced 1 error) -> fixed -> Auditor: CLEAN
Every verification claim reproduced: MATCH.

## Final
Rounds: 5 (3 reviewer, 1 self-check mid-loop, 1 auditor re-run) | Total penalties: 53 | Open: 0 | Verdict: CLEAN (auditor)
```

## Reporting

The final ledger goes to the user when the work is delivered, including every penalty taken along
the way. A clean run that hid three CAPITAL reverts is a dishonest report, and the record of what
went wrong is more useful to the user than the fact that it was eventually fixed.
