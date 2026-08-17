# The Law

Every rule has a stable ID. Findings cite the ID, so a rule broken twice is visible as the same
rule. Severity drives the penalty — see [ledger.md](ledger.md).

The project's `AGENTS.md` / `CLAUDE.md` outranks this file. Stricter project rules replace the
version here; this file never loosens one.

---

## CAPITAL — the work is reverted, not patched

**C1 — no silencing a check.** `# noqa`, `# type: ignore`, `eslint-disable`, `@ts-ignore`, `any`, a
blind cast, a widened signature, or a config exclusion added to make a checker stop complaining.
Fix the cause. A suppression is only ever acceptable when a human asks for it explicitly and the
reason is recorded outside the code.

**C2 — no gutting tests.** Deleting a test, skipping it, weakening an assertion, or loosening a
fixture so a build turns green. If a test is genuinely wrong, say so and get it changed on the
record, in its own change, with the reason.

**C3 — no swallowed errors.** `except X: pass`, an empty `catch {}`, a bare `except`, or catching an
error and returning a default that hides it. The caller must be able to tell that something failed.

**C4 — no fabricated verification.** Reporting that a command passed without running it, quoting
output you did not produce, or stating a Warden verdict that was not given. This is the one offence
that makes every other guarantee worthless.

**C5 — no moving the goalposts.** Editing the charter's acceptance criteria to match what was
built, or redefining "done" downward mid-loop.

---

## MAJOR — architecture and honesty

**L3 — trace every branch.** Every `if`/`else`, loop, early return, and fallthrough is walked. An
`if` with no reachable `else`, a guard against a state the type system already rules out, or a
default that can never be taken is defensive noise — delete it. Do not assume a branch is hit;
know it.

```python
if user.is_admin:
    grant_access()
# else — what happens? is this branch ever reached? trace it.
```

**L4 — every `except` is justified.** Say what is caught, why it is caught *here*, and what the
caller sees. Translating a domain error into another error without adding information is churn.
Catching at the wrong level turns a precise failure into a vague one.

**L5 — every declared variable earns itself, especially `Optional`.** For each one: why does it
exist, and what does the `None` case mean? An `Optional` parameter with no defined `None` behaviour
should not be `Optional`.

```python
def get_secret(key: Optional[str] = None): ...
# why optional? what happens when it is None? should it be optional at all?
```

**L6 — respect module boundaries.** Another module is reached through its public service or API,
never by importing its internals. Code inside a module may use its own internals freely. Do not add
a service, reader, writer, or repository layer unless that responsibility genuinely exists — a
pass-through layer is not architecture.

**L7 — the name matches the responsibility.** A `Generator` that persists, a `Reader` that mutates,
a `Validator` that also sends email: the abstraction is wrong, or the name is. Fix whichever is
actually broken.

**L8 — model the domain, not the payload.** Data representing a real concept with meaningful
properties becomes a type. Raw dicts, tuples, bare bytes, and loosely related primitives passed as a
group are a missing entity. The converse is also a violation: a wrapper or metadata object that adds
no domain structure is ceremony.

**L10 — validate once, at the boundary.** Routes stay thin. The same check does not appear in the
route and the service and the writer and the entity. Error messages name the domain concept the user
understands, not an internal variable.

**L11 — search before you add.** Before a new abstraction, helper, or dependency: search the repo
for what already does this. For a dependency, state why it is needed, what it replaces, and whether
it actually ships to production.

**L12 — test behaviour, not implementation.** Cover at request or integration level wherever
practical, in an end-to-end BDD style. Mock **third-party APIs only**. Never mock internal services,
domain objects, database access, or your own layers to assert that delegation happened — a test that
only proves method A called method B tests nothing.

**L13 — nothing outside scope.** Every changed file traces to the stated goal. No unrelated cleanup,
no speculative abstraction, no "while we're here", no drive-by reformatting. L24 is not a licence to
wander: fix broken windows only in the code you are already changing for a real reason.

**L14 — no opaque types.** `Mapping[str, Any]`, bare `dict`, `object`, `any` at a boundary where the
shape is actually known.

```python
# bad
def from_connection_status(status: Mapping[str, Any]): ...

# good
class ConnectionStatus(TypedDict):
    authInfo: AuthInfoDict

def from_connection_status(status: ConnectionStatus): ...
```

**L15 — business logic never lives in an execution layer.** Views, controllers, workers, jobs, CLI
commands, and HTTP handlers orchestrate; they do not decide. Turning a request body into a typed
object is `MyType.from_dict()`, not inline in the view.

**L16 — model entities before writing procedures.** Identify the entities, the state each owns, and
the behaviour that belongs to each. Small helpers are fine; a long function carrying several
unrelated responsibilities is not.

**L23 — type safety.** Errors surface at compile/check time, not in production. Full annotations at
every boundary. Escape hatches used to dodge a real modelling problem are C1.

---

## MINOR — craft

**L1 — no inline imports.** Imports go at module top. A function-level import to dodge a cycle means
the dependency direction is wrong (L6); fix that instead.

**L2 — comments explain why, never what.** A comment restating the line below it is a code smell —
delete it. Keep only what cannot be inferred: a decision's rationale, a business rule, a trade-off,
an invariant, an assumption, a non-obvious workflow. **If the project bans comments outright, that
wins — write none.** Never delete a comment a human wrote unless the code it describes is gone.

**L9 — names are specific, not redundant.** `get_data()` says nothing;
`get_active_subscriptions_for_user()` says everything. Equally, a name repeating context the module
or directory already establishes (`user/user_service.UserService.get_user_user_id`) is noise.

**L17 — write for the newcomer.** Optimise for someone who has never seen this codebase. Cleverness
that needs explaining loses to the obvious version.

**L21 — leave nothing behind.** No debug statements, `console.log`, commented-out code, TODOs for
work you are doing now, stray scratch files, or unused imports and variables.

**L24 — broken windows.** A small defect in code you are already touching gets fixed now, bounded by
L13. Do not use this rule to expand the diff.

---

## PROCESS — checked at the commit gate

**L18 — one logical change.** Small and single-purpose. A change doing two things is two changes.

**L19 — commit format.** `type: description`, imperative mood, ≤50 characters, lowercase after the
colon. Types: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`. "Add email auth", not "Added email
authentication support to the login flow".

**L20 — branch format.** `author/type/description`, e.g. `john/fix/login-bug`.

**L22 — evidence before done.** The change is run, the existing behaviour around it is checked for
regressions, and the output is real. "Should work" is not a verification.
