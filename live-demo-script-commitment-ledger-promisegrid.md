# Live Demo Script (PromiseGrid Audience)

Use this as a live terminal walkthrough for the PromiseGrid team.

## Intro

Type:

```bash
cd ~/lab/commitment-ledger
```

Say:

This repo is a local-first PromiseGrid app prototype. The point is not only to
track TODO work, but to show a PromiseGrid-shaped separation between:

- source work in ordinary repos
- commitments made against that work
- evidence about what happened
- later explicit assessment

And underneath that, the implementation is trying to follow the PromiseGrid
discipline of:

- frozen protocol docs by exact bytes
- explicit protocol `pCID`s
- signed grid-envelope artifacts
- local CAS retention by CID
- projections as secondary views over artifact history

This demo uses seeded synthetic repos, not real team data.

## 1. Seed the synthetic demo repos

Type:

```bash
make demo-setup
```

Say:

This creates four synthetic repos for Alice, Bob, Dave, and Mallory plus the
demo config. I am intentionally not using real project information during the
demo.

## 2. Show the source work

Type:

```bash
sed -n '1,40p' ~/lab/commitment-ledger-demo/alice-demo/TODO/TODO.md
sed -n '1,40p' ~/lab/commitment-ledger-demo/alice-demo/TODO/TODO-ravud-ship-welcome-flow.md
```

Say:

This is just ordinary TODO-driven repo state. There is work here, but there is
not yet a promise.

That distinction matters. A task board is not the same thing as a commitment
ledger.

## 3. Scan the seeded repos

Type:

```bash
make demo-scan
```

Say:

Now the ledger observes the seeded repos and turns them into branch-qualified
work items. This is still just observation.

## 4. Show branch-qualified projection state

Type:

```bash
grep 'TODO-ravud' data/work_items.jsonl
```

Say:

This is the projection layer. The repo files became machine-readable work rows,
including the parent TODO and the subtasks.

The important PromiseGrid-adjacent point is that this projection is not the
primary artifact contract. It is an operator view over locally observed state.

## 5. Create a commitment

Type:

```bash
make commit COMMIT_ARGS='--promiser Alice --repo alice-demo --branch main --target alice-demo/main/TODO-ravud/1 --due 2026-07-01 --promise "I promise to complete TODO-ravud subtask 1."'
```

Say:

Now the work becomes a promise.

The command returns:

- a local commitment ID for operator workflow
- a CID for the emitted artifact bytes

That is the beginning of the distinction between local handles and
content-addressed protocol artifacts.

## 6. Show the human projection

Type:

```bash
COMMITMENT_ID=$(tail -n 1 data/commitments.jsonl | sed -E 's/.*"commitment_id":"([^"]+)".*/\1/')
cat records/commitments/$COMMITMENT_ID.md
```

Say:

This Markdown record is a projection. It is useful for humans, but it is not
the primary protocol object.

Notice that it still carries:

- the artifact CID
- the protocol `pCID`

So even the human-readable view points back to exact bytes and exact protocol
identity.

## 7. Show the artifact index

Type:

```bash
grep "$COMMITMENT_ID" data/artifacts.jsonl
```

Say:

This is another projection, but now over raw artifact storage.

It records:

- `artifact_cid`
- `protocol_pcid`
- signer identity
- payload and proof CIDs
- related local ID

Again, the key design point is that projection rows are not pretending to be
the artifact itself.

## 8. Inspect the commitment as an operator view

Type:

```bash
go run ./cmd/commitment-ledger inspect --json "$COMMITMENT_ID"
```

Say:

`inspect` is the practical operator bridge between local IDs, artifact CIDs,
protocol docs, signer material, and current projected state.

For a PromiseGrid audience, this is the “how do I actually navigate this local
ledger?” layer.

## 9. Show the frozen protocol doc path

Type:

```bash
sed -n '1,80p' docs/protocols/commitment-promise-v1.md
```

Say:

This repo’s current stance is that protocol meaning is owned by frozen local
docs by exact bytes.

That is intentionally stronger than “the branch says this is the protocol.”

## 10. Do the work in the synthetic source repo

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

Now the source repo changed. This is important because the evidence comes from
observed repo state, not only from statements inside the ledger repo.

## 11. Rescan to derive evidence

Type:

```bash
make demo-scan
grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl
```

Say:

The scan now emits evidence. That is still not final judgment.

The separation is:

- observation
- then explicit assessment

not “checkbox changed, therefore universal verdict.”

## 12. Assess as kept

Type:

```bash
EVIDENCE_ID=$(grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl | grep 'todo_checked' | tail -n 1 | sed -E 's/.*"evidence_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger assess --commitment "$COMMITMENT_ID" --assessor Alice --status kept --basis "$EVIDENCE_ID" --notes "Completed before the due date."
```

Say:

Assessment is explicit local judgment over evidence.

This repo is deliberately not collapsing evidence and assessment into the same
thing.

## 13. Verify the final artifact

Type:

```bash
ASSESSMENT_ID=$(tail -n 1 data/assessments.jsonl | sed -E 's/.*"assessment_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger verify --json "$ASSESSMENT_ID"
```

Say:

`verify` is the local structural and cryptographic check.

It verifies:

- CAS bytes exist
- envelope, payload, and proof CIDs line up
- signature verifies
- signer identity material matches
- protocol `pCID` matches a local frozen doc

That is not social trust, but it is a coherent local integrity story.

## 14. Show conformance publication

Type:

```bash
sed -n '1,120p' CHANGELOG.md
```

Say:

This is the repo-level conformance publication surface.

The implementation currently publishes conformance in two ways:

- signed conformance artifacts
- human-facing `CHANGELOG.md` entries naming exact frozen doc CIDs

That is the shape the PromiseGrid dev guide has been pointing app developers
toward.

## 15. Show operator and exchange surface

Type:

```bash
go run ./cmd/commitment-ledger status --exchange --json
go run ./cmd/commitment-ledger doctor --repairable
```

Say:

Beyond the lifecycle itself, the repo now has the operator surface needed for:

- import/export/send/receive
- receipts and provenance
- trust-policy checks
- repairability and signer-history handling

In a fresh happy-path demo the exchange summary may be sparse, but the point is
that the implementation is no longer only a promise recorder. It has started
to grow the surrounding operator discipline too.

## 16. Close

Say:

So the repo is trying to be PromiseGrid-shaped in four specific ways:

1. protocol docs and `pCID`s own contract meaning
2. signed artifacts in local CAS are the primary records
3. JSONL and Markdown remain projections over artifact history
4. operators get explicit tooling for conformance, verification, exchange, and
   recovery

It is still local-first and still provisional, but the artifact and protocol
discipline are now much closer to the direction the PromiseGrid guide calls
for.
