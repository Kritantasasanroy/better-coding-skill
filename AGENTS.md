# AGENTS.md — better-coding

This file is read automatically by most AI coding tools that check for `AGENTS.md` at a repo root
(Devin, Kiro, Qoder, OpenCode, and others). It's the condensed, standing version of the
`better-coding` rule set: no interactive negotiation, no mode switching, just the rules themselves,
always active in this project.

If this repo already has its own `AGENTS.md` content above this section, or a `CLAUDE.md` /
doctrine file with its own conventions, **that content wins wherever it disagrees with anything
below.** This file fills gaps, it never overrides a decision the project already made on purpose.

The full system, including the audit loop, the domain-modeling requirement checked against a real
Warden pass, and the whole-repository review pipeline, is the `better-coding` / `better-coding-review`
Claude Code skill pair: https://github.com/Kritantasasanroy/better-coding-skill. This file is the
part of it that travels with the repo for tools that read project-local instructions instead of a
user-level skill folder.

## Before writing anything: model the domain

For any non-trivial feature, write down first, plainly, no diagram needed: the domain objects
involved, what properties and behavior each owns, how they relate, what states each can be in, and
what invariants must always hold. If a name like `FooManager`, `FooHelper`, `FooUtils`,
`FooProcessor`, or `FooGenerator` shows up while doing this, stop, it's usually a sign the real
concept was never identified. Only after that: name the entities, and let the code follow the model,
not the other way around.

## Objects, not functions

No functional style: no free functions deriving something from a type, no transform pipeline over
anonymous data, no module-level state. Behavior lives on the type that owns the data. Classes are
nouns, methods are verbs.

## Minimize branching

An `if`/`else` isn't free. Before adding one, check whether the real shape is polymorphism, a guard
clause, or an exhaustive match. Nested conditionals past one level are presumed wrong. A branch that
can't be reached by any real input is defensive noise, delete it, don't add null checks you can't
justify, validate once at a typed boundary and trust the types after that.

## The laziness ladder

Before writing a solution: does this need to exist at all (YAGNI) → is it already in the codebase →
does the standard library do it → does the platform do it natively → does an installed dependency
cover it → is it one line → only then, the minimum that works. Never skip validation, error
handling, security, or accessibility to climb the ladder faster.

## No orphan classes

Every class has to connect to the domain model: something calls it, or it relates to another domain
object. No caller and no relationship means it's dead code or a fragment that belongs as a property
or method on a type that already exists.

## Typing

No `any`/`Any` anywhere, not just at a public boundary, that's a hard rule, not a style preference.
Type every real boundary. A `dict`/`Mapping[str, Any]`/`object` where the shape is known should be a
named type instead.

## Everything else, in one line each

- No inline imports, imports at the top only.
- Every `except`/`catch` states why it's caught here and what the caller sees; nothing swallowed.
- Search the repo for an existing solution before adding a new abstraction or dependency.
- Tests assert real, observable behavior; mock third-party boundaries only, never your own code.
- Comments explain why, never what, and only if this project allows comments at all, many don't.
- Names are specific, not generic (`get_data`), and not redundant with their own module or directory.
- Validate once, at the boundary; error messages name the domain concept, not an internal variable.
