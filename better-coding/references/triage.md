# Triage

A mechanical pass that runs before any agent gets spawned, in every mode, on any amount of code.
It costs a handful of `grep`/`rg` calls, not tokens, and it does two jobs: it catches the subset of
the Law that's genuinely pattern-matchable without judgment, and it narrows what a Warden has to
read cold, so independent review, when it does run, spends its attention on what actually needs it
instead of rediscovering the obvious.

Triage findings are **leads, not verdicts**. A grep hit for `Optional[` is not a violation, `Optional`
is sometimes correct, it's a location worth a judgment call. A grep hit for `# type: ignore` *is*
close to a verdict, C1 has almost no legitimate exception. Treat each pattern below accordingly, the
notes say which is which.

## Scoping the file set

Two counts, always, before any pattern or any agent, and reported to the user as the first line of
any audit: how many files exist, then how many lines. Skipping straight to "here's the report"
without stating scope is how a partial pass quietly gets read as a complete one.

**1. Total tracked source files:**

```
git ls-files -- '*.py' '*.ts' '*.tsx' '*.js' '*.jsx'
```

`git ls-files` already excludes what `.gitignore` excludes: `node_modules`, build output, virtual
environments, lockfiles. If the repo isn't a git repo, fall back to `find` with explicit excludes for
those same categories.

**2. Filter to the important set.** Not every tracked file is something the Law has an opinion on.
Exclude, by default:

```
git ls-files -- '*.py' '*.ts' '*.tsx' '*.js' '*.jsx' \
  ':!:tests/**' ':!:test/**' ':!:__tests__/**' \
  ':!:**/test_*.py' ':!:**/*_test.py' ':!:**/*.test.ts' ':!:**/*.test.tsx' ':!:**/*.spec.ts' \
  ':!:**/*.md' ':!:**/*.mdx' \
  ':!:**/node_modules/**' ':!:**/__pycache__/**' ':!:**/dist/**' ':!:**/build/**' ':!:**/.venv/**' \
  ':!:**/migrations/**'
```

Tests, docs, generated output, and migrations are excluded **by default**, not because the Law
doesn't apply to them (bettercoding.md is explicit that its comment rule covers tests and config
too), but because a compliance pass on production/domain code is a different, smaller, and more
urgent question than "are the tests written correctly," and bundling them inflates every count and
dilutes attention on the code that actually carries the domain model. State the exclusion explicitly
in the report header, and treat it as overridable: a user who wants tests in scope says so, and gets
the same pass with a smaller exclusion list, not a different mechanism.

**3. Line count on the filtered set**, one call, not a per-file loop:

```
git ls-files [same filters] | tr '\n' '\0' | xargs -0 wc -l | tail -1
```

Never trust `xargs wc -l | tail -1` without checking `grep -c total` on its output first, past
`xargs`'s per-call argument limit it silently splits into multiple batches and each one prints its
own `total`, so `tail -1` grabs only the last batch. On a repository with hundreds of files this is
not a hypothetical, use the `tr '\n' '\0' | xargs -0 wc -l` form above, or confirm the batch count is
1 before trusting a plain `xargs wc -l`.

For reference, on a real 1,022-file repository: the full source set is 72,594 lines; filtering out
tests, docs, and generated content drops that to 730 files and 27,181 lines, well under half. That
difference is the whole reason filtering happens before anything else, not after.

## Patterns

Each line is a starting point, extend it for languages or frameworks the project actually uses,
these are not exhaustive.

**Near-verdicts (C1, C2, C3), report as violations, a Warden only needs to confirm the fix, not
rediscover the problem:**

```
# noqa / type: ignore / eslint-disable / ts-ignore
rg -n '#\s*noqa|#\s*type:\s*ignore|eslint-disable|@ts-ignore' -- '*.py' '*.ts' '*.tsx'

# bare `any` / `Any` bypassing real typing
rg -n '\bAny\b|:\s*any\b|<any>|as any\b' -- '*.py' '*.ts' '*.tsx'

# bare except / empty catch
rg -n -U 'except\s*:\s*\n\s*pass' -- '*.py'
rg -n -U 'catch\s*\([^)]*\)\s*\{\s*\}' -- '*.ts' '*.tsx' '*.js'
```

**Leads (need a judgment call), hand to the Warden as "look here first," never auto-fix on a grep
hit alone:**

```
# Optional / nullable, L5 and L30
rg -n 'Optional\[|:\s*\w+\s*\|\s*None|\?\s*:' -- '*.py' '*.ts' '*.tsx'

# generic-suffix names, L26
rg -n 'class \w*(Manager|Helper|Utils|Processor|Generator)\b' -- '*.py' '*.ts' '*.tsx'

# module-level function or constant outside a class, L27 (Python: unindented def is reliable)
rg -n '^def \w+' -- '*.py'

# dead code markers, L21
rg -n 'TODO|FIXME|console\.log|# ?debug' -- '*.py' '*.ts' '*.tsx' '*.js'
```

**Orphan-class candidates, L31, two greps per class, still free:**

```
for name in $(rg -o 'class (\w+)' -r '$1' -- '*.py' '*.ts' '*.tsx'); do
  hits=$(rg -c "\b${name}\b" -- '*.py' '*.ts' '*.tsx' | awk -F: '{s+=$2} END {print s}')
  # hits == 1 means the only mention is the class's own definition line: orphan candidate
done
```

