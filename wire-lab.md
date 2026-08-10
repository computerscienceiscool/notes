# goscalelint results — wire-lab

- **Date:** 2026-08-09
- **Target:** `~/lab/wire-lab` (all 23 Go modules, `./...` each)
- **Linter:** goscalelint built from `~/lab/goscalelint` @ b010b74 (branch `new-features`), all analyzers enabled
- **Note:** 14 modules require Go ≥ 1.25; the local toolchain is 1.24.13 with `GOTOOLCHAIN=local`, so those were run with `GOTOOLCHAIN=auto`. All 23 modules scanned successfully.

## Summary

**112 findings across 15 modules.** 8 modules clean: `implementations/poc3`, `poc4`, `poc5`, `poc6-dag-cbor-interop`, `poc17-m4-lora-runtime`, `tools/mint-handle`, `tools/spec`, `tools/sweep-citations`.

| Rule | Count | Impact |
|---|---|---|
| integer-to-string | 34 | CPU, allocation |
| map-prealloc | 33 | allocation, CPU, memory |
| slice-prealloc | 17 | allocation, GC, CPU |
| time-after-loop | 9 | allocation, GC, memory |
| splitseq | 8 | allocation, GC, memory |
| unbounded-goroutines | 6 | concurrency, memory, CPU |
| fieldsseq | 3 | allocation, GC, memory |
| http-timeout | 2 | reliability, concurrency, network |

### Highest-impact findings

- **http-timeout (2)** — `tools/ga-runner/openai.go:133` and `tools/ga-runner/provider_factory.go:58` build `http.Client` literals with no `Timeout`; requests can hang forever on a dead peer.
- **unbounded-goroutines (6)** — every pocN-supervisor (poc11–poc16) spawns one goroutine per element of `container.Agents` with no concurrency bound. Fine if agent counts stay small; worth a semaphore/errgroup if they can grow.
- **time-after-loop (9)** — `time.After` inside loops in the eventstream dial-retry loops (poc14/15/16/18) and kernel wait loops (poc15/16); each iteration allocates a timer + channel.

The rest (integer-to-string, map/slice-prealloc, splitseq/fieldsseq) are per-call allocation micro-optimizations; many are copies of the same code inherited across poc generations (e.g. `decision.go` `fmt.Sprintf("%d", observation.Turn)` appears in 6 pocs, `agent_cas.go` findings duplicated in poc15/poc16).

## Findings by module

Paths are relative to the module root; line numbers link to the flagged statement.

### `implementations/poc10-llm-autonomous-agents` — 1 finding

- `decision/decision.go:136` **integer-to-string** → `strconv.Itoa(observation.Turn)`

### `implementations/poc11-adaptive-trust-tcp` — 2 findings

- `cmd/poc11-supervisor/main.go:51` **unbounded-goroutines** → `bounding the concurrency when the collection can be large`
- `decision/decision.go:152` **integer-to-string** → `strconv.Itoa(observation.Turn)`

### `implementations/poc12-production-progress` — 2 findings

- `cmd/poc12-supervisor/main.go:71` **unbounded-goroutines** → `bounding the concurrency when the collection can be large`
- `decision/decision.go:153` **integer-to-string** → `strconv.Itoa(observation.Turn)`

### `implementations/poc13-cas-compute-functions` — 3 findings

- `cmd/poc13-supervisor/main.go:75` **unbounded-goroutines** → `bounding the concurrency when the collection can be large`
- `decision/decision.go:153` **integer-to-string** → `strconv.Itoa(observation.Turn)`
- `production/workflow.go:297` **splitseq** → `for rawValue := range strings.SplitSeq(rawValues, ",")`

### `implementations/poc14-wasm` — 5 findings

