# NINIK In CD Int: The Five Questions Answered In Code

This guide takes the five questions from `QuestionsForSteve.txt` and answers
them from the existing CD Int design records and experimental code. Each section
shows the relevant files and a short code segment so you can see where the
answer comes from.

The important overall result is simple: **these are not five requests for a
redesign.** They describe rules the NINIK primitives already provide. The code
is experimental and incomplete in places, but it follows the intended shape.

## 1. If Pure Derivation Depends On Exact Inputs, Where Does It Stop And The Real World Begin?

### The question

If a calculation needs exact inputs, rules, prior state, and runtime identity,
isn't there always some real-world fact left out? Where is the boundary between
a reproducible calculation and something that must be checked later?

### The answer

The boundary is whether the program is only calculating from recorded facts, or
whether it is trying to learn about or change something outside those facts.

- A calculation is pure when every fact that can change its answer is supplied
  as recorded input.
- QuickBooks, OSC, UPS, a file, or a process are outside the calculation.
- The program can calculate a request for an outside action, but it cannot claim
  the action happened until the outside system is observed afterward.

This is why NINIK has both **Pure derivation** and **External effect adapter**.
They are deliberately different jobs.

### The design record that says this

`docs/thought-experiments/TE-dovid-canonical-erp-event-model.md`, lines 43–49:

```text
the result must cite explicit input CIDs, function CIDs, policy/context CIDs,
CAS frontiers or branch heads, and runtime/app roots.

External writes to QuickBooks, OSC, UPS, banks, card processors, or files are
side effects isolated at adapter agents.
```

In plain English: the first paragraph describes the saved recipe for repeating
a calculation. The second says that writing to another system is not part of
that recipe.

### The code that does it

`x/cas-native-index/synchronization_experiment_run.go` records a requested
change before it calls the outside peer:

```go
requestCID, err := experiment.journals[sourceRole].Append(SynchronizationPayload{
    Action: "promise", Operation: "change-request",
    Request: &ChangeRequestPayload{
        OperationID: request.OperationID, TargetPeer: targetRole, Record: request.Record,
        PolicyCID: Tag42FromCID(experiment.policyCID), CodeCID: Tag42FromCID(experiment.codeCID),
    },
})
result, applyErr := target.ApplyChange(request)
```

The first part saves what it intends to do. `ApplyChange` is the moment it asks
the outside peer to change. Those are not treated as the same thing.

### What this means for you

The system is not supposed to capture every fact in the universe. It must
capture the facts that affect a calculation. Facts it cannot control or safely
assume—such as the current state of QuickBooks—are handled as observations.

There is no NINIK redesign problem here. The experiment carries only some of
the full provenance fields described by the design, which is normal unfinished
prototype work rather than a contradiction.

## 2. How Does It Decide Between A Calculation Input And A Later Observation?

### The question

How do we decide which real-world variables belong in the calculation context
and which should be handled through observation or readback later?

### The answer

Use the role the fact plays:

- If it is used to calculate or choose the result, save it first as an input.
- If it is learned by looking at an outside system, record it as an observation.
- If it is learned after attempting a write in order to learn whether that
  write happened, it is readback.

For example: a saved order is calculation input. A fresh QuickBooks customer
lookup is an observation. Looking up a specific invoice after a failed network
response is readback.

### The code that stores the evidence

`x/cas-native-index/qbxml_request.go` defines what a QuickBooks request keeps
with it:

```go
type QBXMLRequest struct {
    ExternalSourceCID      cid.Cid
    QBXMLCID               cid.Cid
    SourceMessageCIDs      []cid.Cid
    CanonicalEventCIDs     []cid.Cid
    OperatorDecisionCIDs   []cid.Cid
}
```

Those links let a later person answer: what source material was used, what
canonical facts were involved, and who approved the request. The request is
evidence of intent; it is not proof that QuickBooks changed.

### The planned workflow

`docs/design-and-rollout.md`, lines 922–933, describes the next steps:

```text
qsync requests qagent to attempt the approved QBXML side effect,
stores raw request/response evidence through CAS-backed storage, and then
observes QuickBooks to prove projected, pending, drifted, failed-side-effect,
duplicate-risk, or correction-required state.
```

So the project does not blur calculation, request, and later observation into
one claim. Each becomes its own piece of evidence.

### What this means for you

The question has a usable answer: classify a fact by when and why it is learned.
It is input when it helps produce the answer; it is observation when it reports
the outside world; it is readback when it checks a requested outside change.

There is no redesign problem here. A developer may still need to make each
operation's fields explicit, but the NINIK distinction is already doing the
organizing work.

## 3. What Makes A View Really Rebuildable?

### The question

What makes a local view practically rebuildable instead of merely theoretically
rebuildable?

### The answer

It is practically rebuildable when you can remove the convenient local copy,
start from the durable records, recreate it, and get the same useful answer
without repeating an outside action.

Think of a music-app search index. It is fine to lose only when the app can
recreate it from the actual music library. It is not fine to lose when it was
the only place that knew what songs you owned.

### The code example

