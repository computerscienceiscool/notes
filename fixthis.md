# Fix This - Priority Issues

## 🔴 Critical Priority (Security)

### 1. Path Validation Bypass (`pkg/sandbox/path.go:14-18`)
**Why:** Current string checks can be bypassed with encoded sequences like `....//` allowing directory traversal.

**Location:** `pkg/sandbox/path.go` - `ValidatePath()` function
**Current Code:**
```go
if strings.HasPrefix(cleanPath, "..") || strings.Contains(cleanPath, "/../") {
    return "", fmt.Errorf("path traversal detected: %s", requestedPath)
}
```

**Fix:**
```go
cleanPath := filepath.Clean(requestedPath)
absPath := filepath.Join(repositoryRoot, cleanPath)

// Ensure resolved path stays within repository
if !strings.HasPrefix(absPath, repositoryRoot+string(filepath.Separator)) {
    return "", fmt.Errorf("path outside repository: %s", requestedPath)
}
```

---

### 2. Scanner Buffer Overflow (`pkg/scanner/scanner.go:109-128`)
**Why:** No size limit on write buffer allows memory exhaustion attacks via unclosed `<write>` tags.

**Location:** `pkg/scanner/scanner.go` - `StateWriteBody` case
**Current Code:**
```go
case StateWriteBody:
    s.buffer.WriteByte(ch)
    buffered := s.buffer.String()
```

**Fix:**
```go
const maxBufferSize = 10 * 1024 * 1024 // 10MB

case StateWriteBody:
    if s.buffer.Len() >= maxBufferSize {
        s.transitionTo(StateScanning)
        s.resetCommand()
        return &Command{
            Type:  "error",
            Error: fmt.Errorf("buffer overflow: write content too large"),
        }
    }
    s.buffer.WriteByte(ch)
```

---

### 3. Container Image Validation (`pkg/config/types.go:28`)
**Why:** Unvalidated image names could pull malicious Docker images from registries.

**Location:** `pkg/config/types.go` and `pkg/sandbox/client.go`

**Fix:** Add validation function:
```go
// pkg/sandbox/client.go
var allowedImages = map[string]bool{
    "alpine:latest":          true,
    "ubuntu:22.04":           true,
    "python-go":              true,
    "llm-runtime-io:latest":  true,
}

func ValidateImageName(image string) error {
    if !allowedImages[image] {
        return fmt.Errorf("image not in whitelist: %s", image)
    }
    return nil
}
```

Call before pulling:
```go
if err := ValidateImageName(image); err != nil {
    return err
}
```

---

### 4. Command Injection in Shell Exec (`pkg/sandbox/container.go:49`)
**Why:** Using `sh -c` interprets shell metacharacters allowing command injection despite whitelist.

**Location:** `pkg/sandbox/container.go` - `RunContainer()`
**Current Code:**
```go
Cmd: strslice.StrSlice{"sh", "-c", cfg.Command},
```

**Fix:** Use exec form when possible:
```go
// For simple commands, use exec form
cmdParts := strings.Fields(cfg.Command)
if len(cmdParts) > 0 && !strings.Contains(cfg.Command, "|") && !strings.Contains(cfg.Command, ">") {
    containerConfig.Cmd = strslice.StrSlice(cmdParts)
} else {
    // For complex commands, escape properly
    containerConfig.Cmd = strslice.StrSlice{"sh", "-c", cfg.Command}
}
```

---

### 5. Error Information Disclosure (`pkg/evaluator/exec.go:45`)
**Why:** Detailed error messages expose internal paths and system configuration to untrusted LLMs.

**Location:** `pkg/evaluator/exec.go` - `ExecuteExec()`

**Fix:** Sanitize errors:
```go
func sanitizeError(err error) error {
    // Remove absolute paths
    msg := err.Error()
    msg = regexp.MustCompile(`/[a-zA-Z0-9/_\-\.]+`).ReplaceAllString(msg, "[path]")
    return fmt.Errorf("%s", msg)
}

// Use in error returns
result.Error = sanitizeError(fmt.Errorf("DOCKER_IMAGE: %w", err))
```

