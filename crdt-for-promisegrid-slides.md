# YJS vs PromiseGrid Protocol Comparison

---


**Goal:** Understand YJS wire protocol to inform PromiseGrid CRDT design

**What I Did:**
- Studied YJS source code (y-protocols/sync.js)
- Documented message formats
- Analyzed sync mechanisms
- Compared to PromiseGrid architecture

**Time Invested:** 12+ hours of research and documentation

---

## Key Findings
**YJS Strengths:**
- Proven CRDT implementation
- Efficient binary protocol
- Minimal wire overhead
- Fast synchronization

---

## Key Findings
**YJS Limitations for PromiseGrid:**
- Allows garbage collection (data loss)
- Mutable operations (incompatible with immutability)
- No content-addressing
- Client-server OR peer-to-peer (not pure P2P)

**Conclusion:** Learn from YJS, but build PromiseGrid-native CRDT

---

## Bottom Line

**Can we use YJS directly?**
No. Fundamental incompatibilities.
**Can we wrap YJS in PromiseGrid?**
No. Would violate PromiseGrid principles.
**Can we learn from YJS?**
Yes! Concepts, not implementation.
**What should we build?**
PromiseGrid-native CRDT inspired by YJS design.

---

# Part 2: YJS Protocol Overview
**Core Concepts:**
- Operations (not states)
- Logical time (causality)
- Unique IDs (client + clock)
- Deterministic merge

---

## YJS Message Types

**Three message types in sync protocol:**

1. **SyncStep1 (type=0):** Initial sync request
   - Contains: State vector
   - Means: "What do I have?"

2. **SyncStep2 (type=1):** Sync response
   - Contains: Missing operations
   - Means: "Here's what you're missing"

3. **Update (type=2):** Incremental update
   - Contains: New operations
   - Means: "Here's what just changed"

---

## YJS Sync Flow

**Initial Synchronization:**

```
Client A                    Client B
   |                           |
   |-- SyncStep1 (state) ----->|
   |                           |
   |<- SyncStep2 (ops) --------|
   |                           |
   |-- SyncStep2 (ops) -------->|
   |                           |
   Both synchronized
```

**Ongoing Updates:**

```
User types 'X':
   |                           |
   |-- Update (op) ----------->|
   |                           |
   Both stay synchronized
```

---

## YJS Binary Format

**SyncStep1 Message:**
```
[0] [length] [state vector bytes]
 ^    ^       ^
 |    |       Map of {clientID: clock}
 |    Length of state vector
 Message type (SyncStep1)
```

**SyncStep2 Message:**
```
[1] [length] [operations bytes]
 ^    ^       ^
 |    |       Missing operations
 |    Length of operations
 Message type (SyncStep2)
```

**Update Message:**
```
[2] [length] [operation bytes]
 ^    ^       ^
 |    |       New operation
 |    Length of operation
 Message type (Update)
```

---

## YJS Encoding Efficiency

**Variable-Length Integers:**
- Small numbers: 1 byte
- Medium numbers: 2 bytes
- Large numbers: 3+ bytes

**Run-Length Encoding:**
- Typing "Hello" = 1 struct (not 5)
- Groups consecutive operations

**State Vectors:**
- Compact summary (not full operation list)
- Example: {42: 100} instead of listing ops 0-100

**Result:** Minimal bytes over network

---

## YJS Data Model

**Internal Structure:**
- Document = Linked list of Items
- Each Item = one character/element
- Items have unique IDs (client, clock)
- Deletions = tombstones (deleted=true)

**Example:**
```
Document: "Hello"

[H] -> [e] -> [l] -> [l] -> [o]
 |      |      |      |      |
(42,0) (42,1) (42,2) (42,3) (42,4)
```

---

## YJS Tombstones

**When you delete 'e':**

```
Before:
[H] -> [e] -> [l] -> [l] -> [o]

After:
[H] -> [e(deleted)] -> [l] -> [l] -> [o]
```

**Item 'e' stays in structure, just marked deleted**

**Why?**
- Concurrent operations might reference it
- Maintains referential integrity
- Prevents broken links

**Problem for PromiseGrid:**
- YJS can garbage collect tombstones
- This loses history (incompatible with audit requirements)

