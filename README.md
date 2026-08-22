# better-coding

Two tools that stop an AI coding agent from grading its own homework.

Here's the problem this solves. Ask an agent to write code, then ask the same agent whether that
code is good, and you're asking one piece of reasoning to check itself. The logic that talked itself
into a shortcut is the same logic doing the review. It usually says yes. `better-coding` splits the
job into two agents that never share context: one writes, a separate one audits, and only the audit
gets to say "done."

## The two tools

**`better-coding`** runs while you're building something new. Before any code gets written, it makes
you write down the domain model, plainly: what are the real objects here, what does each one own,
how do they relate, what states can they be in. Then it builds in small pieces, and an independent
agent checks each piece against a fixed rule set before the next one starts.

**`better-coding-review`** runs against code that already exists, a whole repository nobody's ever
run this against before. It scopes the repo, reads every important file exactly once, and hands you
a full compliance report. It never touches your code on its own, fixing only starts if you say yes
after seeing the report.

They share one rule set and are meant to be installed together.

## Install

### Claude Code, one command

```powershell
irm https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.ps1 | iex
```

Run that once, in PowerShell, on any Windows machine. It downloads this repo and drops both skills
into `~/.claude/skills/`, which is a user-level folder Claude Code checks in every project you
open, not just the one you're standing in right now. So this is genuinely a one-time thing: run it
once, and both `/better-coding` and `/better-coding-review` work from then on, in any repo, on this
machine, forever, no per-project setup.

If you'd rather do it by hand, or you're not on Windows, clone the repo and copy the `better-coding`
and `better-coding-review` folders into your own `~/.claude/skills/`, keeping those exact folder
names, Claude Code matches a skill by the `name` field in its `SKILL.md` and that name has to match
the directory it's sitting in.

### Other tools: Devin, Kiro, and anything that reads AGENTS.md

Claude Code skills are a user-level, per-machine thing. Devin and Kiro don't work that way, they
read instructions that live inside the specific repo you're working in. So for those, the install
is per-project, not per-machine, and it's a second, separate step:

```powershell
# from inside the project you want it in, after the one-time Claude Code install above
irm https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.ps1 -OutFile install.ps1
.\install.ps1 -Project -SkipClaude
```

That drops three things into the current directory: `AGENTS.md` (which Devin, Kiro, Qoder, OpenCode,
and most other AGENTS.md-aware tools pick up automatically, no configuration needed), a
`.devin-plugin/plugin.json` manifest, and a `.kiro/steering/better-coding.md` file. Commit all three
if you want your team to get them too when they pull the repo.

One honest caveat: these project-level files carry the condensed rule set as a static, always-on
instruction. They don't have the interactive parts, the precedence negotiation, the audit loop, the
whole-repository review pipeline below, those are specific to how Claude Code runs a skill. If your
team is on Claude Code, install both ways. If you're on Devin or Kiro, the project files are what
you get, and they're still the real rules, just without the agent that independently checks your
work against them.

## What actually happens when you run it, step by step

This is the part most tool READMEs skip, and it's the part that actually matters, so here it is in
full, using real numbers from a run against an actual production repository (1,022 source files,
72,594 lines) so none of this is abstract.

**1. Scope.** First question, always: how many files, how many lines. Not every tracked file is
something worth reviewing, tests, docs, lockfiles, and generated output get excluded by default,
they're not where the domain model lives, and including them mostly just inflates every number that
follows. On that real repo: 1,022 files dropped to 730 once tests and docs were filtered out, and the
line count dropped from 72,594 to 27,181, well under half. That filtering step is most of what makes
the rest of this affordable.

**2. Triage.** A handful of `grep` searches, no AI involved yet, across every file in scope. This
catches the part of the rule set that's genuinely just a pattern: a suppressed type checker, a bare
`any`, an empty `except` block, a class named `SomethingManager`. It costs nothing and it scales to
any repo size, because it's just text search.

**3. The one real read.** This is `lite` mode, and it's not a lesser version of the other modes,
it's the foundation all of them build on. The filtered file set gets split into chunks a model can
actually read start to finish, and a cheap, fast model reads every single one, in full, once. For
every file and every rule that applies to it, it writes down one of three answers: clean, a real
finding, or honestly unsure. That "honestly unsure" answer matters as much as the other two, a cheap
model that admits it isn't confident is more useful than one that guesses and calls it clean.

