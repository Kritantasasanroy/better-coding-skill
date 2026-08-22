# better-coding

Two tools built to stop an AI coding agent from grading its own work.

Here's the problem. Ask an agent to write code, then ask that same agent if the code is any good,
and you're asking one train of thought to check itself. Whatever reasoning led to a shortcut is
still sitting there when you ask about the shortcut. It usually says the code looks fine.
`better-coding` splits the job across two agents that never share context. One writes. A separate
one audits. Only the audit gets to say "done."

## The two tools

**`better-coding`** runs while you build something new. Before you write any code, it makes you
write down the domain model first. Plainly. What are the real objects here? What does each one own?
How do they relate? What states can they be in? Then it builds in small pieces, and an independent
agent checks each piece against a fixed rule set before you move to the next one. That agent stays
alive for the whole session instead of getting re-spawned for every single piece, so the rules only
get loaded once per feature, not once per piece. Reading the rules again and again for the same
short list of rules was wasted work, so it doesn't happen anymore.

**`better-coding-review`** runs against code that already exists. Maybe a whole repository nobody's
ever checked before. It scopes the repo, reads every file that matters exactly once, and hands you a
full compliance report. It won't touch your code by itself. Fixing only starts if you say yes after
you've read the report.

Install both together. They share one rule set and they're built to work as a pair.

## Install

### macOS / Linux, one command

```bash
curl -fsSL https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.sh | bash
```

### Windows, one command

```powershell
irm https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.ps1 | iex
```

Run either one once. It downloads this repo and drops both skills into `~/.claude/skills/`. That
folder is user-level: Claude Code checks it in every project you open, not only the one you're
sitting in right now. So you really only do this once. After that, `/better-coding` and
`/better-coding-review` work in any repo, on this machine, from now on.

Prefer to do it by hand? Clone the repo and copy the `better-coding` and `better-coding-review`
folders into your own `~/.claude/skills/`. Keep those exact folder names. Claude Code matches a
skill by the `name` field in its `SKILL.md`, and that name has to match the folder it lives in.

### Other tools: Cursor, Windsurf, Cline, Devin, Kiro, and anything that reads AGENTS.md

Claude Code skills live at the user level, once per machine. These other tools don't work that way.
They read instructions that live inside the project you're working in. So for those, you install
per project, and it's a separate step.

