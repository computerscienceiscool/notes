# Wire Lab — Congruence/Convergence (theory grok)

*Personal notes to prep for the meeting. Not a repo artifact.*

## The trigger

Tiny architectural question:

> When we hash a "protocol," what are we actually hashing — the **prose spec** that describes it, or the **code** that implements it?

Answer chosen: **the spec.** `pCID = hash(spec doc bytes)`.

It looks like a pedantic detail. It isn't.

## Why it isn't a pedantic detail

That tiny question is secretly the same question that split the 1998 sysadmin world in two:

- **Congruence camp (Steve Traugott)** — isconf, decomk, "Why Order Matters." Two machines are "the same" only if the **exact same ordered sequence of changes** was applied to both. The trajectory IS the identity.
- **Convergence camp (Mark Burgess)** — cfengine, Promise Theory. Describe **desired state**; each machine self-corrects toward it. The attractor IS the identity.

Both camps published foundational papers months apart at the same conference (LISA '98). 25 years of polite mutual incomprehension since.

Map the pCID options onto the camps:

| pCID hashes... | Worldview |
|---|---|
| **the code** | Congruence — same protocol = byte-identical implementation |
| **the spec** | Convergence — same protocol = same agreement, multiple implementations OK |

So the "implementation detail" was a **vote** for one tribe.

## The escape: pick the layer where the question doesn't apply

The grid hashes the **spec** at the top level. **But** a specific protocol's spec is allowed to say: *"my payloads carry inner code-hashes; my receivers must run that exact code."*

- **Top level:** spec-as-pCID → formalism-neutral.
- **Inside a specific protocol:** whatever that protocol wants → can be code-hashes (congruent shape), state predicates (convergent shape), or hybrid.

Both camps live on the grid. Neither is second-class. The grid stays neutral.

This is **not a compromise** (where both sides give something up). It's a **proactive non-foreclosure** — pick the layer where the question doesn't have to be answered.

Like TCP doesn't compromise between HTTP and SSH; it just sits at a layer where their differences don't apply.

## Why Steve (the congruence guy) picked the convergence-flavored top

Three reasons:

1. **Hash-the-code at the top would lock the convergence camp out.** Partisan from day one.
2. **Hash-the-spec at the top doesn't lock the code camp out** — protocols can still demand byte-identical code via inner hashes. Order survives, just one level down.
3. **Even Traugott's design is secretly Promise-Theory-shaped.** Pull-not-push means hosts *autonomously promise* to fetch and replay the journal. So a journal entry and a host's pull-and-replay promise are two views of the same act.

So Steve isn't betraying his camp — he's playing **referee at the top level** so neither tribe gets locked out.

## Why this works (the deep reason)

Everyone thought the disagreement was about **autonomy vs. command-and-control**. It wasn't. Both camps already agreed on autonomy.

The real disagreement is one axis below:

> What does an autonomous agent **promise *about*?**

- **Congruence:** "I promise about my **trajectory** — the ordered sequence of changes I applied."
- **Convergence:** "I promise about my **state** — the attractor I'm holding myself near."

Both are valid Promise-Theory promises. They differ only in what they assert.

A spec doc is a thing autonomous agents can promise about. **Either** flavor of promise. That's why hashing the spec is formalism-neutral — the pCID names "the agreement," and each peer autonomously promises to honor the agreement in whatever flavor (trajectory or state) the spec calls for.

## Order doesn't disappear

A natural worry: if the grid is convergence-flavored at the top, doesn't congruence give up *order*?

No. Order moves layers.

- **Old-school congruence:** order is baked into the **wire format itself**. The protocol IS the ordered execution.
- **On this grid:** order is baked into the **spec document**. The spec says "apply in order; deviation is a broken promise." The grid hashes that spec. Every peer who claims to speak that pCID is *promising* to honor the order. Trust ledgers police it.

This is exactly where Traugott's discipline always lived anyway — Makefile prereq chains, isconf tuple streams, decomk environment contracts. All prose specifications of order, then enforced by the host's promise to honor them. The wire was never the load-bearing thing; the agreement plus the promise was.

## The speculative bonus (NOT proven)

Famous result: the **Church-Turing thesis** — Turing machines and lambda calculus look totally different but compute exactly the same class of functions. They're two formalisms for the same underlying thing.

The essay claims (carefully, without proof): congruence and convergence might be in that same relationship.

The bridge is a phrase the wire-lab already wrote down, almost by accident:

> *"Promises are assertions of state in the **past, present, or future**, often conditional."*

- **Promise about the past** ("I applied C1, C2, C3 in that order") = a journal entry. Trajectory.
- **Promise about the future** ("I will hold my state matching this description") = an attractor. State.

Both are the same kind of speech act. The spec's vocabulary already lets you write either one.

Nobody has proved the equivalence theorem. Steve doesn't claim to. The essay says: *"I have the shape, and a thread to pull on, and a reason to think the thread is real."* That's it.

If someone proves it later, the grid is the substrate where the work could happen — because the grid didn't pick a side.

## One-breath recap

1. Trigger: hash the spec or the code?
2. Answer: the spec.
3. Surprise: that's the 25-year-old Burgess-vs-Traugott fight in disguise.
4. Stakes: hashing the code would lock convergence out at the top level.
5. Escape: hash the spec at the top, allow code-hashes nested inside specific protocols.
6. Why it works: both camps already share autonomy; they only disagree on *what an agent promises about*. A spec hosts both flavors equally.
7. Bonus: the wire-lab phrase "past, present, or future" might be the bridge to a Church-Turing-shaped equivalence theorem. Unproven. Real thread.

## Tagline for the meeting

> *"We picked the addressing primitive that doesn't pick a tribe — and in doing so, we became the place where the equivalence theorem could eventually be written."*

## Source material in repo (on `ppx/main`)

- `docs/essays/congruence-convergence-and-the-grid.md` — the canonical framing essay.
- `docs/thought-experiments/TE-20260430-064307-congruence-convergence-duality-and-pcid-framing.md` — TE-23, drives the essay's claims toward decisions.
- `docs/thought-experiments/TE-20260429-173520-spec-doc-as-promise.md` — TE-21, *what is a spec doc, in promise-theoretic terms?*
- `docs/thought-experiments/TE-20260429-175530-spec-doc-store-and-pcid-machinery.md` — TE-22, the on-disk machinery.
- `specs/MANIFEST.md` + `tools/spec/` — the freeze-and-check tooling that already implements pCID-as-spec-hash.
