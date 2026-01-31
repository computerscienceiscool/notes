# Storm and Vimbeam Integration: Issues and Concerns

## Executive Summary

This document outlines the architectural challenges of transitioning storm from a single-user application to a multi-user collaborative system using vimbeam as the real-time synchronization mechanism. While vimbeam is functionally complete as a collaborative text editor, storm's current architecture makes several assumptions incompatible with real-time collaborative editing.

**Key Finding**: The integration challenges stem from storm's design, not vimbeam's capabilities. Storm requires fundamental architectural changes to support collaborative editing.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Critical Problems](#critical-problems)
3. [Design Decisions Required](#design-decisions-required)
4. [Integration Challenges](#integration-challenges)
5. [Recommended Refactoring Path](#recommended-refactoring-path)
6. [Vimbeam Considerations](#vimbeam-considerations)
7. [Technical Details](#technical-details)

---

## Architecture Overview

### Current Storm Architecture (Single-User)

```
┌─────────────┐
│   Browser   │
│  (Web UI)   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐      ┌──────────────┐
│Storm Server │─────▶│  Chat.history│
│  (Go)       │      │  (in-memory) │
└──────┬──────┘      └──────────────┘
       │
       │ Batch Write
       ▼
┌─────────────┐
│ Markdown    │
│ File        │
└─────────────┘
```

**Characteristics**:
- Single source of truth: in-memory `Chat.history`
- Periodic full-file rewrites to disk
- File read only at startup
- No monitoring of external file changes
- File locking via `flock`

### Target Architecture (Multi-User with Vimbeam)

```
┌─────────────┐                    ┌─────────────┐
│  Browser A  │                    │  Browser B  │
│  (Storm UI) │                    │  (Storm UI) │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │ HTTP/WS                          │ HTTP/WS
       ▼                                  ▼
┌──────────────────────────────────────────────┐
│           Storm Server (Go)                  │
│  - Watches file for changes                  │
│  - Parses markdown on demand                 │
│  - Pushes updates via WebSocket              │
└──────────────────┬───────────────────────────┘
                   │
                   │ Read/Parse
                   ▼
            ┌─────────────┐
            │  Markdown   │◀──────┐
            │  File       │       │
            └─────────────┘       │
                   ▲              │
                   │              │
            Automerge Sync    Automerge Sync
                   │              │
                   │              │
            ┌──────┴──────┐  ┌───┴────────┐
            │  Neovim A   │  │  Neovim B  │
            │  (vimbeam)  │  │  (vimbeam) │
            └─────────────┘  └────────────┘
```

**Required Characteristics**:
- Automerge document is source of truth
- Storm reads file continuously (file watcher)
- Storm never overwrites entire file
- CRDTs handle concurrent edits
- No file locking (conflicts resolved via Automerge)

---

## Critical Problems

### 1. Dual Source of Truth ⚠️ CRITICAL

**Current Behavior**:
```go
type Chat struct {
    mutex    sync.Mutex
    history  []*ChatRound  // In-memory source of truth
    filename string
}

func (c *Chat) StartRound(query, selection string) (r *ChatRound) {
    round := &ChatRound{Query: query}
    c.history = append(c.history, round)  // Only updates memory
    return round
}
```

**Problem**:
- Storm maintains chat state in memory (`Chat.history`)
- File writes are periodic snapshots of in-memory state
- Vimbeam edits change the file but not storm's memory
- Storm's memory becomes stale immediately after any vimbeam edit

**Impact**:
- User A edits via vimbeam → changes file
- User B sees stale data in storm web UI
- User B's storm generates response → overwrites User A's edits
- Data loss and confusion

**Evidence from Code**:
```go
func (c *Chat) getHistory(lock bool) string {
    // Generates markdown from in-memory c.history
    // Never reads from file after initialization
    for _, msg := range c.history {
        if msg.Response == "" {
            continue
        }
        result += fmt.Sprintf("\n\n**%s**\n", msg.Query)
        result += fmt.Sprintf("\n\n%s\n\n---\n\n", msg.Response)
    }
    return result
}
```

### 2. Full-File Overwrites ⚠️ CRITICAL

**Current Behavior**:
```go
func (c *Chat) _updateMarkdown() error {
    content := c.getHistory(false)  // Regenerate entire file from memory
    
    // Write to temp file
    tempFile, err := ioutil.TempFile("", "storm-chat-*.md")
    tempFile.WriteString(content)
    tempFile.Close()
    
    // OVERWRITE original file
    os.Rename(tempFile.Name(), c.filename)
    return nil
}
```

**Problem**:
- Every storm update regenerates the **entire** file from scratch
- Any concurrent edits in the file are obliterated
- Automerge will see this as deletion of entire document + insertion of new content
- Massive CRDT operations instead of surgical edits

**Impact**:
- Poor sync performance (large deltas)
- Bloated Automerge document history
- Lost edits from vimbeam users
- Network bandwidth waste

**Scenario**:
```
Time 0: File has 1000 lines
Time 1: User A (vimbeam) edits line 500
Time 2: User B (storm) adds response → _updateMarkdown() rewrites all 1000 lines
Result: User A's edit on line 500 is lost
```

### 3. No File Change Detection ⚠️ HIGH

**Current Behavior**:
```go
func NewChat(filename string) *Chat {
    // Read file ONCE at startup
    if _, err := os.Stat(filename); err == nil {
        content, _ := ioutil.ReadFile(filename)
        // Parse content into c.history
    }
    // Never reads file again
    return &Chat{history: history, filename: filename}
}
```

**Problem**:
- File is read only when `NewChat()` is called
- No mechanism to detect external file modifications
- Storm web UI will show stale data indefinitely

**Impact**:
- User A adds content via vimbeam
- User B's storm UI never updates
- Users see different versions of the chat
- Collaborative experience broken

### 4. Structured Content Fragility ⚠️ HIGH

**Current Parser Expectations**:
```go
// From split/split.go
func Parse(r io.Reader) ([]RoundTrip, error) {
    // EXPECTS specific structure:
    // 1. Bold query: **query text**
    // 2. Response body
    // 3. ## References section
    // 4. ## Reasoning section
    // 5. --- separator
    
    boldRegex := regexp.MustCompile(`^\*\*((.|\n)*?)\*\*`)
    referencesMarker := "## References"
    reasoningMarker := "## Reasoning"
    splitRegex := regexp.MustCompile(`(?m)^---[ \t]*$`)
}
```

**Problem**:
- Parser expects rigid markdown structure
- Vimbeam users can edit anywhere, breaking structure
- No validation or constraints on edits

**Impact Scenarios**:

| User Action | Result |
|-------------|--------|
| Delete `## References` heading | Parser assumes no references, misinterprets response |
| Add extra `**bold**` text | Parser treats it as a new query |
| Delete `---` separator | Adjacent rounds merge into one |
| Edit in middle of response | Storm may fail to parse on reload |

**Error Example**:
```
User A is typing in References section
User B's LLM appends new response
Result: References section now has partial response text
Parser: Returns error "no valid roundtrips found"
Storm: Cannot reload chat history
```

### 5. Concurrent Round Creation ⚠️ MEDIUM

**Current Flow**:
```go
// User A sends query
round1 := chat.StartRound(queryA, "")  // Appends to memory
response1 := sendQueryToLLM(...)
chat.FinishRound(round1, response1)    // Writes entire file

// User B sends query (before A finishes)
round2 := chat.StartRound(queryB, "")  // Appends to memory
response2 := sendQueryToLLM(...)
chat.FinishRound(round2, response2)    // Writes entire file again
```

**Problem**:
- Both rounds append to in-memory `c.history` concurrently
- Both `FinishRound()` calls do full-file rewrites
- Race condition: which write wins?
- File locking prevents simultaneous writes, but causes blocking

**Impact**:
```
Timeline:
T0: User A starts round → adds to c.history[0]
T1: User B starts round → adds to c.history[1]
T2: User A finishes → writes file with [round_A]
T3: User B finishes → writes file with [round_A, round_B]
T4: User C's vimbeam reads → sees both rounds
T5: User A's vimbeam reads → sees both rounds (didn't expect round_B)
```

### 6. Pending Round Visibility ⚠️ MEDIUM

**Current Code**:
```go
func (c *Chat) getHistory(lock bool) string {
    for _, msg := range c.history {
        if msg.Response == "" {
            continue  // Skip rounds with no response
        }
        // Only output completed rounds
    }
}
```

**Problem**:
- Rounds with empty responses are invisible to other users
- User A sends query, waits for LLM
- User B sees nothing until response completes (could be 30+ seconds)
- Poor collaborative UX

**Desired Behavior**:
```markdown
**What are the implications of quantum entanglement?**

_Waiting for response..._
```

### 7. Character Offset Complexity ⚠️ LOW

**Vimbeam Behavior**:
```javascript
// From vimbeam/lua/vimbeam/init.lua
function M.show_remote_cursor(user_id, name, color, anchor, head)
    // Uses CHARACTER offsets (not byte offsets)
    local function offset_to_pos(off)
        for i, line in ipairs(lines) do
            local line_len = vim.fn.strchars(line) + 1  // Character count
        end
    end
}
```

**Storm Behavior**:
```go
// From storm/main.go
func markdownToHTML(markdown string) string {
    re := regexp.MustCompile(`\[(\d+)\]`)  // Byte-based regex
    sections := splitMarkdown(markdown)    // String indexing
}
```

**Problem**:
- Storm uses byte-based string operations
- Vimbeam uses character-based offsets
- Unicode/emoji in markdown can cause misalignment

**Example**:
```markdown
**Query with emoji 🚀 in text**
       ^                ^
    byte 17          byte 21
    char 17          char 18
```

**Impact**: Minor - mainly affects cursor position accuracy, not data integrity

---

## Design Decisions Required

### Decision 1: Source of Truth

**Option A: Automerge Document (RECOMMENDED)**

```
File (Automerge-synced) → Storm reads → Parses on demand → Serves to UI
```

**Pros**:
- Single source of truth
- Storm becomes stateless view layer
- Vimbeam edits immediately visible
- No sync conflicts

**Cons**:
- Storm must reload file frequently
- Parse overhead on every read
- Must handle parsing failures gracefully

**Implementation**:
```go
// Remove Chat.history completely
type Chat struct {
    filename string
    watcher  *fsnotify.Watcher
}

func (c *Chat) GetRounds() ([]RoundTrip, error) {
    content, _ := ioutil.ReadFile(c.filename)
    return split.Parse(bytes.NewReader(content))
}
```

**Option B: In-Memory with Bi-Directional Sync**

```
Storm memory ↔ File (Automerge-synced) ↔ Vimbeam
```

**Pros**:
- Storm keeps fast in-memory access
- Can validate before writing

**Cons**:
- Complex: must merge changes bidirectionally
- Conflict resolution needed
- Essentially reimplementing CRDT logic

**Verdict**: Don't do this. Use Automerge's CRDT instead of reinventing.

---

### Decision 2: Editing Model

**Option A: Storm-Only Append (RECOMMENDED for MVP)**

**Rules**:
- Storm server has exclusive write access
- Only storm can append new rounds (LLM responses)
- Vimbeam users can view and scroll (read-only)
- Storm uses append-only operations (not full rewrites)

**Pros**:
- Simple to implement
- Preserves structure integrity
- No concurrent edit conflicts

**Cons**:
- Users cannot edit via vimbeam
- Less collaborative than desired

**Implementation**:
```go
func (c *Chat) AppendRound(query, response string) error {
    // Read current file
    content, _ := ioutil.ReadFile(c.filename)
    
    // Append new round (not overwrite)
    newRound := fmt.Sprintf("\n\n**%s**\n\n%s\n\n---\n\n", query, response)
    content = append(content, []byte(newRound)...)
    
    // Write back
    ioutil.WriteFile(c.filename, content, 0644)
}
```

**Option B: Full Collaborative Editing**

**Rules**:
- Anyone can edit anywhere via vimbeam
- Storm must handle corrupted structure
- Recovery mechanisms for parse failures

**Pros**:
- True collaborative editing
- Users can fix typos, improve wording

**Cons**:
- Complex error handling
- Structure can break easily
- Need UI to show parse errors

**Implementation Challenges**:
```go
func (c *Chat) GetRounds() ([]RoundTrip, error) {
    rounds, err := split.Parse(...)
    if err != nil {
        // What now?
        // - Show error in UI?
        // - Attempt auto-repair?
        // - Lock document until fixed?
        return nil, err
    }
}
```

**Option C: Hybrid - Structured Sections**

**Rules**:
- Document divided into sections
- Storm writes to "LLM Response" sections (protected)
- Users can edit "User Notes" sections (freeform)

**Example**:
```markdown
**Query**: What is quantum entanglement?

<!-- STORM-PROTECTED-START -->
Response generated by AI...
<!-- STORM-PROTECTED-END -->

<!-- USER-NOTES -->
Additional thoughts:
- This relates to Bell's theorem
- See also: EPR paradox
<!-- /USER-NOTES -->
```

**Pros**:
- Balance between structure and flexibility
- Clear boundaries

**Cons**:
- More complex parsing
- Users might delete markers
- Enforcement difficult

---

### Decision 3: Real-Time Update Mechanism

**Option A: File Watcher (RECOMMENDED)**

```go
import "github.com/fsnotify/fsnotify"

func (c *Chat) WatchFile() {
    watcher, _ := fsnotify.NewWatcher()
    watcher.Add(c.filename)
    
    for {
        select {
        case event := <-watcher.Events:
            if event.Op&fsnotify.Write == fsnotify.Write {
                // File changed - notify web UI
                c.notifyClients()
            }
        }
    }
}

func (c *Chat) notifyClients() {
    // Send WebSocket message to all connected browsers
    // Browsers reload chat content
}
```

**Pros**:
- Immediate update detection
- Low overhead
- Standard pattern

**Cons**:
- Requires WebSocket infrastructure
- File system events can be noisy

**Option B: Polling**

```go
func (c *Chat) pollFile() {
    ticker := time.NewTicker(1 * time.Second)
    for range ticker.C {
        info, _ := os.Stat(c.filename)
        if info.ModTime().After(c.lastModTime) {
            c.notifyClients()
        }
    }
}
```

**Pros**:
- Simple
- No external dependencies

**Cons**:
- 1-second delay
- Wastes CPU cycles

---

### Decision 4: LLM Query Serialization

**Problem**: Multiple users send queries simultaneously

**Option A: Queue System (RECOMMENDED)**

```go
type QueryQueue struct {
    queries chan Query
}

func (q *QueryQueue) Process() {
    for query := range q.queries {
        response := sendQueryToLLM(query)
        appendToFile(query, response)
    }
}

// User sends query
queue.queries <- Query{Text: "...", User: "Alice"}
```

**Pros**:
- Guaranteed serial execution
- No interleaving
- Fair ordering (FIFO)

**Cons**:
- Users wait longer (queued)
- Slower overall

**Option B: Concurrent with Conflict Resolution**

```go
// Both queries run in parallel
go func() {
    response1 := sendQueryToLLM(queryA)
    appendToFile(queryA, response1)  // Might conflict
}()

go func() {
    response2 := sendQueryToLLM(queryB)
    appendToFile(queryB, response2)  // Might conflict
}()
```

**Pros**:
- Faster - parallel LLM calls
- Better UX

**Cons**:
- Automerge must resolve append conflicts
- Order may be non-deterministic
- Need to ensure appends don't interleave mid-response

**Hybrid**: Use Automerge transactions
```go
func appendRoundAtomic(query, response string) {
    // This needs Automerge transaction support
    // Append entire round as single atomic operation
    vimbeam.BeginTransaction()
    vimbeam.AppendText("\n\n**" + query + "**\n\n" + response + "\n\n---\n\n")
    vimbeam.CommitTransaction()
}
```

---

### Decision 5: Data Format

**Current**: Markdown with specific structure

**Option A: Keep Markdown (RECOMMENDED for MVP)**

**Pros**:
- Human-readable
- Existing tooling works
- Easy to edit manually

**Cons**:
- Fragile structure
- Parser can break

**Option B: Switch to JSON**

```json
{
  "rounds": [
    {
      "query": "What is quantum entanglement?",
      "response": "Quantum entanglement is...",
      "references": ["[1] https://..."],
      "reasoning": "I approached this by..."
    }
  ]
}
```

**Pros**:
- Structured data
- Easier to parse
- Validation possible

**Cons**:
- Not human-readable
- Vimbeam users editing JSON is error-prone
- Breaks existing storm markdown files

**Option C: YAML**

```yaml
rounds:
  - query: |
      What is quantum entanglement?
    response: |
      Quantum entanglement is...
    references:
      - "[1] https://..."
    reasoning: |
      I approached this by...
```

**Pros**:
- More readable than JSON
- Structured
- Multi-line strings easy

**Cons**:
- Indentation-sensitive (bad for collaborative editing)
- YAML parsers can be strict

**Recommendation**: Keep markdown for MVP, but:
- Add validation/repair utilities
- Consider JSON/YAML for future versions

---

## Integration Challenges

### Challenge 1: Bootstrapping Sync

**Question**: How does storm interact with Automerge?

**Current Storm**: Directly writes files

**With Vimbeam**:
```
Storm → File → Automerge (via vimbeam node helper) → Network
```

**Options**:

**A. Storm is Automerge-Unaware (RECOMMENDED)**
- Storm treats file as regular file
- Vimbeam syncs whatever is in the file
- Simplest integration

**B. Storm Integrates Automerge Directly**
- Storm imports Automerge library
- Storm creates/joins Automerge documents
- More control, more complexity

**Implementation (Option A)**:
```go
// Storm just writes to file
func (c *Chat) AppendRound(query, response string) error {
    f, _ := os.OpenFile(c.filename, os.O_APPEND|os.O_WRONLY, 0644)
    defer f.Close()
    
    round := fmt.Sprintf("\n\n**%s**\n\n%s\n\n---\n\n", query, response)
    f.WriteString(round)
    
    // Vimbeam detects change and syncs automatically
}
```

---

### Challenge 2: Cursor Awareness

**Question**: Should storm show vimbeam users' cursors in web UI?

**Vimbeam Provides**:
- User name
- Cursor color
- Cursor position (character offset)

**Storm Could Display**:
```
Chat Window:

**What is quantum entanglement?**

Response: Quantum entanglement is...
                              ^
                         [Alice is here]
```

**Implementation**:
```javascript
// In storm's JavaScript
socket.on('cursor_update', function(data) {
    // data.userId, data.name, data.offset
    highlightPosition(data.offset, data.color, data.name);
});
```

**Value**: Nice-to-have for awareness, not critical for MVP

---

### Challenge 3: File I/O Integration

**Storm Feature**: Users select input/output files for LLM context

**Storage**: IndexedDB in browser (client-side)

**Problem**: Vimbeam users don't see file selections

**Options**:

**A. Ignore for Now**
- File selections only affect storm web users
- Vimbeam users just see resulting chat

**B. Encode in Document**
```markdown
<!-- STORM-FILES
input: file1.go, file2.go
output: result.txt
-->

**Query**: Analyze these files...
```

**C. Separate Metadata File**
```
chat.md          ← Synced via vimbeam
chat.meta.json   ← Contains file selections, not synced
```

**Recommendation**: Option A for MVP

---

### Challenge 4: Network Partitions

**Scenario**:
1. User A and B collaborate on chat
2. Network partition occurs
3. Both users continue editing
4. Network reconnects

**Automerge Handles**:
- CRDTs merge concurrent edits
- No data loss

**Storm Must Handle**:
- Reparse merged document
- Display merge conflicts if structure broke
- Potentially show both versions to users

**Example**:
```markdown
<!-- User A added this during partition -->
**Query A**: What about X?

Response A: ...

<!-- User B added this during partition -->
**Query B**: What about Y?

Response B: ...
```

**Result**: Both queries preserved, order may be unexpected

---

## Recommended Refactoring Path

### Phase 1: Make Storm Read-Only Monitor (1-2 days)

**Goal**: Storm displays vimbeam edits in real-time

**Changes**:
1. Remove `_updateMarkdown()` calls
2. Add file watcher with fsnotify
3. Reload and reparse on file changes
4. Push updates to web UI via WebSocket

**Code Changes**:
```go
// Remove this function entirely
func (c *Chat) _updateMarkdown() error {
    // DELETE
}

// Add file watching
func (c *Chat) WatchFile() error {
    watcher, err := fsnotify.NewWatcher()
    if err != nil {
        return err
    }
    
    err = watcher.Add(c.filename)
    if err != nil {
        return err
    }
    
    go func() {
        for {
            select {
            case event := <-watcher.Events:
                if event.Op&fsnotify.Write == fsnotify.Write {
                    c.broadcastUpdate()
                }
            case err := <-watcher.Errors:
                log.Printf("Watcher error: %v", err)
            }
        }
    }()
    
    return nil
}

func (c *Chat) broadcastUpdate() {
    // Parse file
    content, _ := ioutil.ReadFile(c.filename)
    rounds, err := split.Parse(bytes.NewReader(content))
    if err != nil {
        log.Printf("Parse error: %v", err)
        return
    }
    
    // Convert to HTML
    html := markdownToHTML(string(content))
    
    // Send to all WebSocket clients
    wsHub.Broadcast(map[string]interface{}{
        "type": "update",
        "html": html,
    })
}
```

**Testing**:
1. Start storm server
2. Open chat in browser
3. Edit file via vimbeam
4. Verify browser updates immediately

**Success Criteria**:
- ✅ Vimbeam edits appear in storm UI within 1 second
- ✅ No data loss
- ✅ Parse errors handled gracefully

---

### Phase 2: LLM Responses Append-Only (2-3 days)

**Goal**: Storm can add new rounds without overwriting file

**Changes**:
1. Replace full-file rewrites with append operations
2. Ensure atomic appends
3. Remove `Chat.history` in-memory state
4. Read file on demand

**Code Changes**:
```go
// Delete the entire Chat.history field
type Chat struct {
    // DELETE: history  []*ChatRound
    filename string
    watcher  *fsnotify.Watcher
    mutex    sync.Mutex
}

// Rewrite StartRound and FinishRound
func (c *Chat) AddRound(query, response string) error {
    c.mutex.Lock()
    defer c.mutex.Unlock()
    
    // Format new round
    round := fmt.Sprintf("\n\n**%s**\n\n%s\n\n## References\n\n## Reasoning\n\n---\n\n", 
        query, response)
    
    // Append to file (atomic operation)
    f, err := os.OpenFile(c.filename, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0644)
    if err != nil {
        return err
    }
    defer f.Close()
    
    _, err = f.WriteString(round)
    return err
}

// Remove StartRound/FinishRound entirely
// Replace with single AddRound call
```

**Update Query Handler**:
```go
func queryHandler(w http.ResponseWriter, r *http.Request) {
    var req QueryRequest
    json.NewDecoder(r.Body).Decode(&req)
    
    // Get LLM response
    response := sendQueryToLLM(req.Query, req.LLM, ...)
    
    // Append to file (no in-memory state)
    err := chat.AddRound(req.Query, response)
    if err != nil {
        http.Error(w, err.Error(), 500)
        return
    }
    
    // File watcher will trigger update to clients
}
```

**Testing**:
1. Send query via storm UI
2. Verify response appends to file
3. Check vimbeam shows update
4. Send concurrent queries from two browsers
5. Verify both append correctly (may be out of order)

**Success Criteria**:
- ✅ No full-file rewrites
- ✅ Concurrent queries don't corrupt file
- ✅ Vimbeam users see new rounds immediately

---

### Phase 3: Graceful Parse Error Handling (1 day)

**Goal**: Storm continues working even if structure breaks

**Changes**:
1. Add validation to parser
2. Display parse errors in UI
3. Provide repair suggestions

**Code Changes**:
```go
func (c *Chat) GetRoundsWithErrors() ([]RoundTrip, []error) {
    content, _ := ioutil.ReadFile(c.filename)
    rounds, err := split.Parse(bytes.NewReader(content))
    
    if err != nil {
        // Try to extract partial rounds
        rounds, partialErrors := split.ParseWithRecovery(bytes.NewReader(content))
        return rounds, partialErrors
    }
    
    return rounds, nil
}
```

**UI Display**:
```html
<div class="parse-error">
    ⚠️ Warning: Document structure may be corrupted
    <ul>
        <li>Missing ## References heading in round 3</li>
        <li>Unexpected bold text on line 45</li>
    </ul>
    <button onclick="attemptRepair()">Auto-Repair</button>
</div>
```

**Auto-Repair**:
```go
func (c *Chat) RepairStructure() error {
    content, _ := ioutil.ReadFile(c.filename)
    
    // Add missing headings
    repaired := addMissingHeadings(content)
    
    // Fix malformed separators
    repaired = fixSeparators(repaired)
    
    // Write back
    ioutil.WriteFile(c.filename, repaired, 0644)
}
```

**Testing**:
1. Manually corrupt markdown (delete `## References`)
2. Verify storm shows error
3. Click repair button
4. Verify file is fixed

---

### Phase 4: Query Queue System (2 days)

**Goal**: Serialize LLM queries to prevent interleaving

**Changes**:
1. Add query queue
2. Process queries sequentially
3. Show queue position to users

**Code Changes**:
```go
type QueryQueue struct {
    queries chan *QueryJob
    stop    chan bool
}

type QueryJob struct {
    Query      string
    LLM        string
    ResultChan chan string
    ErrorChan  chan error
}

func NewQueryQueue() *QueryQueue {
    q := &QueryQueue{
        queries: make(chan *QueryJob, 100),
        stop:    make(chan bool),
    }
    go q.process()
    return q
}

func (q *QueryQueue) process() {
    for {
        select {
        case job := <-q.queries:
            // Process one query at a time
            response := sendQueryToLLM(job.Query, job.LLM, ...)
            job.ResultChan <- response
            
        case <-q.stop:
            return
        }
    }
}

func (q *QueryQueue) Submit(query, llm string) (string, error) {
    job := &QueryJob{
        Query:      query,
        LLM:        llm,
        ResultChan: make(chan string),
        ErrorChan:  make(chan error),
    }
    
    q.queries <- job
    
    // Wait for result
    select {
    case response := <-job.ResultChan:
        return response, nil
    case err := <-job.ErrorChan:
        return "", err
    }
}
```

**UI Updates**:
```javascript
// Show queue position
socket.on('queue_update', function(data) {
    if (data.position > 0) {
        showMessage("Your query is #" + data.position + " in queue");
    }
});
```

---

### Phase 5: Production Hardening (3-5 days)

**Goals**:
- Robust error handling
- Logging and monitoring
- Performance optimization
- Documentation

**Changes**:

1. **Structured Logging**:
```go
import "github.com/sirupsen/logrus"

log.WithFields(logrus.Fields{
    "user":     userId,
    "query":    query,
    "duration": duration,
}).Info("Query completed")
```

2. **Metrics**:
```go
import "github.com/prometheus/client_golang/prometheus"

var (
    queriesTotal = prometheus.NewCounter(...)
    queryDuration = prometheus.NewHistogram(...)
    parseErrors = prometheus.NewCounter(...)
)
```

3. **Rate Limiting**:
```go
import "golang.org/x/time/rate"

limiter := rate.NewLimiter(rate.Every(time.Second), 10)

func queryHandler(w http.ResponseWriter, r *http.Request) {
    if !limiter.Allow() {
        http.Error(w, "Rate limit exceeded", 429)
        return
    }
    // ...
}
```

4. **Document Version Tracking**:
```go
// Add version to each round for debugging
round := fmt.Sprintf("\n\n<!-- version:%s timestamp:%d -->\n**%s**\n\n%s\n\n---\n\n",
    gitCommitHash, time.Now().Unix(), query, response)
```

---

## Vimbeam Considerations

### What Vimbeam Provides (Already Complete)

✅ Real-time collaborative text editing
✅ CRDT-based conflict resolution (Automerge)
✅ Remote cursor display with names and colors
✅ Character-offset based positioning
✅ Awareness protocol for presence
✅ Persistent sync via WebSocket

### Optional Enhancements for Storm Integration

#### Enhancement 1: Transactional Edits

**Purpose**: Group related changes into atomic operations

**Use Case**: Append entire LLM response as single transaction

**API Design**:
```lua
-- In vimbeam/lua/vimbeam/init.lua
function M.begin_transaction()
  M.send({ type = 'begin_transaction' })
end

function M.commit_transaction()
  M.send({ type = 'commit_transaction' })
end

function M.rollback_transaction()
  M.send({ type = 'rollback_transaction' })
end
```

**Node Helper**:
```javascript
// In node-helper/index.js
case 'begin_transaction':
  currentTransaction = [];
  break;

case 'commit_transaction':
  handle.change(d => {
    for (const edit of currentTransaction) {
      applyEdit(d, edit);
    }
  });
  currentTransaction = null;
  break;
```

**Storm Usage**:
```go
// Pseudo-code - would need vimbeam Go bindings
vimbeam.BeginTransaction()
vimbeam.AppendText("\n\n**Query**\n\n")
vimbeam.AppendText(response)
vimbeam.AppendText("\n\n---\n\n")
vimbeam.CommitTransaction()
```

**Priority**: Low - Can achieve similar effect with append-only writes

---

#### Enhancement 2: File Change Notifications

**Purpose**: Let storm know when Automerge updates file

**Current**: Storm must poll or use fsnotify

**Better**: Vimbeam pushes notification

**API Design**:
```lua
-- Register callback
M.on_remote_change(function(change)
  -- change.user_id, change.offset, change.length
  vim.notify('Remote change by ' .. change.user_id)
end)
```

**Use Case**: Storm subscribes to changes
```go
vimbeam.OnChange(func(change Change) {
    log.Printf("File changed by %s", change.UserID)
    reloadAndBroadcast()
})
```

**Priority**: Medium - Useful but fsnotify works

---

#### Enhancement 3: Metadata Storage

**Purpose**: Store application-specific data alongside document

**Use Case**: Store file I/O selections, user preferences

**API Design**:
```lua
M.set_metadata('storm.files.input', {'file1.go', 'file2.go'})
M.get_metadata('storm.files.input')  -- returns table
```

**Automerge Storage**:
```javascript
handle.change(d => {
  if (!d.metadata) d.metadata = {};
  d.metadata['storm.files.input'] = ['file1.go', 'file2.go'];
});
```

**Priority**: Low - Can use separate file

---

#### Enhancement 4: Read-Only Mode

**Purpose**: Allow view-only access without sync conflicts

**Use Case**: Display-only storm clients that can't edit

**API Design**:
```lua
M.setup({
  sync_url = 'ws://localhost:1234',
  read_only = true,  -- NEW
})
```

**Implementation**:
```lua
function M.attach_buffer(initial_content)
  if M.config.read_only then
    vim.bo[bufnr].modifiable = false
    -- Don't send edits to server
    return
  end
  -- Normal behavior
end
```

**Priority**: Low - Not needed for MVP

---

#### Enhancement 5: Conflict Callbacks

**Purpose**: Notify application when CRDTs resolve conflicts

**Use Case**: Storm shows "Your edit was merged with Alice's edit"

**API Design**:
```lua
M.on_conflict(function(conflict)
  vim.notify('Conflict resolved: ' .. conflict.description)
end)
```

**Priority**: Low - CRDTs resolve automatically

---

### Vimbeam Limitations for Storm

#### Limitation 1: No Structure Enforcement

**Issue**: Vimbeam treats document as plain text

**Impact**: Users can break markdown structure

**Mitigation**: Storm handles parse errors gracefully

#### Limitation 2: No Access Control

**Issue**: All users have equal edit permissions

**Impact**: Can't restrict who can add queries

**Mitigation**: Implement access control in storm layer

#### Limitation 3: No Semantic Merging

**Issue**: CRDTs merge at character level, not semantic level

**Example**:
```markdown
User A types: "The answer is 42"
User B types: "The answer is 7"
Result: "The answer is 427"  ← Nonsense
```

**Mitigation**: Use queue system to serialize LLM responses

---

## Technical Details

### Automerge CRDT Behavior

**Concurrent Appends**:
```
User A appends: "Text A"
User B appends: "Text B"

Result (deterministic): "Text AText B" or "Text BText A"
  (depends on Lamport timestamps)
```

**Concurrent Edits at Same Position**:
```
User A inserts "X" at offset 10
User B inserts "Y" at offset 10

Result: "XY" or "YX" at offset 10
  (deterministic based on user IDs)
```

**Delete vs Insert**:
```
User A deletes characters 10-20
User B inserts "Z" at offset 15

Result: "Z" appears (inserts win over deletes)
```

---

### Character Offset Examples

**Simple Case**:
```
Text: "Hello, world!"
       0123456789...

Offset 7 = 'w'
```

**Unicode Case**:
```
Text: "Hello, 世界!"
Bytes: H e l l o ,   世  界  !
       0 1 2 3 4 5 6 7-9 10-12 13

Character offsets:
  0='H', 5=',', 7='世', 8='界', 9='!'

Byte offsets:
  0='H', 5=',', 7='世' (3 bytes), 10='界' (3 bytes)
```

**Vimbeam Uses Character Offsets**:
```lua
vim.fn.strchars(line)  -- Character count
```

**Storm Uses Byte Offsets** (Go strings):
```go
len("Hello, 世界!")  // Returns 14 (bytes)
```

**Impact**: Minor - mainly affects exact cursor positioning

---

### File Watcher Events

**fsnotify Event Types**:
```go
fsnotify.Create  // File created
fsnotify.Write   // File modified
fsnotify.Remove  // File deleted
fsnotify.Rename  // File renamed
fsnotify.Chmod   // Permissions changed
```

**For Storm**:
```go
case event := <-watcher.Events:
    if event.Op&fsnotify.Write == fsnotify.Write {
        // Reload file
        c.broadcastUpdate()
    }
    if event.Op&fsnotify.Remove == fsnotify.Remove {
        // File deleted - handle gracefully
        log.Printf("Chat file deleted!")
    }
```

**Gotcha**: Multiple events for single write
```
Time 0: Write event #1
Time 1: Write event #2
Time 2: Write event #3
```

**Solution**: Debounce
```go
var debounceTimer *time.Timer

case event := <-watcher.Events:
    if debounceTimer != nil {
        debounceTimer.Stop()
    }
    debounceTimer = time.AfterFunc(100*time.Millisecond, func() {
        c.broadcastUpdate()
    })
```

---

### WebSocket Protocol for Storm UI Updates

**Connect**:
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
```

**Message Types**:

**1. Update (Server → Client)**:
```json
{
  "type": "update",
  "html": "<div>...</div>",
  "rounds_count": 42
}
```

**2. Cursor Update (Server → Client)**:
```json
{
  "type": "cursor",
  "user_id": "alice",
  "user_name": "Alice",
  "color": "#FF6B6B",
  "offset": 1234
}
```

**3. Error (Server → Client)**:
```json
{
  "type": "error",
  "message": "Parse error: missing ## References",
  "recoverable": true
}
```

**4. Query Status (Server → Client)**:
```json
{
  "type": "query_status",
  "status": "queued",
  "position": 2,
  "estimated_time": 30
}
```

**Client Implementation**:
```javascript
ws.onmessage = function(event) {
    const msg = JSON.parse(event.data);
    
    switch(msg.type) {
        case 'update':
            document.getElementById('chat').innerHTML = msg.html;
            generateTOC();
            break;
        case 'cursor':
            showRemoteCursor(msg.user_name, msg.offset, msg.color);
            break;
        case 'error':
            showError(msg.message);
            break;
    }
};
```

---

## Summary and Recommendations

### Critical Path for MVP (10-15 days)

1. ✅ **Phase 1**: File watcher + WebSocket updates (2 days)
2. ✅ **Phase 2**: Append-only LLM responses (3 days)
3. ✅ **Phase 3**: Parse error handling (1 day)
4. ✅ **Phase 4**: Query queue (2 days)
5. ✅ **Testing**: Integration testing (2 days)

**Total**: ~10 days to working collaborative storm

### Long-Term Improvements (Post-MVP)

- Switch from markdown to structured format (JSON/YAML)
- Add access control and user roles
- Implement approval workflow for edits
- Add document version history UI
- Support for branching/forking chats
- Integration with more LLM providers

### Key Takeaways

1. **Vimbeam is complete** - No changes needed to vimbeam core
2. **Storm needs refactoring** - Remove in-memory state, add file watching
3. **Start simple** - Append-only mode first, full editing later
4. **Markdown is fragile** - Consider structured formats for v2
5. **CRDTs are powerful** - Leverage Automerge's conflict resolution

### Risk Areas

⚠️ **High Risk**:
- Concurrent query interleaving (mitigate with queue)
- Parse errors from broken structure (mitigate with validation)

⚠️ **Medium Risk**:
- User confusion from CRDT merge behavior
- Performance with large chat files (>10MB)

⚠️ **Low Risk**:
- Character offset misalignment (minor UX issue)
- File watcher event noise (debounce solves)

---

## Appendix: Code Examples

### Complete File Watcher Implementation

```go
package main

import (
    "log"
    "time"
    "github.com/fsnotify/fsnotify"
)

type Chat struct {
    filename string
    watcher  *fsnotify.Watcher
    clients  []*WebSocketClient
    debounce *time.Timer
}

func (c *Chat) StartWatching() error {
    watcher, err := fsnotify.NewWatcher()
    if err != nil {
        return err
    }
    c.watcher = watcher
    
    err = watcher.Add(c.filename)
    if err != nil {
        return err
    }
    
    go c.watchLoop()
    return nil
}

func (c *Chat) watchLoop() {
    for {
        select {
        case event := <-c.watcher.Events:
            if event.Op&fsnotify.Write == fsnotify.Write {
                c.handleFileChange()
            }
        case err := <-c.watcher.Errors:
            log.Printf("Watcher error: %v", err)
        }
    }
}

func (c *Chat) handleFileChange() {
    // Debounce multiple events
    if c.debounce != nil {
        c.debounce.Stop()
    }
    
    c.debounce = time.AfterFunc(100*time.Millisecond, func() {
        c.reloadAndBroadcast()
    })
}

func (c *Chat) reloadAndBroadcast() {
    content, err := ioutil.ReadFile(c.filename)
    if err != nil {
        log.Printf("Read error: %v", err)
        return
    }
    
    rounds, parseErrors := split.Parse(bytes.NewReader(content))
    
    html := markdownToHTML(string(content))
    
    msg := map[string]interface{}{
        "type": "update",
        "html": html,
        "rounds_count": len(rounds),
    }
    
    if len(parseErrors) > 0 {
        msg["errors"] = parseErrors
    }
    
    c.broadcastToClients(msg)
}

func (c *Chat) broadcastToClients(msg map[string]interface{}) {
    data, _ := json.Marshal(msg)
    for _, client := range c.clients {
        client.Send(data)
    }
}
```

### Complete Query Queue Implementation

```go
package main

import (
    "context"
    "sync"
)

type QueryQueue struct {
    jobs   chan *QueryJob
    ctx    context.Context
    cancel context.CancelFunc
    wg     sync.WaitGroup
}

type QueryJob struct {
    ID          string
    Query       string
    LLM         string
    UserID      string
    SubmittedAt time.Time
    Result      chan QueryResult
}

type QueryResult struct {
    Response string
    Error    error
}

func NewQueryQueue() *QueryQueue {
    ctx, cancel := context.WithCancel(context.Background())
    q := &QueryQueue{
        jobs:   make(chan *QueryJob, 100),
        ctx:    ctx,
        cancel: cancel,
    }
    
    q.wg.Add(1)
    go q.processLoop()
    
    return q
}

func (q *QueryQueue) processLoop() {
    defer q.wg.Done()
    
    for {
        select {
        case job := <-q.jobs:
            q.processJob(job)
        case <-q.ctx.Done():
            return
        }
    }
}

func (q *QueryQueue) processJob(job *QueryJob) {
    log.Printf("Processing job %s from user %s", job.ID, job.UserID)
    
    // Call LLM
    response := sendQueryToLLM(job.Query, job.LLM, ...)
    
    // Append to file
    err := chat.AddRound(job.Query, response)
    
    // Send result back
    job.Result <- QueryResult{
        Response: response,
        Error:    err,
    }
}

func (q *QueryQueue) Submit(query, llm, userID string) (string, error) {
    job := &QueryJob{
        ID:          generateID(),
        Query:       query,
        LLM:         llm,
        UserID:      userID,
        SubmittedAt: time.Now(),
        Result:      make(chan QueryResult, 1),
    }
    
    q.jobs <- job
    
    // Notify user of queue position
    position := len(q.jobs) + 1
    notifyQueuePosition(userID, position)
    
    // Wait for result
    result := <-job.Result
    return result.Response, result.Error
}

func (q *QueryQueue) Shutdown() {
    q.cancel()
    q.wg.Wait()
    close(q.jobs)
}
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-31  
**Authors**: Storm/Vimbeam Integration Team