- `cmd/poc14-supervisor/main.go:88` **unbounded-goroutines** → `bounding the concurrency when the collection can be large`
- `decision/decision.go:154` **integer-to-string** → `strconv.Itoa(observation.Turn)`
- `eventstream/eventstream.go:58` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`
- `production/workflow.go:306` **splitseq** → `for rawValue := range strings.SplitSeq(rawValues, ",")`
- `runtime/node.go:2141` **integer-to-string** → `strconv.Itoa(n)`

### `implementations/poc15-multihop-multiarity-dag` — 15 findings

- `cmd/poc15-analyze/main.go:926` **fieldsseq** → `for token := range strings.FieldsSeq(detail)`
- `cmd/poc15-supervisor/main.go:90` **unbounded-goroutines** → `bounding the concurrency when the collection can be large`
- `decision/decision.go:154` **integer-to-string** → `strconv.Itoa(observation.Turn)`
- `eventstream/eventstream.go:80` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`
- `kernel/kernel.go:349` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`
- `kernel/kernel.go:420` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`
- `kernel/kernel.go:630` **map-prealloc** → `receiverSessions := make(map[*transport.PersistentSession]string, len(kernel.receivers))`
- `production/workflow.go:309` **splitseq** → `for rawValue := range strings.SplitSeq(rawValues, ",")`
- `runtime/agent_cas.go:180` **integer-to-string** → `strconv.Itoa(len(objectBytes))`
- `runtime/agent_cas.go:255` **integer-to-string** → `strconv.Itoa(len(cleanParents))`
- `runtime/agent_cas.go:260` **integer-to-string** → `strconv.Itoa(len(cleanParents))`
- `runtime/agent_cas.go:292` **integer-to-string** → `strconv.Itoa(retainedCount)`
- `runtime/agent_cas.go:292` **integer-to-string** → `strconv.Itoa(totalAfter)`
- `runtime/node.go:2427` **integer-to-string** → `strconv.Itoa(n)`
- `runtime/node_test.go:640` **map-prealloc** → `agentsByProfile := make(map[string]*Node, len(cfg.Agents))`

### `implementations/poc16-secure-tokens-maps-encrypted-payloads` — 16 findings

- `cmd/poc16-analyze/main.go:1204` **fieldsseq** → `for token := range strings.FieldsSeq(detail)`
- `cmd/poc16-analyze/main.go:1653` **fieldsseq** → `for word := range strings.FieldsSeq(text)`
- `cmd/poc16-supervisor/main.go:156` **unbounded-goroutines** → `bounding the concurrency when the collection can be large`
- `decision/decision.go:168` **integer-to-string** → `strconv.Itoa(observation.Turn)`
- `eventstream/eventstream.go:104` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`
- `kernel/kernel.go:437` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`
- `kernel/kernel.go:508` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`
- `production/workflow.go:306` **splitseq** → `for rawValue := range strings.SplitSeq(rawValues, ",")`
- `runtime/agent_cas.go:179` **integer-to-string** → `strconv.Itoa(len(objectBytes))`
- `runtime/agent_cas.go:254` **integer-to-string** → `strconv.Itoa(len(cleanParents))`
- `runtime/agent_cas.go:259` **integer-to-string** → `strconv.Itoa(len(cleanParents))`
- `runtime/agent_cas.go:291` **integer-to-string** → `strconv.Itoa(retainedCount)`
- `runtime/agent_cas.go:291` **integer-to-string** → `strconv.Itoa(totalAfter)`
- `runtime/node.go:2455` **integer-to-string** → `strconv.Itoa(n)`
- `runtime/node_test.go:640` **map-prealloc** → `agentsByProfile := make(map[string]*Node, len(cfg.Agents))`
- `runtime/poc16_profiles.go:66` **integer-to-string** → `strconv.Itoa(len(context.Excerpt))`

### `implementations/poc18-cas-git-replacement` — 9 findings

- `agent/agent.go:1018` **map-prealloc** → `kinds := make(map[string]string, len(blocks))`
- `cmd/poc-analyze/main.go:1082` **map-prealloc** → `present := make(map[string]bool, len(messages))`
- `cmd/poc-analyze/main.go:1100` **map-prealloc** → `directions := make(map[string]bool, len(messages))`
- `cmd/poc-analyze/main.go:1113` **map-prealloc** → `messageCIDSet := make(map[string]bool, len(messages))`
- `cmd/poc-analyze/main.go:1202` **map-prealloc** → `promiseKinds := make(map[string]bool, len(messages))`
- `eventstream/eventstream.go:86` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`
- `graph/graph.go:618` **map-prealloc** → `rendered := make(map[string]any, len(typed))`
- `repo/state.go:204` **splitseq** → `for segment := range strings.SplitSeq(slashPath, "/")`
- `repo/state.go:232` **map-prealloc** → `seen := make(map[string]bool, len(paths))`