A count of 1 is a lead, not a verdict, a class can be legitimately instantiated through a factory,
a registry, or reflection, in ways a name-grep won't see. Hand these to the Warden rather than
deleting on sight.

**Long functions, L16 / bettercoding §6's ~50-line guideline, approximate:**

```
awk '/^def |^    def /{name=$0; start=NR} /^def |^    def |^$/{if (name && NR-start>50) print FILENAME":"start": "name; name=""}' file.py
```

Treat the threshold as a flag to look, not a hard rule, some functions earn their length.

## Chunking a whole repository

For `better-coding-review`'s whole-repository mode, chunk by size, not by directory. A module can be
2 files or 200, splitting "by module" alone produces wildly uneven chunks and starves attention on
the large ones.

1. `git ls-files` the source file set (per above).
2. Get line counts with **one** `wc -l` call over the whole file list
   (`git ls-files -z -- '*.py' ... | xargs -0 wc -l`), never a naive `xargs wc -l | tail -1` on a
   large file set, `xargs` silently splits into multiple batches past its argument-length limit and
   each batch prints its own `total`, so `tail -1` grabs only the last batch, not the real total.
   Confirm with `grep -c total` on the output; more than one match means you undercounted. Build the
   manifest as `path, lines`.
3. Bin files into chunks with a target budget: **~6000 lines per chunk in `full` mode, ~1200 in
   `deep` mode.** These aren't the same kind of number. In `deep` mode every file in a chunk gets
   fully read, so the bin size caps a Warden's real reading load. In `full` mode a chunk's Warden
   only reads triage's leads plus a sample within it (Phase 2/3 of the review skill), not the whole
   bin, so the bin size mostly controls spawn count and locality grouping, not reading load, which
   is why it can run 5x larger without asking any one Warden to read more. Keep files from the same
   directory together while filling a bin; split only when a single directory would blow the budget
   alone.
4. Spawn Wardens for a wave of chunks together, in one message, not one at a time, independent
   chunks don't block each other. Cap a wave at roughly 6 to 8 spawns; a repo needing more chunks
   than that runs in multiple waves rather than one enormous parallel burst.
5. In `full` mode, hand each Warden [cheatsheet.md](cheatsheet.md) instead of the full `law.md` +
   `warden.md`. It's the same rules at one line each instead of the full rationale and examples,
   which is most of the fixed cost paid on every spawn, repeated once per chunk. `deep` mode and the
   mandatory Phase 8 gate audit in `better-coding` always get the full files, the compression is a
   `full`-mode-only trade and never applies to the one audit that has to be trustworthy on its own.

For this repository (1,022 source files, 72,594 lines): `full` mode bins to roughly 12 chunks, not
36, once the target moved from 2,000 to 6,000 lines, `deep` mode still bins to roughly 61.

This keeps each Warden's job proportional to what it can actually read and judge carefully,
regardless of whether the repository is 50 files or 5,000, while keeping `full` mode's spawn count
tied to how much ambiguity triage actually found rather than to raw line count.

## Coverage map: what a pattern alone can and can't see

This is the honest boundary of the *mechanical* tier, this section's grep patterns, on their own,
before any reading happens. It is not a description of `lite` mode: `lite` mode is triage plus an
exhaustive cheap-model read (see `better-coding-review` Phase 3), so it has real, if lower-confidence,
coverage of every tier below, not just the mechanical one. What this map actually tells you is which
rules a grep-only pass (no agent at all, if someone strips the reading step out to go even cheaper)
can and can't settle, and which rules stay genuinely open questions even after `lite`'s cheap-model
read, the ones most likely to come back `Ambiguous` in its table rather than a confident `Clean`.

| Coverage | Meaning | Rules |
| --- | --- | --- |
| **Mechanical** | A pattern reliably finds real instances; close to a verdict on its own, grep alone gets this right. | C1, C3, L1, L6, L21 |
| **Lead** | A pattern finds candidates; a cheap-model read can usually resolve these, an unreliable one shows up as `Ambiguous` more often here than in Mechanical. | L2, L5, L8, L12, L14, L15, L23, L26, L27, L28, L29, L30, L31 |
| **Judgment-only** | No textual pattern helps at all; a cheap model's call here is real but lower-confidence than a full Warden's, expect the highest `Ambiguous` rate in this tier. | L3, L4, L7, L9, L10, L16, L17, L25 |
| **N/A to a cold audit** | Ties to an active change, a diff, or the Builder's own conduct mid-loop; doesn't apply to code sitting in a repo with no in-progress change. | C2, C4, C5, L11, L13, L18, L19, L20, L22, L24 |

Of the 26 rules that do apply to a standalone codebase (36 total minus the 10 that are N/A), a
grep-only pass with no reading at all would be reliable on 5, produce unconfirmed candidates on 13,
and have zero visibility into 8, including L3, L7, L16, and L25. `lite` mode does better than that
because it reads: every rule gets a real call on every file, `Clean`, `Finding`, or honestly
`Ambiguous` where a cheap model wasn't confident. What `lite` doesn't have is a *strong* model's
judgment, that's what `full`/`deep`'s confirmation pass supplies, specifically and only for the rows
`lite` marked uncertain, rather than re-earning coverage of the other 90%+ of the codebase it was
already reasonably confident about.
