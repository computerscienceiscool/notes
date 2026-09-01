# NINIK And CD Int: A Plain-English Guide To The Open Problems

This companion explains the NINIK/CD Int questions for someone who did not
write this code and does not need to become a Go programmer to understand why
the questions matter.

It is based on the evidence trace in `NINIK-CDInt-trace.md`. It does **not**
choose the architecture or answer the design questions for Steve. Instead, it
explains the situation in everyday terms so you can see what Steve is being
asked to decide.

## The Very Short Version

CD Int is trying to keep a trustworthy history of what happened while working
with other systems, especially QuickBooks and OSC. It wants to be able to look
back later and say:

> Here is the exact information we used, here is the exact rule/program that
> used it, here is the action we tried, and here is what we later observed.

That is a strong and sensible goal. The hard part is that a computer program
does not control the real world. It can calculate an invoice total perfectly,
but it cannot guarantee that a QuickBooks write completed if the connection
dropped at the wrong moment. It cannot recreate a fact that was never saved.

The NINIK questions are asking where to draw those boundaries in a clear,
practical, and humane way.

## A Few Words You Need

You do not need to memorize these. They are just the vocabulary used in the
documents.

### CID: a fingerprint for exact data

A CID is like a very specific fingerprint for a file or piece of data. If the
data changes even a little, it gets a different CID. So saying “this result was
calculated from CID X” is much stronger than saying “it was calculated from the
order spreadsheet.” CID X points to the exact bytes that were used.

### Pure derivation: a repeatable calculation

Think of a recipe. If you have the same ingredients, the same recipe, and the
same instructions, you should get the same cake. In CD Int, a pure derivation
is that kind of calculation: same recorded inputs and same recorded rules should
produce the same result.

For example: take a saved order, a saved tax policy, and a saved version of the
calculation rules; then produce a proposed invoice. That is something another
person should be able to repeat later.

### External effect: something outside the program changes

Sending an invoice into QuickBooks, changing an OSC order status, buying a UPS
label, writing a file, or starting a process are external effects. They affect
something outside the calculation itself.

This is like clicking “submit” on a web form. You may see a spinner, your Wi-Fi
may cut out, and you may not know whether the website received the form. The
program cannot solve that uncertainty just by calculating again.

### Readback: checking what happened afterward

Readback means asking the outside system what it now says. If a QuickBooks
write might have succeeded but its reply was lost, CD Int can look up the
expected invoice afterward. That is safer than clicking submit again and hoping
it does not create a duplicate.

### View: a helpful local copy, not the official history

An index, queue, cache, or dashboard is a view. It helps the program find and
display information quickly. The goal is that losing one should be annoying,
not disastrous: it should be possible to recreate it from the durable history.

## What The Existing Code Already Does

The repository contains an experimental synchronization system under
`x/cas-native-index`. “Experimental” is important: it is a working testbed, not
a claim that every production rule has been settled.

One good safety behavior is already implemented. Imagine Quinn, the program
role talking to an outside system, sends a change. The outside system applies it
but the response disappears because of a network problem. The experiment does
not immediately send the same change again. It records that the result is
unknown, performs a targeted readback using the operation ID, and records what
it finds. This reduces the risk of creating the same invoice or change twice.

Another real example is the CARv1 storage experiment. Its fast lookup map lives
in memory. When the storage opens again, it scans the durable CAR files and
rebuilds that map. This shows one limited kind of “rebuildable view” actually
working.

Those are useful pieces. The open questions are about turning useful pieces
into a clear, consistent system rather than assuming that one experiment proves
everything.

## Problem 1: What Must Be Saved To Repeat A Calculation?

Suppose a program recommends charging $103.20. Months later, somebody asks,
“Why that amount?” A strong answer needs more than the final number. It should
show the order, tax rule, price rule, and calculation version that led to it.

The NINIK design describes a full receipt for a calculation: exact inputs,
function/code, policy/context, prior state, and runtime version. This is like
keeping the ingredients, recipe, oven settings, and version of the recipe app.

The current synchronization experiment records some of this. In particular, a
change request has a code CID and policy CID. But it does not have a general
field for every input CID, the earlier state/frontier used, or the runtime/app
root. It also embeds a record directly in the message instead of always linking
to a separately CID-addressed input.

Why this matters: without an agreed minimum receipt, two developers may each
think they have made a calculation reproducible while saving different things.
Later, someone may be unable to tell whether a changed result came from changed
data, changed policy, changed code, or a changed running environment.

This is not a request for you to decide which fields to add. It is the question
for Steve: what is the smallest complete record for each kind of calculation,
and which parts can legitimately differ by protocol?

## Problem 2: When Is Something An Input, And When Is It A New Observation?

Some facts are easy: a saved order is an input to a calculation. Some are not:
“What is QuickBooks showing right now?” may change while the program runs.

Here is a useful ordinary example. A grocery list is a stable input to planning
dinner. Whether the grocery store still has milk is not a stable input unless
you check and save that observation. The store can change its shelves after you
look.