### `implementations/poc2` — 1 finding

- `integration_test.go:70` **time-after-loop** → `creating a time.Timer or time.Ticker once before the loop and reusing it (resetting it as needed)`

### `implementations/poc7-capability-token-exchange` — 8 findings

- `cmd/poc7-node/main.go:340` **integer-to-string** → `strconv.Itoa(n)`
- `cmd/poc7-node/main.go:364` **integer-to-string** → `strconv.Itoa(offer.OfferedCount)`
- `cmd/poc7-node/main.go:365` **integer-to-string** → `strconv.Itoa(offer.WantedCount)`
- `cmd/poc7-node/main.go:390` **integer-to-string** → `strconv.Itoa(quote.OfferedCount)`
- `cmd/poc7-node/main.go:391` **integer-to-string** → `strconv.Itoa(quote.OfferedCount)`
- `cmd/poc7-node/main.go:391` **integer-to-string** → `strconv.Itoa(quote.WantedCount)`
- `cmd/poc7-node/main.go:792` **map-prealloc** → `copiedPayload := make(map[string]string, len(payload))`
- `cmd/poc7-node/main.go:818` **map-prealloc** → `fields := make(map[string]string, len(payload))`

### `implementations/poc8-autonomous-promise-economy` — 5 findings

- `cmd/poc8-node/main.go:597` **integer-to-string** → `strconv.Itoa(quote.OfferedCount)`
- `cmd/poc8-node/main.go:597` **integer-to-string** → `strconv.Itoa(quote.WantedCount)`
- `cmd/poc8-node/main.go:785` **integer-to-string** → `strconv.Itoa(inputNumber)`
- `cmd/poc8-node/main.go:824` **map-prealloc** → `fields := make(map[string]string, len(payload))`
- `cmd/poc8-node/main.go:955` **map-prealloc** → `copiedPayload := make(map[string]string, len(payload))`

### `implementations/poc9-peer-discovery-strategy` — 3 findings

- `cmd/poc9-node/main.go:251` **map-prealloc** → `adjacency := make(map[string][]string, len(allNodeNames))`
- `cmd/poc9-node/main.go:980` **map-prealloc** → `fields := make(map[string]string, len(payload))`
- `cmd/poc9-node/main.go:1327` **map-prealloc** → `copiedPayload := make(map[string]string, len(payload))`

### `tools/ga-runner` — 32 findings

