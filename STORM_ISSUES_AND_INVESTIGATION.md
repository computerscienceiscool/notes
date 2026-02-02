# Storm - Potential Issues & Areas for Investigation

This document outlines issues discovered during installation and areas that may need attention.

## Critical Issues Found

### 1. Missing Prerequisites in Documentation

**Issue:** Storm's README doesn't clearly document that grokker must be initialized before Storm can run.

**What happened during installation:**
1. Tried to run `storm serve` immediately after building
2. Got error: "failed to load LLM core: open : no such file or directory"
3. The error message was cryptic - didn't indicate what was actually wrong
4. Root cause: Grokker was not initialized and no default model was set

**What was needed:**
```bash
cd ~/lab/grokker
grok init
grok model gpt-4o
```

**Why this wasn't obvious:**
- Storm's README doesn't mention grokker initialization as a prerequisite
- The error message doesn't suggest running `grok init`
- The relationship between Storm and grokker isn't clearly documented

**The code in main.go was actually correct:**
```go
grok, _, _, _, lock, err = core.Load("", true)
```

This correctly:
- Passes empty string to use the default model from `~/.grok`
- `core.Load()` automatically finds the `.grok` file by walking up directories
- Sets readonly mode to `true`

**Recommendation:** 
- Add clear prerequisites section to Storm's README
- Improve error message to suggest `grok init` if `.grok` file not found
- Document the Storm → grokker dependency relationship

### 2. Missing Dependency Documentation

**Issue:** Installation fails without proper environment setup

**Missing from docs:**
1. `GOTOOLCHAIN=auto` requirement for Go 1.24
2. Grokker initialization required before Storm can run  
3. Model selection requirement (`grok model gpt-4o`)
4. Clear explanation that Storm depends on grokker being set up first

**Recommendation:**
Add a "Prerequisites" section to Storm's README covering:
- **Before running Storm:**
  1. Initialize grokker: `grok init`
  2. Set default model: `grok model gpt-4o`
  3. Set OPENAI_API_KEY environment variable
- Required environment variables
- Go toolchain settings for goenv users

## Potential Issues to Investigate

### 1. Error Message Quality - Most Critical Issue

**Issue:** Cryptic error messages during our installation

**Examples:**
```
Error: failed to load LLM core: /home/jj/lab/grokker/v3/core/api.go:404: open : no such file or directory
```

This doesn't tell the user:
- What file is missing
- That they need to run `grok init`
- That they need to set a model

**Recommendation:**
Improve error handling in `serveRun()`:
```go
grok, _, _, _, lock, err = core.Load("", true)
if err != nil {
    // Check if .grok file exists
    home, _ := os.UserHomeDir()
    grokPath := filepath.Join(home, ".grok")
    if _, statErr := os.Stat(grokPath); os.IsNotExist(statErr) {
        return fmt.Errorf("grokker not initialized - run 'grok init' first")
    }
    return fmt.Errorf("failed to load LLM core: %w\nTry running 'grok model gpt-4o'", err)
}
```

### 2. Dependency on Grokker State

**Issue:** Storm depends on external grokker state in `~/.grok`

**Problems:**
- Storm can't run without grokker being initialized first
- Unclear dependency relationship
- Multiple tools sharing same config file

**Questions to investigate:**
1. Should Storm bundle its own grokker instance?
2. Should Storm have its own model configuration?
3. What happens if someone runs `grok model X` while Storm is running?

**Recommendation:**
Consider one of these approaches:

**Option A: Document the dependency clearly**
```
Storm requires grokker to be initialized:
1. Run `grok init`
2. Run `grok model gpt-4o`  
3. Then start Storm with `storm serve`
```

**Option B: Auto-initialize on first run**
```go
func ensureGrokkerInitialized() error {
    home, _ := os.UserHomeDir()
    grokPath := filepath.Join(home, ".grok")
    if _, err := os.Stat(grokPath); os.IsNotExist(err) {
        // Auto-initialize with sensible defaults
        return initializeGrokker()
    }
    return nil
}
```

### 3. GOTOOLCHAIN Environment Variable

**Issue:** Storm requires `GOTOOLCHAIN=auto` for Go 1.24+

**Problem:**
- Not documented anywhere
- Confusing error message
- goenv users particularly affected

**Error seen:**
```
go: go.mod requires go >= 1.24 (running go 1.22.2; GOTOOLCHAIN=local)
```

