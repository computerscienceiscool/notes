# Ex4 Demo

`ex4-bug-tracker` is the browser-first bug tracker example with a small engineer-focused CLI.

## Run The Seeded Demo

```bash
cd /home/jj/lab/cswg/grid-examples/ex4-bug-tracker
GOCACHE=/tmp/ex4-run-demo-build GOMODCACHE=/tmp/ex4-run-demo-mod bash scripts/run-demo.sh
```

Open the browser:

```text
http://127.0.0.1:7035/
```

## What The Demo Seeds

The seeded demo creates issues that already show:

- a new issue with an attachment
- an issue in progress
- a resolved issue
- a reopened issue back in triage

## CLI Smoke Commands

In another shell:

```bash
cd /home/jj/lab/cswg/grid-examples/ex4-bug-tracker
go run ./cmd/bug-tracker-cli --user engineer assigned
go run ./cmd/bug-tracker-cli --user engineer show BUG-0002
go run ./cmd/bug-tracker-cli --user engineer comment BUG-0002 "cli smoke test"
```

## Runtime Data

The demo launcher uses:

```text
/tmp/grid-examples-ex4-demo
```

A normal non-demo server run uses:

```text
ex4-bug-tracker/.bug-tracker/
```

## Notes

- The browser is the primary demo surface.
- The CLI is intentionally narrow and engineer-focused.
- The demo seed is repeatable and does not duplicate issues on a second seed pass.