`x/cas-native-index/application_storage_migration_experiment_carv1.go` says
that the fast placement map is disposable:

```go
// Its in-memory placement map is disposable and rebuilt from the CAR
// files at every open.
type carV1Container struct {
    placement map[string]carV1Placement
}

func openCARV1Container(rootPath string) (*carV1Container, error) {
    container := &carV1Container{
        rootPath: rootPath, placement: make(map[string]carV1Placement),
    }
    if err := container.rebuildPlacement(); err != nil {
        return nil, err
    }
    return container, nil
}
```

The map is not saved as the truth. On startup, the program rebuilds it by
checking the durable CAR files. This is an actual working example, not just a
theory.

### The rule for broader views

`TODO/TODO-pidaj-poc19-poc20-alignment.md` records `DI-rudum`:

```text
Prove that review queues, root-adoption status, conflict summaries,
prior-action warnings, replay indexes, and approval state can be deleted and
rebuilt from CAS/timeline records before operators depend on the TUI.
```

### What this means for you

“Rebuildable” is not supposed to mean “we hope we could recreate it.” It means
there should be a test like the CARv1 startup test: remove the fast copy, rebuild
from durable evidence, and verify that it works.

There is no redesign problem here. CD Int already chose the correct direction;
the remaining work is to add that kind of proof for more views.

## 4. How Strong Must Readback Be Before An Effect Is Confirmed?

### The question

How much readback evidence is enough before we say an external effect really
happened?

### The answer

It must connect what the outside system now shows to the exact action the
program requested. If it cannot make that connection, the result remains
uncertain.

The exact check depends on the outside system. A system with a stable operation
ID and a version can give stronger proof than one that only returns a similar
looking record. The important rule is: do not turn uncertainty into success just
because a network response was lost.

### The code that handles a lost response

`x/cas-native-index/synchronization_experiment_run.go` does this:

```go
if applyErr != nil {
    outcome = "unknown"
}

reader, ok := target.(PeerReadbackReader)
if !ok {
    return nil, errors.New("uncertain write target has no readback capability")
}
readback, err := reader.Readback(PeerReadbackRequest{
    OperationID: request.OperationID,
    Family: request.Record.Family,
    RecordID: request.Record.RecordID,
})
```

The code does not retry blindly. It changes the outcome to `unknown`, then asks
the peer about that specific operation and record.

The test proves the intended behavior in the experiment:

```go
if !readback.Applied || readback.Record.RecordID != record.RecordID {
    t.Fatalf("readback = %+v, want applied record %s", readback, record.RecordID)
}
if second.Status != "already-applied" {
    t.Fatalf("repeat apply status = %q, want already-applied", second.Status)
}
```

### What this means for you

Readback is not a vague “we checked.” It is a check for the particular requested
change, using the strongest identity/version/field evidence that the external
system can provide. If that link is not strong enough, the system should say
“unknown” and wait for safe reconciliation or human judgment.

There is no redesign problem here. The actual strength has to be tailored to
each adapter because QuickBooks, OSC, UPS, and a file system do not offer the
same kinds of proof.

## 5. How Does This Avoid Making People Constantly Prove Their Work?

### The question

How can PromiseGrid require evidence for external effects without making people
feel that they must constantly prove they completed ordinary work?

### The answer

The software should gather routine evidence itself. The person should be asked
to make decisions, not to reconstruct technical proof that the software was in
a better position to collect.

For a normal successful action, the adapter can automatically retain the
request, outside-system response, readback, and reconciliation result. A human
is needed when authority or judgment is genuinely needed: approving a meaningful
external change, choosing between conflicting facts, or handling an uncertain
result.

### The design record that supports this

`docs/design-and-rollout.md`, lines 303–315:

```text
QuickBooks projections do not run without separate operator approval, and
failed or unknown QuickBooks side effects create CAS reconciliation/correction
promises rather than overwriting CAS facts.
```

The human approval is for the consequential external action. The system keeps
the technical evidence and does not erase an uncertain or failed outcome.

`TODO/TODO-pidaj-poc19-poc20-alignment.md`, `DI-bisir`, adds that conflict and
operator-decision records preserve the evidence rather than hiding it in the
user interface.

### What this means for you

The intended experience is not “prove every task.” It is “the system keeps the
receipts; you decide when a real decision belongs to you.” If everything goes
normally, most evidence collection should be invisible.

There is no redesign problem here. The detailed user interface is still future
work, but the model itself puts evidence collection on the software and adapter
side, not on the person doing normal work.

## Final Takeaway

The five questions all have answers inside the NINIK model and the current CD
Int direction:

1. Record the inputs to calculations; treat outside changes as effects plus
   later observation.
2. Classify facts by their role: input, observation, or post-write readback.
3. Prove a view is rebuildable by deleting/recreating it from durable evidence.
4. Confirm effects by linking readback to the exact requested change; otherwise
   preserve uncertainty.
5. Let the software collect evidence automatically; involve people for genuine
   authority and judgment.

The experimental code does not yet implement every planned detail. That is work
to complete, test, and refine. It is not evidence that Steve must redesign the
eight NINIK primitives or the three supporting mechanisms.
