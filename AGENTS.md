# AGENTS.md — better-coding

This file is read automatically by most AI coding tools that check for `AGENTS.md` at a repo root
(Devin, Kiro, Qoder, OpenCode, and others). It's the condensed, standing version of the
`better-coding` rule set: no interactive negotiation, no mode switching, just the rules themselves,
always active in this project.

If this repo already has its own `AGENTS.md` content above this section, or a `CLAUDE.md` /
doctrine file with its own conventions, **that content wins wherever it disagrees with anything
below.** This file fills gaps, it never overrides a decision the project already made on purpose.

The full system, including the audit loop, the domain-modeling requirement checked by an independent
Reviewer and Auditor, and the whole-repository review pipeline, is the `better-coding` / `better-coding-review`
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
nouns, methods are verbs. In C, Go and Rust the language idiom (functions or methods on a struct) is the equivalent, and that's what to follow there.

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
- Comments explain why, never what, and only if this project allows comments at all, many don't. See Craft below for which kinds and how many.
- Names are specific, not generic (`get_data`), and not redundant with their own module or directory.
- Validate once, at the boundary; error messages name the domain concept, not an internal variable.

## Write it the way this house would have (Craft)

Measured from 756k pre-2020 commits and 3.1M lines of production code in 22 projects (Linux, Git,
Go, PostgreSQL, Redis, SQLite, Django, Rails, Kubernetes and others). Full rules and evidence: the
`better-coding` skill's `craft.md` and `research.md`.

- Match the house first. Read three neighboring files and `git log` for the paths you touch, then
  copy their naming, error idiom, comment density and voice, doc format, logging and test layout.
  Your preference loses to the house's convention.
- Small diffs. Production commits had a median of 5 to 22 changed source lines in 1 to 2 files. Don't
  reformat, re-wrap or reorder lines you didn't need to touch.
- Comments carry what code can't: units, sentinel values, invariants, ordering assumptions, why the
  obvious approach is wrong, RFC or issue references. A rare section label is normal. Narrating
  every step ("# Initialize the counter", "# Step 1:") is not.
- Functions are as small as the house writes them: median 3 to 9 lines in Python, Java, Ruby, Go and
  JS, and 12 to 16 in C. Use early returns, keep nesting shallow, and treat complexity above 10 as
  rare.
- Errors follow the language idiom: narrow exceptions, context in the message (`parsing %q: %v`),
  no broad catch "to be safe". Catching one specific expected exception as a normal branch
  (`except KeyError:` meaning "use the default") is fine.
- Nothing speculative: no parameters, flags, env vars, retries, timeouts, fallbacks or `try` blocks
  the task didn't need.
- Reuse or move existing code. Don't paste near-duplicates.
- A bug fix comes with the test that would have caught it.
- Every external API you call exists in the version the repo actually uses. Check the installed
  source, not memory.
- No assistant artifacts: no `# ... existing code ...` placeholders, no comments addressed to a chat
  ("as requested", "updated to fix"), no changelog notes in code, no `example.com` or `your-api-key`
  values, no emoji in logs, no `_v2` / `Improved…` / `Enhanced…` names.
- Commit messages copy the repo's history: its prefix style, mood and trailers. With no signal, use
  `area: imperative summary` (50 chars, no period), then a wrapped prose body saying what was wrong
  and why this fixes it. Use Conventional Commits only if the history already does (0 to 4% of
  pre-2020 commits used them). No bullet inventories, emoji, or words like comprehensive, robust,
  seamless, leverage or enhance.
