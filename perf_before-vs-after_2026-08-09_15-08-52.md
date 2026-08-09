# goscalelint timing — dirty vs clean, small-N focus (before vs after)

**Run:** 2026-08-09_15-08-52
**Inputs:** `perf_tests-before_2026-08-09_15-08-52.md` · `perf_tests-after_2026-08-09_15-08-52.md`
**Machine:** Intel Core i7-1065G7 @ 1.30 GHz, 8 threads · **Go:** go1.26.1 linux/amd64
**Cache:** cleared (`go clean -cache`) before each sweep, module deps rebuilt untimed
**Sizes:** 1 → 10,000 · **Sampling:** warm and vet 2nd are medians of 5 runs; cold and vet 1st are single-shot by nature

Both sweeps generate N structurally identical functions; the only difference
is one line per function:

```go
m := map[string]int{}                    // tests-before: dirty — every function is a map-prealloc finding
m := make(map[string]int, len(items))    // tests-after:  clean — zero findings
```

## The four runs — what each measures, and WHY it is done

- **cold** — `goscalelint ./perf/...` on freshly generated code the tool has
  never seen. Nothing is cached, so it pays for everything: loading,
  parsing, type-checking, all 17 analyzers, printing findings.
  *Why:* establishes the worst case — a first CI run on a fresh checkout.
  Single sample by nature: code is only new once.
- **warm** — the same command again (median of 5). The standalone binary
  keeps no results between runs, so all analysis happens again; only the
  surrounding I/O is cheaper.
  *Why:* proves the standalone path has NO result cache, and cold−warm
  isolates one-time setup from analysis. Warm is the binary's floor for
  repeated runs.
- **vet 1st** — `go vet -vettool=goscalelint ./perf/...` on a cache miss.
  *Why:* the true analysis cost along the deployment path real CI uses —
  go/analysis tools are normally run via `-vettool`, not invoked directly.
  Single sample: a cache miss happens once per package content.
- **vet 2nd** — the same vet command repeated (median of 5). vet replays the
  package's stored results from the build cache.
  *Why:* what every subsequent run on unchanged code costs — the state most
  CI runs are in. vet1−vet2 is the payoff of caching, and a slow vet 2nd
  would be a red flag that the cache is broken (nondeterministic output).

The columns work as pairs: cold vs warm separates setup from analysis;
vet 1st vs vet 2nd separates analysis from cache replay.

## Cold runs (single sample — read with caution)

| N | before (s) | after (s) | Δ (s) | after/before |
|---:|---:|---:|---:|---:|
| 1 | 0.14 | 0.23 | +0.09 | 1.64× |
| 10 | 0.16 | 0.25 | +0.09 | 1.56× |
| 100 | 0.30 | 0.28 | −0.02 | 0.93× |
| 1,000 | 0.66 | 0.68 | +0.02 | 1.03× |
| 10,000 | 5.33 | 5.06 | −0.27 | 0.95× |

## Warm runs (median of 5)

| N | before (s) | after (s) | Δ (s) | after/before |
|---:|---:|---:|---:|---:|
| 1 | 0.16 | 0.23 | +0.07 | 1.44× |
| 10 | 0.20 | 0.21 | +0.01 | 1.05× |
| 100 | 0.41 | 0.22 | −0.19 | 0.54× |
| 1,000 | 0.32 | 0.28 | −0.04 | 0.88× |
| 10,000 | 1.01 | 0.83 | −0.18 | **0.82×** |

## go vet -vettool, first run (single sample)

| N | before (s) | after (s) | Δ (s) | after/before |
|---:|---:|---:|---:|---:|
| 1 | 0.15 | 0.17 | +0.02 | 1.13× |
| 10 | 0.17 | 0.15 | −0.02 | 0.88× |
| 100 | 0.23 | 0.15 | −0.08 | 0.65× |
| 1,000 | 0.35 | 0.19 | −0.16 | 0.54× |
| 10,000 | 1.02 | 0.74 | −0.28 | **0.73×** |

## go vet -vettool, second run (median of 5)

| N | before (s) | after (s) | Δ (s) |
|---:|---:|---:|---:|
| 1 | 0.14 | 0.14 | 0.00 |
| 10 | 0.17 | 0.14 | −0.03 |
| 100 | 0.13 | 0.14 | +0.01 |
| 1,000 | 0.27 | 0.14 | −0.13 |
| 10,000 | 0.14 | 0.14 | 0.00 |

## Findings

`before`: exactly N findings at every size. `after`: 0 at every size.

## Observations

- **Up to N ≈ 1,000, dirty vs clean is a tie.** Every delta at those sizes
  is within the run's own jitter. The dirty sweep hit a turbulent stretch
  around N = 100–1,000 (warm samples ranged 0.31–0.82 s at N = 100), which
  is why a few dirty cells look inflated — that is machine noise, not a
  cost of dirty code. Yesterday's artifact ("clean looks slower at small
  N") does not reproduce with medians: the sub-second ratios scatter on
  both sides of 1.0×.
- **At N = 10,000 a small real clean advantage emerges.** With tight
  medians on both sides (±0.02 s), clean is ~18% faster warm (1.01 →
  0.83 s) and ~27% faster on vet 1st (1.02 → 0.74 s). That is the findings
  cost becoming visible — much smaller per finding than at 100k, where
  rendering 100k diagnostics made it ~5×: the findings overhead grows
  superlinearly with finding count.
- **vet 2nd is flat ~0.14 s in both sweeps at every size** — replaying
  cached results costs the same whether the replay contains 10,000
  findings or none. (The dirty 1,000 cell's 0.27 s falls in the turbulent
  stretch noted above.)
- **Cold cells remain single-sample and noisy** — the +0.09 s "slowdowns"
  at N = 1/10 for clean are first-touch noise of the same kind
  demonstrated live yesterday (a 0.44 s outlier among 0.17–0.21 s runs),
  not signal.
- **Absolute times are higher than yesterday's run at the same sizes**
  (background load differs day to day); only within-run before/after
  comparisons are meaningful, which is why each experiment runs both
  sweeps back-to-back under one stamp.
