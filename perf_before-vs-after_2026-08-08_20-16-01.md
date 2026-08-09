# goscalelint timing — dirty vs clean (before vs after)

**Run:** 2026-08-08_20-16-01
**Inputs:** `perf_tests-before_2026-08-08_20-16-01.md` · `perf_tests-after_2026-08-08_20-16-01.md`
**Machine:** Intel Core i7-1065G7 @ 1.30 GHz, 8 threads · **Go:** go1.26.1 linux/amd64
**Cache:** cleared (`go clean -cache`) before each sweep, module deps rebuilt untimed
**Sizes:** 1 → 100,000. (No 1M data yet: a follow-up 1M attempt was aborted —
its vet step ran 46+ minutes at ~11 GB RSS; see `perf_tests-before_2026-08-08_20-30-04.md`.)

Both sweeps generate N structurally identical functions and time the same
four runs; the only difference is one line per function:

```go
m := map[string]int{}                    // tests-before: dirty — every function is a map-prealloc finding
m := make(map[string]int, len(items))    // tests-after:  clean — zero findings
```

So `before` measures goscalelint over code where **every function reports a
finding** (N findings), and `after` measures the identical workload with
**zero findings**.

## What each column means

- **cold** — `goscalelint ./perf/...` on freshly generated code the tool has
  never seen. Nothing is cached, so it pays for everything: loading the
  package, parsing, type-checking, running all 17 analyzers, and printing
  findings. Worst case — what a first CI run on a fresh checkout feels like.
- **warm** — the exact same command immediately again. The standalone binary
  keeps no results between runs, so all analysis happens again; only the
  surrounding I/O is cheaper (OS page cache, Go build cache). The cold−warm
  gap is one-time setup cost; warm is the binary's floor for repeated runs.
- **vet 1st** — `go vet -vettool=goscalelint ./perf/...`: Go's vet command
  driving the same analyzers through the build system. First time through it
  must still analyze everything, so it lands near warm.
- **vet 2nd** — the same vet command repeated. vet caches analysis results
  in the build cache keyed by package contents, so an unchanged package
  replays the stored result (~0.1 s at any size) instead of re-analyzing.

Practical reading: the standalone binary re-pays full analysis cost on every
run, while vet only pays for packages that changed — use `go vet -vettool`
for repeated runs (CI, hooks), the direct binary for one-shot scans.

## Cold runs (first run after generation)

| N | before (s) | after (s) | Δ (s) | after/before |
|---:|---:|---:|---:|---:|
| 1 | 0.14 | 0.14 | 0.00 | 1.00× |
| 10 | 0.13 | 0.15 | +0.02 | 1.15× |
| 100 | 0.15 | 0.19 | +0.04 | 1.27× |
| 1,000 | 0.37 | 0.54 | +0.17 | 1.46× |
| 10,000 | 3.08 | 3.40 | +0.32 | 1.10× |
| 100,000 | 54.56 | 34.37 | −20.19 | **0.63×** |

## Warm runs (immediate second run)

| N | before (s) | after (s) | Δ (s) | after/before |
|---:|---:|---:|---:|---:|
| 1 | 0.13 | 0.15 | +0.02 | 1.15× |
| 10 | 0.13 | 0.16 | +0.03 | 1.23× |
| 100 | 0.13 | 0.18 | +0.05 | 1.38× |
| 1,000 | 0.17 | 0.24 | +0.07 | 1.41× |
| 10,000 | 0.62 | 0.55 | −0.07 | 0.89× |
| 100,000 | 26.90 | 5.33 | −21.57 | **0.20×** |

## go vet -vettool, first run

| N | before (s) | after (s) | Δ (s) | after/before |
|---:|---:|---:|---:|---:|
| 1 | 0.13 | 0.13 | 0.00 | 1.00× |
| 10 | 0.11 | 0.10 | −0.01 | 0.91× |
| 100 | 0.11 | 0.13 | +0.02 | 1.18× |
| 1,000 | 0.14 | 0.16 | +0.02 | 1.14× |
| 10,000 | 0.70 | 0.52 | −0.18 | 0.74× |
| 100,000 | 30.55 | 5.21 | −25.34 | **0.17×** |

## go vet -vettool, second run (vet result cache)

Flat ~0.1 s at every size in both sweeps (0.09–0.13 s). With the cache
cleared before each sweep, both first-run columns above are genuinely cold;
the second vet run is a pure cache hit regardless of findings.

## Findings

`before` reported exactly N findings at every size; `after` reported 0 at
every size — confirming the generated code is fully dirty and fully clean
respectively.

## Repeatability

A second dirty sweep the same evening (`perf_tests-before_2026-08-08_20-30-04.md`,
aborted at its 1M step but complete through 100k) reproduced the before
numbers within ~10%: at 100k, cold 60.31 s vs 54.56 s, warm 30.86 s vs
26.90 s, vet 1st 31.46 s vs 30.55 s. Sub-second rows jitter by ±0.05 s.
Treat single-run cells at that granularity.

## Observations

- **Reporting findings is a real cost at scale.** At N = 100,000 the warm
  run drops from 26.90 s (100k findings) to 5.33 s (0 findings) — 5× faster,
  ≈ 0.22 ms per finding. That overhead is the match-path analysis work plus
  rendering and printing 100,000 diagnostic lines.
- **Cold runs converge, but findings still dominate.** Cold time includes
  parsing and type-checking 800k lines (~30 s), identical for both; the
  dirty sweep still pays ~20 s more on top for the findings.
- **Below N ≈ 10,000 the difference is noise.** Both sweeps live in the
  0.1–0.6 s range there; the small apparent slowdowns for `after` at tiny N
  (+0.02–0.07 s) are within run-to-run jitter, not a real cost of clean
  code.
- **vet mirrors the standalone warm runs** (0.17× at 100k) and its result
  cache flattens everything to ~0.1 s on the second run — for CI over a
  mostly-unchanged codebase, `go vet -vettool` remains the cheap way to run
  goscalelint repeatedly.
- **vet-mode over massive finding counts is its own failure mode.** The
  aborted 1M attempt showed `go vet -vettool` at one million findings
  running 46+ minutes at ~11 GB RSS (JSON diagnostic encoding), while the
  direct binary handled the same package in minutes. For dirty megapackages,
  use the direct binary; `VET=0` in perftime.sh skips the vet columns.