macOS / Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.sh -o install.sh
bash install.sh --project --skip-claude
```

Windows:
```powershell
irm https://raw.githubusercontent.com/Kritantasasanroy/better-coding-skill/main/install.ps1 -OutFile install.ps1
.\install.ps1 -Project -SkipClaude
```

Run it from inside the project you want it in, after the one-time Claude Code install above. It
drops six files into the current directory, one per tool, using each tool's own real convention,
not a generic file dumped in six places and hoped for:

| File | Read by |
| --- | --- |
| `AGENTS.md` | Devin, Kiro, Qoder, OpenCode, and most other AGENTS.md-aware tools, no setup needed |
| `.cursor/rules/better-coding.mdc` | Cursor |
| `.windsurf/rules/better-coding.md` | Windsurf |
| `.clinerules/better-coding.md` | Cline |
| `.devin-plugin/plugin.json` | Devin's plugin manifest |
| `.kiro/steering/better-coding.md` | Kiro's steering system |

Commit all six so your team gets them too when they pull the repo.

One honest note here. These project-level files carry the condensed rule set as a static, always-on
instruction. They skip the interactive parts: the precedence negotiation, the audit loop, the
whole-repository pipeline described below. Those need Claude Code actually running the skill. If
your team's on Claude Code, install both ways. On any of these other tools, the project files are
what you get, and they carry the real rules, just without a second agent independently checking
your work against them.

## What actually happens when you run it

Most tool READMEs skip this part. Here it is in full. The steps below are described generically on
purpose, not with numbers from one specific repository presented as if they're typical, since your
repo's real file count, line count, and chunk count will be its own and nobody else's. Every number
that matters gets reported fresh, from the actual scope of the actual run, every time.

**1. Scope.** First question, always: how many files, how many lines. Not every tracked file
deserves a review. `better-coding-review` excludes tests, docs, lockfiles, and generated output by
default, since that's not where the domain model lives, and keeping them in just inflates every
number that follows. Filtering out tests alone typically removes a large share of a repo's tracked
lines, test code is often as large as or larger than the code it tests, so this one step is usually
most of what makes the rest of the pass affordable. The report states the real before-and-after
counts for your repo, computed on that run, not carried over from anywhere else.

**2. Triage.** A handful of `grep` searches. No AI involved yet. It runs across every file in scope
and catches the part of the rule set that's just a pattern: a suppressed type checker, a bare `any`,
an empty `except` block, a class named `SomethingManager`. It costs nothing, and it scales to any
repo size because it's just text search.

**3. The one real read.** This is `lite` mode, and don't think of it as a cut-down version of the
other two. Everything else builds on it. `better-coding-review` splits the filtered file set into
chunks a model can read start to finish, and a cheap, fast model reads every single one, in full,
once. For every file and every rule that applies, it writes down an answer: clean, a real finding,
or honestly unsure. That last answer matters. A cheap model that admits it isn't confident beats one
that guesses and calls everything clean.

**4. Confirm, only where it's needed.** This is what `full` and `deep` modes do, and it's easy to
get wrong if you assume they re-read everything. They don't, that would mean paying for the
expensive step twice. Instead, they take the short list of things the cheap pass marked uncertain
and send only that list to a stronger, slower, independent agent for a real verdict. `deep` mode
also spot-checks a slice of what the cheap pass called clean, in case it missed something. Everything
else in `full` mode stays trusted as read. The cost here tracks how much the cheap pass was unsure
about, not how big the repository is.

**5. Report, then stop.** You get every finding, every rule checked, and a full checklist table
covering all 36 rules against the whole scope, not a summary that hides gaps. If a rule was never
independently confirmed, the table says so out loud instead of letting a low finding count read as
"everything's fine."

**6. Ask before touching anything.** You see the report first. Fixing anything, even one line, only
starts if you say yes after reading it. This is the one step that never runs on its own.

**7. Fix, and check the fix too.** Say yes, and each fix goes through the same discipline as
`better-coding`'s build loop. Written in a small piece, checked by an independent agent, and only
counted as done once that check comes back clean and every test still passes.

## Modes

Set one with an argument, `/better-coding-review lite`, `full`, or `deep`. Or just say which one you
want. `full` runs by default.

- **`lite`**: step 3 above, and that's it. The exhaustive read, on the cheapest model, no
  confirmation pass. Fast. Honest that a cheap model's "unsure" rows stay unsure in the report.
- **`full`**: step 3 plus step 4. Confirms everything the cheap pass flagged, trusts everything it
  called clean.
- **`deep`**: step 3, step 4, and a spot-check on the "clean" rows too. The most thorough option,
  and the only one that spends tokens re-checking work the cheap pass already trusted.

One rule holds no matter which mode you pick. The very last check, right before anything gets
marked finished and committed, always runs as a real independent pass at full rigor. A cheap `lite`
session speeds up everything in the middle. It never gets to skip that final check.

## Your project's own rules come first

Got an `AGENTS.md`, a `CLAUDE.md`, or your own doctrine file already? That wins wherever it
disagrees with anything here. In Claude Code, you get asked once, the first time either skill runs
in a repo, how you want that handled: your file wins outright, this rule set wins outright, or both
apply and any real conflict gets flagged the moment it shows up. In the project-level files for
Devin and Kiro, it's just stated as a plain rule, since those tools don't do that back-and-forth:
your project's own file wins, this one only fills in what yours doesn't cover.

## Where the rule set came from

It started as a generalized version of a real production codebase's engineering standard.
Object-oriented, zero comments, strict typing, a backend and frontend where a lot of the sharper
rules came straight out of real PR review feedback. Every company-specific detail got stripped or
generalized out on purpose. What's left is the pattern, not the source. On top of that: a
requirement to write down the domain model before touching code, and an over-engineering check
borrowed from [ponytail](https://github.com/DietrichGebert/ponytail)'s YAGNI-first ladder: does this
need to exist, is it already here, does the standard library already cover it, before writing
anything new.

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
| `.cursor/rules/`, `.windsurf/rules/`, `.clinerules/` | The same condensed rule set, in each tool's own format. |
| `.devin-plugin/`, `.kiro/steering/` | Devin's plugin manifest and Kiro's steering file. |
| `install.sh` | The macOS/Linux installer described above. |
| `install.ps1` | The Windows installer described above. |

## License

MIT. See [LICENSE](LICENSE).
