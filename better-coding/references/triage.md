# Triage

A mechanical pass that runs before any agent is spawned, in every mode, on any amount of code. It
costs a script run, not tokens, and it does two jobs. It catches the part of the Law and Craft that
is genuinely pattern-matchable. And it narrows what the Reviewer and the Auditor have to read cold.

Triage findings are **leads, not verdicts**, with one tier of exceptions. A hit for `Optional[` is a
place to look, since `Optional` is sometimes right. A hit for `# type: ignore` or `# ... existing
code ...` is close to a verdict.

## Running it

```
python3 -I <skill-dir>/scripts/triage.py <repo-root> --diff <baseline-ref>   # a slice or a whole change
python3 -I <skill-dir>/scripts/triage.py <repo-root> --files <path> ...      # specific files
python3 -I <skill-dir>/scripts/triage.py <repo-root>                         # whole repo, important set
python3 -I <skill-dir>/scripts/triage.py <repo-root> --diff <base> --commit HEAD   # also the message
python3 -I <skill-dir>/scripts/triage.py <repo-root> --diff <base> --format json    # for CI to parse
```

Standard library only, Python 3.8+. In `--diff` mode it reports only lines added since the
baseline (untracked files count in full), so pre-existing code isn't charged to the current change.
For Python it measures function length (code lines, docstring excluded), approximate cyclomatic
complexity and nesting depth from the AST. For other languages it uses `lizard` if that's on
`PATH`, and otherwise says plainly that shape was not measured.

The script was validated on a seeded repository (every planted violation caught, zero hits on a
clean file) and on pre-2020 Django and Flask. On Django's 55 KLOC it produced 3 near-verdicts, all
real `except Exception: pass` blocks.

### If Python isn't available

Use `rg` with **`-g` globs**, never `-- '*.py'`. After `--`, ripgrep treats `'*.py'` as a literal
path, errors with "No such file or directory", and finds nothing. That exact bug made every
pattern in an earlier version of this file silently return nothing. If `rg` isn't installed, use
`grep -rnE … --include='*.py' .`.

Always pass an explicit path (`.`) as the last argument. When stdin isn't a terminal, which is the
normal case for an agent's shell, `rg` with no path reads stdin and waits forever.

```
rg -n '#\s*noqa|#\s*type:\s*ignore|eslint-disable|@ts-ignore|@ts-nocheck' -g '*.py' -g '*.ts' -g '*.tsx' .
rg -n '(->|:|\[|,)\s*Any\b|:\s*any\b|<any>|\bas any\b' -g '*.py' -g '*.ts' -g '*.tsx' .
rg -n -U '^\s*except\s*(Exception\s*)?:\s*\n\s*pass\b' -g '*.py' .
rg -n 'catch\s*(\([^)]*\))?\s*\{\s*\}' -g '*.ts' -g '*.tsx' -g '*.js' -g '*.java' .
rg -n -i '(#|//)\s*\.\.\.\s*(existing|rest of|remaining)|(#|//)\s*(as requested|updated to fix|changed from \w+ to)' .
rg -n 'class \w*(Manager|Helper|Utils|Processor|Generator|Handler|Builder|Engine|Coordinator|Data|Info)\b' .
```

Run one sanity check first: a pattern you know matches something in this repo. A triage pass that
returns zero hits without that check has proven nothing.

## What it checks

| Tier | Rule | Check |
| --- | --- | --- |
| Near-verdict | C1 | Checker suppressions; `Any`/`any` in typing positions (comments and docstrings excluded) |
| Near-verdict | C3 | `except:` / `except Exception:` followed by `pass`/`...`/`return`/`continue`; empty `catch {}`; `.catch(() => {})` |
| Near-verdict | H16 | Placeholders for code (`# ... existing code ...`, "rest of implementation"); chat-addressed or changelog text in comments |
| Near-verdict | H10 | Commit subject over 72 chars; emoji in the commit message |
| Lead | H2 | Narration comments ("Initialize the …", "Loop through …", "Step 1:"); judged by density, per H2 |
| Lead | H4, L16 | Function over `--max-lines` (default 50) code lines, complexity over `--max-branches` (default 10), nesting depth over 3 |
| Lead | H5 | Broad catch (`except Exception`, `catch (Exception`) |
| Lead | H8 | Versioned or hype identifiers (`_v2`, `Improved…`, `Enhanced…`, `_final`, `_fixed`) |
| Lead | H10 | Bullet-list body, markdown in body, body not wrapped, AI-register vocabulary |
| Lead | H12 | Emoji in source |
| Lead | H16 | Invented example values in code (`example.com`, `your-api-key`, `sk-test`) |
| Lead | L5 | `Optional` / nullable |
| Lead | L21 | Debug output and unowned TODO/FIXME |
| Lead | L26 | Generic-suffix and adjective-as-state class names |
| Lead | L27 | Verb-named classes; module-level `def` (Python) |
| Lead | L31 | Orphan-class candidates: a class whose name appears once across every tracked file |

Calibrate the H4 thresholds to the house. Pass the fingerprint's p90 function length as
`--max-lines` when the house runs smaller or larger than the default.

## Scoping the file set (whole-repository mode)

Two counts, always, before any pattern or any agent, reported to the user as the first line of any
audit: how many files, then how many lines. Skipping straight to "here's the report" without stating
scope is how a partial pass gets read as a complete one.

1. Total tracked source files: `git ls-files` filtered to source extensions. It already excludes
   what `.gitignore` excludes.
2. The important set: exclude tests, docs, generated output, vendored code and migrations by
   default. `triage.py` applies the same default exclusions. State the exclusion list in the report
   header, and treat it as overridable (`--include-tests`).
3. Line count of the important set, one call, not a per-file loop and not `xargs wc -l`:

   ```
   git ls-files -z -- <filters> | xargs -0 cat | wc -l
   ```

   `xargs wc -l | tail -1` is wrong on large repos: past `xargs`'s argument limit it runs `wc` more
   than once, each run prints its own `total`, and `tail -1` keeps only the last. Piping every file
   through `cat` first means one `wc -l`, however many batches `xargs` uses.

Report the real counts from this run, never a number from another run or another repo. If filtering
out tests barely moved the count, check whether the exclusions matched anything.

## Chunking a whole repository

For `better-coding-review`'s exhaustive pass, chunk by size, not by directory.

1. Get per-file line counts as a manifest (`git ls-files -z … | xargs -0 wc -l`, using the per-file
   rows and ignoring any `total` rows).
2. Bin files into chunks of about **3,000 lines**, keeping files from the same directory together,
   and splitting a directory only when it alone exceeds the budget.
3. Spawn the Reviewers for a wave of chunks in one message, at most 6–8 per wave.

## Coverage map: what a pattern alone can and can't see

| Coverage | Meaning | Rules |
| --- | --- | --- |
| **Mechanical** | A pattern reliably finds real instances | C1, C3, L1, L6, L21, H10 (format), H12, H16 (placeholders) |
| **Lead** | A pattern finds candidates; reading resolves them | L2, L5, L8, L12, L14, L15, L23, L26, L27, L28, L29, L30, L31, H2, H4, H5, H8, H13 |
| **Judgment-only** | No textual pattern helps | L3, L4, L7, L9, L10, L16, L17, L25, H1, H3, H6, H7, H14 |
| **Change-only** | Applies to a change in progress, not code at rest | C2, C4, C5, L11, L13, L18, L19, L20, L22, L24, H9, H10 (content), H11, H15 |

The Reviewer's exhaustive read gives every rule a real call on every file. What it lacks is the
strongest model's judgment, which the Auditor supplies for the rows the Reviewer wasn't sure of.
