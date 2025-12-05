# llm-runtime Agent Mode Specification

## Overview

Transform llm-runtime from a passive command executor into an autonomous agent that communicates directly with LLMs.

---

## Components

### 1. LLM Client Layer
**Dependencies:** None (can build first)

**Purpose:** Abstract communication with LLM providers.

**Requirements:**
- Interface that supports multiple providers
- Initial targets: Anthropic, OpenAI, Ollama (local)
- Handle authentication (API keys via env vars or config)
- Send messages, receive responses
- Basic error handling (rate limits, network errors, retries)
- Streaming optional (can start with blocking calls)

**Config additions:**
```yaml
llm:
  provider: "anthropic"  # or "openai", "ollama"
  model: "claude-sonnet-4-20250514"
  api_key_env: "ANTHROPIC_API_KEY"  # read from environment
  endpoint: ""  # optional, for custom endpoints
  max_tokens: 4096
  temperature: 0.7
```

---

### 2. Conversation Management
**Dependencies:** LLM Client Layer

**Purpose:** Maintain conversation state and context.

**Requirements:**
- Store message history (role + content)
- System prompt injection (use existing SYSTEM_PROMPT.md or custom)
- Append command results as "user" or "system" messages
- Track token usage (if API provides it)

**Future considerations:**
- Context window management (truncate old messages)
- Summarization when context gets too long

---

### 3. Agent Loop
**Dependencies:** LLM Client, Conversation Management, existing command executor

**Purpose:** The core autonomous execution cycle.

**Flow:**
```
1. User provides goal/task
2. Build initial prompt with system instructions + task
3. Send to LLM
4. Receive response
5. Parse for commands (<open>, <write>, <exec>, <search>)
6. If no commands → check if done, otherwise prompt for clarification
7. Execute commands
8. Format results
9. Append results to conversation
10. Go to step 3
```

**Requirements:**
- Max iteration limit (default: 20?)
- Detect completion (no commands + affirmative language, or explicit signal)
- Handle errors gracefully (command fails → tell LLM, let it adapt)
- User interrupt (Ctrl+C) should exit cleanly

---

### 4. Termination Detection
**Dependencies:** Agent Loop

**Purpose:** Know when to stop.

**Strategies:**
- No commands in response for N consecutive turns
- LLM uses explicit marker (e.g., "TASK_COMPLETE")
- Max iterations reached
- User interrupts

**Requirements:**
- Configurable max iterations
- Clear exit messaging ("Completed after 7 iterations" or "Stopped: max iterations")

---

### 5. Configuration Updates
**Dependencies:** None (can do anytime)

**Purpose:** Add new settings for agent mode.

**New config sections:**
```yaml
agent:
  enabled: false
  max_iterations: 20
  auto_confirm_writes: false  # require confirmation for writes?
  auto_confirm_exec: false    # require confirmation for exec?
  show_llm_responses: true    # print full LLM responses?
  completion_marker: "TASK_COMPLETE"  # optional explicit marker
```

---

### 6. CLI/UX Updates
**Dependencies:** Agent Loop working

**Purpose:** User interface for agent mode.

**New flags:**
```
--agent              Enable agent mode
--goal "task"        Initial task/goal (or prompt interactively)
--provider anthropic Override LLM provider
--model claude-xxx   Override model
--max-iterations 20  Override iteration limit
--confirm            Require confirmation for writes/exec
```

**Modes after implementation:**
- Pipe mode (existing): `echo "text with commands" | llm-runtime`
- Interactive mode (existing): `llm-runtime --interactive`
- Agent mode (new): `llm-runtime --agent --goal "add tests for auth"`

---

## Implementation Order Options

### Option A: Bottom-up (safest)
1. Configuration updates (add new fields, no behavior change)
2. LLM Client Layer (build and test in isolation)
3. Conversation Management (build on top of client)
4. Agent Loop (integrate everything)
5. Termination Detection (refine loop behavior)
6. CLI/UX Updates (polish)

### Option B: Vertical slice (fastest to demo)
1. Minimal LLM Client (one provider, hardcoded settings)
2. Minimal Agent Loop (basic flow, fixed iterations)
3. Iterate: add config, add providers, add termination logic, add CLI

### Option C: Parallel workstreams
- **Track 1:** LLM Client + Conversation (API side)
- **Track 2:** Configuration + CLI (interface side)
- **Merge:** Agent Loop (brings them together)

---

## File Structure (Proposed)

```
internal/
  llm/
    client.go         # Interface + factory
    anthropic.go      # Anthropic implementation
    openai.go         # OpenAI implementation
    ollama.go         # Ollama implementation
    conversation.go   # Message history management
  agent/
    loop.go           # Main agent loop
    termination.go    # Completion detection
```

---

## Risks and Considerations

### Token costs
- Agent loops can burn through tokens fast
- Consider: token budget limit, cost estimation before starting

### Runaway loops
- LLM could get stuck or keep going forever
- Mitigation: max iterations, no-progress detection

### Destructive actions
- Agent might write/exec something unintended
- Mitigation: confirmation prompts, dry-run mode, exec stays sandboxed

### Context window limits
- Long tasks could exceed context
- Mitigation: summarization, sliding window (later enhancement)

### API key security
- Don't commit keys, don't log them
- Use environment variables only

---

## Success Criteria

**MVP:**
- Can run `llm-runtime --agent --goal "read the README and summarize it"`
- Agent calls LLM, parses commands, executes, returns results, LLM summarizes, done

**V1:**
- Multiple providers supported
- Configurable via YAML
- Graceful termination
- Confirmation prompts for dangerous operations

---

## Non-Goals (for now)

- Function calling / tool use format (stick with XML commands)
- Multi-agent collaboration
- Persistent memory across sessions
- Web UI
- Cost tracking dashboard

---

## Open Questions

1. Should agent mode replace interactive mode or be separate?
2. How verbose should output be during agent execution?
3. Should we support "planning" step before execution?
4. Do we want a dry-run mode that shows what would happen?
