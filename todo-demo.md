# todo-report Demo Cheatsheet

This file is a practical walkthrough for demos, onboarding, and manager handoff.
It covers:

- the webpage and what each screen is for
- how the backend works and where the code lives
- the CLI, including how to scan a specific branch

## How to regenerate this file

Use the Makefile target from the repo root:

```bash
make demo-doc
```

By default this writes to:

```text
~/Documents/todo-demo.md
```

You can override the output path:

```bash
make demo-doc DEMO_DOC=/tmp/todo-demo.md
```

## 1. Webpage Cheatsheet

### Main pages

- Root dashboard: `index.html`
  This is the manager-facing landing page. It shows the latest published fleet status.
- Latest published report: `reports/latest.html`
  This is the full detail view for the most recent fleet scan.
- Report archive: `reports/index.html`
  This lists previously published daily reports so people can review earlier snapshots.
- Product overview: `info.html`
  This explains what the tool is, what it measures, and how the published reports fit together.
- Help pages: `errors.html` and `warnings.html`
  These explain what a repo `ERROR` or `WARNING` means and what action to take.

### What the root dashboard shows

- `Status`
  Overall fleet status from the latest published run.
- `Repos`
  How many repos were included and how many scanned successfully.
- `Open TODOs`
  Count of currently open top-level TODOs found across the scanned repos and indexes.
- `Completed`
  Count of completed top-level TODOs found across the scanned repos and indexes.
- `Repo Errors`
  Count of repo-level scan failures such as access problems or missing branches.
- `Lint Errors`
  Count of blocking TODO-structure failures.

### What the repo table shows

- `Repo`
  The repo display name. The repo URL under the name is clickable when a URL is known.
- `Branch`
  The actual branch scanned for that repo.
- `Status`
  Repo-level result such as `CLEAN`, `WARNING`, or `ERROR`.
- `Mode`
  Whether the repo was scanned as a single index or with `all-indexes`.
- `Indexes`
  Number of TODO indexes included in that repo’s report.
- `Open`
  Open top-level TODO count for that repo.
- `Completed`
  Completed top-level TODO count for that repo.
- `Lint Errors`
  Blocking TODO-structure problems.
- `Lint Warnings`
  Non-blocking TODO-structure problems.
- `Drift`
  Number of branch-difference rows when compare mode is enabled.
- `Notes`
  Short summary of the main reason a repo needs attention.

### What a manager should click first

1. Open the root dashboard.
2. Look at `Repositories Needing Attention`.
3. Open the latest report for the full repo list.
4. Click a repo link to go to the repo when follow-up is needed.
5. Click `ERROR` or `WARNING` guidance if the status meaning is not obvious.
6. Open the report archive to compare day-to-day snapshots.

### What the archive is for

- The archive is not just one old test.
- Each published daily run creates a timestamped report under `reports/daily/YYYY-MM-DD/`.
- The archive page is the historical list of those published runs.
- This is the place a lead or manager can review progress across days.

## 2. Backend And Code Cheatsheet

### High-level flow

1. The CLI reads the command and flags in `cmd/todo-report/main.go`.
2. The repo source is opened through the Git layer.
3. The selected branch is resolved.
4. The tool discovers one index or many indexes.
5. It parses TODO entries and detail files.
6. It runs age, lint, health, drift, or fleet aggregation.
7. It renders text, markdown, JSON, TSV, or published HTML reports.

### Main code areas

- `cmd/todo-report/main.go`
  CLI entrypoint, command routing, flags, branch options, and output selection.
- `engine/gitrepo/`
  Opens local or remote Git sources and reads files from the requested branch.
- `engine/todo/`
  TODO discovery, parsing, index selection, and compatibility detection.
- `engine/lint/`
  Structure checks such as malformed IDs, duplicate IDs, orphan detail files, and mismatches.
- `engine/age/`
  Computes TODO age from Git history.
- `engine/drift/`
  Compares TODO state across two branches.
- `engine/health/`
  Builds repo-level health summaries from age, lint, and optional drift data.
- `engine/fleet/`
  Runs fleet scans across many repos, loads config, and publishes the daily reports.
- `engine/report/`
  Converts results into text, markdown, JSON, TSV, and report-friendly output.
- `engine/model/`
  Shared data structures used across commands and renderers.
- `engine/testrepo/`
  Test fixtures and helpers for realistic repo samples.

### How branch-aware scanning works

- For single-repo commands such as `age`, `lint`, `health`, `detect`, and `indexes`, `--branch` selects the branch to scan.
- If `--branch` is omitted:
  - local repos default to the current checked-out branch
  - remote repos default to the repo’s default branch
- For branch comparison, `drift` uses `--branch-a` and `--branch-b`.
- `health --compare` keeps one main branch for counts and adds drift against another branch.
- Fleet runs can set a branch in several places:
  - command line `--branch`
  - config-level `default_branch`
  - per-repo `branch`