**Recommendation:**
1. Document in README
2. Consider adding to Makefile:
```makefile
export GOTOOLCHAIN=auto
```

### 4. Port Conflicts

**Issue:** Storm defaults to port 8080 with no conflict detection

**What happens:**
- If 8080 is in use, Storm fails silently or with unclear error
- No automatic port selection
- No clear indication of what went wrong

**Recommendation:**
Add better error handling:
```go
listener, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
if err != nil {
    return fmt.Errorf("failed to start server on port %d: %w\nTry a different port with --port flag", port, err)
}
```

### 5. Database Migration Messages

**Observation:** During startup we saw:
```
migrating from 3.0.37 to 3.0.39
```

**Questions:**
1. Is this expected every time?
2. What triggers migration?
3. Are there migration failures to handle?
4. Should this be logged differently (not as an error)?

**Recommendation:**
- Make this an INFO log, not appearing as an error
- Document what triggers migrations
- Add migration failure handling

## Testing Gaps

### Unit Tests Needed

1. **core.Load() parameter validation**
   - Test with empty string (should use default)
   - Test with invalid model name
   - Test with missing .grok file

2. **serveRun() initialization**
   - Test without grokker initialized
   - Test without model set
   - Test with invalid OPENAI_API_KEY

3. **Project creation edge cases**
   - Test with non-existent base directory
   - Test with non-existent markdown file
   - Test with invalid project IDs

### Integration Tests Needed

1. **Fresh installation flow**
   - Test full setup from scratch
   - Verify error messages are helpful
   - Test with different Go versions

2. **Multi-user scenarios**
   - Multiple Storm instances
   - Shared .grok file
   - Concurrent access

## Documentation Improvements Needed

### 1. README.md Updates

**Add sections for:**
- Prerequisites (grokker setup)
- Environment variables required
- Common error messages and fixes
- Relationship between Storm and grokker

### 2. Installation Guide

Current README has basic install steps but missing:
- goenv-specific instructions
- GOTOOLCHAIN requirements
- Grokker initialization steps
- Model selection requirement

### 3. Architecture Documentation

**Missing:**
- Dependency diagram (Storm → grokker → OpenAI)
- State management explanation
- Configuration file locations
- How components interact

## Code Quality Issues

### 1. Magic Strings

**Found throughout:**
```go
".grok"
"~/.storm/data.db"
"gpt-4o"
```

**Recommendation:**
Create constants:
```go
const (
    GrokConfigFile = ".grok"
    StormDBPath = "~/.storm/data.db"
    DefaultModel = "gpt-4o"
)
```

### 2. Error Handling Consistency

**Inconsistent patterns:**
- Some places use `fmt.Errorf`
- Some use custom error types
- Some return nil without logging

**Recommendation:**
Standardize error handling:
```go
// Use structured errors
type InitError struct {
    Component string
    Reason    string
    Fix       string
}

func (e *InitError) Error() string {
    return fmt.Sprintf("%s initialization failed: %s\nSuggested fix: %s", 
        e.Component, e.Reason, e.Fix)
}
```

### 3. Configuration Management

**Current state:**
- Environment variables (`OPENAI_API_KEY`)
- CLI flags (`--port`, `--db-path`)
- External file (`~/.grok`)
- No config file for Storm itself

**Recommendation:**
Consider adding `~/.storm/config.yaml`:
```yaml
server:
  port: 8080
  db_path: ~/.storm/data.db

llm:
  default_model: gpt-4o
  api_key_env: OPENAI_API_KEY

logging:
  level: info
  file: ~/.storm/storm.log
```

## Performance Considerations

### 1. Startup Time

**Observed:** ~2-3 seconds to start

**Investigate:**
- Database migration overhead
- grokker initialization time
- Can anything be lazy-loaded?

### 2. Memory Usage

**Not measured during install**

**Should investigate:**
- Memory usage with multiple projects
- Memory usage with large files
- Memory leaks in long-running server

### 3. Concurrent Request Handling

**Not tested**

**Should investigate:**
- How many concurrent users can it handle?
- WebSocket connection limits
- Database locking issues

## Security Concerns

### 1. API Key Storage

**Current:** Environment variable only

**Concerns:**
- Visible in process list (`ps aux`)
- Logged in some error messages
- No encryption at rest

**Recommendation:**
- Support reading from secure file with 0600 permissions
- Mask API key in logs and error messages
- Document security best practices

### 2. File Access Control

**Concern:** Can Storm read any file the user has access to?

