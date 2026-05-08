# The Bakers' Guild of Transports

*A story, followed by the same content in protocol terms.*

---

## Pass One: The Story

In the Town of Transports, the first guild to write a rulebook was the Bakers' Guild. The Mayor had explained that he would not write any rulebooks himself — only the rules of the town. So the Bakers gathered to write the first one.

They called their kind of shop a **group bakery**.

A group bakery is a place where between two and a few dozen bakers all work together in the same room. Every baker can see every loaf the others bake. There is no head baker. There are no secret kitchens. Anyone present can put a new loaf on the counter at any time.

The Bakers settled on nine principles, which I'll call the Nine Rules of the Bakery.

### The Nine Rules of the Bakery

**Rule One: One room, no separate pantries.**
The bakery is one big room. There are no separate pantries, no per-baker shelves, no walk-in coolers off to the side. Every loaf sits on the same counter. The Bakers debated whether to organize loaves by baker, or by date, or by topic, but they decided every such organization would either duplicate information already visible elsewhere, or pretend one axis was more important than the others. *Flat is honest*, they said.

**Rule Two: The loaf's name is the loaf.**
Every loaf is labeled with a tag. The tag is computed from the loaf itself — its weight, its shape, its exact composition down to the last seed. Two loaves baked identically will produce identical tags. Two loaves with even the smallest difference will produce different tags.

The tag is the loaf's name. The loaf is named what it is. There is no separate "loaf number" written by a clerk.

This has consequences:

- Two bakers can't accidentally name two different loaves the same thing.
- Anyone can verify a loaf is what it claims to be, just by re-weighing and re-measuring it.
- If a baker tries to "edit" a loaf — add a raisin after the fact — the loaf now has a different tag, which means it's a different loaf. The old loaf still exists. The edit is just a new loaf sitting next to the old one.
- The Bakery is therefore append-only by construction. You can't change a loaf. You can only bake another one.

**Rule Three: The tag is computed a specific way.**
The Bakers specify exactly how the tag is computed. A particular hash, over the loaf's exact bytes, in a particular encoding. Anyone with the loaf can re-compute and check.

**Rule Four: The shape of every loaf.**
Every loaf has the same five-part shape:

1. A banner across the top of the loaf saying which guild's rulebook this loaf was baked under.
2. A blank space.
3. A short list of attached cards: who baked it, when, and which earlier loaves it acknowledges as ancestors.
4. Another blank space.
5. The bread itself — the actual content, in plain language, which must contain at least one explicit promise.

The Bakers were deliberate about what cards they did *not* include. There is no "kind of loaf" card, because a loaf's kind is something humans figure out from looking at it, not from a label. There is no "loaf number" card, because the loaf already has a name (its tag). There is no "which bakery this is" card, because the bakery is identified by the room the loaf is sitting in.

The cards must appear in a specific order, and the loaf is encoded in a specific text format with specific line endings. This precision matters because the tag is computed over exact bytes; sloppy encoding produces a different tag and breaks all references.

**Rule Five: Every loaf must contain a promise.**
The bread itself — the actual writing on the loaf — must contain at least one sentence beginning with "I promise."

The Bakers chose this rule to keep the bakery faithful to the town's promise-theory tradition. A loaf without a promise might still be food, but it isn't bakery food. The promise-language requirement keeps the meaning of each loaf legible as a voluntary act, not a directive.

**Rule Six: How to acknowledge another loaf.**
A baker who wants to acknowledge a previous loaf does so in two places. First, on the parents card attached to their new loaf — listing the tags of the loaves they're acknowledging. Second, in the bread itself, in plain language: *"I promise that I have observed and accepted the following loaves: [tag], [tag]."*

Both must agree. Every tag listed in the bread must also appear on the parents card, and vice versa. Headers for graph-walking, body for human-and-LLM readability.

The Bakers considered a more efficient form — *"I have everything up to last Tuesday"* — but decided to leave that for a future revision. For now, every acknowledgement is per-loaf and explicit.