**4. Confirm, only where needed.** This is what `full` and `deep` modes actually do, and it's the
part that's easy to get wrong: they do **not** read the repository again. That would just be paying
for the expensive step twice. Instead, they take the small list of things the cheap pass marked
uncertain and send exactly those, and nothing else, to a stronger, more careful independent agent for
a real verdict. `deep` mode additionally spot-checks a slice of what the cheap pass called clean, in
case it missed something, everything else in `full` mode is trusted as read. The cost of this step
scales with how much the cheap pass was unsure about, not with how big the repository is.

**5. Report, then stop.** Every finding, every rule checked, and a full checklist table showing the
status of all 36 rules against the whole scope, not just a summary. If a rule was never independently
confirmed, the table says so, out loud, rather than letting a low finding count read as "everything's
fine."

**6. Ask, before touching anything.** The report gets shown to you first. Fixing anything, even one
line, only starts if you say yes after reading it. This is the one step in the whole system that's
never automatic, on purpose.

**7. Fix, and check the fix too.** If you say yes, each fix goes through the exact same discipline as
`better-coding`'s build loop: written in a small piece, checked by an independent agent, and only
counted as done once that check comes back clean and every test still passes.

## Modes

Set with an argument, `/better-coding-review lite`, `full`, or `deep`, or just say which one you
want. `full` is the default.

- **`lite`**: step 3 above, and nothing past it. The exhaustive read, on the cheapest model, no
  confirmation pass. Fast, and honest that a cheap model's "unsure" rows stay unsure in the report.
- **`full`**: step 3 plus step 4. Confirms everything the cheap pass flagged, trusts everything it
  called clean.
- **`deep`**: step 3, step 4, plus a spot-check of the "clean" rows too. The most thorough option,
  and the only one that spends tokens re-checking what the cheap pass was already confident about.

One rule holds in every mode without exception: the very last check, right before anything gets
called finished and committed, is always a real independent pass at full rigor. A cheap `lite`
session speeds up everything in the middle. It never gets to skip the final check.

## Your project's own rules come first

If your repo already has an `AGENTS.md`, a `CLAUDE.md`, or its own doctrine file, that wins wherever
it disagrees with anything here. In Claude Code, you get asked once, the first time either skill runs
in a repo, which of three ways you want that handled: your file wins outright, this rule set wins
outright, or both apply and a real conflict gets flagged the moment it's found rather than guessed
at. In the project-level files for Devin and Kiro, it's stated as a plain rule instead, since those
tools don't have that same interactive back-and-forth: your project's own file wins, this one only
fills what yours doesn't cover.

## Where the rule set came from

It started as a generalized version of a real production codebase's engineering standard, an
object-oriented, zero-comment, strictly-typed backend and frontend where a lot of the sharper rules
came directly out of real PR review feedback. Every company-specific detail, names, a specific
codebase's file layout, has been stripped or generalized out on purpose, what's left is the pattern,
not the source. On top of that: a domain-modeling requirement (write the objects and their
relationships down before the code), and an over-engineering check borrowed from
[ponytail](https://github.com/DietrichGebert/ponytail)'s YAGNI-first ladder, does this need to exist,
is it already here, does the standard library already do it, before writing anything new.

## What's inside

| File | What it's for |
| --- | --- |
| `better-coding/SKILL.md` | The build loop: domain model, design, build, audit, fix, verify, gate. |
| `better-coding-review/SKILL.md` | The whole-repository pipeline described above. |
| `better-coding/references/law.md` | The full rule set, one stable ID per rule. |
| `better-coding/references/triage.md` | The mechanical patterns, the scoping rules, and the chunking math. |
| `better-coding/references/cheatsheet.md` | The condensed rule set the cheap exhaustive pass reads. |
| `better-coding/references/warden.md` | The independent auditor's brief. |
| `better-coding/references/ledger.md` | How violations get tracked and penalized across a build session. |
| `AGENTS.md` | The condensed, static rule set for Devin/Kiro/other AGENTS.md-aware tools. |
| `install.ps1` | The installer described above. |

## License

MIT. See [LICENSE](LICENSE).