---

# Part 3: PromiseGrid Protocol Overview

---

## PromiseGrid Architecture

**What PromiseGrid Is:**
- Decentralized computing system
- Content-addressable storage
- Capability-based security
- Consensus-based governance

**Core Principles:**
- Everything immutable
- Everything content-addressed
- Everything preserved forever
- Pure peer-to-peer

---

## PromiseGrid Message Model

**Messages are Function Calls:**

```
Message = capability token + payload
```

**Where:**
- Token = hash of the function
- Payload = arguments to function
- Message = function call

**Example:**
```
Message to insert 'H':
  Token: hash("insert_character")
  Payload: {client: 42, clock: 0, content: "H"}
```

---

## PromiseGrid Protocol Structure

**From README:**

```
"A message consists of a capability token followed by a payload"
"The token is the hash of the function that will fulfill the promise"
"A message can contain one or more messages in its payload"
```

**Key difference from YJS:**
- YJS: Type byte + data
- PromiseGrid: Function hash + arguments

---

## PromiseBase Storage

**Content-Addressable Storage (CAS):**
- Every piece of data gets a hash
- Hash = permanent address
- Same content = same hash
- Automatic deduplication

**Merkle Trees:**
- Organize hashes hierarchically
- Root hash = proof of all children
- Efficient verification

**WORM (Write Once Read Many):**
- Data never changes
- Data never deleted
- Perfect audit trail

---

## PromiseGrid Requirements

**For CRDT implementation, PromiseGrid needs:**

1. **Immutability:** Nothing ever changes
2. **Content-addressing:** Everything has a hash
3. **Complete history:** No data loss ever
4. **Peer-to-peer:** Fully decentralized
5. **Audit trail:** Full provenance

**These are NON-NEGOTIABLE for:**
- Legal compliance
- Medical records
- Financial audits
- National labs
- High-stakes collaboration

---

# Part 4: Side-by-Side Comparison

---

## Protocol Comparison Matrix

| Aspect | YJS | PromiseGrid |
|--------|-----|-------------|
| **Message Format** | Type byte + data | Function hash + args |
| **Encoding** | Binary (varUint) | Content-addressed |
| **State** | Mutable | Immutable |
| **History** | Optional GC | Mandatory preservation |
| **Addressing** | Position-based | Hash-based |
| **Architecture** | Client-server OR P2P | Pure P2P |
| **Deletion** | Tombstones (can GC) | Operations (never deleted) |
| **Sync** | State vectors | Message exchange |

---

## Message Format Comparison

**YJS SyncStep1:**
```
[0] [length] [state vector]
 ^    ^       ^
 |    |       What I have
 |    Size
 Type
```

**PromiseGrid Equivalent:**
```
[hash_sync_request] [state_vector_hash]
 ^                   ^
 |                   Argument (hash of state)
 Function address
```

**Key Difference:**
- YJS: Type is a number (0, 1, 2)
- PromiseGrid: Type is a hash (content-addressed function)

---

## Sync Mechanism Comparison

**YJS Sync:**
1. Exchange state vectors
2. Calculate missing operations
3. Send missing operations
4. Apply operations

**PromiseGrid Sync (proposed):**
1. Call sync_request(state_hash)
2. Receive sync_reply(operations_hash)
3. Retrieve operations by hash
4. Apply operations (store in PromiseBase)

**Similarity:**
Both use state summaries to minimize data transfer

**Difference:**
PromiseGrid uses content-addressing throughout

---

## Storage Comparison

**YJS Storage:**
```
In-memory linked list:
[Item] -> [Item] -> [Item]

Can save to:
- IndexedDB
- File system
- Database
```

**PromiseGrid Storage:**
```
PromiseBase (content-addressed):
hash_op1 -> Operation 1
hash_op2 -> Operation 2
hash_tree -> Tree [hash_op1, hash_op2, ...]

Everything immutable, forever
```

**Key Difference:**
- YJS: Mutable storage, optional persistence
- PromiseGrid: Immutable storage, mandatory persistence

---

## Deletion Comparison

**YJS Deletion:**
```
Insert 'H': Create Item
Delete 'H': Set Item.deleted = true
Garbage Collect: Remove Item completely

Result: History can be lost
```

