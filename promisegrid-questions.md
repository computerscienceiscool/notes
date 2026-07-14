# grid-editor PromiseGrid questions

Print cheat sheet for the meeting.

Date: July 14, 2026

## 1. What is `grid-editor` in PromiseGrid terms?

Short answer:
- a PromiseGrid example app
- a collaborative editor
- browser + Neovim embodiments
- one shared protocol boundary

Current answer:
- live editing uses `live-document`
- presence uses `live-awareness`
- document labels and catalog use `document-metadata`
- durable handoff uses `publish-document`

Why this matters:
- the app is not "just a web app"
- it is already split into grid-shaped protocol surfaces

Source:
- `DI-tofug`
- `DI-ramuv`
- `DI-loruk`
- `DI-gosaf`

## 2. Is the relay the source of truth?

Short answer:
- not for live text

Current answer:
- browser and Neovim own local Automerge replicas
- the relay signs, verifies, stores, and relays
- the relay is not the canonical merged text owner

Why this matters:
- shared meaning lives at the protocol boundary
- not inside one central application server

Source:
- `DI-ramuv`
- `DI-lumek`
- `DI-larok`

## 3. What protocol IDs does it use?

Current protocols:
- `live-document`
- `live-awareness`
- `document-metadata`
- `publish-document`

Short answer:
- each protocol has its own pCID
- each pCID is derived from the exact local spec bytes

Why this matters:
- protocol selection is explicit
- no hidden app-specific wire contract

Source:
- `DI-tofug`
- `DI-sukip`
- `DI-gosaf`

## 4. How are messages carried?

Short answer:
- signed grid envelopes

Current answer:
- `grid([42(pCID), payload, proof])`
- pCID selects meaning
- payload carries protocol data
- proof carries signer evidence

Why this matters:
- transport can change
- protocol meaning stays stable

Source:
- `DI-tofug`

## 5. What is stored durably?

Current durable relay storage:
- relay identity seed
- append-only message log
- CAS-backed signed envelopes
- CAS-backed published text bytes
- CAS-backed published replica bytes
- CAS-backed metadata envelopes

Short answer:
- durable relay artifacts are stored under the relay data root

Why this matters:
- clear evidence path
- replay path
- durable publish/import path

Source:
- `DI-jilin`
- `DI-tavul`
- `DI-loruk`

## 6. What is still browser-local?

Current local browser workflow state:
- recent docs
- open tabs
- local timestamps
- comments
- saved versions
- snapshots
- preferences

Short answer:
- workflow and review conveniences are still partly local

Why this matters:
- not all product features are PromiseGrid-native yet
- this is an honest boundary to mention

Source:
- `DI-dovoz`
- `DI-nuvif`
- `DI-safor`

## 7. Does it already work on the grid?

Best answer:
- it is PromiseGrid-shaped now
- but the server-hosted transport path is the next step

Current truth:
- local relay works
- browser works
- Neovim works
- publish/import works
- relay-backed metadata works
- server-hosted browser + WebSocket path is not the final finished model yet

Good wording:
- "The protocol boundaries are grid-shaped now. The next step is transport and deployment shaping."

## 8. What about WebSocket?

Short answer:
- WebSocket should be transport, not protocol meaning

Current position:
- current repo uses local HTTP polling
- server deployment can move live transport to WebSocket
- but `live-document`, `live-awareness`, `document-metadata`, and
  `publish-document` should stay explicit

Why this matters:
- do not let WebSocket become an undocumented app protocol

Source:
- `DI-ramuv`
- `DI-loruk`
- `DI-gosaf`

## 9. What about identity?

Current answer:
- relay uses durable `Ed25519` identity
- browser display name is not durable identity
- browser participant ID is session-local

Good wording:
- "Human-facing presence labels are separate from durable signing identity."

Source:
- `DI-jilin`

## 10. What about permissions and auth?

Current answer:
- not fully implemented yet
- current local mutation endpoints are loopback-only
- this was a security hardening step

Important to say:
- remote multi-user server mode needs authenticated mutation
- permissions / owner / guest / invite is the next major backend slice

Source:
- `DI-rabod`

## 11. What about storage semantics for metadata?

Current answer:
- metadata is not mixed into live document typing
- metadata is a separate latest-state signed protocol
- title, description, summary, tags, collections, favorite, archived
  are relay-backed

Why this matters:
- document-management state is durable and searchable
- but still separate from CRDT edit traffic

Source:
- `DI-loruk`
- `DI-sukip`

## 12. What about publish/import?

Current answer:
- publish can target:
  - current state
  - named saved version
- relay signs a publish manifest
- manifest references CAS-backed text + replica bytes
- import creates a new local document from that artifact

Important wording:
- publish/import is not live sync
- publish/import is durable handoff

Source:
- `DI-tavul`
- `DI-gosaf`

## 13. What are the current hard limits?

Be honest:
- remote authenticated mutation mode is not done yet
- permissions are not done yet
- PromiseGrid-style restore semantics are not done yet
- some workflow/review state is still browser-local
- local relay transport is still more mature than server-hosted transport

## 14. What is the next correct engineering move?

Recommended answer:
- server experiment first
- keep protocol boundaries
- add authenticated remote mutation
- add WebSocket transport as transport only
- then implement permissions

Good wording:
- "The shape is right now. The next work is deployment hardening and auth, not rethinking the core boundaries."

## 15. What if he asks: why not just keep one protocol?

Answer:
- because live typing, awareness, metadata, and durable publish are not the
  same kind of thing
- they have different cadence
- different durability
- different trust/evidence needs

Good wording:
- "One transport is fine. One meaning surface is not."

## 16. What if he asks: why Automerge?

Answer:
- real CRDT convergence
- browser and Neovim can both use it
- relay does not have to become the canonical editor

Good wording:
- "Automerge gives us real shared editing while keeping the relay focused on signed transport and storage."

Source:
- `DI-ramuv`
- `DI-lumek`

## 17. What if he asks: what would move server-side first?

Best answer:
- authenticated mutation path
- WebSocket live transport
- server bootstrap endpoint
- maybe more relay-backed workflow state later

## 18. One-sentence summary

Use this if needed:

`grid-editor already has PromiseGrid-shaped protocol boundaries, signed relay storage, browser and Neovim embodiments, and separate live-edit, awareness, metadata, and publish flows; the next work is authenticated server-hosted transport and deployment hardening.`