- `compare.go:306` **slice-prealloc** → `summaries := make([]backfillComparisonSimSummary, 0, len(aggregates))`
- `ga_runner_test.go:689` **map-prealloc** → `parentIDs := make(map[string]bool, len(state.Parents))`
- `ga_runner_test.go:2857` **integer-to-string** → `strconv.Itoa(parentCount)`
- `ga_runner_test.go:2858` **integer-to-string** → `strconv.Itoa(scenarioCount)`
- `ga_runner_test.go:2859` **integer-to-string** → `strconv.Itoa(childCount)`
- `ga_runner_test.go:2880` **map-prealloc** → `parentIDs := make(map[string]bool, len(state.Parents))`
- `ga_runner_test.go:2926` **map-prealloc** → `parentIDs := make(map[string]bool, len(state.Parents))`
- `ga_runner_test.go:2955` **slice-prealloc** → `paths := make([]string, 0, len(scenarioIDs))`
- `ga_runner_test.go:3102` **slice-prealloc** → `ids := make([]string, 0, len(parents))`
- `ga_runner_test.go:3110` **slice-prealloc** → `ids := make([]string, 0, len(scenarios))`
- `generate.go:448` **map-prealloc** → `parentByID := make(map[string]GAStateParent, len(state.Parents))`
- `generate.go:468` **slice-prealloc** → `ids := make([]string, 0, len(ranked))`
- `generate.go:476` **map-prealloc** → `parentOriginalIndex := make(map[string]int, len(state.Parents))`
- `generate.go:523` **map-prealloc** → `scoreByID := make(map[string]parentFitnessRank, len(ranked))`
- `generate.go:555` **integer-to-string** → `strconv.Itoa(selectionIndex)`
- `generate.go:660` **map-prealloc** → `selected := make(map[string]bool, len(options.ChildIDs))`
- `openai.go:133` **http-timeout** → `setting Timeout (or otherwise bounding requests, for example with per-request contexts)`
- `planning.go:166` **map-prealloc** → `byID := make(map[string]PopulationSim, len(population))`
- `planning.go:223` **map-prealloc** → `byID := make(map[string]T, len(items))`
- `population.go:158` **slice-prealloc** → `population := make([]GAStateSim, 0, len(plan.Population))`
- `population.go:336` **slice-prealloc** → `simIDs := make([]string, 0, len(bySim))`
- `population.go:536` **slice-prealloc** → `statePopulation := make([]GAStateSim, 0, len(population))`
- `population.go:544` **map-prealloc** → `hardHit := make(map[string]bool, len(selection.HardHitSimIDs))`
- `population.go:548` **map-prealloc** → `cleanEnvelope := make(map[string]bool, len(selection.CleanEnvelopeSimIDs))`
- `population.go:606` **slice-prealloc** → `scenarioIDs := make([]string, 0, len(scenarioByID))`
- `population.go:611` **slice-prealloc** → `scenarios := make([]GAStateScenario, 0, len(scenarioIDs))`
- `population.go:615` **slice-prealloc** → `parentIDs := make([]string, 0, len(parentCounts))`
- `provider_factory.go:58` **http-timeout** → `setting Timeout (or otherwise bounding requests, for example with per-request contexts)`
- `score.go:395` **map-prealloc** → `parentIDs := make(map[string]bool, len(state.Parents))`
- `validate.go:718` **map-prealloc** → `rootContracts := make(map[string]bool, len(result.Source.RootContractPaths))`
- `validate.go:907` **map-prealloc** → `summaries := make(map[string]auditSummary, len(aggregates))`
- `validate.go:1004` **slice-prealloc** → `deduped := make([]auditRecord, 0, len(byPair))`

### `tools/matrix-runner` — 9 findings

- `compare.go:154` **slice-prealloc** → `timestamps := make([]string, 0, len(byTimestamp))`
- `compare.go:243` **slice-prealloc** → `scenarios := make([]string, 0, len(oldScenarios))`
- `compare.go:268` **slice-prealloc** → `ranked := make([]rankItem, 0, len(grouped))`
- `compare.go:283` **map-prealloc** → `avgs := make(map[string]float64, len(items))`
- `compare.go:296` **map-prealloc** → `out := make(map[string]float64, len(grouped))`
- `compare.go:312` **slice-prealloc** → `timestamps := make([]string, 0, len(cells))`
- `main.go:90` **splitseq** → `for part := range strings.SplitSeq(value, ",")`
- `state.go:139` **slice-prealloc** → `statuses := make([]string, 0, len(counts))`
- `validate.go:220` **splitseq** → `for line := range strings.SplitSeq(string(bytes), "\n")`

### `tools/migrate-handles` — 1 finding

- `main.go:301` **splitseq** → `for line := range strings.SplitSeq(string(data), "\n")`
