# better_coding

A Claude Code skill that won't let an agent grade its own homework.

Most AI coding tools trust the same model that wrote the code to also judge it. That's a strange
setup if you think about it: the reasoning that produced a shortcut is the same reasoning you're
relying on to catch it. `better_coding` splits the job in two instead. One agent builds. A separate
agent, called the Warden, audits the diff against a fixed rule set called the Law. The Warden never
sees the builder's reasoning, only the code and the rules. Break a rule, and you get penalized, and
the work goes back for rework. That cycle repeats until the goal is fully met and the audit comes
back clean.

## Install

Pick one, depending on how you want it to show up.

**Personal, works in every project on your machine:**

```
git clone https://github.com/Kritantasasanroy/better-coding-skill.git ~/.claude/skills/better_coding
```

**Project-level, ships with a specific codebase so your whole team gets it on clone:**

```
git clone https://github.com/Kritantasasanroy/better-coding-skill.git .claude/skills/better_coding
```

Either way, keep the folder name as `better_coding`. Claude Code matches a skill by the `name` field
in its frontmatter, and that name has to match the directory it lives in. Rename the folder and the
skill just won't load.

## Use it

```
/better_coding add rate limiting to the login endpoint
```

That's it. The skill takes over from there. It writes a charter with concrete, checkable acceptance
criteria, works through a plan, and builds in small slices, sending each one to the Warden before
moving forward. Nothing counts as done until every criterion has real evidence behind it and the
Warden's last audit, run after your very last edit, comes back clean.

## What's actually enforced

The rule set lives in [`references/law.md`](references/law.md). It's a mix of two things: a strict
PR review checklist (trace every branch, justify every `except`, question every `Optional`, respect
module boundaries) and a set of team handbook conventions (commit format, branch naming, test
philosophy, what counts as scope creep). Every rule carries a stable ID, so if the same one breaks
twice, the loop notices and starts enforcing it harder from then on.

Some things are never allowed to slide, no matter how close to "done" things look. Silencing a
linter with `# type: ignore` or `eslint-disable`. Deleting or weakening a test just to turn a build
green. Catching an exception only to swallow it. Claiming a command passed without running it. These
are CAPITAL offenses. They don't get patched. They get reverted, and the slice gets rebuilt from a
clean base.

## How the penalty actually works

Points on their own don't change behavior. Here's the thing that does: three real mechanisms behind
them.

- **Forced rework.** A CAPITAL finding means the change is stashed, not patched, and rewritten from
  scratch.
- **Standing Orders.** Break the same rule twice and it gets promoted into a list that's re-read
  before every slice from that point on. It stops being one line among thirty and starts acting as
  a live constraint on whatever gets written next.
- **A public ledger.** Every penalty, from every round, gets reported back to you at the end, even
  when the final run is clean. Especially then.

There's a circuit breaker too, so this doesn't spin forever hoping to get lucky. If the same rule
breaks three times, or a criterion needs a call only you can make, or two rounds in a row make no
progress, the loop stops and hands you the problem with the full ledger attached. Escalating with a
clear blocker beats declaring victory on work nobody actually checked.

## Your project's rules come first

If your repo already has an `AGENTS.md` or a `CLAUDE.md`, those win. The Law only fills the gaps
where your project stays silent, and it never loosens something your project already locked down.
Say your team bans comments outright. The Law's "comments should explain why" clause doesn't reopen
that door. Your rule stands, full stop.

## What's inside

| File | What it's for |
| --- | --- |
| `SKILL.md` | The loop itself: charter, recon, design, build, audit, sentencing, verify, gate. |
| `references/law.md` | The rule set, with a stable ID on every rule. |
| `references/warden.md` | The auditor's brief, handed to the Warden agent as is. |
| `references/ledger.md` | The penalty schedule and the format for recording findings. |

## License

MIT. See [LICENSE](LICENSE).
