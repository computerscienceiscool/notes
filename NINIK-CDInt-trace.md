# NINIK Questions Traced Into CD Int

This is an evidence trace for the five questions in `QuestionsForSteve.txt`.
It does not answer the design questions or propose architecture. It identifies
the existing documentation and experimental implementation that bear on each
question, then states what remains unresolved for Steve.

## Source Note And Scope

The cited NINIK design-philosophy review is retained in this repository's Git
history at commits `ece2d0b` and `6bfc2b1`, but is not present in the current
`main` checkout. Its model identifies eight durable primitives and three
supporting mechanisms. The relevant supporting mechanisms are:

9. **Pure derivation** — a referentially transparent transformation over exact
   input, function, policy/context, prior-state, and runtime CIDs.
10. **Disposable local view** — a local index, queue, cache, or projection that
   is rebuildable from durable evidence when its design calls it disposable.
11. **External effect adapter** — the system-specific boundary for changes
   outside a pure transformation, accountable through an attempted-effect
   record, observation/readback, and reconciliation.

The code below is primarily in the `x/cas-native-index` experiment; it is not
evidence that a production implementation exists.

## Evidence Trace

| Question | NINIK primitive(s) | File/path | Symbol or section | What the repo currently does | What remains unclear for Steve |
| --- | --- | --- | --- | --- | --- |
| If pure derivation depends on exact inputs, function, policy/context, prior state, and runtime CIDs, where is the boundary between reproducible derivation and external effects/readback? | 9. Pure derivation; 11. External effect adapter | `docs/thought-experiments/TE-dovid-canonical-erp-event-model.md`; `x/cas-native-index/synchronization_experiment.go`; `x/cas-native-index/synchronization_experiment_run.go` | TE-dovid lines 43–49; `ChangeRequestPayload`; `applyWithDurableReadback` | The design requires derived outputs to cite explicit input, function, policy/context, CAS-frontier or branch-head, and runtime/app-root CIDs. The experiment records only `PolicyCID` and `CodeCID` on a change request, with its business record embedded rather than CID-addressed. It separately records an attempted external change and readback. | No rule defines which real-world factors must become captured context and which are necessarily external. The experimental payload also lacks several context links the design describes as replay-critical. |
| How do we decide which real-world variables belong in derivation context versus later observation/readback? | 9. Pure derivation; 11. External effect adapter | `x/cas-native-index/qbxml_request.go`; `docs/design-and-rollout.md` | `QBXMLRequest`; QuickBooks projection and reconciliation | A QuickBooks request links external-source, canonical-event, source-message, and operator-decision CIDs. The planned workflow separates approved request, raw response, observation/readback, and reconciliation. | The repository does not state a general selection test for classifying a changing fact as derivation input versus adapter observation. The QBXML request itself does not carry the derivation function, policy, or runtime-root links. |
| What makes a view practically rebuildable rather than only theoretically rebuildable? | 10. Disposable local view; 3. Immutable CID-addressed block and visible CID link | `TODO/TODO-pidaj-poc19-poc20-alignment.md`; `x/cas-native-index/application_storage_migration_experiment_carv1.go`; `docs/thought-experiments/TE-tonod-repository-reference-set-signature-models.md` | `DI-rudum`; `openCARV1Container` / `rebuildPlacement`; Scenario 24: Hundred-Year Recovery | `DI-rudum` makes projection rebuild a pre-code proof obligation. The CARv1 experiment verifies installed segments and reconstructs its in-memory placement map at every open. The repository/reference-set TE rejects a candidate that cannot restart, rebuild, verify, and serve sparse proofs. | No repository-wide acceptance metric sets required rebuild duration, completeness checks, necessary retained inputs, operator usability, or failure recovery for every kind of view. |
| How strong must readback evidence be before an external effect is confirmed? | 11. External effect adapter; 2. pCID-defined promise; 7. Local acceptance decision | `x/cas-native-index/synchronization_experiment_run.go`; `x/cas-native-index/synchronization_experiment_test.go`; `docs/design-and-rollout.md` | `applyWithDurableReadback`; `TestSynchronizationPeerIdempotenceAndReadback`; QuickBooks reconciliation | For a lost response, the experiment records an `unknown` attempt, requires a readback-capable peer, records whether the operation was applied plus a version, and prevents blind retry. The rollout plan requires immediate targeted QuickBooks readback and reconciliation before dependent OSC changes. | There is no cross-adapter standard for sufficient confirmation: matching fields, a source version, freshness timing, independent observation, or operator confirmation remain protocol-specific or undecided. |
| How do we avoid making people feel they must constantly prove they completed work when external effects require readback/evidence? | 2. pCID-defined promise; 7. Local acceptance decision; 11. External effect adapter | `docs/design-and-rollout.md`; `TODO/TODO-pidaj-poc19-poc20-alignment.md` | QuickBooks approval/reconciliation; `DI-bisir` | Evidence collection is designed largely for adapters and CAS-backed audit paths. External projections require approval; conflicts present evidence to an operator; unknown effects become correction or reconciliation records instead of silent rewrites. | No explicit human-factors policy specifies what evidence is collected automatically, when an operator must intervene, how much evidence the UI presents, or how ordinary successful work avoids becoming a repeated proof ceremony. |

