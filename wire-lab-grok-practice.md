# Wire Lab — Congruence/Convergence (practical grok)

*Personal notes to prep for the meeting. Not a repo artifact. The "what does this mean for actual systems?" version.*

## The bottom line

The grid is a **substrate**. It hashes specs and routes promise-stacks. It does not, itself, take a side on how peers should agree about behavior.

Specific protocols built **on** the grid take their own sides. A protocol can be:

- **Congruent-shaped** — "run this exact code" — by carrying inner code-hashes.
- **Convergent-shaped** — "match this desired state" — by carrying state predicates.
- **Hybrid** — deterministic harness orchestrating a non-deterministic responder (e.g., LLM call).

All three live on the same grid, addressed the same way at the top, with different content at the bottom.

## Worked example A — a congruent-shaped protocol

Imagine **isconf reborn on the grid**: a "config-replay" protocol.

**1. Write the spec, in prose:**

> *Protocol "config-replay-v1": Payloads are ordered change-records, each carrying a sequence number. Receivers MUST apply changes strictly in sequence. A receiver that applies seq N before seq N-1 has broken its promise. Each receiver publishes a content-hash of resulting state after each apply.*

**2. Hash the spec.** CIDv1 of those bytes = `pCID-config-replay-v1`. That's now an addressable protocol.

**3. Two peers adopt it.** Alice and Bob each say: *"I promise to speak `pCID-config-replay-v1`."* By saying that, they have promised to enforce order — the spec they just adopted demands it.

**4. Wire traffic:**

```
[pCID-config-replay-v1, {seq:1, change:"install foo"}, sig-Alice]
[pCID-config-replay-v1, {seq:2, change:"edit /etc/hosts"}, sig-Alice]
[pCID-config-replay-v1, {seq:3, change:"restart bar"}, sig-Alice]
```

**5. Bob applies in order.** Publishes a state-hash after each one. Alice verifies the hashes. Bob's trust ledger entry for "keeps config-replay promises" goes up.

**6. Carol applies seq 3 before seq 2.** Her published state-hash diverges from what Alice expected. Carol has demonstrably broken her promise. Her trust score on this protocol drops. Other peers stop relying on her replay.

**What makes this congruent in spirit:** order is normative; trajectory is identity; replay is verifiable.

**What makes this work on the grid:** the grid never knew about "order." It just hashed bytes and routed promises. Order was enforced because **the spec said so + peers promised to honor the spec + broken promises cost trust**.

## Worked example B — a convergent-shaped protocol

Same grid, different protocol — call it "desired-state-v1."

**1. Spec:**

> *Protocol "desired-state-v1": Payloads are state predicates ("file X exists with permissions 644," "daemon Y is running"). Receivers periodically sample local state and apply whatever local actions move the system toward the predicate. Order of payload arrival is irrelevant; final state must match the predicate set.*

**2. Hash the spec.** That's `pCID-desired-state-v1`.

**3. Wire traffic:**

```
[pCID-desired-state-v1, {predicate:"file /etc/hosts contains line 'foo'"}]
[pCID-desired-state-v1, {predicate:"daemon nginx is running"}]
```

**4. Receivers do whatever local logic they need.** Maybe one receiver patches `/etc/hosts` with `sed`; another uses an Ansible module; another already had the line and does nothing. All three are conformant.

**5. The grid does the same job as before** — hashes bytes, routes promises. The protocol carries entirely different semantics on top. The grid doesn't notice.

**What makes this convergent in spirit:** state is the agreement; trajectory is irrelevant; multiple implementations are first-class.

## Worked example C — the hybrid case (LLM-orchestration)

This is the one Steve flagged as concrete and increasingly common: **deterministic code calls an LLM**.

- **Outer wrapper:** the client code. Referenceable by **hCID** (its compiled-bytes hash). Runs byte-identically on every host. Congruent.
- **System message sent to the model:** a **pCID** (the spec the model is asked to behave according to). Convergent — the model "promises" to behave per that spec, in the model's own non-deterministic way.
- **User prompt:** payload, addressed to that pCID.

The hCID + pCID together = the interpreter. The convergent receiver (the model) does its work inside that frame.

In grid terms: this is **pCID-inside-hCID** nesting. Naturally expressible. Grid doesn't need to know about it; it just routes pCIDs and lets the protocol's spec define what's nested.

## What this enables in practice

- **Multi-implementation protocols become first-class.** A team can write a protocol in Go; another in Rust; both speak the same pCID, both interoperate.
- **A protocol can demand byte-identical code when it actually needs it** (deterministic replay, security-critical handlers) — by writing that requirement into its own spec.
- **The grid is portable.** GitHub today, PromiseGrid eventually. The merge ceremony is `git push` to `main` by Steve's signing key, not a forge-specific PR. Same shape carries forward to PromiseGrid's "canonical pointer follows the signing key" semantics.
- **Trust does the policing, not the wire format.** Peers who break promises pay in trust score. The wire is dumb; the agreement and the trust ledger are smart.

## What this enables in the long arc

- **A grid that hosts both worldviews is a grid that can hold the conversation between them.** 25 years of polite mutual incomprehension might end here, because both camps can ship working protocols on the same substrate without a tribal precondition.
- **The substrate where a future Church-Turing-style equivalence theorem could be tested** — congruent and convergent protocols running side by side, instrumented, observed, compared. The wire-lab harness exists precisely to support this kind of experimentation.

## Already in code (on `ppx/main`)

The wire-format machinery is no longer prose-only. It ships:

- **`tools/spec/`** — single Go binary with `freeze`, `check`, `cid`, `ls` subcommands.
- **`specs/MANIFEST.md`** — single-fenced-YAML manifest of frozen pCIDs.
- **First frozen spec:** `harness-spec.md` was renamed to `specs/harness-spec-bafkreigtaivld55rekcswfj26mo26e267m3ytzgflqb2qcclyiicpfzc6i.md` — its filename now contains its own CIDv1.
- **Working draft:** `specs/harness-spec-draft.md` — the next freeze candidate.

CIDv1 parameters: multibase=base32, multihash=sha2-256, codec=raw. Hash input = raw file bytes, no normalization.

## Suggested talking points

1. **The framing move is the headline.** "We picked the choice that doesn't pick a tribe." Spec-as-pCID at the top, code-hashes nested per-protocol if a protocol wants them.

2. **The wire format is now operational, not just prose.** First Go binary. First frozen pCID. Manifest in place. TE-22 is real on disk.

3. **Order isn't lost.** It moves from "physics of the wire" to "content of the agreement." Exactly where Traugott's tools always put it (Makefiles, tuple streams, journals — all prose specifications of order honored by promise).

4. **Open question for the room (TE-23 still unlocked):** how heavily should the harness-spec foreground the duality framing? Brief paragraph + link to essay (recommended), or full framing section, or stay vocabulary-only?
