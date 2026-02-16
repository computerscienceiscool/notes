# TODO 012.3 - Integration Boundaries Analysis

## The Core Question
How should Storm integrate with collab-web-editor and llm-runtime without creating unmaintainable coupling?

## Why This Matters
- **Wrong boundaries = technical debt**: Tight coupling makes it hard to evolve components independently
- **Right boundaries = flexibility**: Clean interfaces let each component improve without breaking others
- **"Move everything in" is tempting but dangerous**: Creates a monolith that becomes harder to maintain over time

## Current Component Landscape

### Storm (stevegt/grokker/x/storm)
- **Language**: Go
- **Strengths**: Multi-user discussions, file management, project state, LLM-proposed edits with review gates
- **Architecture**: Server-side application
- **Current state**: Has roadmap items that overlap with TODO 006 needs

### collab-web-editor (computerscienceiscool/collab-web-editor) 
- **Language**: JavaScript/TypeScript (Node.js + browser)
- **Strengths**: Real-time collaborative editing, Automerge CRDT, CodeMirror, offline support
- **Architecture**: Client-server (sync server + awareness server + web client)
- **Current state**: Extracted, production-ready, well-documented
- **Protocols**: Automerge WebSocket (port 1234), Awareness JSON (port 1235)

### llm-runtime (computerscienceiscool/llm-runtime)
- **Language**: Go
- **Strengths**: Secure containerized LLM-to-repository bridge, file I/O, command execution, semantic search
- **Architecture**: CLI tool with Docker containers for all operations + Ollama for search
- **Current state**: Production-ready, comprehensive documentation, 40+ Go packages
- **Key features**: 
  - File read/write in isolated containers
  - Whitelisted command execution in Docker
  - Semantic search via Ollama embeddings
  - Audit logging, container pooling for performance

## Integration Pattern Options (from TODO 011.5)

### Pattern 1: Link-Only (iframe embed)
**What it is**: Storm serves an iframe that loads collab-web-editor
```
┌─────────────────────────────────┐
│  Storm UI (Go templates/React)  │
│  ┌───────────────────────────┐  │
│  │  <iframe>                 │  │
│  │    collab-web-editor      │  │
│  │  </iframe>                │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

**Pros:**
- Zero coupling - each component deploys independently
- Can update collab-web-editor without touching Storm
- Each team works in their own repo with their own tools
- Easiest to implement today

**Cons:**
- Limited integration - no shared state between Storm and editor
- UX feels "bolted on" rather than integrated
- Hard to share user identity/permissions across iframe boundary
- Two separate network connections, separate auth

**When to use**: MVP/prototype phase, quick experiments, low integration needs

### Pattern 2: Bridge (shared awareness/presence)
**What it is**: Storm imports `@collab-editor/awareness` npm package to share user presence
```
┌─────────────────────────────────────┐
│  Storm (Go)                         │
│    ├─ WebSocket server              │
│    └─ Awareness protocol bridge ────┼──► collab-awareness protocol
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  collab-web-editor                  │
│    └─ connects to Storm WS          │
└─────────────────────────────────────┘
```

**Pros:**
- Moderate coupling - only through well-defined protocol (JSON messages)
- Storm can show "who's editing what" from its Go code
- collab-web-editor remains independent but Storm-aware
- Can version the protocol independently of implementations

**Cons:**
- Storm needs to run Node.js or reimplement awareness protocol in Go
- Two-language maintenance (Go + JavaScript)
- More complex deployment (need both runtimes)

**When to use**: When you need shared presence/cursors but want to keep repos separate

### Pattern 3: Deep Integration (shared Automerge state)
**What it is**: Storm directly manipulates the same Automerge CRDT documents
```
┌─────────────────────────────────────┐
│  Storm (Go)                         │
│    └─ Automerge Go library          │
│         │                            │
│         ▼                            │
│    Shared CRDT Document ◄───────────┼──► Automerge sync protocol
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│  collab-web-editor (JavaScript)     │
│    └─ Automerge JS library          │
└─────────────────────────────────────┘
```

**Pros:**
- True real-time collaboration - Storm and editor see same state instantly
- Single source of truth for document content
- Can build unified features (Storm AI edits → visible in editor immediately)
- Best UX - feels like one integrated product

**Cons:**
- Tight coupling - both sides must understand Automerge format
- Requires Automerge library in Go (may not exist or be immature)
- Breaking changes in Automerge affect both sides
- Hard to change document schema without coordinating releases
- "Move everything in" temptation - leads to monolith

**When to use**: When real-time collaborative editing is core feature and worth the coupling cost

## Integration Boundary for llm-runtime

**Recommended: Pattern 1 (Service) - HTTP/gRPC API**

llm-runtime is a **complete, standalone Go application** that provides secure LLM-repository interaction. It has:
- Well-defined CLI interface (processes `<open>`, `<write>`, `<exec>`, `<search>` commands)
- No overlap with Storm's functionality
- Heavy Docker dependencies (all operations containerized)
- Clean separation of concerns

**Integration approach:**

```
┌─────────────────────────────────┐
│  Storm (Go)                     │
│    └─ HTTP/gRPC client ─────────┼──► llm-runtime service
└─────────────────────────────────┘    │
                                       ├─ Docker (file I/O)
                                       ├─ Docker (exec)
                                       └─ Ollama (search)