**Rule Seven: Loaves are forever.**
Once a loaf is on the counter, it stays. No baker may remove a loaf. No baker may modify a loaf. The bakery accumulates loaves indefinitely. This is what append-only means.

If the bakery ever needs to do anything fancier — discard old loaves, summarize them, rotate them out — that would require a different kind of bakery, a different rulebook, a different sign above the door.

**Rule Eight: Membership is set at the start.**
When a group bakery opens, the founding bakers are listed, and that list is final. No new baker joins later. If a baker wants to leave or a new baker wants to join, the existing bakery does not change — the bakers instead open a new bakery with a new sign, with the new membership.

The old bakery doesn't go away. It just stops gaining new loaves, because no one is left who promised to bake there.

**Rule Nine: How bakers actually deliver loaves to each other.**
The Bakers' Guild added a long ninth section about how bakers in different physical locations actually share their loaves. They explained that this section is not part of the contract — it's just the recommended way of doing things. The contract is *"what loaves look like and how they relate."* The mechanism for getting them from baker to baker is a separate concern.

The recommended mechanism: each baker keeps their own delivery cart. They only put their own loaves on their own cart. When they see another baker's cart, they take a complete copy of every loaf they don't already have, verify each loaf (re-compute the tag, check the shape), and add the verified copies to their own cart.

This works smoothly because of Rule Two: every loaf's name is itself, so two carts that both have loaf X are guaranteed to have exactly the same loaf X. There's no version conflict possible. Two carts merging is just a union — verified copies, same names.

A baker should always merge other carts onto their own *before* baking a new loaf, because the new loaf's parents card will name earlier loaves, and those loaves need to be on the baker's own cart for the parents references to resolve.

The Bakers note that other delivery mechanisms are possible (a single shared cart, separate carts per topic) but the per-baker-cart pattern is the one they recommend, because no two bakers ever conflict on a name and consistency emerges from copying rather than coordination.

### The Things the Rulebook Doesn't Settle

The Bakers were honest about what they hadn't decided yet. Five questions are written on a board in the corner of the bakery, deferred for later:

- Should the "who baked this" card eventually be a cryptographic signature instead of just a name?
- What does an efficient "I have everything up to here" acknowledgement look like?
- When two bakers bake at the exact same moment, the bread tree forks; do the bakers have to converge it back, or is it left to convention?
- Should every bakery's first loaf be a special "we hereby open this bakery" loaf naming the founding bakers? Right now there is no such requirement.
- For bakeries with many bakers, should the rulebook insist that every founding baker bakes at least one loaf before the bakery is considered "real"?

The Bakers chose to leave these unanswered rather than guess. Real bakeries will surface real answers.

### When the Rulebook Becomes Official

The rulebook is still a draft. It becomes official when four things happen:

1. The Mayor's outer town rules are themselves official.
2. At least one real group bakery has opened and the bakers have exchanged at least one round-trip of loaves, exercising the tagging rule, the shape rule, the parents card, the body-acknowledgement, and the append-only rule.
3. The Mayor signs a paper authorizing the freeze.
4. A clerk runs the tool that mints the official code, snapshots the rulebook forever, and adds it to the town manifest.

Until then, the rulebook is a working draft and may still change.

---

## Pass Two: The Same Content, in Protocol Terms

### What this spec is

This is the first protocol any guild has written for the wire-lab. It governs a particular kind of group communication: a closed group of two or more participants, where every participant sees every message, where any participant can post at any time, where messages link to each other in a graph (not a chain), and where nothing is ever deleted or modified.

The Codex-and-Perplexity case (two participants) is just the smallest instance of this protocol. There's no separate spec for two-party. Two is just N=2.

### What this spec governs

Everything inside a directory named `transports/<this-protocol's-pCID>--<slug>/`. The outer transport spec governs the directory's name and the rule that messages don't declare their transport. This spec governs everything else: how messages are encoded, named, and linked.

### The nine sections

**§1. Flat directory.**
No subdirectories. All message files live as siblings directly under the transport directory. Subdivision by sender, date, or topic is rejected as either redundant with the parent-link graph, presentational (belongs in a viewer), or privileging an axis the protocol doesn't have.