**PromiseGrid Deletion:**
```
Insert 'H': hash_abc -> Operation(insert 'H')
Delete 'H': hash_def -> Operation(delete Item_abc)

Both operations exist forever

Result: History always preserved
```

**Fundamental Incompatibility:**
- YJS mutates and can delete
- PromiseGrid never mutates, never deletes

---

## Efficiency Comparison

**YJS Efficiency:**
- Variable-length encoding: 1-3 bytes per number
- Run-length encoding: Group operations
- State vectors: Compact summaries
- Result: Very small messages

**PromiseGrid Efficiency:**
- Content-addressing: 32-64 bytes per hash
- Merkle trees: Hierarchical organization
- Deduplication: Same content = same hash
- Result: Larger individual messages, but deduplication

**Trade-off:**
- YJS: Optimized for wire size
- PromiseGrid: Optimized for immutability and verification

---

# Part 5: Can YJS Messages Be Wrapped in PromiseGrid?

---

## The Wrapping Question

**Could we do this?**
```
PromiseGrid Message:
  Token: hash("yjs_sync")
  Payload: [YJS binary message]
```

**Answer: Technically yes, but fundamentally wrong**

Let me explain why...

---

## Why Wrapping Fails: Problem 1 - State Mutation

**YJS expects mutable state:**
```
YJS: "Update Item 42 to deleted=true"
PromiseGrid: "Nothing can change after creation"
```

**What would happen:**
```
1. Receive YJS update message
2. Unwrap from PromiseGrid message
3. Try to apply update
4. YJS tries to mutate document
5. CONFLICT with immutability
```

**Resolution:** Would need to translate, not wrap

---

## Why Wrapping Fails: Problem 2 - Garbage Collection

**YJS can garbage collect:**
```
User: "Select all, delete"
YJS: "Create new empty document, GC old data"
```

**PromiseGrid cannot:**
```
User: "Select all, delete"
PromiseGrid: "Create delete operations for all Items"
              "Store all delete operations"
              "Keep all original insert operations"
              "Never remove anything"
```

**Wrapping YJS messages would import YJS's GC behavior**

---

## Why Wrapping Fails: Problem 3 - Addressing

**YJS uses positions:**
```
"Insert 'X' at position 5"
```

**PromiseGrid uses hashes:**
```
"Insert 'X' at hash_abc"
```

**Positions change, hashes don't:**
```
YJS: Position 5 might be different after edits
PromiseGrid: hash_abc always refers to same Item
```

**Can't wrap position-based protocol in hash-based system**

---

## Why Wrapping Fails: Problem 4 - State Vectors

**YJS state vector:**
```
{
  client 42: clock 100,
  client 99: clock 50
}
```

**This is mutable state!**
- Changes as operations arrive
- Can't be content-addressed (always changing)

**PromiseGrid needs:**
```
Each state vector gets a hash
State vectors are immutable snapshots
```

**Wrapping preserves YJS's mutability**

---

## What Would Happen If We Tried

**Scenario: Wrap YJS in PromiseGrid**

```
Step 1: Receive YJS update wrapped in PromiseGrid message
Step 2: Extract YJS update from PromiseGrid payload
Step 3: Apply YJS update to YJS document
Step 4: YJS modifies its internal state

Problem: We just violated immutability!

Step 5: Try to store in PromiseBase
Step 6: PromiseBase says "what do I store?"
        - The mutable YJS document?
        - How do I hash something that changes?

FAILURE
```

---

## Conclusion on Wrapping

**Direct wrapping: NO**

**Reasons:**
1. YJS mutations violate immutability
2. YJS GC violates history preservation
3. YJS positions incompatible with hashes
4. YJS state vectors are mutable

**Alternative: Translation, not wrapping**

---

# Part 6: What Would Need to Change

---

## Changes Required: High-Level

To adapt YJS concepts for PromiseGrid:

1. **Replace mutations with immutable operations**
2. **Replace positions with content addresses**
3. **Replace state vectors with immutable snapshots**
4. **Remove garbage collection**
5. **Add Merkle tree organization**
6. **Implement in terms of PromiseGrid messages**

Let's look at each...

