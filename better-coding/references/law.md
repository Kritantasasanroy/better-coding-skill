# The Law

Every rule has a stable ID. Findings cite the ID, so a rule broken twice is visible as the same
rule. Severity drives the penalty, see [ledger.md](ledger.md).

## Precedence is negotiated, not assumed

This Law is a baseline, not an automatic override. The first time `better-coding` or
`better-coding-review` runs in a repository, it checks for existing instruction files (`AGENTS.md`,
`CLAUDE.md`, a project-specific doctrine file, `.cursorrules`, or similar) and, if any exist, asks
the user how the two should relate. That's a call only the user gets to make:

- **Project wins.** The project's file is authoritative; the Law fills only what the project leaves
  unstated, and never loosens what the project locked down.
- **Law wins.** This Law is authoritative; the project's file fills gaps instead.
- **Hand in hand.** Both apply. A genuine conflict is surfaced to the user the moment it's found,
  rather than resolved by assumption in either direction.

The answer is recorded once and applied for the rest of the session. "Adapting in real time" means
a new conflict discovered later is resolved by that standing choice, not that the question gets
asked again every time one turns up.

The rule set below was written by generalizing a real production codebase's `AGENTS.md`,
`bettercoding.md`, and `object-style.md`: an object-oriented, zero-comment, strictly-typed backend
and frontend where a named senior reviewer's PR feedback shaped the review checklist directly.
Project-specific detail that doesn't generalize, an exact audit-logging decorator, a frontend
component catalogue, a literal file layout, stays owned by that project's own instruction file and
reaches this loop through "Project wins" or "Hand in hand," not by being copied in here.

---

## CAPITAL: the work is reverted, not patched

**C1: no silencing a check, and no `any`.** `# noqa`, `# type: ignore`, `eslint-disable`,
`@ts-ignore`, a blind cast, a widened signature, or a config exclusion added to make a checker stop
complaining. This includes a bare `any` / `Any` / untyped `dict` used to dodge a real typing
problem, in any language, in any position, not only at a public boundary. Fix the underlying type:
proper typing, a cast that's actually sound, an overload, a `TypedDict`. A suppression is only ever
acceptable when a human asks for it explicitly and the reason is recorded outside the code.

**C2: no gutting tests.** Deleting a test, skipping it, weakening an assertion, or loosening a
fixture so a build turns green. If a test is genuinely wrong, say so and get it changed on the
record, in its own change, with the reason.

**C3: no swallowed errors.** `except X: pass`, an empty `catch {}`, a bare `except`, or catching an
error and returning a default that hides it. The caller must be able to tell that something failed.

**C4: no fabricated verification.** Reporting that a command passed without running it, quoting
output you didn't produce, or stating a Warden verdict that wasn't given. This is the one offense
that makes every other guarantee worthless.

**C5: no moving the goalposts.** Editing the charter's acceptance criteria to match what was built,
or redefining "done" downward mid-loop.

---

## MAJOR: domain, architecture, and honesty

**L25: the domain gets modeled before the code does.** For any non-trivial backend feature, before
substantial implementation, write down, in plain text, no diagram required:

- What are the important domain objects?
- What properties and behavior belong to each?
- How do they relate to each other?
- What states can each one be in?
- What rules or invariants must always hold?
- What should the API resources look like, given this model?

The goal is a codebase that accurately represents the system, not one that jumps straight from a
ticket to whatever class makes the feature pass. If the task is "generate an MS Teams app package,"
the first question is never "what generator class do I need." It's: what are the actual objects?
A file, a zip file, an app package, a manifest. If an account pays a subscription fee plus usage,
model `Subscription`, `SubscriptionStatus`, `TokenUsage`, `TokenCreditBalance`, `AccountStatus`,
their relationships and rules, explicitly, rather than spreading strings, booleans, and integers
through the codebase. This model is written once per feature, lives with the charter, and the Warden
checks the implementation against it.

The [domain-modelling skill](../../domain-modelling/SKILL.md) is the canonical, interactive way to
produce this model for any feature substantial enough to warrant an actual session rather than a
paragraph: run it before Phase 2 of `better-coding`'s loop, or before starting a `better-coding-review`
fixing-pass slice that a finding below reveals is really a missing model. Its output (a design
document, usually at `docs/designs/<feature>.md`) satisfies this rule directly and is what the Warden
checks the implementation against. For work too small to justify that session, or when auditing code
nobody modeled going in, the checks below are what the Warden and the Builder's own self-check apply
instead, generalized from that same skill so the standard doesn't drop just because the full session
didn't run:

