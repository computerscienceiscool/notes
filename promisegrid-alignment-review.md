# PromiseGrid Alignment Review

## Purpose and authority

This report assesses downstream PromiseGrid material against the current
cdint-grid architecture.

**cdint-grid is the source of truth.** The PromiseGrid Dev Guide and Wire Lab
should change when their public explanation, protocol guidance, or executable
examples conflict with cdint-grid decisions, documentation, and evidence.

This is not a proposal to change cdint-grid, and it is not a wholesale reversal
of PromiseGrid. Most of the downstream model remains sound. The required work
is to make important distinctions explicit, avoid treating draft choices as
universal rules, and ensure operational safety claims match the production
architecture.

## Scope and evidence

This report assesses:

- `promisegrid-dev-guide/README.md`, current checkout reviewed September 4,
  2026.
- `wire-lab`, including its root README, POC19 orientation, and POC21 design.
- cdint-grid's `GLOSSARY.md`, protocol and design documents, thought
  experiments, and active Decision Intents (DIs).

Historical alignment reviews are useful background, but current downstream
files and current cdint-grid decisions take precedence.

## Executive summary

The Dev Guide and Wire Lab are substantially aligned with cdint-grid in these
important ways:

- pCID-selected protocol semantics rather than a universal application API;
- the general Grid envelope shape `grid([42(pCID), ...protocol-defined-slots])`;
- proof placement and slot meaning being owned by the selected protocol;
- no global trust score or centralized authority;
- local adoption rather than automatic fleet update;
- CAS-backed durable evidence with rebuildable indexes and projections; and
- corrections and migrations preserving historical evidence.

The highest-priority downstream updates are:

1. Do not equate durable agent identity with a signing key.
2. Require readback and reconciliation before retrying an external effect with
   an unknown outcome.
3. Qualify pCID-as-frozen-document wording as a current production profile,
   rather than a permanently settled universal model.
4. Correct Wire Lab's historical WASI-first POC19 statement: cdint-grid selects
   fetched native/static stage1 bootstrap first, with WASI deferred.
5. State that CID links and CID possession do not prove semantic dependency,
   authority, availability, retention, or recoverability.

## PromiseGrid Dev Guide assessment

### 1. Correct the identity model

**Current downstream wording.** The Dev Guide says the durable identity anchor
is the signing key and replacement history.

**cdint-grid position.** `AgentID` is a draft, method-neutral identifier for a
durable agent. It is not a signing key, process, host, repository, or repository
commit. A valid signature establishes control of one key under the relevant
proof rules; it does not by itself establish durable identity, freshness, trust,
or authorization.

**Required change.** Replace the claim that the signing key is the durable
identity anchor with:

> A signing key is verification material used by an agent identity lifecycle.
> PromiseGrid must not treat a key, process, host, repository, or friendly label
> as the durable agent identity by itself. The exact AgentID method and
> rotation/recovery rules remain protocol and policy questions.

The Guide may retain signing-key continuity as a useful current design pressure,
but must not define identity as the key.

**Evidence.** `GLOSSARY.md`; `docs/DN-jibut-agent-identity-did-resolution-and-freshness.md`;
`docs/thought-experiments/TE-tanum-agent-identity-freshness-methods.md`; DI-tuhop.

### 2. Qualify the pCID-as-frozen-document statement

**Current downstream wording.** The Dev Guide defines pCID as the
content-addressed identifier of a protocol specification and directs readers to
treat frozen specifications cited by pCID as the primary contract reference.

**cdint-grid position.** A pCID selects the exact specification defining
protocol-selected syntax and semantics. For the selected August production
profile, DI-dugot specifies exact approved Markdown specification bytes. The
broader raw-prose versus manifest versus signed-wrapper question remains open
under DR-vilak.

**Required change.** Keep the practical instruction, but qualify it:

> In the current production profile, a pCID identifies exact approved Markdown
> specification content. More generally, a pCID selects protocol semantics; the
> long-term specification-manifest/publication representation remains under
> design.

A pCID is not a message CID, payload CID, executable identity, address, or
proof of availability, trust, retention, or authorization.

**Evidence.** `GLOSSARY.md`; `docs/grid-cbor-link-indexing.md`;
`docs/pcid-specification-manifests.md`;
`docs/thought-experiments/TE-vitup-pcid-specification-identity.md`; DI-dugot;
DR-vilak.

