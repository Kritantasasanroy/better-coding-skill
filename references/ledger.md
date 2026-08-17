# The Ledger

The ledger is the loop's memory. Without it, the same mistake is made in round four that was made in
round one, and "penalty" means nothing.

It lives at `<scratchpad>/better_coding/ledger.md`. Never in the repository.

## Penalty schedule

| Severity | Points | Consequence |
| --- | --- | --- |
| CAPITAL | 10 | The slice is stashed and rewritten from the clean base. Not patched. |
| MAJOR | 5 | Fixed before anything else is written. No commit while one is open. |
| MINOR | 2 | Fixed this round, or contested once in writing. |

Escalation, applied per round:

- **Any open violation** — the work cannot be committed and cannot be called done.
- **Repeat of the same rule ID** — points double, and the rule is promoted to Standing Orders.
- **Third offence on the same rule ID** — stop the loop, escalate to the user with the ledger. Two
  rounds have already failed to teach it; a third will not.
- **15+ points in one round** — the whole slice returns to the design phase. Points concentrated
  like that are a design failure, not a coding failure.
- **A contested MINOR that the Warden upholds** — counts double. Contesting is not free.
- **Two consecutive rounds with no reduction in open violations** — circuit breaker; escalate.

## The revert penalty

A CAPITAL finding means the slice is not repaired, it is redone. Patching over a suppressed check or
a gutted test leaves the shape of the mistake in the code.

```
git stash push -m "better_coding penalty R<round>" -- <files this iteration touched>
```

- **Stash, never discard.** The work is recoverable; it just does not count.
- **Only files this loop wrote in this iteration.** Never a file the user had already modified.
- If the working tree was dirty at loop start, those changes belong to the user — leave them alone
  and ask before going near them.

## Standing Orders

Any rule broken twice is copied here verbatim and **re-read before every subsequent slice**. This is
the mechanism that makes a penalty change behaviour instead of just recording it — the rule stops
being one line among thirty and becomes an active constraint on the next thing written.

## Format

```markdown
# Ledger — <goal>

Baseline: <branch> @ <sha> | tree at start: clean | dirty (<files — untouchable>)

## Standing Orders
- [L13] Every changed file traces to the stated goal. (broken R1, R3 — 2x points)

## Round 3
Warden: VIOLATIONS
| ID | Severity | Location | Points | State |
| --- | --- | --- | --- | --- |
| C1 | CAPITAL | src/api/session.py:44 | 10 | fixed — stashed, rewritten without `# type: ignore` |
| L13 | MAJOR | src/utils/format.py | 10 (2x repeat) | fixed — reverted, unrelated to goal |
| L9 | MINOR | src/api/session.py:12 | 2 | contested — `handle` is the repo's term |

Round total: 22 → slice returned to design (15+ rule)
Open: 0

## Verification
- `pytest tests/` — 84 passed
- `mypy src/` — no issues in 12 files
- Criterion 3 (401 on bad password) — MET, `curl` returned 401

## Final
Rounds: 4 | Total penalties: 38 | Open: 0 | Verdict: CLEAN
```

## Reporting

The final ledger goes to the user when the work is delivered — including every penalty taken along
the way. A clean run that hid three CAPITAL reverts is a dishonest report, and the record of what
went wrong is more useful to the user than the fact that it was eventually fixed.