## Concrete Mismatches To Discuss

- The stated derivation model requires more context than the synchronization
  experiment currently records in `ChangeRequestPayload`.
- Readback is operationally required for uncertain writes, but the repository
  does not define a general readback-confidence threshold.
- Rebuildability is a documented proof obligation with a working physical
  placement-map example, but its broad acceptance criteria remain incomplete.

## Mismatch Guide: What These Gaps Mean

This section explains the mismatches in ordinary language. It is not a design
answer. It separates a promise already made by the repository from a question
that the repository has not yet decided.

### 1. The Design's Derivation Receipt Is Richer Than The Experiment's Record

Imagine Olivia produces an invoice recommendation. To repeat that calculation
later, a reviewer needs to know the source records Olivia used, the exact code
that performed the calculation, the policy it followed, the prior accepted
state, and the version of the running application. The NINIK model calls those
items the derivation context. They let a later reviewer distinguish “the same
calculation gave the same answer” from “a similar calculation happened to give
the same answer.”

The current synchronization experiment only attaches `CodeCID` and `PolicyCID`
to `ChangeRequestPayload`. Its `Record` is embedded directly in the payload;
the payload has no general field for a CID-addressed input set, prior-state
frontier, or runtime/app root. That does not make the experiment wrong: it is a
bounded synchronization prototype. It does mean the prototype is not yet an
implementation of the full derivation receipt described by the design note.

For the developer, the important work is first to classify every experimental
record as one of three things: a pure derived result, a request for an external
effect, or an observation of external state. For each pure result, compare its
actual fields to the documented provenance set. For each external-effect
request, identify the parent decision and source evidence that authorize it.
The unresolved decision for Steve is whether every listed context item must be
present on every derived result, or whether pCID-specific rules may define a
smaller complete set for particular result families.

### 2. The Boundary Between Calculation And Observation Is Named, Not Yet Tested

A calculation can use a recorded price list and an order as inputs. It cannot
make the current state of QuickBooks, a package on a truck, or an operator's
unrecorded choice become reproducible merely by running again. Those are facts
to observe through an adapter and record as new evidence.

The repository clearly separates the two categories in broad terms: pure work
is referentially transparent, while QuickBooks, OSC, UPS, files, and process
launches are external effects. The QBXML request model also carries several
useful links: external source, canonical events, source messages, and operator
decisions. What it does not provide is a written classification test for a
borderline variable. For example, a QuickBooks customer lookup could be an
input to a recommendation, an observation used to decide whether a request is
safe, or a post-write readback. The repository does not say which role applies
in each case or what evidence each role must carry.

For the developer, this calls for an inventory, not a new mechanism. List the
values consumed by each derivation and adapter operation. Mark whether each is
immutable CID-addressed evidence, local mutable process state, an external
observation, or an external command/result. Then identify where the operation's
pCID or protocol draft states that classification. Missing classifications are
the precise questions for Steve; they should not be silently filled in by code.

### 3. “Rebuildable” Has A Real Example But No Common Completion Test

The CARv1 experiment gives a concrete, narrow meaning to rebuildable. When the
store opens, it scans the installed immutable CAR segments, verifies them, and
recreates the in-memory placement map. It can read a block afterward without
depending on a separately preserved map. This is strong evidence for that one
physical placement view.

The broader design extends the same expectation to review queues, TUI state,
conflict summaries, replay indexes, and approval state. `DI-rudum` makes this a
pre-code proof obligation, but it does not define what every proof must show.
For an operator-facing view, a successful rebuild may need more than matching
bytes: it may need the correct source frontier, complete explanation of pending
work, acceptable elapsed time, and a safe response if an input is missing.

