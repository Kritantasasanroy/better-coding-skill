# Cheat sheet

A condensed version of `law.md`, `craft.md` and `reviewer.md`'s standing position. The Reviewer
reads this instead of the full files in two places: a `full`-mode build session (read once, at the
first round) and the exhaustive chunk pass of `better-coding-review`. It cuts the fixed overhead paid
on every spawn. `deep` mode and the Auditor always read the full files, never this. The compression
trades detail for cost, and the final verdict is the one place that trade isn't allowed.

If a finding needs rationale or an example beyond its one-line trigger, or something in scope doesn't
map cleanly onto one of these lines, read the real `law.md` or `craft.md` entry for that ID before
deciding. Don't guess from the compression.

## Standing position (full text, unabridged, this part doesn't compress)

The code is the evidence, not the Writer's claims about it. No praise, findings and a verdict only.
No padding, a finding needs a location and a rule or it doesn't go in the report. No softening for
"consistent with existing bad code" under the Law. Under Craft, the house *is* the standard: judge
H-rules against the fingerprint, not your taste. Don't negotiate precedence, apply the mode you were given.
Triage's leads are a starting point, verify them, don't just restate them, and don't assume the rest
of your scope is clean because some of it came pre-flagged. A lighter model is a cost decision, not
a license to skim.

## Rules

CAPITAL
- **C1** — any suppression (`# noqa` / `# type: ignore` / `eslint-disable` / `@ts-ignore`) or a bare
  `any`/`Any` anywhere, not just at a boundary.
- **C2** — a test deleted, skipped, or weakened to make a build pass.
- **C3** — an `except`/`catch` that swallows an error: empty, bare, `except Exception`, or silently
  returns a default. Not C3: one specific expected exception used as control flow when absence is
  the intended branch (`except KeyError:` → default).

MAJOR
- **L3** — a branch you can't name real inputs for, or one that's dead.
- **L4** — an `except` with no stated reason it's caught *here*, or no clarity on what the caller sees.
- **L5** — an `Optional`/nullable with no defined `None` behavior; could be an explicit state instead.
- **L6** — a module reaching into another module's `internals/` instead of its public surface.
- **L7** — a class/function name that doesn't match what it actually does.
- **L8** — a real domain concept passed as a raw dict/tuple, or a wrapper adding no structure. Also:
  2+ booleans that can't all be true (missing enum), a `str` with known values (missing enum), an
  int whose unit you'd forget (missing value type), fields that always travel together (missing
  concept), or a mutated running total (should be derived from an append-only record).
- **L10** — the same validation duplicated across route, service, writer, and entity.
- **L11** — a new dependency or abstraction with no evidence anything existing was checked first.
- **L12** — a test mocking an internal object instead of a third-party boundary.
- **L13** — a changed file that doesn't trace to the stated goal (diff mode only, N/A for a cold
  whole-repo audit with no goal to trace to).