```

**Implementation:**
1. **Expose llm-runtime as service**: Add HTTP/gRPC server wrapper around existing CLI
2. **Storm calls via API**: Send commands, receive results
3. **Keep repos separate**: Storm and llm-runtime evolve independently
4. **Protocol versioning**: Use API versioning for compatibility

**Why service pattern works:**
- ✅ **Clean separation**: Storm doesn't need to understand Docker/Ollama internals
- ✅ **Same language**: Both Go, but still loose coupling via protocol
- ✅ **Independent scaling**: Can run llm-runtime separately with its own resources
- ✅ **Security boundary**: llm-runtime handles all sandboxing/containerization
- ✅ **No code sharing needed**: llm-runtime is complete as-is

**Alternative (if service is too heavy):**
Could run llm-runtime as **subprocess** and communicate via stdin/stdout (it already works this way). Storm would spawn `llm-runtime` process, send commands, parse results. Simpler than HTTP but less flexible.

## Decision Framework

### For collab-web-editor integration:
**Recommend starting with Pattern 1 (iframe embed) because:**
1. **Fastest to ship**: No code changes to either component
2. **Lowest risk**: Can't break either component by accident
3. **Validate assumptions**: Let real usage tell us what integration we actually need
4. **Easy to upgrade**: If we need Pattern 2 or 3 later, we'll know why

**Progression path:**
- **v0 (MVP)**: Pattern 1 - iframe embed, get it in front of planning group
- **v1**: Pattern 2 - if we discover we need shared presence/awareness
- **v2**: Pattern 3 - only if real-time collaborative editing becomes critical requirement

### For llm-runtime integration:
**Need more information first:**
- Investigate what llm-runtime does
- Compare with Storm's existing LLM capabilities
- Determine overlap vs gaps
- Then choose pattern based on findings

## Key Principles for Integration Boundaries

1. **Start loose, tighten only when needed**
   - Loose coupling is easier to tighten than tight coupling is to loosen
   - Let real usage drive integration depth

2. **Protocol over code sharing**
   - Define clean protocols (HTTP, WebSocket, JSON)
   - Let each side implement protocol in their preferred language
   - Version protocols independently of implementations

3. **Resist "move everything in"**
   - Only move code that is:
     - Small (<1000 lines)
     - Stable (not changing frequently)
     - Truly shared (used by 3+ components)
   - Otherwise: keep as separate repo/service and integrate via protocol

4. **Make coupling explicit**
   - Document dependencies clearly
   - Use semantic versioning for protocols
   - Write integration tests at boundaries

5. **Plan for change**
   - Assume each component will evolve independently
   - Design boundaries that can accommodate version skew
   - Prefer optional features over required dependencies

## Recommended Next Steps

### Immediate (this week):
1. ~~**Investigate llm-runtime**~~ ✅ **COMPLETE**
   - **Finding**: Production-ready Go tool for secure LLM-repository interaction
   - **Recommendation**: Integrate as **service** (HTTP API) or **subprocess**
   - **No overlap** with Storm - complementary functionality

2. **Decide llm-runtime integration approach**
   - **Option A (recommended)**: Run as service with HTTP/gRPC API
   - **Option B (simpler)**: Run as subprocess, communicate via stdin/stdout
   - **Trade-off**: Service = more flexible, subprocess = simpler to start
   - **Action**: Prototype subprocess integration first (it already works this way)

3. **Validate iframe integration for collab-web-editor**
   - Prototype Storm serving collab-web-editor in iframe
   - Test with planning group for one session
   - Document pain points

### Short-term (next sprint):
4. **Implement TODO 006 MVP with Pattern 1**
   - Ship working integration quickly
   - Gather real usage data
   - Identify actual integration needs

5. **Monitor integration points**
   - Track what breaks when
   - Note where loose coupling hurts
   - Note where tight coupling would help

### Medium-term (next month):
6. **Re-evaluate based on usage**
   - Did iframe pattern work? 
   - What integration did we actually need?
   - Upgrade to Pattern 2 or 3 only if needed

## Questions to Answer

1. ~~**What does llm-runtime do?**~~ ✅ **ANSWERED**: Secure LLM-repository bridge (file ops, exec, search) via Docker
2. **What does Storm's LLM integration look like today?** (need to review Storm code)
3. **Do we need real-time collaborative editing for TODO 006?** (ask planning group)
4. **Are we building for developers or non-technical users?** (affects UI integration needs)
5. **What's our deployment model?** (single-user, multi-tenant, self-hosted?)

## Anti-Patterns to Avoid

❌ **"Let's just merge the repos"** - Creates monolith, loses ability to evolve independently  
❌ **"We'll fix the boundaries later"** - Technical debt compounds, never gets fixed  
❌ **"It's just a quick hack"** - Quick hacks become permanent architecture  
❌ **"More integration = better UX"** - Often false; clean separation can improve UX  
❌ **"We need feature X so we must tightly couple"** - Usually a failure of API design  

## Success Criteria

✅ Each component can be developed, tested, deployed independently  
✅ Clear, documented protocols at boundaries  
✅ Can upgrade one component without breaking others  
✅ New team member can contribute to one component without understanding all others  
✅ Integration complexity lives in well-defined bridge layer, not spread throughout codebases  

---

## Recommendation Summary

**For collab-web-editor:**
- Start with **Pattern 1** (iframe embed)
- Ship MVP quickly
- Upgrade to Pattern 2 or 3 only if real usage demands it

**For llm-runtime:**
- Use **Pattern 1** (Service/Subprocess)
- **Start simple**: Run as subprocess, communicate via stdin/stdout (already works)
- **Evolve if needed**: Wrap in HTTP/gRPC service later for scalability
- **Keep separate**: Don't merge into Storm - it's a complete tool with no overlap
- **Benefits**: Storm gets secure LLM-repository interaction without Docker complexity

**Overall philosophy:**
- **Start loose, tighten only when needed**
- **Protocol over code sharing**
- **Real usage drives integration depth**