### 3. Retain the general envelope rule and provisional status

The Guide's general envelope,
`grid([42(pCID), ...protocol-defined-slots])`, is aligned. The outer Grid tag
identifies a Grid envelope; slot 0 is pCID; later slots have pCID-defined syntax
and semantics. A Grid message is not universally required to carry an
independent signature.

Preserve the distinction between the general rule and historical specimens such
as `grid([42(pCID), payload, proof])`. Proof placement, arity, parent links, and
payload role remain protocol-owned.

**Evidence.** `docs/grid-cbor-link-indexing.md`; `GLOSSARY.md`; DI-tivah.

### 4. State that CID links are structural, not semantic proof

Generic tag-42 CID scanning creates an unlabeled graph edge. It does not prove
parenthood, dependency, trust, retention, availability, authority, merge,
ownership, or safe executability. A selected protocol may assign one of those
meanings to a particular field.

**Required change.** Add this warning where the Guide introduces CIDs and CAS:

> A CID link is generic graph structure until the selected protocol assigns it a
> meaning. It does not itself promise availability, retention, authority,
> dependency, or safety.

**Evidence.** `GLOSSARY.md`; `docs/grid-cbor-link-indexing.md`.

### 5. Strengthen local acceptance and freshness language

The Guide correctly rejects global trust scores. It should make clear that
valid, discovered, known, current, fresh, authorized, trusted, and accepted are
different local judgments. There is no globally current repository head,
runtime root, or trusted peer merely because an artifact is newer, signed,
replicated, or observed.

Use qualifiers such as “accepted by this agent under local policy,” “a
discovered candidate,” “a locally selected runtime root,” and “signature-valid.”

**Evidence.** `GLOSSARY.md`; `docs/DN-jibut-agent-identity-did-resolution-and-freshness.md`;
`docs/DN-zibad-agent-repositories-storage-and-atproto.md`; DI-tuhop.

### 6. Separate CID possession from availability, retention, and recovery

The Guide correctly identifies indexes, caches, JSON files, SQLite tables, and
projections as rebuildable local views. It needs a closure-level caveat: a known
CID or local replica does not prove that the required closure is available,
retained, shareable, or recoverable.

**Required change.** A claimed replay, restore, or runtime adoption must name
the required closure and the availability/retention evidence that makes it
obtainable.

**Evidence.** `GLOSSARY.md`; `docs/protocols/object-lifecycle.md`;
`docs/protocols/runtime-root.md`; `docs/deployment-and-production-testing.md`;
DI-jozin; DI-moroh.

### 7. Add external-effect readback and retry safety

Intent, dispatch, a response, and an action hash do not prove that an external
system changed. Production evidence distinguishes source snapshot/key, approval,
request, response, immediate readback, reconciliation, retry decision, and
correction.

**Required change.** Add this operational principle:

> Before retrying an external action with an unknown outcome, read back and
> reconcile the target system. Record the resulting evidence and make any
> corrective action a new, explicit event. Never describe a retry as safe merely
> because the original request was recorded.

**Evidence.** `docs/DN-timis-decentralized-vm-side-effects-barrier-etc.md`;
`docs/thought-experiments/TE-halul-qagent-exclusive-qsync-boundary.md`;
`TODO/TODO-dobab-august-osc-qb-production.md`.

### 8. Keep publication, adoption, execution, and correction separate

The Guide's local-adoption direction is aligned. It should reflect current
cdint-grid detail: stage0 is the small installed bootstrap; stage1 is fetched
generic microkernel functionality; Phase 1A records a launch handoff rather
than requiring stage0 supervision/readiness; and runtime roots remain draft.

Selecting a prior root or binary does not erase history or guarantee reversal
of peer, physical, or external-system effects. Use prior-root retention,
corrective-root adoption, recovery metadata, and explicit full-state restore
attempts.

**Evidence.** `GLOSSARY.md`; DI-furin; DI-tibuk; DI-mavub; DI-sapoh;
`docs/protocols/executable-descriptor.md`; `docs/protocols/runtime-root.md`.

## Wire Lab assessment

### Role and authority

Wire Lab is an experimental repository. Its simulations, thought experiments,
POCs, and historical decisions are valuable executable evidence, but they are
not the architecture authority when they differ from cdint-grid.

### 1. Supersede the WASI-first POC19 execution claim

**Current Wire Lab wording.** Its root README describes POC19 as using
“WASI-first execution,” and says native binaries are later, higher-risk
profiles.