**Questions:**
1. Should there be a whitelist of allowed directories?
2. Can users escape project baseDir?
3. Are there path traversal vulnerabilities?

**Recommendation:**
Audit all file access code:
```bash
grep -rn "ReadFile\|Open\|Create" ~/lab/grokker/x/storm/*.go
```

### 3. WebSocket Security

**Current:** Local-only by default

**Questions:**
1. What if someone exposes port 8080 externally?
2. Is there authentication?
3. Are messages validated?

**Recommendation:**
- Add authentication layer
- Add CORS protection
- Validate all WebSocket messages

## Cross-Platform Issues

### 1. Windows Support

**Not tested** - Linux paths used throughout

**Known issues:**
- `filepath.Join(os.Getenv("HOME"), ...)` won't work
- Forward slashes in paths
- Executable extensions

**Recommendation:**
- Use `filepath.Join` everywhere (not string concat)
- Use `os.UserHomeDir()` instead of HOME env var
- Test on Windows

### 2. macOS Support

**Not tested**

**Should verify:**
- goenv behavior on macOS
- File permissions
- WebSocket behavior

## Build System Issues

### 1. Makefile Assumptions

**Current Makefile assumes:**
- Git is installed and initialized
- Go is in PATH
- Unix-like environment

**Problems:**
- "Uncommitted changes found" appears as error (it's not)
- No Windows support
- No CI/CD examples

**Recommendation:**
- Add Windows targets
- Make git checks optional
- Add Docker build option

### 2. Dependency Management

**go.mod requires go >= 1.24**

**Issues:**
- Very new Go version requirement
- Not all systems have 1.24 yet
- goenv workflow not documented

**Recommendation:**
- Document why 1.24 is required
- Provide alternative for older Go versions
- Consider backporting to 1.22 if possible

## User Experience Issues

### 1. No "Getting Started" Tutorial

**Current state:**
- README shows commands
- No step-by-step walkthrough
- No example project

**Recommendation:**
Create `GETTING_STARTED.md` with:
1. First-time setup
2. Creating first project
3. Sending first query
4. Understanding the UI
5. Common workflows

### 2. Unclear Error Messages

**Examples seen:**
```
Error: failed to load LLM core
```

**What it should say:**
```
Error: Could not initialize LLM
Possible causes:
1. Run 'grok init' if this is your first time
2. Run 'grok model gpt-4o' to set default model
3. Check that OPENAI_API_KEY is set
```

### 3. No Progress Indicators

**During install:**
- Long pauses during `go install`
- No indication of what's happening
- User might think it's frozen

**Recommendation:**
Add progress messages:
```go
log.Println("Downloading dependencies...")
log.Println("Compiling Storm...")
log.Println("Installing binary...")
```

## Monitoring & Observability

### Missing Features

1. **Logging**
   - No structured logging
   - No log levels
   - No log rotation

2. **Metrics**
   - No request counting
   - No latency tracking
   - No error rates

3. **Health Checks**
   - No `/health` endpoint
   - No readiness probe
   - No liveness probe

**Recommendation:**
Add basic observability:
```go
// Add logging
import "log/slog"

// Add metrics endpoint
http.HandleFunc("/metrics", metricsHandler)

// Add health check
http.HandleFunc("/health", healthCheck)
```

## Next Steps

### High Priority

1. **Add prerequisites section to README** - Document that grokker must be initialized first
2. **Improve error messages** - Suggest `grok init` when .grok file is missing
3. **Document grokker dependency** - Explain the Storm → grokker relationship
4. Add GOTOOLCHAIN to docs

### Medium Priority

1. Add configuration file support
2. Improve cross-platform support
3. Add unit tests
4. Security audit

### Low Priority

1. Add monitoring
2. Performance testing
3. Integration tests
4. Windows support

## Contributing

If fixing any of these issues:

1. Create issue in grokker repo
2. Reference this document
3. Include reproduction steps
4. Test fix with fresh install

## Summary

Storm works well but has rough edges around:
- **Installation documentation** - Prerequisites aren't clearly stated
- **Error messages** - Don't guide users to solutions (e.g., "run grok init")
- **Dependencies** - The grokker relationship and setup requirements aren't documented
- **Cross-platform** - Only tested on Linux with goenv

The core code is solid and works correctly. The main issues are:
1. Missing documentation about prerequisites
2. Cryptic error messages that don't suggest fixes
3. Assumption that users already know about grokker

**Most critical improvement needed:** Better documentation and error messages, not code changes.