- **The durable-noun test.** A feature usually arrives phrased as a question — "warn them if the repo
  is still cloning," "check whether these credentials can write" — and the question is never the
  concept. List the nouns that exist whether or not this feature ships (an invoice, a subscription, a
  repository, a connection) before modeling the question itself, and check each candidate concept two
  ways: does it survive the feature being cancelled, and is it a noun or a question wearing a noun
  costume (`PaymentEligibility`, `InvoiceValidationResult`, `AccessFinding` are questions). Model the
  invoice first and the warning falls out as a state on it; model the warning first and the invoice
  never shows up.
- **Definition before name.** Every concept gets a one-sentence definition — what it is, independent
  of how this codebase happens to build it — written before any class name is chosen, and the name is
  then tested against that sentence, not against the code. If defending a name means describing how
  the system works ("well, we connect and then read the grant tables, so..."), the name describes a
  code path, not a concept.
- **General, ours, or plumbing, and each lives somewhere different.** Mark every concept: **general**
  (any product doing this kind of work has it, and it means the same thing everywhere — `Invoice`,
  `Money`, `Subscription`), **ours** (how this specific business does it — our plan tiers, our dunning
  sequence), or **plumbing** (no business meaning — encryption, JWTs, config, retries). General does
  **not** mean shared infrastructure: a generic `Invoice` is still billing and lives in
  `modules/billing/types.py` underneath the specific rules, not in `application/common`. Depth inside
  the module, not a move out of it. Only plumbing leaves the module, as a **helper**
  (`EncryptionHelper`, never `CryptoService`); the business-specific layer is exposed as a **service**.
  A business rule quietly buried in `application/common` because it was tempting to generalize is a
  finding under this rule as much as a missing model is.
- **Layering, not a flat list of peers.** A base concept owns identity; things that belong to it hang
  off it; states and enums sit at the bottom. Two checks: every child should be describable as "the X
  of a Y" (if Y isn't in the model, add it, no further than the thing the user actually acts on — the
  word they'd use, not a part of it only an implementer would name); and two types that both carry the
  same identifying fields are the signature of a missing base concept, not a coincidence.
- **The transaction unit.** For a cluster of concepts, ask whether a real invariant (not just
  relatedness) would be broken if they were saved separately. If yes, they're one unit with one entity
  as the way in; other units are referenced by id, never by held object, and one operation changes one
  unit. This is why `ApplicationRepository[Entity, Query]` takes exactly one entity type — if a
  proposed model doesn't map onto one repository, either the unit is wrong or the module boundary is.
- **CRUD is a modeling question, decided before any route exists.** For every entity: what's a valid
  create, and what precondition must hold first; which fields are immutable after creation (most
  engineers default everything to mutable — an `account_id`, an `amount`, a `created_at` usually
  aren't); whether "update" is actually a named state transition (`cancel()`, `renew()`) rather than a
  generic field patch; what delete actually means here (really gone / a terminal status the row keeps,
  for anything financial, audited, or referenced elsewhere / not deletable at all — choosing hard
  delete for something another entity points at is a data-integrity bug agreed to in advance); and
  whether it's append-only (usage records, ledger entries, audit events: create-and-read, no update,
  no delete, and no setter added later). A running total that gets mutated in place is usually this
  same mistake: prefer an append-only record with the total derived.
- **Write the full shape, then cut.** Every field gets a real type, every method a real signature —
  the argument and return types are where modeling mistakes hide, and a method named without one is a
  wish, not a design. Then go back over what got written and delete what isn't earning its place: a
  wrapper around one primitive with no behavior and no invariant (a `str` in a costume); a type that's
  another type plus two fields (split one concept in two, forcing every caller to hold both halves);
  a type with one construction site and one read site (a promoted local variable). The test: delete
  the type in your head and ask what breaks; "nothing, it'd just be a `str`" means delete it for real.
  This pass runs in the direction opposite every other check here, all of which push toward adding
  types, so it's an explicit, separate step, not a hope that restraint happens automatically.

