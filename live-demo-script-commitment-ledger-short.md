# Live Demo Script (Short)

Use this for a 5-minute live walkthrough with no real project data.

## Intro

Type:

```bash
cd ~/lab/commitment-ledger
```

Say:

This tool tracks promises made against TODO work in Git repos. The core flow is
work, promise, evidence, and assessment, with signed artifacts underneath and
operator tools for inspection and verification.

This demo uses seeded synthetic repos, not real team data.

## 1. Seed the demo repos

Type:

```bash
make demo-setup
```

Say:

This creates four synthetic repos for Alice, Bob, Dave, and Mallory, plus the
demo config file.

## 2. Scan available work

Type:

```bash
make demo-scan
```

Say:

This observes TODO work from the seeded repos. At this point there is only
available work, not promises.

## 3. Create a commitment

Type:

```bash
make commit COMMIT_ARGS='--promiser Alice --repo alice-demo --branch main --target alice-demo/main/TODO-ravud/1 --due 2026-07-01 --promise "I promise to complete TODO-ravud subtask 1."'
```

Say:

Now the work becomes a promise. The command returns both a local commitment ID
and an artifact CID.

## 4. Inspect the commitment

Type:

```bash
COMMITMENT_ID=$(tail -n 1 data/commitments.jsonl | sed -E 's/.*"commitment_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger inspect --json "$COMMITMENT_ID"
```

Say:

`inspect` is the operator lookup view. It resolves the commitment to artifact
identity, protocol doc, signer, and current status.

## 5. Do the work and rescan

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
make demo-scan
```

Say:

Now the seeded source repo changed. The next scan turns that observed change
into evidence.

## 6. Assess as kept

Type:

```bash
EVIDENCE_ID=$(grep '"commitment_id":"'"$COMMITMENT_ID"'"' data/evidence.jsonl | grep 'todo_checked' | tail -n 1 | sed -E 's/.*"evidence_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger assess --commitment "$COMMITMENT_ID" --assessor Alice --status kept --basis "$EVIDENCE_ID" --notes "Completed before the due date."
```

Say:

Evidence is observation. Assessment is explicit judgment. The tool keeps those
separate.

## 7. Verify the result

Type:

```bash
ASSESSMENT_ID=$(tail -n 1 data/assessments.jsonl | sed -E 's/.*"assessment_id":"([^"]+)".*/\1/')
go run ./cmd/commitment-ledger verify --json "$ASSESSMENT_ID"
```

Say:

`verify` checks the stored artifact bytes, signature, signer material, and
protocol linkage.

## 8. Show the summary

Type:

```bash
make status
make demo-report REPORT_ARGS='--promiser Alice'
```

Say:

At this point we can see the full chain: work, promise, evidence, and
assessment.

## Close

Say:

So the system starts from ordinary-looking TODO repos, but adds explicit
promises and signed evidence/assessment artifacts on top. And because the demo
uses synthetic repos, we can show the whole workflow without exposing real
project information.
