# PromiseGrid Demo Cue Card

Use this when you want the absolute minimum live prompt sheet.

## 1. Seed demo repos

Type:

```bash
cd ~/lab/commitment-ledger
make demo-setup
```

Say:

This demo uses seeded synthetic repos, not real project data.

Point at:

- Alice, Bob, Dave, Mallory repo setup

## 2. Show source work

Type:

```bash
sed -n '1,40p' ~/lab/commitment-ledger-demo/alice-demo/TODO/TODO.md
sed -n '1,40p' ~/lab/commitment-ledger-demo/alice-demo/TODO/TODO-ravud-ship-welcome-flow.md
```

Say:

There is work here, but not yet a promise.

Point at:

- parent TODO
- subtasks

## 3. Scan

Type:

```bash
make demo-scan
```

Say:

This observes the repos and derives branch-qualified work items.

Point at:

- `alice-demo main`
- open work count

## 4. Show projection rows

Type:

```bash
grep 'TODO-ravud' data/work_items.jsonl
```

Say:

This is a projection over observed repo state, not the primary artifact.

Point at:

- `alice-demo/main/TODO-ravud`
- subtask rows

## 5. Create commitment

Type:

```bash
make commit COMMIT_ARGS='--promiser Alice --repo alice-demo --branch main --target alice-demo/main/TODO-ravud/1 --due 2026-07-01 --promise "I promise to complete TODO-ravud subtask 1."'
```

Say:

Now the work becomes a promise with both a local ID and an artifact CID.

Point at:

- `COMMITMENT-...`
- artifact CID

## 6. Show human projection

Type:

```bash
COMMITMENT_ID=$(tail -n 1 data/commitments.jsonl | sed -E 's/.*"commitment_id":"([^"]+)".*/\1/')
cat records/commitments/$COMMITMENT_ID.md
```

Say:

This record is a projection, but it still points back to exact artifact and protocol identity.

Point at:

- `Artifact CID`
- `Protocol pCID`

## 7. Show artifact index

Type:

```bash
grep "$COMMITMENT_ID" data/artifacts.jsonl
```

Say:

The operator layer stays anchored to the signed artifact and its protocol doc.

Point at:

- `artifact_cid`
- `protocol_pcid`
- `signer`

## 8. Inspect

Type:

```bash
go run ./cmd/commitment-ledger inspect --json "$COMMITMENT_ID"
```

Say:

`inspect` bridges local IDs, artifact CIDs, protocol docs, and projected state.

Point at:

- `protocol_pcid`
- signer
- status/details

## 9. Show frozen protocol doc

Type:

```bash
sed -n '1,80p' docs/protocols/commitment-promise-v1.md
```

Say:

Protocol meaning is owned by frozen docs by exact bytes.

Point at:

- versioned protocol doc

## 10. Do the work

Type:

```bash
python3 - <<'PY'
from pathlib import Path
path = Path.home() / "lab" / "commitment-ledger-demo" / "alice-demo" / "TODO" / "TODO-ravud-ship-welcome-flow.md"
text = path.read_text()
text = text.replace("- [ ] 1. Add route", "- [x] 1. Add route")
path.write_text(text)
PY
git -C ~/lab/commitment-ledger-demo/alice-demo add TODO/TODO-ravud-ship-welcome-flow.md
git -C ~/lab/commitment-ledger-demo/alice-demo -c user.name=Alice -c user.email=alice@example.com commit -m "Complete Alice subtask 1"
```

Say:

Evidence comes from observed repo state, not only from claims in the ledger repo.

Point at:

- checked subtask in source repo

## 11. Rescan for evidence

Type:

```bash
make demo-scan
grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl
```

Say:

The repo change becomes evidence, but still not final judgment.

Point at:

- `todo_checked`

## 12. Assess

Type:

```bash
EVIDENCE_ID=$(grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl | grep 'todo_checked' | tail -n 1 | sed -E 's/.*"evidence_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger assess --commitment "$COMMITMENT_ID" --assessor Alice --status kept --basis "$EVIDENCE_ID" --notes "Completed before the due date."
```

Say:

Assessment is explicit judgment over evidence.

Point at:

- assessment ID
- final status

## 13. Verify

Type:

```bash
ASSESSMENT_ID=$(tail -n 1 data/assessments.jsonl | sed -E 's/.*"assessment_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger verify --json "$ASSESSMENT_ID"
```

Say:

`verify` checks artifact bytes, signature, signer material, and protocol linkage.

Point at:

- `signature_verified`
- `local_protocol_match`
- `overall_trusted`

## 14. Conformance

Type:

```bash
sed -n '1,120p' CHANGELOG.md
```

Say:

Conformance is published against exact frozen doc CIDs.

Point at:

- conformance entries

## 15. Operator surface

Type:

```bash
go run ./cmd/commitment-ledger status --exchange --json
go run ./cmd/commitment-ledger doctor --repairable
```

Say:

The repo also has exchange, trust, and recovery tooling, not just promise recording.

Point at:

- exchange summary
- repairable findings

## Close

Say:

The core PromiseGrid shape here is frozen protocol docs, signed artifacts in CAS, projections as secondary views, and explicit operator tooling around them.
