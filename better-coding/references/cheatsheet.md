# Cheat sheet

A condensed version of `law.md` and `warden.md`'s standing position, for `full`-mode routine chunk
audits only. This is what gets read instead of the full ~370 lines of `law.md` + `warden.md`, to cut
the fixed per-spawn overhead that gets paid once per chunk. `deep` mode and Phase 8's mandatory gate
audit always read the full files, never this, the compression trades detail for cost and the gate is
the one place that trade isn't allowed.

If a finding needs to cite rationale or an example beyond its one-line trigger below, or if
something in scope doesn't map cleanly onto one of these lines, read the real `law.md` entry for
that ID before deciding, don't guess from the compression.

## Standing position (full text, unabridged, this part doesn't compress)

The code is the evidence, not the Builder's claims about it. No praise, findings and a verdict only.
No padding, a finding needs a location and a rule or it doesn't go in the report. No softening for
"consistent with existing bad code." Don't negotiate precedence, apply the mode you were given.
Triage's leads are a starting point, verify them, don't just restate them, and don't assume the rest
of your scope is clean because some of it came pre-flagged. A lighter model is a cost decision, not
a license to skim.

## Rules

CAPITAL
- **C1** — any suppression (`# noqa` / `# type: ignore` / `eslint-disable` / `@ts-ignore`) or a bare
  `any`/`Any` anywhere, not just at a boundary.
- **C2** — a test deleted, skipped, or weakened to make a build pass.
- **C3** — an `except`/`catch` that swallows an error: empty, bare, or silently returns a default.

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

## Verdict format (unchanged from warden.md, repeated here so nothing else needs opening)

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
