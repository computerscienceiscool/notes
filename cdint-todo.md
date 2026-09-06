# CD Int TODO

Everything below is work to do **directly in or against the `cdint-grid` / CD Int repo**.  
This intentionally excludes unrelated work such as public Dev Guide edits, Wire Lab edits, `goscalelint`, and general final synthesis.

## Priority order

**7 -> 4 -> 3 -> 2 -> 1**

---

## 7. Update `todo-report` for the current `cdint-grid` world

- [ ] Run/report across **all `cdint-grid` branches/worktrees**.
- [ ] Keep unrelated repos out of scope for now.
- [ ] Inventory TODO / TE / TI / DI / design-note formats added or changed in the last two months.
- [ ] For each format, identify the minimum fields `todo-report` needs to recognize it reliably.
- [ ] Update the parser so current formats are detected without false positives from ordinary prose/examples.
- [ ] Capture enough surrounding context to explain **why a TODO exists**, not only the TODO text.
- [ ] Add source metadata:
  - [ ] repo
  - [ ] branch/worktree
  - [ ] file path
  - [ ] line/location
  - [ ] related design record, when available
- [ ] Experiment with exposing:
  - [ ] priority
  - [ ] prerequisites/dependencies
  - [ ] blocked-by relationships
  - [ ] likely execution order
- [ ] Use several TODOs whose dependency chains you already understand as a truth set.
- [ ] Compare `todo-report` output against what you know to be correct.
- [ ] Check whether the same TODO appears on multiple branches/worktrees.
- [ ] Decide how duplicates should be distinguished or collapsed.
- [ ] Separate **deterministic source facts** from **LLM-inferred fields**.
- [ ] Mark every inferred field clearly as `INFERRED`.
- [ ] Test the smallest useful context window instead of sending the whole repo to an LLM.
- [ ] Produce a short findings note:
  - [ ] works now
  - [ ] missing
  - [ ] wrong / ambiguous
  - [ ] smallest next improvement
- [ ] Create one sample output showing:
  - [ ] TODO text
  - [ ] context
  - [ ] dependency
  - [ ] branch/worktree
  - [ ] inferred priority
- [ ] Define done for this pass:
  - [ ] current formats work
  - [ ] branch coverage is visible
  - [ ] dependency context is useful enough to discuss

---

## 4. Create a signing/encryption design-question note

Work from the current repo evidence and keep only questions that remain genuinely unresolved.

- [ ] Write the bootstrap question plainly: **How does a brand-new agent obtain its first key?**
- [ ] Determine how the first key is anchored to the agent identity / genesis message chain.
- [ ] Identify what the durable identity is when keys:
  - [ ] rotate
  - [ ] expire
  - [ ] are compromised
  - [ ] change algorithms
- [ ] Separate the **human** key-use case from **unattended agents/daemons**.
- [ ] Determine where private keys are expected to live.
- [ ] Determine how private keys are unlocked.
- [ ] Identify the minimum acceptable key protection for launch.
- [ ] Determine what another agent needs in order to:
  - [ ] verify a signing chain
  - [ ] determine which key is current enough to rely on
- [ ] Treat `agent-signing-party` only as a bootstrap idea to investigate, not as decided architecture.
- [ ] Remove questions that repo evidence can answer conclusively.
- [ ] Keep only real design choices that still need Steve.
- [ ] For each remaining question, record why it matters to:
  - [ ] launch
  - [ ] interoperability
  - [ ] future evolution
- [ ] Separate:
  - [ ] must decide before launch
  - [ ] safe to defer

**Done when:** you can explain the unresolved key/bootstrap choices without pretending an answer has already been selected.

---

## 3. Review identity, signing, and encryption in the repo

- [ ] Ask Codex to map the current identity design into:
  - [ ] decided
  - [ ] launch choice
  - [ ] still open
- [ ] Review GopenPGP / Proton as a possible Go implementation path.
- [ ] Verify whether GopenPGP and the `gpg` tool interoperate for:
  - [ ] Ed25519 signing
  - [ ] X25519 / cv25519 encryption
- [ ] Clarify whether the design expects separate signing and encryption keys/subkeys.
- [ ] Compare GPG tooling with a native-Go approach on:
  - [ ] portability
  - [ ] agent/process integration
  - [ ] key storage
  - [ ] unattended automation
  - [ ] debugging
  - [ ] maintenance
- [ ] Investigate why Codex keeps suggesting the pure-Go `age` library.
- [ ] Record explicitly that `age` may help with encryption but does **not** solve signing/identity by itself.
- [ ] Capture the launch-time post-quantum tradeoff:
  - [ ] desirable long term
  - [ ] currently heavier computationally/operationally
  - [ ] requires an explicit design choice
- [ ] Do **not** choose the crypto architecture yourself.
- [ ] End with a concise tradeoff/question note.

---

## 2. Create a CD Int architecture-status note

Use repo evidence, not intuition.

Create these sections:

- [ ] **Decided**
- [ ] **Direction but not final**
- [ ] **Needs discussion**
- [ ] **Deferred until after launch**
- [ ] **Implemented**
- [ ] **Experimental evidence**

Then:

