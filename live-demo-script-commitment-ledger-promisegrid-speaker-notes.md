# Live Demo Script (PromiseGrid Audience, Speaker Notes)

Use this version when you want a smoother presentation voice and lighter
command framing while still driving the terminal live.

## Opening framing

Type:

```bash
cd ~/lab/commitment-ledger
```

Say:

What I want to show here is not just a TODO tool.

This repo is trying to act like a local-first PromiseGrid app prototype. The
important separation is between:

- work in ordinary repos
- commitments made against that work
- evidence about what happened
- later explicit assessment

And underneath that, the implementation is trying to respect a PromiseGrid
discipline:

- frozen protocol docs by exact bytes
- protocol identity by `pCID`
- signed artifacts as the primary records
- local CAS retention by CID
- projections as secondary operator views

Also, for this demo I am not using real team or project data. Everything here
is staged from seeded synthetic repos.

## 1. Seed the synthetic repos

Type:

```bash
make demo-setup
```

Say:

This creates the Alice, Bob, Dave, and Mallory repos plus the demo config.

I want the audience to see a realistic workflow shape, but I do not want the
demo to depend on live internal repo state.

## 2. Show the source work

Type:

```bash
sed -n '1,40p' ~/lab/commitment-ledger-demo/alice-demo/TODO/TODO.md
sed -n '1,40p' ~/lab/commitment-ledger-demo/alice-demo/TODO/TODO-ravud-ship-welcome-flow.md
```

Say:

At this point there is only work.

That is a useful distinction for PromiseGrid thinking: a task list is not yet a
commitment ledger. It is just available work in a repo.

## 3. Observe the repos

Type:

```bash
make demo-scan
```

Say:

Now the ledger observes the seeded repos and discovers branch-qualified work
items.

This is still observation. We have not created a promise yet.

## 4. Show the projection layer

Type:

```bash
grep 'TODO-ravud' data/work_items.jsonl
```

Say:

This is the first projection layer: local machine-readable rows derived from
repo files.

For this audience, the important thing is not the JSON itself. The important
thing is that this is a projection over observed state, not yet the primary
artifact contract.

## 5. Create a commitment

Type:

```bash
make commit COMMIT_ARGS='--promiser Alice --repo alice-demo --branch main --target alice-demo/main/TODO-ravud/1 --due 2026-07-01 --promise "I promise to complete TODO-ravud subtask 1."'
```

Say:

Now we have moved from work to promise.

The command returns two identities:

- a local commitment ID for operator workflow
- a CID for the signed emitted artifact

That difference between local handles and content-addressed artifact identity is
one of the central ideas here.

## 6. Show the human-readable projection

Type:

```bash
COMMITMENT_ID=$(tail -n 1 data/commitments.jsonl | sed -E 's/.*"commitment_id":"([^"]+)".*/\1/')
cat records/commitments/$COMMITMENT_ID.md
```

Say:

This Markdown record is not pretending to be the protocol artifact.

It is a projection for humans, but it still carries the artifact CID and the
protocol `pCID`, so it points back to exact bytes and exact protocol identity.

## 7. Show the artifact index

Type:

```bash
grep "$COMMITMENT_ID" data/artifacts.jsonl
```

Say:

This is another projection, but now over raw artifact storage.

What matters here is that the repo keeps a visible relationship between:

- artifact CID
- protocol `pCID`
- signer
- payload CID
- proof CID

So the operator layer stays anchored to the actual emitted object.

## 8. Use the operator lookup view

Type:

```bash
go run ./cmd/commitment-ledger inspect --json "$COMMITMENT_ID"
```

Say:

`inspect` is the practical bridge between the local operator world and the
artifact world.

It resolves the local ID back to protocol docs, signer material, artifact
identity, and current projected state.

## 9. Show the frozen protocol doc

Type:

```bash
sed -n '1,80p' docs/protocols/commitment-promise-v1.md
```

Say:

This is where the repo is trying to follow the PromiseGrid line most clearly:
protocol meaning is owned by frozen local docs by exact bytes.

Not by a mutable branch path, and not by loose human convention.

## 10. Change the source repo

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

Now the source repo changes.

That matters because evidence should come from observed repo state, not only
from claims written directly into the ledger repo.

## 11. Rescan for evidence

Type:

```bash
make demo-scan
grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl
```

Say:

The ledger now derives evidence from the observed repo change.

But evidence is still not assessment. That separation is deliberate.

## 12. Assess explicitly

Type:

```bash
EVIDENCE_ID=$(grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl | grep 'todo_checked' | tail -n 1 | sed -E 's/.*"evidence_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger assess --commitment "$COMMITMENT_ID" --assessor Alice --status kept --basis "$EVIDENCE_ID" --notes "Completed before the due date."
```

Say:

Now we move from evidence to explicit judgment.

That is another important design choice: observable state changes are not being
treated as automatic universal verdicts.

## 13. Verify the resulting artifact

Type:

```bash
ASSESSMENT_ID=$(tail -n 1 data/assessments.jsonl | sed -E 's/.*"assessment_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger verify --json "$ASSESSMENT_ID"
```

Say:

`verify` is the local integrity check.

It verifies:

- stored bytes
- envelope and CID linkage
- signature correctness
- signer identity resolution
- protocol `pCID` match against local frozen docs

That is not shared governance or social trust. But it is a coherent local
artifact-integrity story.

## 14. Show conformance publication

Type:

```bash
sed -n '1,120p' CHANGELOG.md
```

Say:

This is the human-facing conformance publication surface.

So the implementation now has both:

- signed conformance artifacts
- repo-level changelog publication naming exact frozen doc CIDs

That is much closer to the app-developer shape the PromiseGrid guide has been
calling for.

## 15. Show the surrounding operator surface

Type:

```bash
go run ./cmd/commitment-ledger status --exchange --json
go run ./cmd/commitment-ledger doctor --repairable
```

Say:

The repo has also grown the surrounding operator discipline:

- exchange summaries
- provenance
- verification
- trust-policy checks
- repairability hints
- signer-history handling

So this is no longer just a promise recorder. It is starting to become an
operator-facing local artifact system.

## Closing summary

Say:

So the claim here is not that this is a finished upstream PromiseGrid app
contract.

The claim is narrower:

1. protocol docs and `pCID`s are being treated as the contract boundary
2. signed artifacts in CAS are the primary records
3. projections are kept secondary and explicit
4. conformance, verification, exchange, and recovery are all becoming part of
   the operator model

It is still local-first and provisional, but it is much closer to a coherent
PromiseGrid-shaped app than a normal task CLI.
