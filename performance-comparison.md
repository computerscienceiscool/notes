# Test performance comparison

This report compares the warm-cache, serial test baselines recorded on
2026-08-08 for the original repository and its lint-fixed sister copy.

- Original baseline: `../grid-examples/docs/test-performance.md`
- Fixed-copy baseline: `docs/test-performance.md`

Both reports use the same declared test-command inventory: seven Go modules
and two web applications. The two Neovim sidecars remain outside the total
because they declare build commands but no test command.

## Executive summary

All nine suites passed in both copies. The original run took **3.218 seconds**;
the fixed-copy run took **11.719 seconds**, a difference of **+8.501 seconds**
(+264%). That is not evidence that the lint fixes made the repository slower:
the two largest increases, **Ex1 (+6.247 s)** and **Ex2 (+1.627 s)**, are in
modules that the lint patch did not touch.

For the three modified modules only, the original total was **1.274 seconds**
and the fixed-copy total was **1.321 seconds**: **+47 ms**. A single
warm-cache wall-clock sample is not precise enough to attribute a 47 ms change
to these allocation-level edits. The available data demonstrates that the
fixed copy remains correct; it does not demonstrate a whole-suite speedup or
slowdown caused by the fixes.

## Per-suite results

| Program | Original | Fixed copy | Delta | Modified by lint patch? |
| --- | ---: | ---: | ---: | --- |
| `ex1-order-flow` | 293 ms | 6,540 ms | +6,247 ms | No |
| `ex2-grid-editor` | 319 ms | 1,946 ms | +1,627 ms | No |
| `ex3-grid-editor-websocket` | 353 ms | 347 ms | -6 ms | Yes |
| `ex4-bug-tracker` | 244 ms | 539 ms | +295 ms | No |
| `ex5-operational-knowledge-system` | 431 ms | 483 ms | +52 ms | Yes |
| `ex6-operational-knowledge-agent-runtime` | 490 ms | 491 ms | +1 ms | Yes |
| `ex7-makerspace-stewardship` | 255 ms | 533 ms | +278 ms | No |
| `ex2-grid-editor/web` | 346 ms | 339 ms | -7 ms | No |
| `ex3-grid-editor-websocket/web` | 467 ms | 481 ms | +14 ms | No |
| **Total** | **3,218 ms** | **11,719 ms** | **+8,501 ms** | — |

The individual suite durations sum to 3,198 ms in the original run and
11,699 ms in the fixed-copy run. Each report's additional 20 ms is the
separately measured loop and command overhead, so the total delta reconciles
exactly with the per-suite deltas.

## What changed in the fixed copy

The lint patch contains 27 mechanical allocation-focused replacements across
Ex3, Ex5, and Ex6. It does not change protocol behavior, test behavior, or
the test inventory.

| Change type | Count | Purpose |
| --- | ---: | --- |
| `strings.Split` to `strings.SplitSeq` | 4 | Avoid materializing a split slice when each token is consumed once. |
| Map capacity preallocation | 22 | Allocate maps with the known input size to avoid incremental map growth. |
| Slice capacity preallocation | 1 | Allocate the result slice with the known state length before appending. |

The changes occur only in `ex3-grid-editor-websocket`,
`ex5-operational-knowledge-system`, and
`ex6-operational-knowledge-agent-runtime`. Therefore they cannot explain the
large Ex1, Ex2, Ex4, or Ex7 timing differences.

## Limits of this comparison

These are single serial warm-cache samples, taken fourteen minutes apart while
other development work was occurring. They are useful for observing the
developer-feedback cost at those moments, but they are not a controlled
microbenchmark. Wall-clock test duration can vary with CPU scheduling,
background browser activity, filesystem state, Go test-cache state, and the
particular browser-oriented test timing.

To measure a causal performance effect, benchmark the affected operations
directly with Go benchmarks, run repeated samples under the same machine load,
and compare medians (and variation) rather than comparing one whole-repository
test pass from each checkout.

## What changes had the biggest impact?

**Measured impact:** none of the 27 changes has a demonstrated meaningful
whole-test-suite impact in these two samples. Among modified modules, Ex3 was
6 ms faster, Ex5 was 52 ms slower, and Ex6 was 1 ms slower; those differences
are too small and too confounded to rank causally.

**Most likely allocation impact:** the 15 map-capacity preallocations in
`ex5-operational-knowledge-system/promisegrid/records/helpers.go` are the
strongest candidate, because that file builds multiple indexes over complete
record collections and therefore avoids repeated internal map growth whenever
those helpers run on nontrivial inputs. The four `SplitSeq` substitutions are
also direct allocation reductions, but their inputs are short header, host, or
fact strings, so their absolute effect is expected to be smaller. This is a
reasoned expectation from the code shape, not a result proven by the two
whole-suite timings above.