CD Int already says, broadly, that QuickBooks and OSC are external systems. It
has request objects that link useful evidence such as the source, canonical
events, and an operator decision. But it has no simple written rule for the
gray areas. Is a QuickBooks customer lookup part of the calculation? Is it a
safety check before writing? Is it proof after writing? The answer changes what
should be saved and when it should be read.

Why this matters: if the boundary is vague, the same fact might be treated as a
reliable input in one feature and as a temporary outside observation in another.
That can make retries, audits, and disagreement handling inconsistent.

The developer does not need to invent a new system first. The sensible evidence
work is to list what each operation reads and label it: saved evidence, local
temporary state, outside observation, or outside command/result. The missing
labels become the actual questions for Steve.

## Problem 3: “Rebuildable” Needs A Test You Can Trust

Calling something rebuildable means you can throw away the convenient copy and
make it again from the important records. This is a little like deleting a
music-app playlist cache: it is fine only if the app can recreate the playlist
from your saved songs and preferences.

The CARv1 test is encouraging because it demonstrates this for one map used to
find blocks in storage. The project also says that review queues, indexes, TUI
state, conflict summaries, and approval state should be reconstructible from
durable CAS/timeline records.

But “it rebuilt” can mean several different things:

- It found the same data.
- It found the same data from the same chosen point in history.
- It finished soon enough to be usable.
- It clearly tells you when a needed input is missing.
- It does not accidentally redo an external action while rebuilding.

The repository has not yet chosen one common checklist for all those meanings.
That is the mismatch. The goal exists, and one narrow example works, but the
project does not yet have a shared finish line for saying, “This view is truly
safe to delete and rebuild.”

## Problem 4: A Readback Is Helpful, But When Is It Enough?

The existing experiment treats a lost response responsibly. It does not claim a
failed network response means the outside action failed. Instead it says, “We
do not know,” then it looks.

That is excellent as far as it goes. But a readback can be stronger or weaker
depending on the outside system. Seeing an invoice with the expected ID may be
good evidence. Seeing a similar invoice with no stable ID may be weak evidence.
Seeing an invoice once may not prove it will still be there after a system
restore. Some systems provide versions or idempotency keys; others do not.

So the missing decision is not “should we read back?” The existing documents
already favor that for uncertain writes. The missing decision is “what facts
must readback show before this particular adapter is allowed to say confirmed?”

This matters because a too-weak confirmation could allow later work to depend
on something that did not really happen. A too-heavy confirmation rule could
slow normal work or demand unnecessary human attention. Steve needs to set the
right requirements per kind of external system, and decide whether there is a
small common minimum.

## Problem 5: Trustworthy Evidence Must Not Turn Into Homework

The fear behind the final question is understandable: if the system says every
real-world action needs evidence, does that mean a person must constantly stop,
take screenshots, write explanations, and prove they did their job?

The intended direction in the repository is better than that. The software and
adapters should automatically retain requests, responses, readbacks, and
reconciliation information. A person should be brought in mainly when a real
decision is needed: approving a meaningful external change, resolving a
conflict, or deciding what to do after uncertainty.

The gap is that this user experience is not yet written down as a rule. The
current material says what evidence is valuable, but not clearly enough which
evidence happens quietly in the background and which moments must interrupt a
person for approval.

Why this matters: a technically perfect audit system can still feel awful if it
asks people to act like its data-entry clerks. A good system should collect
routine proof automatically, show the important facts when a decision is truly
needed, and avoid making the user repeat information the computer already has.

## What You Can Take To Steve

You do not need to ask Steve to explain all of CD Int. These are the focused
things that would make the project clearer:

1. For each kind of pure calculation, what is the minimum saved “recipe card”
   needed to reproduce and explain it?
2. What simple rule tells a developer whether a fact is an input, an external
   observation, or readback evidence?
3. What must a rebuild test prove before a local view can honestly be called
   disposable?
4. For each external adapter, what exact observation is enough to call a write
   confirmed, and what leaves it uncertain?
5. Which evidence should be automatic, and what rare situations genuinely need
   a person to decide?

Those questions do not accuse the current code of being bad. They identify the
places where the code, experiments, and design direction have not yet been
joined by a single clear rule.

## Where This Came From

The technical evidence is in the companion trace and in this repository:

- `docs/thought-experiments/TE-dovid-canonical-erp-event-model.md` describes
  the full provenance expected for derived results.
- `x/cas-native-index/synchronization_experiment.go` and
  `synchronization_experiment_run.go` show the experimental request/attempt/
  readback flow.
- `x/cas-native-index/application_storage_migration_experiment_carv1.go` shows
  one real placement-map rebuild at store open.
- `TODO/TODO-pidaj-poc19-poc20-alignment.md` records the project decision that
  projection rebuild must be proved before operators depend on it.
- `docs/design-and-rollout.md` describes the planned QuickBooks reconciliation
  and operator approval flow.
