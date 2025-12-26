# YJS vs PromiseGrid CRDT Design

**Date:** December 23, 2024  
**Author:** JJ  
**Purpose:** Understanding YJS protocol to design a PromiseGrid-native CRDT

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [YJS Fundamentals](#yjs-fundamentals)
3. [YJS Internal Structure](#yjs-internal-structure)
4. [YJS Wire Protocol](#yjs-wire-protocol)
5. [PromiseGrid Architecture](#promisegrid-architecture)
6. [PromiseBase Storage](#promisebase-storage)
7. [Key Differences](#key-differences)
8. [Design Challenges](#design-challenges)
9. [Questions for Steve](#questions-for-steve)

---

## Executive Summary

**Goal:** Design a CRDT for PromiseGrid that enables collaborative editing while maintaining PromiseGrid's core principles of immutability and content-addressable storage.

**YJS Strengths:**
- Proven CRDT implementation
- Efficient wire protocol
- Handles offline collaboration
- Fast synchronization

**PromiseGrid Requirements:**
- Complete immutability (nothing ever deleted)
- Content-addressable storage (everything has a hash)
- Peer-to-peer architecture
- Full audit trail preservation
- No data loss under any circumstances

**The Challenge:** YJS allows garbage collection and data loss (select-all-delete). PromiseGrid cannot allow this for compliance/audit requirements.

---

## YJS Fundamentals

### What Problem Does YJS Solve?

**The Collaborative Editing Problem:**
- Multiple people edit same document simultaneously
- Need to merge changes deterministically
- No central server to resolve conflicts
- Must work offline

**YJS Solution: Operation-Based CRDTs**
- Send operations (insert/delete), not final state
- Each operation has a unique ID
- Deterministic merge algorithm
- Both clients arrive at same result

### Core Concepts

#### 1. Logical Time (Causality)

**Not wall-clock time!** Logical time = "what did you know when you made your edit?"

```
Scenario A - Different logical times:
  You type "A" → I receive it → I type "B"
  Result: "AB" (B came after A logically)

Scenario B - Same logical time:
  You type "A" (offline)
  I type "B" (offline, didn't know about A)
  Result: Determined by client ID tiebreaker
```

**Key Insight:** Two operations at "same logical time" = neither knew about the other.

#### 2. Unique IDs for Every Operation

Every operation gets a globally unique ID:

```
ID = (client ID, clock)

Examples:
  Your first operation: (client=42, clock=0)
  Your second operation: (client=42, clock=1)
  My first operation: (client=99, clock=0)
```

**Why this works:**
- Different client IDs = IDs never collide
- Clock increments = operations ordered within each client
- Works offline (no coordination needed)

#### 3. Deterministic Merge Algorithm

**When operations happen at same logical time:**

```
Rule: Sort by client ID (lowest first)

Example:
  Client 42 inserts "A"
  Client 99 inserts "B"
  Result: "AB" (42 < 99)

Both computers compute the same result!
```

#### 4. Operations vs State

**State (bad for collaboration):**
```
"The document says: Hello"
Just the final result, no history
```

**Operations (good for collaboration):**
```
Operation 1: insert 'H' at (client=42, clock=0)
Operation 2: insert 'e' at (client=42, clock=1)
...

Actions + metadata that create the state
Can be replayed, merged, undone
```

### Why YJS Works Offline

```
You go offline:
  Type "Hello"
  Create operations (42,0), (42,1), (42,2), (42,3), (42,4)

I go offline (same time):
  Type "World"  
  Create operations (99,0), (99,1), (99,2), (99,3), (99,4)

We reconnect:
  Exchange operations
  Merge: client 42 < 99
  Result: "HelloWorld"
  
Both of us get the same result!
```

**No server needed!** IDs are globally unique by design.

---

## YJS Internal Structure

### The Item Data Structure

YJS documents are **linked lists of Items**:

```javascript
Item {
  id: {
    client: 42,
    clock: 0
  },
  content: 'H',
  left: null,              // Previous Item
  right: [Item:e],         // Next Item  
  deleted: false           // Tombstone flag
}
```

### Example Document Structure

```
Document: "Hello"

[H] -> [e] -> [l] -> [l] -> [o]
 ↓      ↓      ↓      ↓      ↓
(42,0) (42,1) (42,2) (42,3) (42,4)
```

Each character is an Item with:
- Unique ID
- The actual content
- Links to neighbors
- Deleted flag

### Tombstones (Critical Concept!)

**What happens when you delete?**

```
Before: [H] -> [e] -> [l] -> [l] -> [o]

Delete 'e':
After:  [H] -> [e] -> [l] -> [l] -> [o]
               ↑
           deleted: true

The Item STAYS in the structure!
Just marked as deleted.
```

**Why keep deleted Items?**

```
You delete 'e': Item:e.deleted = true
I insert 'X' after 'e' (offline): Item:X.left = [Item:e]

When we sync:
  Item:e still exists (as tombstone)
  Item:X can still reference it
  Links don't break!
```

**Rendering vs Storage:**
- **Storage:** All Items exist (including deleted ones)
- **Rendering:** Skip Items where deleted=true
- User sees: "Hllo" (no 'e')
- Structure has: H, e(deleted), l, l, o

### Concurrent Operations Example

```
Starting: [A] -> [B] -> [C]

Person 1 (offline): 
  Deletes B → Item:B.deleted = true
  Inserts X after B → Item:X with left=[Item:B]

Person 2 (offline):
  Deletes C → Item:C.deleted = true
  Inserts Y after C → Item:Y with left=[Item:C]

Merged structure:
  [A] -> [B(deleted)] -> [X] -> [C(deleted)] -> [Y]

User sees: "AXY"
History preserved: All 5 Items exist!
```

---

## YJS Wire Protocol

### Three Message Types

From `y-protocols/sync.js`:

```javascript
const messageYjsSyncStep1 = 0  // Initial sync request
const messageYjsSyncStep2 = 1  // Reply with missing data
const messageYjsUpdate = 2     // Ongoing updates
```

### Message 1: SyncStep1

**Purpose:** "Tell me what you're missing"

**Code:**
```javascript
export const writeSyncStep1 = (encoder, doc) => {
  encoding.writeVarUint(encoder, messageYjsSyncStep1)  // Type: 0
  const sv = Y.encodeStateVector(doc)                   // Get state vector
  encoding.writeVarUint8Array(encoder, sv)              // Write state vector
}
```

**Binary format:**
```
[0] [length] [state vector bytes...]
 ↑    ↑       ↑
 |    |       Summary of what I have
 |    How many bytes
 Message type
```

**State Vector Example:**
```
{
  client 42: clock 5,   // I have operations 0-5 from client 42
  client 99: clock 7    // I have operations 0-7 from client 99
}
```

### Message 2: SyncStep2

**Purpose:** "Here's what you're missing"

**Code:**
```javascript
export const writeSyncStep2 = (encoder, doc, encodedStateVector) => {
  encoding.writeVarUint(encoder, messageYjsSyncStep2)  // Type: 1
  encoding.writeVarUint8Array(encoder, 
    Y.encodeStateAsUpdate(doc, encodedStateVector)     // Missing operations
  )
}
```

**Binary format:**
```
[1] [length] [missing operations...]
 ↑    ↑       ↑
 |    |       Actual operations you need
 |    How many bytes
 Message type
```

### Message 3: Update

**Purpose:** "Here's what just happened"

**Code:**
```javascript
export const writeUpdate = (encoder, update) => {
  encoding.writeVarUint(encoder, messageYjsUpdate)  // Type: 2
  encoding.writeVarUint8Array(encoder, update)       // New operations
}
```

**Binary format:**
```
[2] [length] [update bytes...]
 ↑    ↑       ↑
 |    |       New operations
 |    How many bytes
 Message type
```

### The Sync Flow

**Initial Sync:**
```
Client A → Client B: SyncStep1 (state vector)
Client B → Client A: SyncStep2 (missing ops)
Client B → Client A: SyncStep1 (state vector)
Client A → Client B: SyncStep2 (missing ops)

Both clients now fully synced!
```

**Ongoing Updates:**
```
User types 'X' on Client A:
  Create operation → Immediately send as Update message
Client B receives Update → Applies operation → In sync
```

### Efficiency Techniques

#### 1. Variable-Length Integers

**Problem:** Most numbers are small, but need to support large numbers

**Solution:**
```
Number < 128:     1 byte
Number < 16,384:  2 bytes
Larger numbers:   3+ bytes

Example:
  Clock = 5:     [0x05]           (1 byte)
  Clock = 200:   [0xC8, 0x01]     (2 bytes)
  Clock = 50000: [0xD0, 0x86, 0x03] (3 bytes)
```

#### 2. Run-Length Encoding

**Problem:** Typing "Hello" creates 5 operations

**Naive approach:**
```
5 separate operations = ~20 bytes
```

**YJS approach:**
```
One struct covering all 5 characters = ~10 bytes

{
  client: 42,
  clock_start: 0,
  length: 5,
  content: "Hello"
}
```

#### 3. State Vectors

**Problem:** How to efficiently say "what I have"?

**Solution:** Don't list all operations, just the highest clock per client

```
Instead of: "I have (42,0), (42,1), (42,2), ..., (42,100)"
Send: "client 42: clock 100"

~1000x smaller!
```

### Peer-to-Peer Sync

**Important for PromiseGrid!**

From the YJS documentation:

```
"In a peer-to-peer network, you may want to introduce a SyncDone message type.

Both parties should initiate the connection with SyncStep1.

When a client received SyncStep2, it should reply with SyncDone.

When the local client received both SyncStep2 and SyncDone,
it is assured that it is synced to the remote client."
```

**Why this matters:**
- PromiseGrid is decentralized (peer-to-peer)
- Both nodes are equal
- Both can initiate sync
- No central authority

---

## PromiseGrid Architecture

### Core Principles

From the PromiseGrid README:

**1. Decentralized Computing:**
```
"PromiseGrid is to computation what the Internet is to communication"
"Owned and operated by its users"
"No single legal entity controls it"
```

**2. Content-Addressable Everything:**
```
"Every piece of code/data has a unique address"
"Address is the cryptographic hash of the content"
"Content cannot be changed without changing its address"
```

**3. Immutable Storage:**
```
"Once stored, content never changes"
"All modifications create new addresses"
"Perfect audit trail and reproducibility"
```

**4. Message-as-Function-Call:**
```
"A message consists of a capability token followed by a payload"
"The token is the hash of the function that will fulfill the promise"
"A message is a function call"
```

### Capability-as-Promise Model

**Key insight:** Capabilities are promises

```
Issuer creates capability token:
  - Hash a closure containing the fulfillment function
  - Hash = both the token AND the address

Holder presents token:
  - Sends message to the hash address
  - Issuer can: fulfill, revoke, or defer

Promise Theory principles:
  1. Cannot make promises for others
  2. Cannot impose obligations on others
```

### Merge-as-Consensus Model

**How PromiseGrid handles conflicts:**

```
"Merges are a form of consensus formation"
"Merge conflicts occur when a merge function cannot fulfill its promise"
"Applications use heuristics that include a cascade of merge functions,
 ultimately falling back to LLMs and finally to human intervention"
```

**Key point:** Merging is optional, not required!

---

## PromiseBase Storage

### What is PromiseBase?

**From the PromiseBase document:**

> PromiseBase is a content-addressable storage (CAS) system that stores data by its cryptographic hash rather than by filename or location.

### Key Features

**1. Content-Addressable Storage:**
```
Store data → Get back SHA-256/SHA-512 hash
Hash = permanent address
Same content = same hash (deduplication)
```

**2. Immutability:**
```
"Once stored, content cannot be changed without changing its address"
"WORM Storage (Write Once Read Many)"
"Automatic hash computation during write"
```

**3. Merkle Trees:**
```
"Each tree node contains hashes of child nodes"
"Enables efficient verification of large datasets"
"Supports both leaf nodes (blocks) and internal nodes (trees)"
```

**4. Content-Defined Chunking:**
```
"Uses Rabin fingerprinting to create consistent chunk boundaries"
"Maximizing deduplication even when files are modified"
"Produces consistent chunks regardless of insertion/deletion"
```

### Core Operations

**Storing a Block:**
```python
data = "Hello World"
hash = promisebase.put_block(data)
# Returns: hash_abc123...

# Data is now permanently stored at hash_abc123
# Cannot be modified
# Can be retrieved forever
```

**Creating a Tree:**
```python
tree = promisebase.put_tree([
  hash_op1,  # Operation 1
  hash_op2,  # Operation 2
  hash_op3   # Operation 3
])
# Returns: hash_tree_xyz...

# Tree itself has a hash
# Tree contains references to child hashes
# All immutable
```

### Storage Structure

**Modern approach (using IPFS CIDs):**

```
CID Example:
zb2rhe5P4gXftAwvA4eXQ5HJwsER2owDyS9sKaQRRVQPn93bA

Human readable:
base58btc - cidv1 - raw - sha2-256-256-[hash]

Path structure (dynamic depth based on directory size):
gm/3d/km/jr/gm3dkmjrmeydambxme2den3dhe2tcmlghezdant...
```

### Why This Matters for CRDTs

**1. Operations are Content:**

```
Operation = {
  type: "insert",
  id: {client: 42, clock: 0},
  content: "H"
}

Store in PromiseBase → hash_abc
hash_abc = permanent address of this operation
```

**2. Automatic Deduplication:**

```
If two people create identical operations:
  Same content → Same hash → Stored once
```

**3. Merkle Trees for Organization:**

```
Tree of operations:
├─ hash_op1 (insert 'H')
├─ hash_op2 (insert 'e')
├─ hash_op3 (insert 'l')
└─ hash_op4 (insert 'l')

Tree itself gets hash: tree_root

tree_root = proof you have all operations
```

**4. Complete History:**

```
Nothing ever deleted
All operations exist forever
Perfect audit trail
Can reconstruct any historical state
```

---

## Key Differences

### YJS vs PromiseGrid Comparison

| Aspect | YJS | PromiseGrid |
|--------|-----|-------------|
| **Storage Model** | Mutable state | Immutable content |
| | One document that changes | New version per change |
| | Items can be modified | Nothing ever changes |
| **Deletion** | Tombstones (deleted=true) | Create delete operation |
| | Can garbage collect | Never remove anything |
| | "Select all, delete" loses data | Everything preserved |
| **Addressing** | In-memory references | Content hashes |
| | Items linked by pointers | Items referenced by hash |
| | Position-based | Content-based |
| **Architecture** | Client-server OR peer-to-peer | Pure peer-to-peer |
| | Can have central server | Fully decentralized |
| **Sync Protocol** | State vectors + deltas | Messages as function calls |
| | Binary encoding | Content-addressed messages |
| **History** | Optional garbage collection | Mandatory complete history |
| | Can lose old data | Never lose anything |
| **Use Case** | Collaborative editing (general) | High-stakes collaboration |
| | Google Docs style | Legal/medical/financial |
| | Performance-optimized | Compliance-optimized |

### The Fundamental Incompatibility

**YJS allows data loss:**
```
User does "select all, delete":
  YJS: Creates new empty document
       Old document thrown away
       Tombstones garbage collected
       
Result: History lost
```

**PromiseGrid forbids data loss:**
```
User does "select all, delete":
  PromiseGrid: Creates delete operations for each item
               All original insert operations still exist
               All delete operations stored with hashes
               
Result: Complete history preserved
        Can reconstruct document at any point
        Full audit trail
```

### Timeline/Branch Model

**YJS (implicit branches):**
```
Usually linear history
Conflicts resolved automatically
Branches not explicitly tracked
```

**PromiseGrid (explicit branches):**
```
       tree_abc ("Hello")
      /                    \
tree_def ("Helplo")    tree_xyz ("Hello World")
      |                      |
(both exist forever!)

Multiple futures allowed
Branches are first-class
Merging is optional
```

---

## Design Challenges

### Challenge 1: Operation Storage Model

**Question:** What do we store in PromiseBase?

**Option A: Store Operations Only**
```
Pros:
  ✓ Complete history
  ✓ Full audit trail
  ✓ Each operation immutable
  ✓ Easy to attribute changes

Cons:
  ✗ Must replay to see current state
  ✗ Slow with many operations
  ✗ No quick access to "what does it look like now?"
```

**Option B: Store Document Versions**
```
Pros:
  ✓ Fast access to any version
  ✓ No replay needed
  ✓ Efficient for reading

Cons:
  ✗ Lose detailed operation history
  ✗ Harder to attribute individual changes
  ✗ Branches harder to track
```

**Option C: Store Both (Hybrid)**
```
Pros:
  ✓ Best of both worlds
  ✓ Fast reads (versions)
  ✓ Complete history (operations)
  ✓ Flexible access patterns

Cons:
  ✗ More complex
  ✗ More storage
  ✗ Need sync between operations and versions
```

**Steve's hint:** "sort of like Git, but more" → Suggests Option C

### Challenge 2: Hashing Strategy

**Problem:** How do we hash operations?

**Option A: Hash the encoding directly**
```
YJS encoding: [0x2A, 0x00, 0x05, 0x48, 0x65, 0x6C, 0x6C, 0x6F]
Hash those bytes → hash_abc

Problem:
  Different encodings = different hashes
  Same semantic content might have different hashes
```

**Option B: Hash semantic content**
```
Operation: {client: 42, clock: 0, content: "Hello"}
Normalize to canonical format (e.g., JSON)
Hash normalized form → hash_abc

Benefit:
  Same content always → same hash
  Deduplication works
  
Cost:
  Extra normalization step
```

### Challenge 3: Tombstone Immutability

**Problem:** YJS sets `deleted = true` (mutation). PromiseGrid can't mutate.

**YJS approach (mutable):**
```
Item:X exists with deleted = false
Delete operation → Change to deleted = true
Same Item, modified
```

**PromiseGrid approach (immutable):**
```
Original: hash_abc → Operation: insert 'X'
Delete:   hash_def → Operation: delete Item (42, 0)

Both exist forever
When rendering:
  - Apply insert → 'X' appears
  - Apply delete → 'X' marked invisible
  - Result: 'X' not shown
```

**Key insight:** "Deleted" is derived by replaying operations, not stored state!

### Challenge 4: Merge Function

**How do branches merge in PromiseGrid?**

**YJS approach:**
```
Merge is implicit
Operations applied deterministically
Result is a modified document
```

**PromiseGrid approach (from README):**
```
"Cascade of merge functions"
"Ultimately falling back to LLMs and finally to human intervention"

Merge creates NEW version:
  tree_a + tree_b → tree_c
  
All three exist forever:
  tree_a (branch 1)
  tree_b (branch 2)  
  tree_c (merged)
```

**Question:** Who decides which merge function to use?

### Challenge 5: Sync Protocol Translation

**YJS sync:**
```
SyncStep1: State vector
SyncStep2: Missing operations
Update: New operations
```

**PromiseGrid sync:**
```
Message = function call
Token = hash of function
Payload = arguments

How to map:
  SyncStep1 → call sync_request(state_vector)
  SyncStep2 → call sync_reply(operations)
  Update → call apply_update(operation)
  
But: Functions need to be content-addressed!
```

### Challenge 6: Garbage Collection

**YJS has garbage collection** to remove old tombstones.

**PromiseGrid cannot garbage collect** due to immutability.

**Consequences:**
```
After 1 year of editing:
  YJS: ~1000 items (current state)
  PromiseGrid: ~1,000,000 items (every operation ever)
  
Storage grows forever!

Mitigation strategies:
  1. Efficient Merkle tree organization
  2. Compression
  3. Periodic snapshots (keeping all operations)
  4. Accept that storage is cheap
```

---

## Questions for Steve

### 1. CRDT Storage Model

**Question:** 
> For the PromiseGrid CRDT, do we store just operations, just document versions, or both? I understand we keep ALL information, but I need to know the structure.

**Context:**
- Operations = detailed history, requires replay
- Versions = fast access, but less detail
- Both = hybrid approach (Git-like)

**Steve said:** "Sort of like Git, but more"

**My interpretation:** Probably both, but need confirmation on structure.

---

### 2. PromiseBase Integration

**Question:**
> How should CRDT operations map to PromiseBase's content-addressable storage? Should each operation get its own hash, or should we group them?

**Context:**
- Each operation = more hashes, more granular history
- Grouped operations = fewer hashes, efficiency

**Example:**
```
Option A: Each keystroke is a separate hash
  'H' → hash_1
  'e' → hash_2
  'l' → hash_3
  
Option B: Group by transaction/batch
  "Hello" → hash_1 (contains all 5 operations)
```

---

### 3. Merkle Trees for CRDTs

**Question:**
> Should we use PromiseBase's Merkle tree structure to organize CRDT operations/versions?

**Context:**
PromiseBase already has Merkle trees for organizing content.

**Possible structure:**
```
Document Tree:
├─ Operations Tree
│  ├─ hash_op1
│  ├─ hash_op2
│  └─ hash_op3
└─ Versions Tree
   ├─ hash_v1
   ├─ hash_v2
   └─ hash_v3
```

**Question:** Is this the right model?

---

## Next Steps

### For JJ While Steve is on Vacation (2 weeks)

**1. Deepen YJS Understanding:**
- [ ] Capture actual YJS messages with browser dev tools
- [ ] Document exact binary format with hex dumps
- [ ] Understand YJS's internal StructStore
- [ ] Study how YJS handles large documents

**2. Study PromiseBase Code:**
- [ ] Read PromiseBase source code
- [ ] Understand Merkle tree implementation
- [ ] Study content-defined chunking
- [ ] Review the WORM storage implementation

**3. Create Comparison Presentation:**
- [ ] Slides showing YJS protocol
- [ ] Comparison with PromiseGrid architecture
- [ ] Design proposals for PromiseGrid CRDT
- [ ] Pros/cons of different approaches

**4. Prototype Ideas:**
- [ ] Simple operation storage in PromiseBase
- [ ] Hash operations and store them
- [ ] Create Merkle tree of operations
- [ ] Test deduplication

**5. Document Everything:**
- [ ] Keep notes on discoveries
- [ ] Document code snippets
- [ ] Save example encodings
- [ ] Prepare questions for Steve

### Open Research Questions

**Technical Questions:**
1. How do we handle very large documents (millions of operations)?
2. What's the performance impact of replaying all operations?
3. How do we efficiently query "what did this look like on date X"?
4. Can we use PromiseGrid's capability system for access control?

**Design Questions:**
1. Should operations be self-contained or reference other operations?
2. How do we handle schema changes in operations over time?
3. What's the merge algorithm for concurrent branches?
4. How do we represent "delete" in an immutable system?

**Protocol Questions:**
1. How do we adapt state vectors to content-addressed storage?
2. What's the peer discovery mechanism?
3. How do nodes announce new operations?
4. What happens if a node is offline for months?

---

## Key Insights

### What Makes YJS Good

1. **Proven CRDT implementation** - battle-tested in production
2. **Efficient wire protocol** - minimal bytes over network
3. **Deterministic merging** - same result everywhere
4. **Offline-first** - works without connectivity
5. **Fast synchronization** - state vectors are clever

### What Makes PromiseGrid Different

1. **Complete immutability** - nothing ever changes
2. **Content addressing** - everything has a hash
3. **Audit requirements** - must preserve all history
4. **Peer-to-peer** - no central authority
5. **Capability-based** - security through capabilities

### The Core Design Challenge

> How do we get YJS's collaborative editing features (CRDT, offline, sync) while maintaining PromiseGrid's guarantees (immutability, content-addressing, complete history)?

**The answer is NOT:**
- Wrap YJS in PromiseGrid (incompatible models)
- Translate YJS protocol directly (loses immutability)

**The answer IS:**
- Learn from YJS's approach
- Design a new CRDT that fits PromiseGrid's model
- Use similar concepts (IDs, logical time, operations)
- But make everything immutable and content-addressed

---

## Glossary

**CRDT:** Conflict-free Replicated Data Type - data structure that can be updated independently and merged deterministically

**Logical Time:** Causality-based ordering (what caused what) rather than wall-clock time

**State Vector:** Compact summary of what operations a client has, mapping client ID to highest clock value

**Tombstone:** Deleted item that remains in data structure to maintain referential integrity

**Content-Addressable Storage:** System where data is addressed by its cryptographic hash rather than location

**Merkle Tree:** Tree of hashes where each node contains hashes of its children, enabling efficient verification

**Run-Length Encoding:** Compression technique that represents consecutive items as (value, count)

**Variable-Length Integer:** Encoding scheme where small numbers use fewer bytes

**Immutable:** Cannot be changed after creation

**Operation:** Atomic change to a document (insert, delete, etc.)

**Capability:** Token that grants permission to perform an action

**Promise:** In Promise Theory, a voluntary commitment that an agent makes

---

## References

**YJS:**
- Main repo: https://github.com/yjs/yjs
- Protocol repo: https://github.com/yjs/y-protocols
- Documentation: https://docs.yjs.dev/

**PromiseGrid:**
- Main repo: https://github.com/stevegt/grid-cli
- README: (included in this document)

**PromiseBase:**
- Documentation: promisebase.md (included with this document)

**Related Concepts:**
- CRDTs: https://crdt.tech/
- Promise Theory: Mark Burgess
- Content-Addressable Storage: IPFS, Git

---

## Document History

**2024-12-23:** Initial document created after day-long learning session with Claude
- Covered YJS fundamentals
- Studied YJS source code
- Mapped to PromiseGrid architecture
- Identified design challenges

**Next update:** After Steve returns from vacation (2 weeks)
