---
title: better-coding, domain-model-first object-oriented standard
inclusion: always
---

# better-coding

Before writing any non-trivial feature, write down the domain model first, plainly, no diagram
needed: the objects involved, the properties and behavior each owns, how they relate, what states
each can be in, what invariants must always hold. If a name like `FooManager`, `FooHelper`,
`FooUtils`, `FooProcessor`, or `FooGenerator` shows up while doing this, stop, it's usually a sign
the real concept was never identified. Code follows the model, not the other way around.

Objects, not functions: no free function deriving something from a type, no transform pipeline over
anonymous data, no module-level state. Behavior lives on the type that owns the data. Classes are
nouns, methods are verbs.

Minimize branching: an `if`/`else` isn't free, check first whether the real shape is polymorphism, a
guard clause, or an exhaustive match. Nested conditionals past one level are presumed wrong. A branch
no real input can reach is defensive noise, delete it. Validate once, at a typed boundary, and trust
the types after that, a null check deep in a call chain means the boundary above it wasn't typed.

The laziness ladder, before writing a solution: does this need to exist at all (YAGNI) → is it
already in the codebase → does the standard library do it → does the platform do it natively → does
an installed dependency cover it → is it one line → only then, the minimum that works. Never skip
validation, error handling, security, or accessibility to climb it faster.

No orphan classes: every class connects to the domain model, something calls it or it relates to
another domain object. No caller and no relationship means dead code, or a fragment that belongs on
a type that already exists.

No `any` anywhere, not just at a boundary. Type every real boundary; a bare `dict`/`object` where the
shape is known should be a named type instead.

Everything else, one line each: no inline imports; every caught error states why it's caught here
and what the caller sees, nothing swallowed; search for an existing solution before adding a new
abstraction or dependency; tests assert real observable behavior, mock third-party boundaries only;
comments explain why, never what, and only if this project allows comments at all; names are
specific, not generic, and not redundant with their own module; validate once, at the boundary.

If this project already has its own steering files or conventions with different rules, those win
wherever they disagree with anything above, this file fills gaps, it doesn't override a decision the
project already made on purpose.

Full system: https://github.com/Kritantasasanroy/better-coding-skill (the Claude Code skill pair
this file is a condensed, always-on excerpt of).