---

## 🟡 High Priority (Reliability)

### 6. Missing Rate Limiting Implementation (`pkg/middleware/logging.go:20`)
**Why:** Placeholder function allows DoS attacks with unlimited rapid requests.

**Fix:** Implement token bucket rate limiter:
```go
import "golang.org/x/time/rate"

var limiter = rate.NewLimiter(rate.Limit(100.0/60.0), 10) // 100/min, burst 10

func RateLimitMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if !limiter.Allow() {
            http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

---

### 7. Hardcoded Embedding Model (`pkg/search/embedding.go:18`)
**Why:** Configuration allows model selection but code ignores it and hardcodes "nomic-embed-text".

**Location:** `pkg/search/embedding.go` - `generateEmbedding()`

**Fix:**
```go
func generateEmbedding(ollamaURL string, text string, model string) ([]float32, error) {
    reqBody := OllamaEmbeddingRequest{
        Model:  model, // Use parameter instead of hardcoded value
        Prompt: text,
    }
    // ...
}

// Update call sites to pass cfg.EmbeddingModel
```

---

### 8. Race Condition in File Writes (`pkg/evaluator/write.go:91-119`)
**Why:** TOCTOU between stat check and write allows concurrent modifications to corrupt backups.

**Fix:** Use file locking:
```go
import "syscall"

// Before backup/write operations
lockFile, err := os.OpenFile(safePath+".lock", os.O_CREATE|os.O_RDWR, 0600)
if err != nil {
    return result
}
defer lockFile.Close()

