# Live Demo Script

Use this as a live terminal walkthrough by main feature.

## Intro

Type:

```bash
cd ~/lab/cswg/todo-report
```

Say:

This tool reports on TODO systems in Git repos. The main features are `age`,
`drift`, `lint`, and `health`, with `indexes`, `detect`, and `fleet health`
covering monorepo and multi-repo use.

## 1. Age

Type:

```bash
go run ./cmd/todo-report age --repo ~/lab/cswg/coordination --branch jj --format text
```

Say:

This shows top-level TODOs ordered by age using Git history. It helps surface
stale work and long-lived items.

## 2. Drift

Type:

```bash
go run ./cmd/todo-report drift --repo ~/lab/cswg/coordination --branch-a main --branch-b jj --format text
```

Say:

This compares TODO state across two branches. It is branch-aware, so
completion and subtask state are treated as context-specific, not globally
true everywhere.

Note:

This output is long on `coordination`. Narrate briefly and move on.

## 3. Lint

Type:

```bash
go run ./cmd/todo-report lint --repo ~/lab/cswg/coordination --branch jj --format markdown
```

Say:

This validates the TODO structure itself. It catches malformed IDs, broken
links, orphaned detail files, and index/detail consistency issues.

## 4. Health

Type:

```bash
go run ./cmd/todo-report health --repo ~/lab/cswg/coordination --branch jj --format text
```

Say:

This is the summary view. It combines age and lint into one report, and can
also include drift when needed.

## 5. Health JSON export

Type:

```bash
go run ./cmd/todo-report health --repo ~/lab/cswg/coordination --branch jj --format json
```

Say:

The same report can be emitted as machine-readable JSON for scripts or
downstream tooling.

## 6. Index discovery

Type:

```bash
go run ./cmd/todo-report indexes --repo ~/lab/wire-lab --branch main --format text
```

Say:

This discovers authoritative TODO indexes in a monorepo. It is the entry
point for repos with multiple TODO roots.

## 7. Monorepo health

Type:

```bash
go run ./cmd/todo-report health --repo ~/lab/wire-lab --branch main --all-indexes --exclude-index archive/ --format text
```

Say:

This rolls multiple discovered TODO indexes into one repo-wide summary. I am
excluding archived paths here to keep the demo focused on active work.

## 8. Compatibility detection

Type:

```bash
go run ./cmd/todo-report detect --repo ~/lab/wire-lab --branch main --index protocols/wire-lab.d/TODO/TODO.md --format text
```

Say:

This inspects the repo’s TODO dialect. It tells us what top-level ID styles,
subtask styles, and special features the repo uses before we adopt or tighten
lint rules.

## 9. Fleet health

Type:

```bash
go run ./cmd/todo-report fleet health --repo ~/lab/cswg/coordination --repo ~/lab/wire-lab --branch main --all-indexes --exclude-index archive/ --format text
```

Say:

This is the multi-repo view. It rolls multiple repos into one summary, either
from repeated `--repo` flags or a `--repo-list` file.

## 10. Exit codes

Type:

```bash
go run ./cmd/todo-report drift --repo ~/lab/cswg/coordination --branch-a main --branch-b jj --format text >/dev/null; echo $?
```

Say:

The tool is script-friendly. `0` means clean, `1` means warnings or
differences, and `2` means errors.

## Close

Say:

So the tool works at three scopes: single repo, monorepo, and fleet. It is
readable for humans, structured for scripts, and grounded in the TODO files
and Git history teams already have.