For the developer, retain the CARv1 test as a useful pattern but do not claim it
proves all views are rebuildable. For every claimed disposable view, document:
the durable inputs and exact frontier; the command or startup path that rebuilds
it; the comparison that establishes equivalence; expected performance; and the
behavior when an input, protocol, or required retained block is unavailable.
Steve still needs to decide which of those conditions are mandatory, and which
may vary by view type or pCID.

### 4. Readback Exists, But “Confirmed” Is Not A Shared Contract

The synchronization experiment handles one important failure safely. Quinn may
apply a change and lose the response. The experiment records the result as
unknown, reads back by operation identifier, records whether the change was
applied and the observed version, and avoids a blind duplicate retry. The
QuickBooks plan uses the same general pattern: request, response evidence,
targeted readback, and reconciliation before a later OSC action depends on it.

That establishes a recovery pattern, not a universal definition of confirmation.
For one external system, an operation identifier and a version may be enough.
For another, confirmation could need a field-by-field comparison, a source
epoch check, a freshness interval, a second observation, or explicit human
review. Treating the Boolean `Applied` in the experiment as a general standard
would overstate what has been decided.

For the developer, describe each adapter's actual observable guarantees:
whether it offers stable identifiers, versions, conditional writes, read-after-
write consistency, deletion detection, and reliable targeted reads. State what
the current code treats as a confirmed, uncertain, drifted, or conflicting
outcome. A pCID or adapter-specific contract can then make those rules
reviewable. Steve's unresolved decision is whether a shared minimum exists and
where the stricter adapter-specific conditions belong.

### 5. Evidence Should Be Collected By The System, Not Repeatedly Demanded Of A Person

The existing plan is already partly aligned with this concern. Adapter and CAS
paths retain requests, raw responses, readbacks, and reconciliation evidence.
The operator is asked for a decision before a meaningful external projection or
when conflicting evidence needs judgment. This is different from asking a
person to manually prove every ordinary action after the fact.

However, the repository has no explicit interaction rule that says when evidence
is automatic, when a review is required, what a normal successful completion
looks like in the TUI, or how much underlying evidence must be exposed. Without
that rule, a technically correct audit trail could still become a burdensome
workflow.

For the developer, trace each proposed operator step to its trigger: approval
of a new external effect, conflict resolution, retry after uncertainty, or
ordinary background capture. Identify which evidence the system collects and
validates automatically, and which decision only a human is authorized to
make. The remaining question for Steve is the desired operator experience and
the threshold at which an automated flow must become a human review.

## Developer Follow-Up Checklist

This is a fact-finding and specification checklist, not an instruction to make
an architectural choice.

1. Build a provenance-field matrix for each existing experimental payload and
   protocol draft: input CIDs, function/code CID, policy/context CID, prior
   state or frontier CID, runtime/app-root CID, and external observation links.
2. For every absent field, label it either intentionally inapplicable, supplied
   by a parent link, supplied by a pCID-defined rule, or unresolved. Cite the
   exact source for the label.
3. Build an adapter-capability matrix covering identifiers, versions,
   idempotency, targeted reads, enumeration, deletion detection, readback
   consistency, and source-epoch or restore detection.
4. Turn every “disposable” claim into a focused rebuild test with named durable
   inputs, a clean-start condition, a result comparison, and an explicit
   failure-mode result.
5. Identify every user-visible evidence/review step and record its trigger,
   automatic evidence, required authority, and failure/retry behavior.
6. Put unresolved questions into the appropriate decision record instead of
   implementing an assumed general rule.

## Current Evidence Pointers

- `docs/thought-experiments/TE-dovid-canonical-erp-event-model.md`, lines
  41–49: rebuildable views, full derivation provenance, and external adapters.
- `docs/thought-experiments/TE-tonod-repository-reference-set-signature-models.md`,
  lines 70–74, 270–280, and 907–928: referential transparency, local indexes,
  restart/rebuild qualification, and durable recovery evidence.
- `TODO/TODO-pidaj-poc19-poc20-alignment.md`, `DI-rudum`: projection rebuild
  is a pre-code proof obligation.
- `x/cas-native-index/synchronization_experiment.go` and
  `synchronization_experiment_run.go`: experimental request, attempt, and
  targeted-readback behavior.
- `x/cas-native-index/qbxml_request.go`: exact QuickBooks request and outcome
  evidence model.
- `docs/design-and-rollout.md`, especially the QuickBooks reconciliation and
  planned test sections: intended operator and reconciliation behavior.
