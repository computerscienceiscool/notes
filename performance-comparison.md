# Controlled test performance comparison

This report compares the cache-disabled serial test baselines recorded on
2026-08-08 for the original repository and its lint-fixed sister copy.

- Original baseline: `../grid-examples/docs/test-performance.md`
- Fixed-copy baseline: `docs/test-performance.md`

Both copies ran the same declared test inventory: seven Go modules and two web
applications. The two Neovim sidecars remain outside the total because they
declare build commands but no test command.

## Method

Every Go suite ran as `go test -count=1 ./...`. The `-count=1` flag disables
Go's test-result cache, so the tests execute rather than returning a cached
success. Each web suite ran with its declared `npm test` command. The two
repositories were alternated per suite, rather than always running one first,
to reduce ordering bias. Durations are nanosecond-resolution wall-clock
measurements reported in whole milliseconds.

This is substantially more comparable than the earlier cached measurements.
It still represents one machine under real load, not a statistical benchmark
series, so small deltas should not be overinterpreted.

## Result

All tests passed in both copies.

| Program | Original | Fixed copy | Delta (fix - original) | Changed by lint patch? |
| --- | ---: | ---: | ---: | --- |
| `ex1-order-flow` | 6,475 ms | 6,484 ms | +9 ms | No |
| `ex2-grid-editor` | 1,811 ms | 1,861 ms | +50 ms | No |
| `ex3-grid-editor-websocket` | 4,411 ms | 4,380 ms | -31 ms | Yes |
| `ex4-bug-tracker` | 453 ms | 392 ms | -61 ms | No |
| `ex5-operational-knowledge-system` | 12,880 ms | 12,641 ms | -239 ms | Yes |
| `ex6-operational-knowledge-agent-runtime` | 8,021 ms | 2,641 ms | -5,380 ms | Yes |
| `ex7-makerspace-stewardship` | 394 ms | 383 ms | -11 ms | No |
| `ex2-grid-editor/web` | 314 ms | 319 ms | +5 ms | No |
| `ex3-grid-editor-websocket/web` | 513 ms | 685 ms | +172 ms | No |
| **Total** | **35,272 ms** | **29,786 ms** | **-5,486 ms** | — |

The fixed copy completed the full declared suite **5.486 seconds faster**,
which is a **15.6% reduction** from the original total.

## Scope of the lint patch

The patch contains 27 allocation-focused replacements, all within Ex3, Ex5,
and Ex6:

| Change type | Count | Purpose |
| --- | ---: | --- |
| `strings.Split` to `strings.SplitSeq` | 4 | Avoid a temporary split slice when tokens are consumed once. |
| Map capacity preallocation | 22 | Avoid incremental internal map growth when input size is known. |
| Slice capacity preallocation | 1 | Avoid growth and copying while appending a known-size result. |

The modified-module subtotal changed from **25.312 s** in the original copy to
**19.662 s** in the fixed copy: **5.650 s faster (22.3%)**. The untouched
modules and web suites were collectively 164 ms slower in this run, which is
normal run-to-run variation and does not weaken the modified-module result.

## Ex6 confirmation

Ex6 produced the dominant improvement. Because it was unexpectedly large, it
was immediately rerun with repository order reversed, still using
`go test -count=1 ./...`:

| Run order | Original Ex6 | Fixed Ex6 | Fixed-copy improvement |
| --- | ---: | ---: | ---: |
| Alternating full-suite run | 8,021 ms | 2,641 ms | 5,380 ms |
| Reverse-order confirmation | 6,855 ms | 2,185 ms | 4,670 ms |

The absolute duration varies, but both independent executions show a large
fixed-copy advantage. That makes a real Ex6 performance improvement likely;
it is not explained by Go's test-result cache or by always running the fixed
copy first.

## What changes had the biggest impact?

**Largest measured impact: the Ex6 patch group.** It accounts for **5.380 s**
of the **5.486 s** total improvement in the paired full-suite run. Ex5 is next
at **239 ms faster**, and Ex3 is **31 ms faster**.

The whole-module timing cannot isolate one line with certainty. Within Ex6,
the likely contributors are the allocation reductions in workflows and package
processing: preallocated receipt/operation maps, preallocated item-output
slices, manifest claim maps, and `SplitSeq` iteration for host and fact
parsing. The test-only CAS map preallocation cannot explain a multi-second
runtime change by itself.

To rank individual edits conclusively, add focused Go benchmarks around those
functions and compare repeated median results. But at the repository-test
level, the evidence is clear: the 27 lint fixes produced a substantial,
repeatable improvement centered in Ex6.