**§2. Filename = CID.**
Every message file is named by its content identifier (CID), with `.txt` appended. The CID is computed from the file's bytes. Filename collisions are impossible — same bytes produce same CID, different bytes produce different CID. Anyone can verify a message by re-hashing and comparing to the filename. Two participants who independently obtain the same message produce byte-identical files; git treats this as a clean union. Editing a message changes its CID, which changes its filename, which means the edit becomes a separate file rather than a mutation. Append-only is structurally enforced by this rule alone.

**§3. CID computation.**
CIDv1, base32 encoding, SHA-256 hash, raw codec. Computed over the entire canonical bytes of the file from the first byte through the trailing newline. Two messages with different bytes (even just whitespace) produce different CIDs. This is what `Parents:` references rely on.

**§4. Envelope.**
Every message file has the same five-part shape:

1. Carrier line: `grid <pcid>\n` where the pCID is this protocol's pCID.
2. Blank line.
3. Header block: zero or more `Header-Name: value\n` lines.
4. Blank line.
5. Body: free-form UTF-8 text containing at least one explicit "I promise" clause.

Plus a trailing newline at end of file. Canonical encoding is UTF-8 with LF line endings. CRLF is rejected. Headers don't span lines. Header names are case-sensitive.

Headers that exist:

- `Date:` — mandatory, single-valued, UTC timestamp in ISO format. Records when the sender claims to have authored. Not authoritative for ordering.
- `From:` — mandatory, single-valued, free-form printable-ASCII string identifying the sender. Identity scheme is unspecified (could be email, key, pCID, plain string).
- `Parents:` — optional, single-line, space-separated CIDs of prior messages this message acknowledges as direct ancestors. If no parents, omit the header entirely. Each parent is a base32 CIDv1 with no prefix. Order matters for the canonical bytes (since order changes the hash) but is not semantically privileged — readers should treat parents as a multiset.

Headers that explicitly do not exist:

- No `Message-ID:` — the CID (and thus the filename) is the message's identifier.
- No `Kind:` — message kind is presentational, lives in body convention.
- No `IHave:` — acknowledgement is a body concern, not an envelope concern (see §6).
- No `Transport:` — per the outer spec, the message does not name its transport.

Headers must appear in canonical order: `Date:`, `From:`, `Parents:` (if present). Future revisions may add headers at locked positions. Unknown headers must not be silently dropped — readers must reject what they cannot fully parse, because the CID covers all bytes including unknowns.

**§5. Body must contain a promise.**
At least one explicit "I promise" clause. This keeps messages legible as promise-theory discourse and prevents the envelope from devolving into a fixed schema. Otherwise free-form UTF-8 text. Markdown is conventional but not required. No length limit beyond filesystem constraints.

**§6. Receipts in the body, not headers.**
Acknowledging another message means listing its CID twice: in the `Parents:` header (so graph-walkers see it structurally) and in the body in prose ("I promise that I have observed and accepted the following message(s): [CID list]"). The two must be consistent — every CID in body must appear in `Parents:` and vice versa. This is per-message acknowledgement. There is no compact "I have everything up to here" form in v0. That's deferred.

**§7. Append-only persistence.**
Once a message file is committed, it is not modified or deleted. The protocol does not bound retention. Compactable, bounded-retention, or ephemeral variants would require a different protocol with a different pCID.

**§8. Closed membership.**
Membership is fixed at transport creation. The set of `From:` values that may appear is determined by social/organizational context, not enforced cryptographically in v0. The slug typically names the participants. If membership changes, a new transport instance is created.

**§9. Per-author-branch git binding (non-normative).**
This section describes a recommended way to use git as the transport. It is explicitly non-normative — the protocol's actual contract is the on-disk shape plus canonical bytes. Other git bindings remain compatible.

The recommended binding:

- Each participant has their own write branch named `<author-id>/main`.
- Each participant authors only on their own branch.
- Each participant fetches every other branch and propagates verified messages onto their own branch (verbatim file copy — same CID, same filename).