- [ ] Put each major concept under exactly one status heading.
- [ ] Mark ambiguous items unresolved.
- [ ] Cite the design note / experiment / code path that supports each status.
- [ ] Define **launch** as the first production UPS label print.
- [ ] Keep **design status** separate from **implementation status**.
- [ ] Call out architecture that is decided but not yet implemented.
- [ ] Treat experiments separately from production code.
- [ ] For each experiment, capture:
  - [ ] question tested
  - [ ] what it proved
  - [ ] what it disproved
  - [ ] what it left unanswered
- [ ] Add a short **Questions for Steve** section containing only decisions the repo cannot resolve.
- [ ] Keep the note short enough to use live in discussion.

---

## 1. Have a focused Codex conversation inside `cdint-grid`

Ask Codex to classify the architecture into:

- [ ] decided
- [ ] direction but not final
- [ ] needs discussion
- [ ] deferred
- [ ] implemented
- [ ] experimental

Ask specifically about:

- [ ] **pCIDs everywhere**
- [ ] using simple pCID-based solutions now with room to evolve later
- [ ] identity in `grid()` message chains with a genesis message
- [ ] what part of identity is decided vs still changing
- [ ] where the Alice -> Bob timeline communication idea currently sits
- [ ] whether Alice -> Bob is:
  - [ ] restored original design
  - [ ] experiment
  - [ ] current direction
  - [ ] final architecture
- [ ] where PGP/GPG vs other identity methods currently sits
- [ ] which crypto/identity decisions are launch choices vs long-term commitments
- [ ] what production code exists today
- [ ] where that production code lives
- [ ] what is experiment/scaffolding rather than production
- [ ] what experiments exist
- [ ] what each experiment tested
- [ ] what each experiment proved/disproved
- [ ] what has intentionally been deferred until after launch
- [ ] source paths / design-note names for anything important

**Stop when you have the gestalt.**  
The goal is to understand the moving pieces, not memorize the repo.

---

## 5. Review the Alice -> Bob timeline communication direction

- [ ] Write the current flow in your own words:
  - [ ] Alice writes data in a `grid()` message on Alice's own timeline.
  - [ ] Alice sends Bob a lightweight notice: roughly, "please pull."
  - [ ] Bob tells Alice the last Alice message he already has.
  - [ ] Alice sends everything after that point.
  - [ ] Bob examines the new messages and locally decides what to accept / act on.
- [ ] Ask Codex which parts exist in:
  - [ ] production code
  - [ ] experiments
  - [ ] design discussion only
- [ ] Explore failure/recovery cases:
  - [ ] missed notice
  - [ ] duplicate pull
  - [ ] missing gap
  - [ ] concurrent updates
  - [ ] stale frontier
  - [ ] reconnect after long absence
  - [ ] unavailable history
- [ ] Sketch one concrete recovery case, such as Bob being offline for two days.
- [ ] Determine what local state Bob must retain to ask for the correct continuation point.
- [ ] Mark clearly what is current direction vs final architecture.

**Done when:** you can explain the normal flow and at least two failure/recovery cases without relying on Codex wording.

---

## 6. Use an exploratory branch/worktree for repo investigations

- [ ] Create a branch named `jj/<name>`.
- [ ] Use it only for experiments, notes, or prototypes.
- [ ] Keep experiments visibly separate from production/final architecture.
- [ ] If Codex changes code, require it to state the experiment question first.
- [ ] Use `git worktree` where helpful so investigations can coexist.
- [ ] Keep a tiny experiment log:
  - [ ] question
  - [ ] change
  - [ ] result
  - [ ] what it means
  - [ ] what it does **not** prove
- [ ] Summarize what the branch taught you before keeping any artifact.
- [ ] Delete or clearly label dead-end experiment artifacts.

**Done when:** the branch/worktree answers a specific architecture question and leaves a short readable conclusion.

---

## Repo facts to keep in mind while working

- `libgrid` / `gridlib` is only a working name.
- The intended concept is a batteries-included Grid library, roughly analogous to `libgit2` / `go-git`.
- It is expected to handle Grid plumbing such as:
  - CAS
  - local/remote communication
  - signing/authentication
  - message generation/receiving
  - other common Grid operations
- Many repo TODOs are waiting on architecture choices, not merely implementation.
- Steve uses many worktrees/sessions; tooling should tolerate that.
- **Decided does not mean coded.**
- **Experimental code does not mean decided.**
- When evidence conflicts, find the newest governing design note before assuming older material is wrong.

---

## Do not do yet

- [ ] Do not edit the public Dev Guide directly from private CD Int material.
- [ ] Do not update Wire Lab from private CD Int details.
- [ ] Do not create new public PromiseGrid/Wire Lab examples until Steve says the design is stable enough.
- [ ] Do not build a major `todo-report` AI scheduler before the smaller dependency/context experiment proves useful.
- [ ] Do not choose crypto/identity architecture on Steve's behalf.

---

## For each important repo finding, capture

- [ ] Plain-English idea in 1-2 sentences.
- [ ] Status: `decided / direction / open / deferred / implemented / experimental`.
- [ ] Source path or design note.
- [ ] Why it matters to launch, interoperability, or future Dev Guide explanation.
- [ ] What is still unclear or conflicting.
- [ ] Next action: `ask Codex / experiment / ask Steve / wait`.