**L26: generic-suffix names are a signal, not a rule.** `FooManager`, `FooHelper`, `FooUtils`,
`FooProcessor`, `FooGenerator`, and the same failure under a different suffix: `FooHandler`,
`FooBuilder`, `FooEngine`, `FooCoordinator`, `FooData`, `FooInfo`. These aren't automatically wrong,
but they're often the tell that the underlying domain concept was never identified — a verb turned
into a noun by suffix (`PaymentProcessor` is `ProcessPayment` wearing a hat). Before accepting one,
ask what real thing it's standing in for, and whether naming that thing directly would collapse the
class into something smaller and more obvious. The exception is genuine shared plumbing living in
`application/common`, named `Helper` deliberately (L25's general/ours/plumbing split), not a business
concept anywhere else in the codebase wearing the same suffix.

Two more naming smells worth calling out by name, because they survive a correct entity list and
still cause the damage:

- **An adjective bolted onto a noun is a state, not a kind.** `ConnectedRepository`,
  `ActiveSubscription`, `VerifiedAccount`, `PaidInvoice`. A repository doesn't become a different sort
  of thing once it's connected; it's the same thing with a fact attached. Drop the adjective, put the
  fact on the noun as a field, a status enum, or a method. Test: if the adjective can become false and
  the thing survives, it's a state, not a kind, and the rare genuine subtype is the exception, not the
  default assumption. This differs from a **qualifier**, which disambiguates a name that collides with
  another meaning the team uses daily (`GitRepository` vs. the storage-layer `Repository`) — the test
  is whether the qualifying word can ever become false for that object; "git" can't, "connected" can.
- **A padding word hides a merge, not a second concept.** `Audit`, `Verdict`, `Record`, `Entry`,
  `Detail`, `Item`, `Result`, `Finding`, `Info`, `State` are usually complete names wearing an extra
  word. Strip it; if what's left is a name already used for something else in the model, this isn't a
  second concept, it's the first one split in two, and the two should merge.

**L27: no functional style, no free functions over domain data.** Objects are the default; a
functional pipeline of transforms over anonymous structures is not a style choice here, it's not
used at all. Concretely:

- Behavior lives beside the data it manipulates: on the service, the domain object, or the dataclass
  holding the fields.
- A function that takes a type and derives something from it is a method or a `@classmethod` on
  that type, not a free function beside it.
- No module-level `def` that belongs to a class, and no module-level variable, constant, or function
  that belongs to one either. The only acceptable module-level names are imports and type aliases.
- Classes (and, on the frontend, components) are nouns. Functions, methods, and hooks are verbs.
  `Subscription.renew()`, not `update_subscription_status(sub, "active")`. A class named with a verb
  (`ProcessPayment`, `GenerateManifest`, `ValidateConnection`, `CheckAccess`) is this same failure at
  its root, one step before the suffix family in L26: a class is a thing, a verb is something done to
  a thing, and a verb-named class is always either a function that hasn't admitted it or a noun that
  was never found. Find the noun (`Payment`, `Manifest`) and the verb becomes a method on it.
- Not every piece of behavior has a home on the concept nearest to it, and forcing it there is its own
  failure. Three homes, in order of preference: on the concept itself, when it needs only that
  concept's own state (the default, and where most behavior belongs); on a reader or writer, when the
  decision spans concepts or needs something fetched, but is still a business decision and stays in
  the module (`SubscriptionWriter.cancel(...)`); or nowhere in the domain, when it's orchestration
  rather than a decision — fetching, retrying, logging, transactions, calling a vendor — which belongs
  to the caller, not to a domain object bolted with a method it doesn't own. The test isn't branch
  count: a five-`if` method that only routes data is orchestration, and a one-line method deciding
  whether a customer keeps access is domain logic.

**L28: minimize branching; reach for it last, not first.** An `if`/`else` is not free. Before adding
one, ask whether the real shape is polymorphism (a state's behavior lives on the type representing
that state), an early-return guard clause, or an exhaustive match over an enum the type system can
check. A conditional chain selecting behavior by a type tag is usually a missing class hierarchy.
Nested conditionals beyond one level are presumed wrong until proven otherwise. This governs the
*shape* of the code; L3 below governs whether each branch that does exist is actually reachable.
Together: fewest branches that could possibly work, and every branch that remains is provably live.

**L29: the laziness ladder runs before any code gets written.** Before writing a solution, stop at
the first rung that holds:

```
1. Does this need to exist at all?     -> no: skip it (YAGNI)
2. Already in this codebase?           -> reuse it, don't rewrite
3. Standard library does it?           -> use it
4. Native platform feature does it?    -> use it
5. An installed dependency does it?    -> use it
6. Is it one line?                     -> one line
7. Only then: the minimum that works
```

The ladder runs *after* understanding the problem, not instead of it: read the code the change
touches and trace the real flow before picking a rung. Lazy about the solution, never about reading.
Lazy, not negligent: trust-boundary validation, data-loss handling, security, and accessibility are
never on the chopping block to climb the ladder faster. When the Warden reports a laziness finding,
it uses these tags: `delete` (dead code or a speculative feature), `stdlib` (reinvented standard
library), `native` (a dependency doing what the platform already does), `yagni` (an abstraction with
exactly one implementation), `shrink` (same logic, fewer lines), `cut` (L25's cut-pass over-typing: a
wrapper around one primitive with no behavior and no invariant, a type that's another type plus two
fields, or a type with one construction site and one read site — a promoted local variable).

**L3: trace every branch.** Every `if`/`else`, loop, early return, and fallthrough is walked. An
`if` with no reachable `else`, a guard against a state the type system already rules out, or a
default that can never be taken is defensive noise, delete it. Don't assume a branch is hit; know it.

```python
if user.is_admin:
    grant_access()
# else: what happens? is this branch ever reached? trace it.
```

**L4: every `except` is justified.** Say what's caught, why it's caught *here*, and what the caller
sees. Translating a domain error into another error without adding information is churn. Catching at
the wrong level turns a precise failure into a vague one.

**L5: `Optional` is presumed guilty.** For every declared variable, and especially every
`Optional`/nullable one: why does it exist, and what does the absent case actually mean? Before
reaching for `Optional`, check whether the domain has a state that a type can represent directly,
an enum, a variant class, a separate type for the "not yet set" case, rather than a nullable flag
threaded through everything downstream. An `Optional` parameter with no defined `None` behavior
shouldn't be `Optional` at all.

```python
def get_secret(key: Optional[str] = None): ...
# why optional? what happens when it's None? should it be optional at all,
# or is this actually two different states that deserve two different types?
```

**L30: no defensive coding; validate once at the boundary, then trust the types.** Don't sprinkle
`if value is None` checks through a call chain without knowing why the value could be absent at that
specific point. Validate at the module boundary, a request schema, a Pydantic model, a typed DTO,
and rely on the types for everything downstream of it. A null check (or any other re-validation)
found deep inside a call chain is a symptom, not a fix: it almost always means the boundary above it
was never actually typed, so trace it back to that boundary and fix it there instead of guarding
every call site individually. This is L5's boundary-level partner: L5 asks whether a declared
`Optional` earns itself at all; this rule says that once a boundary has ruled `None` out, nothing
downstream gets to re-litigate it.

**L6: respect module boundaries.** Another module is reached through its public service or API,
never by importing its internals. Code inside a module may use its own internals freely. Don't add
a service, reader, writer, or repository layer unless that responsibility genuinely exists, a
pass-through layer is not architecture.

**L7: the name matches the responsibility.** A `Generator` that persists, a `Reader` that mutates, a
`Validator` that also sends email: the abstraction is wrong, or the name is. Fix whichever is
actually broken. See also L26 for the specific generic-suffix case.

**L8: model the domain, not the payload.** Data representing a real concept with meaningful
properties becomes a type. Raw dicts, tuples, bare bytes, and loosely related primitives passed as a
group are a missing entity. The converse also holds: a wrapper or metadata object that adds no
domain structure is ceremony. Concrete smells that mean the same thing:

- **Two or more booleans that can't all be true together** are one enum with an illegal-state
  problem hiding in it. `is_active` + `is_trialing` + `is_cancelled` is `SubscriptionStatus`.
- **A `str` whose values you know by heart** is an enum, no exception.
- **An int whose unit you have to remember** is a value type (`TokenCount`, not `count: int`), the
  same way a raw dict is a missing entity.
- **Fields that always travel together** are a concept of their own: `period_start` + `period_end` is
  a `BillingPeriod`; `amount` + `currency` is `Money`.
- **A running total that gets written to** usually wants to be an append-only record with the total
  derived instead. A mutated balance loses its own audit trail and races under concurrency; the fix is
  rarely a lock, it's changing what gets persisted.

**L31: no orphan classes.** Every class introduced while modeling the domain (L25) has to actually
connect to that model: something calls it, something composes it, or it relates to another domain
object the way the model says it should. A class with no caller, no relationship to anything else in
the domain, and no state or behavior beyond a couple of fields is one of two things: dead code L29's
`delete` tag already catches, or a concept that was never really independent and belongs as a
property or method on a type that already exists. Before keeping a new class, be able to name what
it relates to and how; if there's no answer, it's an orphan, fold it into the type it actually
belongs to.

**L10: validate once, at the boundary.** Routes stay thin. The same check doesn't appear in the
route and the service and the writer and the entity. Error messages name the domain concept the user
understands, not an internal variable, and give a way forward, not a dead end: "email already
registered, sign in instead or use a different email," not "invalid input."

**L11: search before you add.** Before a new abstraction, helper, or dependency: search the repo for
what already does this. For a dependency, state why it's needed, what it replaces, and whether it
actually ships to production.

**L12: test behavior, not implementation.** Cover at request or integration level wherever
practical, exercising the real public entry point against real wiring. Mock **third-party APIs
only**, never internal services, domain objects, database access, or your own layers to assert that
delegation happened. A test that only proves method A called method B tests nothing.

**L13: nothing outside scope.** Every changed file traces to the stated goal. No unrelated cleanup,
no speculative abstraction, no "while we're here." L24 is not a license to wander; fix broken windows
only in code you're already changing for a real reason.

**L15: business logic never lives in an execution layer.** Views, controllers, workers, jobs, CLI
commands, and HTTP handlers orchestrate; they don't decide. Turning a request body into a typed
object is `MyType.from_dict()`, not inline in the view.

**L16: model entities before writing procedures.** Identify the entities, the state each owns, and
the behavior that belongs to each. Small helpers are fine; a long function carrying several
unrelated responsibilities is not. This is the implementation-level companion to L25's design-level
domain model, one is written down before coding, this is what the code itself should look like once
that model exists.

**L23: type safety.** Errors surface at compile or check time, not in production. Full annotations
at every boundary. An escape hatch used to dodge a real modeling problem is C1, not a shortcut.

---

## MINOR: craft

**L1: no inline imports.** Imports go at the module top. A function-level import to dodge a cycle
means the dependency direction is wrong (L6); fix that instead.

**L2: comments explain why, never what, and only when the project allows comments at all.** A
comment restating the line below it is a code smell, delete it. Where comments are permitted, keep
only what can't be inferred: a decision's rationale, a business rule, a trade-off, an invariant, an
assumption, a non-obvious workflow. **Many projects ban comments outright; that wins, write none.**
In such a project, a deliberately cut corner (the kind a `ponytail:` marker would normally flag) is
never left as an inline comment either, since that's still a comment. Record it in the PR
description or the ledger instead, or don't defer it, do it now. Never delete a comment a human
wrote unless the code it describes is gone.

**L9: names are specific, not redundant.** `get_data()` says nothing;
`get_active_subscriptions_for_user()` says everything. Equally, a name repeating context the module
or directory already establishes (`user/user_service.UserService.get_user_user_id`) is noise.

**L14: avoid opaque containers.** `Mapping[str, Any]`, a bare `dict`, `object`, at a boundary where
the actual shape is known and could be named. This is the general craft version of C1's absolute ban
on `any`/`Any` used to bypass typing; this rule covers the merely-untyped-but-not-strictly-`Any`
cases, like an unnamed dict with known keys.

```python
# bad
def from_connection_status(status: Mapping[str, Any]): ...

# good
class ConnectionStatus(TypedDict):
    authInfo: AuthInfoDict

def from_connection_status(status: ConnectionStatus): ...
```

**L17: write for the newcomer.** Optimize for someone who has never seen this codebase. Cleverness
that needs explaining loses to the obvious version.

**L21: leave nothing behind.** No debug statements, `console.log`, commented-out code, TODOs for
work you're doing now, stray scratch files, or unused imports and variables.

**L24: broken windows.** A small defect in code you're already touching gets fixed now, bounded by
L13. Don't use this rule to expand the diff.

---

## PROCESS: checked at the commit gate

**L18: one logical change.** Small and single-purpose. A change doing two things is two changes.

**L19: commit format.** `<type>(<scope>): <subject>`, scope optional, subject under 50 characters,
present tense and imperative ("add," not "added"), no trailing period, and the message communicates
*why*. Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`, `perf`,
`revert`. A breaking change adds `!` after the type.

**L20: branch format.** `author/type/description`, e.g. `john/fix/login-bug`.

**L22: evidence before done.** The change is run, the existing behavior around it is checked for
regressions, and the output is real. "Should work" is not a verification.