### How published reports are generated

- `fleet report daily` writes report files under `reports/`.
- It creates timestamped daily files under `reports/daily/YYYY-MM-DD/`.
- It refreshes `reports/latest.html`, `reports/latest.md`, and `reports/latest.json`.
- It rebuilds the root dashboard and archive pages so GitHub Pages can serve the latest state.

### What to point engineers at in the code

- If they want CLI behavior: start in `cmd/todo-report/main.go`.
- If they want parser behavior: start in `engine/todo/parser.go` and `engine/todo/discovery.go`.
- If they want lint rules: start in `engine/lint/lint.go`.
- If they want fleet publishing: start in `engine/fleet/fleet.go` and `engine/fleet/publish.go`.
- If they want HTML and text output: start in `engine/report/render.go` and the publish renderer helpers in `engine/fleet/publish.go`.

## 3. CLI Cheatsheet

### Local launcher

From this repo, the simplest way to run the tool is:

```bash
./todo-report health --repo ~/lab/cswg/coordination --branch jj --format text
```

If you want the bare command:

```bash
go install ./cmd/todo-report
todo-report health --repo ~/lab/cswg/coordination --branch jj --format text
```

### Core commands

- `age`
  Show TODO age from Git history.
- `drift`
  Compare TODO state across two branches.
- `lint`
  Validate TODO structure.
- `health`
  Summarize repo health.
- `indexes`
  Discover all authoritative `TODO/TODO.md` indexes in a repo.
- `detect`
  Show what TODO shapes and compatibility patterns were found.
- `fleet health`
  Scan many repos and show one combined health report.
- `fleet report daily`
  Publish the manager-facing HTML, markdown, and JSON report set.

### How to specify a branch

#### Single repo scan

```bash
./todo-report health --repo ~/lab/cswg/coordination --branch jj --format text
```

This scans the `jj` branch for that repo.

#### Single repo lint on `main`

```bash
./todo-report lint --repo ~/lab/cswg/coordination --branch main --format text
```

#### Compare two branches directly

```bash
./todo-report drift --repo ~/lab/cswg/coordination --branch-a main --branch-b jj --format text
```

#### Health on one branch, drift against another

```bash
./todo-report health --repo ~/lab/cswg/coordination --branch main --compare jj --format text
```

This keeps the main repo counts anchored to `main`, then adds drift against `jj`.

#### Scan all indexes in a monorepo on a specific branch

```bash
./todo-report health --repo ~/lab/wire-lab --branch main --all-indexes --format text
```

#### Scan a specific nested index on a specific branch

```bash
./todo-report health \
  --repo ~/lab/wire-lab \
  --branch main \
  --index protocols/wire-lab.d/TODO/TODO.md \
  --format text
```

### Fleet scanning

#### Repo list with one branch for all repos

```bash
./todo-report fleet health --repo-list repos.txt --branch main --all-indexes --format text
```

#### Inline repos with one branch for all repos

```bash
./todo-report fleet health \
  --repo ~/lab/cswg/coordination \
  --repo ~/lab/wire-lab \
  --branch main \
  --all-indexes \
  --format text
```

#### Publish the daily fleet report

```bash
./todo-report fleet report daily --config fleet.json
```

### Branch selection through config

Example:

```json
{
  "default_branch": "main",
  "compare_branch": "jj",
  "all_indexes": true,
  "reports_dir": "reports",
  "repos": [
    {
      "repo": "~/lab/cswg/coordination",
      "daily": true
    },
    {
      "repo": "~/lab/wire-lab",
      "branch": "main",
      "all_indexes": true,
      "daily": true
    },
    {
      "repo": "https://github.com/ciwg/grid-examples",
      "branch": "main",
      "compare_branch": "jj",
      "daily": true
    }
  ]
}
```

What each branch field means:

- `default_branch`
  The branch used for repos that do not override it.
- `compare_branch`
  Default compare target when branch drift is enabled.
- `repos[].branch`
  Per-repo branch override.
- `repos[].compare_branch`
  Per-repo compare override.

### Good demo commands

```bash
./todo-report indexes --repo ~/lab/wire-lab --branch main --format text
./todo-report detect --repo ~/lab/wire-lab --branch main --all-indexes --format text
./todo-report fleet health --repo-list repos.txt --branch main --all-indexes --format markdown
./todo-report fleet report daily --config fleet.json
```

### Demo talking points

- The tool is local-first and read-only.
- It supports multiple TODO styles instead of forcing one repo shape.
- It can scan one repo, a monorepo, or a fleet.
- It is branch-aware, so the report can reflect `main`, a feature branch, or a compare view.
- It publishes manager-friendly HTML without requiring manager access to local developer machines.