---

## Change 1: Immutable Operations

**YJS Approach:**
```
Item exists in memory
Update Item's deleted field
Item mutated
```

**PromiseGrid Approach:**
```
Operation 1 exists: hash_abc -> insert('H')
Operation 2 exists: hash_def -> delete(hash_abc)

Both exist forever
Rendering: apply both, 'H' not shown
```

**What changes:**
- No in-place modification
- Every change = new operation with new hash
- Deletion = operation, not mutation

---

## Change 2: Content-Addressed References

**YJS Approach:**
```
Insert 'X' after Item at position 5
```

**PromiseGrid Approach:**
```
Insert 'X' after Item at hash_abc
```

**What changes:**
- Replace position integers with hashes
- Items reference each other by hash
- Links never break (hashes don't change)

**Benefit:**
- Referential integrity guaranteed
- No "position shifted" bugs

---

## Change 3: Immutable State Vectors

**YJS Approach:**
```
State vector is updated as ops arrive:
  {42: 5}  -> {42: 6}  -> {42: 7}
Same object, mutated
```

**PromiseGrid Approach:**
```
Each state vector is immutable:
  hash_sv1 -> {42: 5}
  hash_sv2 -> {42: 6}
  hash_sv3 -> {42: 7}

Different hashes, all preserved
```

**What changes:**
- State vectors become immutable snapshots
- Each version gets its own hash
- Can reference any historical state

---

## Change 4: No Garbage Collection

**YJS Approach:**
```
Tombstones can be removed after:
- All clients have seen the delete
- Enough time has passed
```

**PromiseGrid Approach:**
```
Tombstones never removed:
- All operations preserved forever
- Complete audit trail
- Can reconstruct any historical state
```

**What changes:**
- Remove all GC code
- Accept that storage grows
- Use compression and Merkle trees for efficiency

**Trade-off:**
- More storage required
- But complete history preserved

---

## Change 5: Merkle Tree Organization

**YJS Approach:**
```
Operations stored in flat list or by client
```

**PromiseGrid Approach:**
```
Operations organized in Merkle trees:

Tree Root: hash_root
  ├─ Branch 1: hash_branch1
  │  ├─ Op 1: hash_op1
  │  └─ Op 2: hash_op2
  └─ Branch 2: hash_branch2
     ├─ Op 3: hash_op3
     └─ Op 4: hash_op4

Root hash proves all operations
```

**What changes:**
- Add Merkle tree layer
- Operations grouped efficiently
- Can verify without retrieving all operations

---

## Change 6: Message-as-Function-Call

**YJS Approach:**
```
Binary message:
[type byte] [data bytes]
```

**PromiseGrid Approach:**
```
Message = function call:
[function hash] [argument hashes]
```

**Example transformation:**

**YJS:**
```
[0] [length] [state vector]
```

**PromiseGrid:**
```
hash("sync_request") hash(state_vector)
  ^                   ^
  Function to call    Argument
```

**What changes:**
- Replace type bytes with function hashes
- Payload becomes function arguments
- Everything content-addressed

---

## Change 7: Storage Model

**YJS Approach:**
```
Store: YJS document (mutable)
Optional: Persist updates
```

**PromiseGrid Approach:**
```
Must store: Every operation (immutable)
Organization: In PromiseBase
Format: Content-addressed blocks + trees
```

**What changes:**
- Store operations, not document state
- Or store both (operations + snapshots)
- Use PromiseBase as storage layer

**Question for Steve:**
Store operations only? Snapshots only? Both?

---

## Summary of Changes

| Aspect | YJS | PromiseGrid Change |
|--------|-----|-------------------|
| Operations | Mutations | Immutable operations |
| References | Positions | Content hashes |
| State vectors | Mutable | Immutable snapshots |
| Garbage collection | Allowed | Forbidden |
| Organization | Flat/client-grouped | Merkle trees |
| Messages | Type + data | Function + args |
| Storage | Optional | Mandatory (PromiseBase) |

**Bottom line:** Major architectural changes required

---

# Part 7: Recommendations

---

## Recommendation 1: Don't Use YJS Directly

**Why:**
- Fundamental incompatibilities
- Would violate PromiseGrid principles
- Would compromise audit requirements
- Can't wrap, can't translate easily

**Instead:**
- Build PromiseGrid-native CRDT
- Learn from YJS design
- Reuse concepts, not code

---

## Recommendation 2: Reuse YJS Concepts

**What to reuse:**

1. **Operation-based CRDT**
   - Send operations, not states
   - Works well, proven approach

2. **Logical time + unique IDs**
   - (client, clock) for unique IDs
   - Deterministic merge

3. **State vector approach**
   - Efficient sync
   - Minimal data transfer
   - Just make them immutable

4. **Peer-to-peer capable**
   - YJS supports P2P
   - PromiseGrid requires it

---

## Recommendation 3: Design from PromiseGrid Principles

**Start with requirements:**

1. Everything immutable
2. Everything content-addressed
3. Everything preserved
4. Peer-to-peer
5. Audit trail

**Then add CRDT features:**
- Operations with unique IDs
- Deterministic merge
- Conflict-free
- Offline-capable

**Not the other way around!**

---

## Recommendation 4: Storage Strategy

**Proposed approach:**

1. **Store operations in PromiseBase**
   - Each operation = content block
   - Gets content-addressed hash
   - Immutable forever

2. **Organize in Merkle trees**
   - Tree of operations
   - Efficient verification
   - Compact references

3. **Optional: Periodic snapshots**
   - For fast access
   - Don't replace operations
   - Also content-addressed

**Question for Steve:** Confirm this approach?

---

## Recommendation 5: Protocol Design

**Proposed PromiseGrid CRDT protocol:**

**Sync Request:**
```
Message:
  Function: hash("sync_request")
  Args: hash(immutable_state_vector)
```

**Sync Reply:**
```
Message:
  Function: hash("sync_reply")
  Args: hash(merkle_tree_of_operations)
```

**Update:**
```
Message:
  Function: hash("apply_operation")
  Args: hash(operation)
```

**All messages follow PromiseGrid's message-as-function-call model**

---

## Recommendation 6: Phased Development

**Phase 1: Research (DONE)**
- Understand YJS
- Document protocol
- Identify incompatibilities

**Phase 2: Design (NEXT)**
- Spec out PromiseGrid CRDT
- Define message formats
- Design storage schema

**Phase 3: Prototype**
- Implement basic operations
- Test sync
- Verify immutability

**Phase 4: Integration**
- Integrate with PromiseBase
- Test with Storm
- Performance testing

---

# Part 8: Questions for Discussion

---

## Design Questions

1. **Storage Model:**
   - Store operations only?
   - Store snapshots only?
   - Store both?

2. **Merkle Tree Organization:**
   - How to structure trees?
   - How deep?
   - How to balance?

3. **Sync Protocol:**
   - Use state vectors (immutable)?
   - Or different approach?
   - How to handle large documents?

---

## Implementation Questions

4. **Operation Format:**
   - What fields in an operation?
   - How to serialize?
   - How to hash?

5. **Deletion Semantics:**
   - How to represent delete in immutable system?
   - How to render (skip deleted items)?
   - How to handle "undelete"?

6. **Conflict Resolution:**
   - Use client ID tiebreaker (like YJS)?
   - Or different approach?
   - How to handle merges?

---

## Integration Questions

7. **PromiseBase Interface:**
   - How to map operations to PromiseBase blocks?
   - How to use Merkle trees?
   - How to query efficiently?

8. **Storm Integration:**
   - How does CRDT fit with Storm?
   - Does Storm need CRDT? Or just PromiseBase?
   - What's the architecture?

9. **Performance:**
   - How to handle millions of operations?
   - How to keep sync fast?
   - How to compress/optimize?

---

## Timeline Questions

10. **Priorities:**
    - What to build first?
    - What's minimum viable?
    - What can wait?

11. **Resources:**
    - Who works on what?
    - What's the timeline?
    - What are dependencies?

12. **Validation:**
    - How do we test?
    - What are success criteria?
    - When do we know it works?

---

# Conclusion

---

## Summary

**What We Learned:**
- YJS has excellent CRDT concepts
- YJS protocol is well-designed
- YJS is incompatible with PromiseGrid principles

**What We Recommend:**
- Build PromiseGrid-native CRDT
- Reuse YJS concepts
- Don't wrap or directly translate

**What We Need to Decide:**
- Storage strategy
- Protocol details
- Implementation approach

---

## Next Steps

**Immediate:**
1. Review this presentation
2. Discuss questions
3. Make design decisions

**Short-term:**
4. Spec out PromiseGrid CRDT
5. Design storage schema
6. Define message formats

**Medium-term:**
7. Build prototype
8. Test and iterate
9. Integrate with PromiseBase

---

## Resources

**Documentation Created:**
- yjs-promisegrid.md (comprehensive reference)
- yjs-sync-protocol-commented.js (annotated code)
- This presentation (slides.md)

**Code Reviewed:**
- y-protocols/sync.js (YJS sync protocol)
- PromiseGrid README
- PromiseBase documentation

**Time Invested:**
- 12+ hours research and documentation

---

## Thank You

**Questions?**

**Ready to discuss design decisions?**

**Let's build the PromiseGrid CRDT!**

---

# Appendix: Technical Details

---

## Appendix A: YJS Binary Format Details

**Variable-Length Integer Encoding:**

```
Value Range    | Bytes | Format
---------------|-------|--------
0-127          | 1     | 0xxxxxxx
128-16,383     | 2     | 1xxxxxxx xxxxxxxx
16,384-2M      | 3     | 1xxxxxxx 1xxxxxxx xxxxxxxx
...
```

**State Vector Encoding:**

```
[num_clients] [client1] [clock1] [client2] [clock2] ...
    ^            ^         ^
    |            |         Highest clock for client1
    |            Client ID
    How many clients
```

---

## Appendix B: PromiseGrid Message Examples

**Hypothetical sync_request:**

```
Token: sha256("sync_request_v1") = 0xabc123...
Payload: sha256({42: 5, 99: 7}) = 0xdef456...

Message: [0xabc123...][0xdef456...]
```

**Hypothetical apply_operation:**

```
Token: sha256("apply_operation_v1") = 0x789abc...
Payload: sha256({
  type: "insert",
  id: (42, 0),
  content: "H"
}) = 0xfed321...

Message: [0x789abc...][0xfed321...]
```

---

## Appendix C: Comparison to Other CRDTs

**YJS vs Automerge:**
- Both: Operation-based CRDTs
- YJS: Binary encoding, faster
- Automerge: JSON-friendly, easier debugging

**YJS vs Operational Transform (OT):**
- YJS: Commutative, no central server needed
- OT: Requires server, order-dependent

**PromiseGrid CRDT vs YJS:**
- Both: Operation-based
- PromiseGrid: Immutable, content-addressed
- YJS: Mutable, position-addressed

---

## Appendix D: Performance Considerations

**YJS Performance:**
- Sync: O(missing operations)
- Apply: O(1) per operation
- Memory: O(document size + tombstones)

**PromiseGrid CRDT (estimated):**
- Sync: O(missing operations)
- Apply: O(1) per operation + hash computation
- Storage: O(all operations ever) - grows forever
- Retrieval: O(log n) with Merkle trees

**Trade-off:**
- YJS: Optimized for speed
- PromiseGrid: Optimized for auditability

---

## Appendix E: Security Considerations

**YJS Security:**
- No built-in authentication
- No access control
- Trust-based collaboration

**PromiseGrid Security:**
- Capability-based access control
- Cryptographic verification
- Tamper-proof (content-addressed)
- Audit trail (immutable history)

**PromiseGrid CRDT must preserve security model**

---

## Appendix F: References

**YJS:**
- Repository: github.com/yjs/yjs
- Protocol: github.com/yjs/y-protocols
- Docs: docs.yjs.dev

**PromiseGrid:**
- Repository: github.com/stevegt/grid-cli
- PromiseBase: (documentation provided)

**CRDT Background:**
- crdt.tech
- "Conflict-free Replicated Data Types" (Shapiro et al.)

---

## End of Presentation

**Files Delivered:**
1. slides.md (this presentation)
2. yjs-promisegrid.md (detailed reference)
3. yjs-sync-protocol-commented.js (annotated code)

**Ready for discussion with Steve**
