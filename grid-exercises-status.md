# Grid Exercises Verification Status

Date: 2026-08-11

This is a fresh verification-pass report for Ex1 through Ex6. It records
commands that completed during this pass and distinguishes a completed pass
from an interrupted or non-terminating command.

| Exercise | Status | Fresh evidence |
| --- | --- | --- |
| Ex1 Order Flow | Partial | `go test ./...` and `errcheck ./...` passed. The Docker multi-agent demo was started but manually interrupted before it produced a result. |
| Ex2 Grid Editor | Pass | `go vet ./...`, `go test ./...`, and `errcheck ./...` passed. Browser `npm test` and `npm run build` passed. |
| Ex3 Grid Editor WebSocket | Fail | `go test ./...` failed in `TestHeadlessBrowserRecoversFromBlankSnapshotState`: the test expects `browser sync: websocket`, while the rendered page reports `browser sync: polling · awareness: websocket · path: relay`. Browser `npm test`, browser build, and Neovim sidecar build passed. `errcheck ./...` was not reached because the Go test command stopped on that failure. |
| Ex4 Bug Tracker | Incomplete | `scripts/verify.sh` reached successful Go tests and printed `browser WebCrypto workflow: PASS`, but the combined Node/browser command did not exit and was manually stopped. Treat the complete gate as incomplete until the lifecycle issue is fixed. |
| Ex5 Operational Knowledge System | Pass | `go test ./...`, `go vet ./...`, and `errcheck ./...` passed. Chrome-only setup, launch, real handshake verification, and the attach-only Playwright suite passed all 15 interactions. Chromium remains explicitly deferred. |
| Ex6 Operational Knowledge Agent Runtime | Pass | `go test ./...`, `go vet ./...`, and `errcheck ./...` passed. Both opt-in proofs passed: Docker-confined procedure adapter E2E and two-node relay E2E. |

## PromiseGrid alignment observations

- Ex1 through Ex4 remain explicitly scoped as local-draft profiles; none claims
  frozen-upstream conformance.
- Ex5 states verified Chrome support and keeps Chromium explicitly deferred.
- Ex6 retains unknown-family bytes exactly and keeps semantic author evidence
  separate from relay-carriage signatures.

## Follow-up required for an all-green pass

1. Repair Ex3's stale headless-browser transport expectation, then rerun its
   Go gate and `errcheck ./...`.
2. Repair Ex4 verification-process cleanup, then rerun `bash scripts/verify.sh`
   until it exits zero.
3. Rerun Ex1's Docker multi-agent demo to a final result.