Filename = CID makes merges trivial because:

- Distinct messages produce distinct filenames, so no naming conflict.
- Identical messages produce identical filenames, so propagation is a clean union.
- Forwarding is verbatim copying, no edits.

The cycle is: **merge phase** (mandatory when new messages observed) — fetch all branches, list new files, verify each, copy to working tree, commit, push. Then **post phase** (optional) — author new message, compute CID, rename file to CID, commit, push.

Merge before post, because a new message's `Parents:` references must already be on your own branch for readers fetching only your branch to resolve them.

State is eventually consistent. Every branch eventually contains every message. The git commit graph is incidental — the message graph (via `Parents:` headers) is the only authoritative ordering.

Infrastructure files (like a README) are not protocol messages. The merge phase only propagates `*.txt` message files. Infrastructure is coordinated out-of-band.

Append-only is structurally enforced because mutation changes the CID, which changes the filename. Force-push is forbidden as a standing rule, making accidental deletion recoverable.

Membership under this binding is the set of `<author-id>/main` branches a participant fetches from. Unrecognized branches are ignored on read.

Other bindings work too. A single shared branch with merge-on-pull works but breaks under concurrent writes. Per-thread branches work but lose the all-see-all property unless threads are merged. The per-author binding is recommended because it eliminates merge conflicts by construction and reaches consistency through propagation.

### What this spec does not specify

- The pCID itself (minted at freeze).
- Message-graph algorithms (frontier, lowest-common-ancestor, conflict resolution) — those are reader concerns.
- Cryptographic signing — v0 has none.
- Retention beyond append-only.
- Membership-change semantics beyond "new transport instance."
- Compact/frontier-style receipts.

### Open questions

- Should `From:` be tightened to a structured identity (key, pCID)?
- What does cumulative-prefix or frontier acknowledgement look like?
- When two writers concurrently extend the same parent set, the DAG fans out. Is fan-in convergence a protocol obligation or just convention?
- Should every transport have a canonical "genesis" message naming participants and slug?
- For larger N, are there observability or fairness rules to add?

All deferred to future TEs.

### Freeze gate

Four conditions:

1. The outer transport spec is frozen first.
2. At least one real transport instance has exchanged at least one round-trip exercising §3, §4, §4.6, §6, §7. Codex-Perplexity is anticipated first.
3. Steve signs a `merge-group-transport-spec` promise authorizing freeze.
4. The `tools/spec freeze` tool mints the pCID, snapshots the file, appends to manifest.

Until then, the spec lives at the draft path and is a working draft.

---

## Mapping: story ↔ protocol

| Story | Protocol |
|---|---|
| Town of Transports | The `transports/` directory tree governed by the wire-lab outer spec |
| Mayor | The outer transport spec |
| Sign above the door | Directory name `<pcid>--<slug>/` |
| Official code on the sign | pCID |
| Bakers' Guild | The first transport-protocol authors |
| Group bakery | A `group-session` transport instance |
| The Nine Rules | The nine sections of the group-session spec |
| Loaf | Message file |
| Loaf's tag | CID (CIDv1, base32, SHA-256, raw codec) |
| Counter (one room, no pantries) | Flat directory, no subdirectories |
| Banner across the top | `grid <pcid>` carrier line |
| Cards (who baked, when, which ancestors) | `From:`, `Date:`, `Parents:` headers |
| The bread itself | Message body |
| "I promise" sentence | Mandatory promise clause in body |
| Parents card + bread acknowledgement | Header `Parents:` + body receipt prose, both consistent |
| Loaves are forever | Append-only persistence |
| Membership set at the start | Closed membership at transport creation |
| Delivery cart | A participant's `<author-id>/main` git branch |
| Take a copy of every loaf you don't have | Merge phase: fetch, verify, propagate |
| Merge before baking | Merge before post |
| Board of deferred questions | Open questions (OQ-G1 through OQ-G5) |
| Mayor signs the paper | Steve's `merge-group-transport-spec` promise |
| Minting the official code | `tools/spec freeze` mints the pCID |