**cdint-grid position.** The first stage1 execution profile is a fetched
native/static bootstrap module. Stage0 verifies CID-addressed executable bytes,
materializes an execution cache, performs local execution checks, starts stage1
as a process, and records launch-attempt evidence. WASI is deferred to later,
capability-bounded application/runtime modules.

**Required change.** Preserve historical POC19 evidence but add a clear
successor notice in active orientation material:

> Historical POC19 explored WASI-first execution. cdint-grid now selects a
> native/static fetched stage1 bootstrap for the first execution profile. WASI
> remains a later, capability-bounded application/runtime option.

**Evidence.** `TODO/TODO-junuh-stage1-execution-profile.md`, DI-tibuk and
DI-mavub; `GLOSSARY.md`.

### 2. Qualify pCID-as-spec-document language

Wire Lab's root README and several thought experiments state that a pCID is the
CID of a protocol-spec document. Preserve this as historical/current production
profile language, but qualify active orientation exactly as in the Dev Guide:
the pCID selects protocol semantics, and the general publication/manifest
representation remains unresolved.

### 3. Keep the general envelope; prevent specimen overreach

Wire Lab's general envelope and pCID-owned later-slot rules are aligned. Keep
them. Mark individual signatures, three-slot envelopes, specific parent-link
placement, and token encodings as POC/profile evidence unless the applicable
pCID freezes them.

### 4. Preserve CID/availability/retention separation

Wire Lab already correctly says a CID does not itself promise availability,
retention, access, or trustworthiness; POC18 includes separate availability and
retention promises. Add the closure-level recovery caveat: claimed replay,
runtime adoption, correction, and restore require evidence that the complete
needed closure can be obtained and retained.

### 5. Preserve local adoption; sharpen preconditions

POC21's model of local candidate adoption and history-preserving corrective
roll-forward is aligned. Make the preconditions explicit: local policy,
signature verification, host-capability approval, complete closure evidence,
and availability/retention evidence are separate judgments. Publication,
synchronization, or a valid signature does not automatically cause adoption.

### 6. Treat capability-token mechanisms as experimental profiles

Wire Lab's CWT/COSE-shaped bearer and non-transferable capability-token work is
valuable evidence. The principle is aligned: fetched code must receive narrow,
locally approved capabilities rather than ambient authority. The exact token
encoding and redemption profile remain draft, so active orientation must not
present them as final universal rules.

### 7. Do not use POC21 replay as external-effect retry evidence

POC21's disposable-container replay demonstrates ordered machine-change
evidence. It does not establish safe retry for effects in external systems. A
timeout, disconnect, or otherwise unknown external write outcome requires
targeted observation and reconciliation before retry; blind replay is forbidden.

## Material to preserve

Both downstream repositories should preserve:

- Promise Theory-first local agency;
- no global trust score or global authority;
- pCID-selected semantic dispatch;
- the general Grid envelope with pCID-defined later slots;
- sparse CAS and distinct availability/retention promises;
- local acceptance and local adoption;
- durable CAS evidence with rebuildable projections;
- independent histories and visible disagreement; and
- correction rather than historical erasure.

## Remaining open decisions

Downstream prose and examples must not silently settle these cdint-grid
questions:

- AgentID/DID method, rotation/recovery profile, and freshness evidence;
- long-term pCID specification-manifest/root format;
- repository-commit/reference-set schema and succession rules;
- final authentication/proof profile;
- detailed external-effect retry authorization and evidence schema;
- fencing for dangerous shared resources after partitions;
- final availability/retention gates for replay, adoption, and restore;
- exact runtime-root/update/restore object model; and
- final capability-token encoding and redemption profile.

## Recommended downstream priority

1. Correct the Dev Guide identity language.
2. Add readback/reconciliation-before-retry guidance.
3. Correct Wire Lab's WASI-first POC19 statement with a successor notice.
4. Qualify pCID-as-frozen-document language in active orientation.
5. Add CID-link and closure availability/retention cautions.
6. Tighten local-acceptance and “latest/current” wording in examples.

## Conclusion

The downstream repositories are already compatible with cdint-grid’s central
PromiseGrid direction. The needed revisions are focused: distinguish agents
from keys, qualify pCID publication identity, make evidence and local acceptance
requirements explicit, correct the first-stage execution profile, and treat
external-effect safety as a first-class operational rule.
