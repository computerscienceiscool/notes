# Live Demo Script

Use this as a live terminal walkthrough by main feature.

## Intro

Type:

```bash
cd ~/lab/commitment-ledger
```

Say:

This tool is a local-first PromiseGrid app prototype for tracking commitments
against TODO work in Git repos. The main flow is `scan`, `commit`, `evidence`,
and `assess`, with `inspect`, `verify`, `status`, `report`, and `reconcile`
covering operator lookup, integrity checking, exchange, and audit.

Important demo note:

This walkthrough uses seeded synthetic repos for Alice, Bob, Dave, and
Mallory. It does not require real team or project data.

## 1. Seed the demo repos

Type:

```bash
make demo-setup
```

Say:

This creates four synthetic local repos and writes `config/repos.demo.json`.
The demo starts from ordinary-looking TODO repos, but the data is staged for
presentation rather than pulled from real project work.

## 2. Scan available work

Type:

```bash
make demo-scan
```

Say:

This observes the seeded repos and turns their TODO files into branch-qualified
work items. At this point there is only work, not promises.

## 3. Show discovered work

Type:

```bash
grep 'TODO-ravud' data/work_items.jsonl
```

Say:

This is the projection layer. The tool has turned repo files into machine-readable
work items, including the parent TODO and its subtasks.

## 4. Create a commitment

Type:

```bash
make commit COMMIT_ARGS='--promiser Alice --repo alice-demo --branch main --target alice-demo/main/TODO-ravud/1 --due 2026-07-01 --promise "I promise to complete TODO-ravud subtask 1."'
```

Say:

Now the work becomes a promise. The command returns a local commitment ID and a
content-addressed artifact CID, so we get both an operator handle and exact
artifact identity.

## 5. Inspect the commitment

Type:

```bash
COMMITMENT_ID=$(tail -n 1 data/commitments.jsonl | sed -E 's/.*"commitment_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger inspect --json "$COMMITMENT_ID"
```

Say:

`inspect` is the operator lookup view. It resolves the local record, artifact
CID, protocol doc, signer, and current projected state in one place.

## 6. Show the human projection

Type:

```bash
cat records/commitments/$COMMITMENT_ID.md
```

Say:

The Markdown record is a projection, not the primary artifact. It is still
useful because it keeps the artifact CID and protocol pCID visible to humans.

## 7. Do the promised work

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

Now Alice changes the seeded source repo itself. The key point is that evidence
lives in the work repo, not only inside the ledger repo.

## 8. Rescan for evidence

Type:

```bash
make demo-scan
grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl
```

Say:

The second scan sees the promised subtask is now checked and records evidence.
Evidence is observation, not yet judgment.

## 9. Assess the commitment

Type:

```bash
EVIDENCE_ID=$(grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl | grep 'todo_checked' | tail -n 1 | sed -E 's/.*"evidence_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger assess --commitment "$COMMITMENT_ID" --assessor Alice --status kept --basis "$EVIDENCE_ID" --notes "Completed before the due date."
```

Say:

This turns evidence into explicit assessment. The system keeps observation and
judgment separate on purpose.

## 10. Verify the assessment artifact

Type:

```bash
ASSESSMENT_ID=$(tail -n 1 data/assessments.jsonl | sed -E 's/.*"assessment_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger verify --json "$ASSESSMENT_ID"
```

Say:

`verify` checks local CAS bytes, signature integrity, protocol linkage, signer
material, and local trust-policy interpretation. It proves structural and
cryptographic consistency, not moral truth.

## 11. Show summary views

Type:

```bash
make status
make demo-report REPORT_ARGS='--promiser Alice'
```

Say:

`status` is the repo-level summary and `report` is the filtered human-facing
view. At this point we can see the full chain: work, promise, evidence, and
assessment.

## 12. Show exchange and audit surface

Type:

```bash
go run ./cmd/commitment-ledger status --exchange --json
go run ./cmd/commitment-ledger doctor --repairable
```

Say:

The tool also has an operator surface for exchange, trust, and recovery.
`status --exchange` summarizes imported and received artifacts, and `doctor`
checks local integrity plus recoverability hints.

Note:

If the exchange summary is empty in a fresh demo, that is fine. The point is to
show that the exchange and recovery layer exists even when the happy path does
not need it yet.

## 13. Contrast Bob

Type:

```bash
go run ./cmd/commitment-ledger commit --promiser Bob --repo bob-demo --branch main --target bob-demo/main/TODO-muban/1 --target bob-demo/main/TODO-muban/2 --due 2026-06-21 --promise "I promise to complete TODO-muban subtasks 1 and 2."
go run ./cmd/commitment-ledger expire
go run ./cmd/commitment-ledger report --repo bob-demo --branch main
```

Say:

Bob is the well-meaning but unreliable contrast. Expiration is not
automatically the same thing as moral failure; the system records
`expired_unassessed` first and leaves final judgment explicit.

## 14. Contrast Mallory

Type:

```bash
sed -n '1,40p' ~/lab/commitment-ledger-demo/mallory-demo/TODO/TODO-falun-handle-malformed-packet-report.md
go run ./cmd/commitment-ledger report --repo mallory-demo --branch jj
```

Say:

Mallory is the adversarial contrast. The point is not just lateness or failure,
but confusing or malformed source structure that should be observed
conservatively rather than treated as a universal verdict.

## Close

Say:

So the tool starts from ordinary-looking TODO repos, but adds a second layer:
explicit promises, evidence, and assessments. It keeps exact signed artifact
bytes locally, gives operators inspection and verification tools, and can be
demoed safely with seeded synthetic repos before pointing it at real work.