if err := syscall.Flock(int(lockFile.Fd()), syscall.LOCK_EX); err != nil {
    result.Error = fmt.Errorf("failed to acquire lock: %w", err)
    return result
}
defer syscall.Flock(int(lockFile.Fd()), syscall.LOCK_UN)
```

---

### 9. No Test Coverage for Critical Packages
**Why:** Sandbox, search, and exec packages lack tests making bugs likely in production.

**Missing Tests:**
- `pkg/sandbox/io_container.go`
- `pkg/sandbox/container.go`
- `pkg/search/*.go` (entire package)
- `pkg/evaluator/exec.go`

**Action:** Create test files with minimum 70% coverage for security-critical code.

---

### 10. Insufficient Input Validation (`pkg/sandbox/exec_validation.go:15-18`)
**Why:** Empty commands and malformed input should fail fast before expensive operations.

**Fix:**
```go
func ValidateExecCommand(command string, whitelist []string) error {
    command = strings.TrimSpace(command)
    
    if command == "" {
        return fmt.Errorf("empty command")
    }
    
    if len(command) > 1000 {
        return fmt.Errorf("command too long")
    }
    
    if len(whitelist) == 0 {
        return fmt.Errorf("no commands are whitelisted")
    }
    
    // Rest of validation...
}
```

---

## 🟠 Medium Priority (Performance)

### 11. Container Startup Overhead
**Why:** Starting fresh containers for every I/O operation adds 1-3 seconds latency per file access.

**Solution:** Implement container pooling:
```go
type ContainerPool struct {
    available chan *Container
    maxSize   int
}

func (p *ContainerPool) Get() *Container {
    select {
    case c := <-p.available:
        return c
    default:
        return p.createNew()
    }
}

func (p *ContainerPool) Return(c *Container) {
    select {
    case p.available <- c:
    default:
        c.Destroy()
    }
}
```

---

### 12. No Streaming for Large Files
**Why:** Loading entire files into memory causes OOM for large codebases or binary files.

**Fix:** Add streaming reader:
```go
func (se *SearchEngine) SearchStream(query string, w io.Writer) error {
    // Stream results instead of loading all
}

func ExecuteOpenStream(filepath string, cfg *config.Config, w io.Writer) error {
    // Stream file contents
}
```

---

### 13. Inefficient Vector Similarity Calculation
**Why:** Pure Go loop for 768-dimension vectors is 10x slower than SIMD implementations.

**Fix:** Use optimized library:
```go
import "github.com/viterin/vek/vek32"

func cosineSimilarity(a, b []float32) float32 {
    return vek32.CosineSimilarity(a, b)
}
```

---

### 14. Synchronous Command Execution
**Why:** Serial execution blocks on slow operations preventing concurrent LLM requests.

**Fix:** Add async executor:
```go
type AsyncExecutor struct {
    tasks chan Command
    results chan ExecutionResult
}

func (e *AsyncExecutor) ExecuteAsync(cmd Command) <-chan ExecutionResult {
    resultChan := make(chan ExecutionResult, 1)
    go func() {
        result := e.Execute(cmd)
        resultChan <- result
    }()
    return resultChan
}
```

---

## 🟢 Low Priority (Quality of Life)

### 15. Search Index Staleness
**Why:** Manual reindexing required after file changes makes search results outdated.

**Fix:** Add background file watcher:
```go
import "github.com/fsnotify/fsnotify"

func (se *SearchEngine) WatchAndReindex() {
    watcher, _ := fsnotify.NewWatcher()
    defer watcher.Close()
    
    watcher.Add(se.repoRoot)
    
    for event := range watcher.Events {
        if event.Op&fsnotify.Write == fsnotify.Write {
            se.ReindexFile(event.Name)
        }
    }
}
```

---

### 16. Hardcoded Embedding Dimensions
**Why:** Different models use different dimensions making code fragile when switching models.

**Fix:**
```go
type SearchConfig struct {
    EmbeddingDimensions int `yaml:"embedding_dimensions"`
    // ...
}

// Use cfg.EmbeddingDimensions instead of const
```

---

### 17. No Metrics or Monitoring
**Why:** No visibility into container usage, timeouts, or errors makes debugging difficult.

**Fix:** Add Prometheus metrics:
```go
import "github.com/prometheus/client_golang/prometheus"

var (
    containerExecutions = prometheus.NewCounterVec(
        prometheus.CounterOpts{Name: "container_executions_total"},
        []string{"command", "status"},
    )
    containerDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{Name: "container_duration_seconds"},
        []string{"command"},
    )
)
```

---

### 18. Audit Log Rotation Missing
**Why:** Unbounded audit log growth will eventually fill disk space.

**Fix:** Use log rotation:
```go
import "gopkg.in/natefinch/lumberjack.v2"

logger := &lumberjack.Logger{
    Filename:   "audit.log",
    MaxSize:    100, // MB
    MaxBackups: 5,
    MaxAge:     30, // days
    Compress:   true,
}
```

---

### 19. Duplicate Error Handling Code
**Why:** Same error patterns repeated across evaluator packages reduces maintainability.

**Fix:** Create error helper:
```go
// pkg/evaluator/errors.go
type EvaluatorError struct {
    Type    string
    Message string
    Cause   error
}

func NewSecurityError(msg string, cause error) *EvaluatorError {
    return &EvaluatorError{"PATH_SECURITY", msg, cause}
}
```

---

### 20. Magic Numbers Throughout Code
**Why:** Unexplained constants like buffer sizes and timeouts make code hard to tune.

**Fix:** Centralize constants:
```go
// pkg/config/constants.go
const (
    DefaultMaxFileSize     = 1 * 1024 * 1024  // 1MB
    DefaultMaxWriteSize    = 100 * 1024       // 100KB
    DefaultScanBufferSize  = 10 * 1024 * 1024 // 10MB
    DefaultExecTimeout     = 30 * time.Second
    DefaultContainerMemory = "512m"
)
```

---

## Summary Statistics

- **Critical (Security):** 5 issues
- **High (Reliability):** 5 issues  
- **Medium (Performance):** 4 issues
- **Low (Quality):** 6 issues

**Total Issues:** 20

**Recommended Fix Order:**
1. Fix path validation (30 min)
2. Add buffer limits (15 min)
3. Validate container images (20 min)
4. Fix shell injection (45 min)
5. Sanitize errors (30 min)
6. Implement rate limiting (1 hour)
7. Fix embedding model parameter (10 min)
8. Add file locking (30 min)
9. Write critical tests (4 hours)
10. Add input validation (20 min)

**Estimated Total Time:** ~8-10 hours for all critical and high priority fixes.