- **L15** — a decision made inside a view/controller/worker/handler instead of a domain object.
- **L16** — a long function mixing responsibilities instead of entities with owned behavior.
- **L23** — a missing type annotation at a real boundary.
- **L25** — a non-trivial feature with no discoverable domain model (objects, states, relationships,
  rules); for existing code, judge whether the structure implies one was ever thought through. Also
  flag: the feature's question modeled instead of the durable noun behind it; a concept unmarked as
  general/ours/plumbing, especially a business rule sitting in `application/common`; layering that's
  flat instead of "every child names its parent"; two types sharing identity fields (missing base
  concept); an entity with no decided CRUD semantics (what's immutable, what delete means, whether
  it's append-only); or a leftover wrapper-around-one-primitive / type-plus-two-fields / promoted
  local variable a cut pass should have removed. See `../../domain-modelling/SKILL.md` for the full
  session this generalizes from.
- **L26** — a class named `*Manager`/`*Helper`/`*Utils`/`*Processor`/`*Generator`/`*Handler`/
  `*Builder`/`*Engine`/`*Coordinator`/`*Data`/`*Info`, a signal, name what it's standing in for before
  flagging it as a real finding. Also: a name with an adjective that can become false while the
  object survives (`ConnectedRepository` — that's a state, put it on the noun), or a name that's
  another one in the model plus a padding word (`Finding`, `Result`, `Info`, `State`) — a merge, not
  a second concept.
- **L27** — a module-level function or transform pipeline instead of behavior on the owning type, or
  a class named with a verb (`ProcessPayment`) instead of the noun it acts on. Behavior with no home
  on one concept still needs a home: the concept itself (default), a reader/writer if the decision
  spans concepts, or the caller if it's orchestration, not a decision — never bolted onto a domain
  object that doesn't own it.
- **L28** — an `if`/`else` chain that should be polymorphism, or nesting beyond one level.
- **L29** — code reinventing stdlib/a native feature/an installed dependency, or a one-implementation
  abstraction. Also: a wrapper around one primitive with no behavior/invariant, a type that's another
  type plus two fields, or a promoted local variable — L25's cut pass, tag `cut`. Never flag
  validation, error handling, security, or accessibility as removable here.
- **L30** — a null check deep in a call chain instead of at a typed boundary; trace it back, the
  finding is on the boundary.
- **L31** — a class with no caller and no relationship to anything else in the domain model.

MINOR
- **L1** — an import inside a function body.
- **L2** — a comment restating the line below it, or any comment at all if the project bans them
  outright (check the negotiated precedence).
- **L9** — a name that's generic (`get_data`) or redundant with its own module/directory context.
- **L14** — `dict`/`Mapping[str, Any]`/`object` where the real shape is knowable and could be named.
- **L17** — code a newcomer couldn't follow without the author explaining it out loud.
- **L21** — dead code, debug prints, commented-out blocks, stale TODOs, unused imports or variables.
- **L24** — a small, real defect in code already being touched, left unfixed (bounded by L13).

## Craft (craft.md), judged against the fingerprint

CAPITAL
- **H16** — a placeholder standing in for real code (`# ... existing code ...`, a stub returning fake
  data) in work reported as done.

MAJOR
- **H1** — a convention that differs from the house (naming, error idiom, comment voice and density,
  doc format, imports, tests, logging). Quote the house example it departs from.
- **H4** — a new function past the house's p90 length or CCN 10 with no parser / state-machine reason;
  nesting where a guard clause would flatten it. C `goto` cleanup is idiomatic, not a finding.
- **H5** — errors not in the language idiom, a broad catch "to be safe", or a message with no context.
- **H6** — a parameter, flag, option, env var, retry, timeout, fallback or `try` the task didn't need.
- **H7** — five-plus lines pasted from or near-duplicating existing code instead of reusing or moving it.
- **H11** — a bug fix with no test that would have caught it, or no record that it was seen failing.
- **H14** — an internal invariant re-validated as a runtime branch with invented fallback behavior.
- **H15** — an external API call with no evidence it exists in the installed version.
- **H16** — text addressed to a chat, changelog notes in code, invented example values, debug output.

MINOR
- **H2** — narration comments as a habit (judge density: ~1 per 25 new lines or consecutive trivial
  labels), comments restating names, density outside the house band.
- **H3** — doc comments not in the house form, or boilerplate Args/Returns on trivial private helpers.
- **H8** — versioned or hype names (`_v2`, `Improved…`), or placeholders (`data`, `result`) in wide scopes.
- **H9** — reformatting, re-wrapping or import reordering of lines the change didn't need.
- **H12** — print/console output in library code; emoji, banners or exclamations in logs or errors.
- **H13** — a marker not in the house form (`TODO(owner)` where the house uses owners) or with no condition.

In a whole-repository pass, H9, H10, H11 and H15 are N/A (they concern a change in progress).

## Verdict format (unchanged from reviewer.md, repeated here so nothing else needs opening)

```
VERDICT: CLEAN | VIOLATIONS | BLOCKED

FINDINGS
[<ID>] <SEVERITY> — <file>:<line>
  Broken: <the rule, one line>
  Evidence: <quote the code>
  Failure: <the concrete consequence>
  Required: <what must change>

LADDER
[<tag>] <file>:<line> — <what to cut>. <replacement>. (only when L29 applies)

UNVERIFIED
- <anything you couldn't check, and what would be needed to>

ACCEPTANCE
- <each charter criterion, if any>: MET | NOT MET | NOT VERIFIABLE FROM CODE
```

`CLEAN` only with zero findings. `BLOCKED` if you couldn't get the code at all. A finding without a
file, a line, and a concrete failure doesn't count, drop it rather than pad the report.
