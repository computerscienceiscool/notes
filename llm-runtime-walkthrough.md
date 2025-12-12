# LLM Runtime Tool - Complete Code Walkthrough

## Overview

The LLM Runtime Tool is a Go-based system that enables Large Language Models to interact with local filesystems and execute sandboxed commands. It supports four main operations:
1. **Open** - Read files from the repository
2. **Write** - Create or modify files in the repository
3. **Exec** - Execute commands in isolated Docker containers
4. **Search** - Semantic search across the codebase using embeddings

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│  (internal/cli/root.go, commands.go, config.go)            │
│  - Flag parsing                                              │
│  - Configuration loading                                     │
│  - Command routing                                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Application Layer                        │
│  (internal/app/bootstrap.go, app.go)                        │
│  - Session management                                        │
│  - Input/Output handling                                     │
│  - Executor coordination                                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Executor Layer                          │
│  (pkg/evaluator/executor.go, open.go, write.go, exec.go)   │
│  - Command dispatch                                          │
│  - Security validation                                       │
│  - Result aggregation                                        │
└────────────┬────────────────────────────────────────────────┘
             │
   ┌─────────┴──────────┬──────────────┬──────────────┐
   │                    │              │              │
┌──▼────────┐  ┌────────▼─────┐  ┌────▼──────┐  ┌───▼──────┐
│  Scanner   │  │   Sandbox    │  │  Search   │  │  Config  │
│  Layer     │  │   Layer      │  │  Engine   │  │  Layer   │
└────────────┘  └──────────────┘  └───────────┘  └──────────┘
```

---

## 1. OPEN Command - Reading Files

### User Input
```
<open path/to/file.go>
```

### Code Flow

#### Step 1: Scanner Parsing (`pkg/scanner/scanner.go`)

**Line 72-77**: Scanner detects `<open` tag
```go
case StateTagOpen:
    if strings.HasPrefix(buffered, "<open") {
        s.startCommand("open")
        s.transitionTo(StateOpen)
        s.buffer.Reset()
    }
```

**Line 94-102**: Collects filepath until `>`
```go
case StateOpen:
    if ch == '>' {
        s.currentCmd.Argument = strings.TrimSpace(s.buffer.String())
        s.transitionTo(StateScanning)
        cmd := s.currentCmd
        s.resetCommand()
        return cmd
    }
```

**Returns**: `Command{Type: "open", Argument: "path/to/file.go"}`

#### Step 2: Command Execution (`pkg/evaluator/executor.go`)

**Line 29-34**: Dispatch to ExecuteOpen
```go
func (e *Executor) Execute(cmd scanner.Command) scanner.ExecutionResult {
    switch cmd.Type {
    case "open":
        result = ExecuteOpen(cmd.Argument, e.config, e.auditLog)
    // ...
}
```

#### Step 3: Path Validation (`pkg/sandbox/path.go`)

**ExecuteOpen calls ValidatePath** (`pkg/evaluator/open.go` line 17-25)

**Path Security Checks** (`pkg/sandbox/path.go` line 8-17):
```go
func ValidatePath(requestedPath, repositoryRoot string, excludedPaths []string) (string, error) {
    cleanPath := filepath.Clean(requestedPath)
    
    // Check for path traversal
    if strings.HasPrefix(cleanPath, "..") || strings.Contains(cleanPath, "/../") {
        return "", fmt.Errorf("path traversal detected: %s", requestedPath)
    }
    
    // Check excluded paths
    for _, excluded := range excludedPaths {
        // Match logic...
    }
```

**Line 44-56**: Makes path absolute
```go
if filepath.IsAbs(cleanPath) {
    absPath = cleanPath
    if !strings.HasPrefix(absPath, repositoryRoot) {
        return "", fmt.Errorf("path is not within repository")
    }
} else {
    absPath = filepath.Join(repositoryRoot, cleanPath)
}
```

#### Step 4: File Reading (`pkg/evaluator/open.go`)

**Two modes**: Direct or Containerized I/O

##### Mode A: Direct Read (default)
**Line 58-70**:
```go
if cfg.IOContainerized {
    // Container path...
} else {
    content, err = os.ReadFile(safePath)
    if err != nil {
        result.Error = fmt.Errorf("READ_ERROR: %w", err)
        return result
    }
}
```

##### Mode B: Containerized Read
**Line 52-57**: Calls `sandbox.ReadFileInContainer`

**Container execution** (`pkg/sandbox/io_container.go` line 94-99):
```go
func ReadFileInContainer(filePath, repoRoot, containerImage string, 
                        timeout time.Duration, memLimit string, cpuLimit int) (string, error) {
    relPath, err := filepath.Rel(repoRoot, filePath)
    command := fmt.Sprintf("cat /workspace/%s", relPath)
    return RunIOContainer(repoRoot, containerImage, command, timeout, memLimit, cpuLimit)
}
```

#### Step 5: Result Formatting (`internal/app/app.go`)

**Line 80-96**: Formats output
```go
switch cmd.Type {
case "open":
    fmt.Fprintf(output, "=== FILE: %s ===\n", cmd.Argument)
    fmt.Fprint(output, result.Result)
    if !strings.HasSuffix(result.Result, "\n") {
        fmt.Fprint(output, "\n")
    }
    fmt.Fprint(output, "=== END FILE ===\n")
```

### Output Format
```
=== LLM TOOL START ===
=== COMMAND: <open path/to/file.go> ===
=== FILE: path/to/file.go ===
[file contents here]
=== END FILE ===
=== END COMMAND ===
=== LLM TOOL COMPLETE ===
Commands executed: 1
Time elapsed: 0.05s
=== END ===
```

---

## 2. WRITE Command - Creating/Modifying Files

### User Input
```
<write path/to/file.go>
package main

func main() {
    println("Hello!")
}
</write>
```

### Code Flow

#### Step 1: Scanner Parsing (`pkg/scanner/scanner.go`)

**Line 72-77**: Detects `<write` tag
```go
case StateTagOpen:
    if strings.HasPrefix(buffered, "<write") {
        s.startCommand("write")
        s.transitionTo(StateWrite)
        s.buffer.Reset()
    }
```

**Line 104-114**: Collects filepath
```go
case StateWrite:
    if ch == '>' {
        s.currentCmd.Argument = strings.TrimSpace(s.buffer.String())
        s.transitionTo(StateWriteBody)
        s.buffer.Reset()
    }
```

**Line 116-128**: Accumulates content until `</write>`
```go
case StateWriteBody:
    s.buffer.WriteByte(ch)
    buffered := s.buffer.String()
    if strings.Contains(buffered, "</write>") {
        idx := strings.Index(buffered, "</write>")
        content := buffered[:idx]
        s.currentCmd.Content = strings.TrimSpace(content)
        // Return command
    }
```

**Returns**: `Command{Type: "write", Argument: "path/to/file.go", Content: "package main..."}`

#### Step 2: Executor Dispatch (`pkg/evaluator/executor.go`)

**Line 32**: Routes to ExecuteWrite
```go
case "write":
    result = ExecuteWrite(cmd.Argument, cmd.Content, e.config, e.auditLog)
```

#### Step 3: Security Validation (`pkg/evaluator/write.go`)

**Path Validation** (Line 61-71):
```go
safePath, err := sandbox.ValidatePath(filePath, cfg.RepositoryRoot, cfg.ExcludedPaths)
if err != nil {
    result.Error = fmt.Errorf("PATH_SECURITY: %w", err)
    return result
}
```

**Extension Validation** (Line 73-81):
```go
if err := sandbox.ValidateWriteExtension(filePath, cfg.AllowedExtensions); err != nil {
    result.Error = fmt.Errorf("EXTENSION_DENIED: %w", err)
    return result
}
```

**Extension check** (`pkg/sandbox/extension.go` line 8-24):
```go
func ValidateWriteExtension(filePath string, allowedExtensions []string) error {
    lastDot := strings.LastIndex(filePath, ".")
    if lastDot == -1 {
        return fmt.Errorf("file has no extension")
    }
    
    ext := strings.ToLower(filePath[lastDot:])
    for _, allowedExt := range allowedExtensions {
        if strings.ToLower(allowedExt) == ext {
            return nil
        }
    }
    return fmt.Errorf("file extension not allowed: %s", ext)
}
```

**Size Validation** (Line 83-91):
```go
contentBytes := []byte(content)
if int64(len(contentBytes)) > cfg.MaxWriteSize {
    result.Error = fmt.Errorf("RESOURCE_LIMIT: content too large")
    return result
}
```

#### Step 4: Backup Creation (if enabled)

**Check if file exists** (Line 93-113):
```go
if _, err := os.Stat(safePath); err == nil {
    fileExists = true
    result.Action = "UPDATED"
    
    if cfg.BackupBeforeWrite {
        backupPath, err = CreateBackup(safePath)
        result.BackupFile = backupPath
    }
}
```

**CreateBackup function** (`pkg/evaluator/write.go` line 17-31):
```go
func CreateBackup(filePath string) (string, error) {
    timestamp := time.Now().Unix()
    backupPath := fmt.Sprintf("%s.bak.%d", filePath, timestamp)
    
    originalContent, err := os.ReadFile(filePath)
    err = os.WriteFile(backupPath, originalContent, 0644)
    
    return backupPath, nil
}
```

#### Step 5: Content Formatting

**FormatContent** (Line 115-122):
```go
formattedContent, err := FormatContent(filePath, content)
```

**Format based on extension** (`pkg/evaluator/write.go` line 33-59):
```go
func FormatContent(filePath, content string) (string, error) {
    ext := strings.ToLower(filePath[lastDot:])
    
    switch ext {
    case ".go":
        formatted, err := format.Source([]byte(content))
        return string(formatted), nil
    case ".json":
        // JSON formatting...
    default:
        return content, nil
    }
}
```

#### Step 6: File Writing

**Two modes**: Direct or Containerized

##### Mode A: Direct Write (default)
**Atomic write** (Line 144-168):
```go
tempPath := safePath + ".tmp." + strconv.FormatInt(time.Now().UnixNano(), 10)
err = os.WriteFile(tempPath, []byte(formattedContent), 0644)
err = os.Rename(tempPath, safePath)
```

##### Mode B: Containerized Write
**Container write** (Line 135-143):
```go
err = sandbox.WriteFileInContainer(
    safePath,
    formattedContent,
    cfg.RepositoryRoot,
    cfg.IOContainerImage,
    cfg.IOTimeout,
    cfg.IOMemoryLimit,
    cfg.IOCPULimit,
)
```

**Container implementation** (`pkg/sandbox/io_container.go` line 104-162):
- Creates container with read-write mount
- Uses atomic write (temp file + rename)
- Enforces resource limits

#### Step 7: Result Formatting (`internal/app/app.go`)

**Line 98-106**:
```go
case "write":
    fmt.Fprintf(output, "=== WRITE SUCCESSFUL: %s ===\n", cmd.Argument)
    fmt.Fprintf(output, "Action: %s\n", result.Action)
    fmt.Fprintf(output, "Bytes written: %d\n", result.BytesWritten)
    if result.BackupFile != "" {
        fmt.Fprintf(output, "Backup: %s\n", result.BackupFile)
    }
    fmt.Fprint(output, "=== END WRITE ===\n")
```

---

## 3. EXEC Command - Sandboxed Command Execution

### User Input

**Single-line** (no stdin):
```
<exec go test -v>
```

**Multi-line** (with stdin):
```
<exec python3>
print("Hello from Docker!")
for i in range(5):
    print(f"Number: {i}")
</exec>
```

### Code Flow

#### Step 1: Scanner Parsing (`pkg/scanner/scanner.go`)

**Detects `<exec`** (Line 72-77):
```go
if strings.HasPrefix(buffered, "<exec") {
    s.startCommand("exec")
    s.transitionTo(StateExec)
}
```

**Parses command** (Line 129-149):
```go
case StateExec:
    if ch == '>' {
        s.currentCmd.Argument = strings.TrimSpace(s.buffer.String())
        s.buffer.Reset()
        
        remainingLine := strings.TrimSpace(line[i+1:])
        if remainingLine == "" {
            s.transitionTo(StateExecBody)  // Multi-line mode
        } else {
            // Single-line mode
            return cmd
        }
    }
```

**Collects stdin content** (Line 150-173):
```go
case StateExecBody:
    s.buffer.WriteByte(ch)
    buffered := s.buffer.String()
    
    if strings.Contains(buffered, "</exec>") {
        idx := strings.Index(buffered, "</exec>")
        content := buffered[:idx]
        s.currentCmd.Content = strings.TrimSpace(content)
        return cmd
    }
```

#### Step 2: Command Validation (`pkg/evaluator/exec.go`)

**ValidateExecCommand** (Line 17-19):
```go
if err := sandbox.ValidateExecCommand(cmd.Argument, cfg.ExecEnabled, cfg.ExecWhitelist); err != nil {
    result.Error = fmt.Errorf("EXEC_VALIDATION: %w", err)
    return result
}
```

**Whitelist check** (`pkg/sandbox/exec_validation.go` line 8-30):
```go
func ValidateExecCommand(command string, execEnabled bool, whitelist []string) error {
    if !execEnabled {
        return fmt.Errorf("exec command is disabled")
    }
    
    commandParts := strings.Fields(command)
    baseCommand := commandParts[0]
    
    // Check against whitelist
    for _, allowed := range whitelist {
        if allowed == baseCommand || strings.HasPrefix(command, allowed) {
            return nil
        }
    }
    
    return fmt.Errorf("command not in whitelist: %s", baseCommand)
}
```

#### Step 3: Docker Setup

**Check Docker availability** (Line 24-32):
```go
if err := sandbox.CheckDockerAvailability(); err != nil {
    result.Error = fmt.Errorf("DOCKER_UNAVAILABLE: %w", err)
    return result
}
```

**CheckDockerAvailability** (`pkg/sandbox/client.go` line 11-24):
```go
func CheckDockerAvailability() error {
    cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
    defer cli.Close()
    
    ctx := context.Background()
    _, err = cli.Ping(ctx)
    if err != nil {
        return fmt.Errorf("Docker not available: %w", err)
    }
    return nil
}
```

**Pull image if needed** (Line 34-42):
```go
if err := sandbox.PullDockerImage(cfg.ExecContainerImage, cfg.Verbose); err != nil {
    result.Error = fmt.Errorf("DOCKER_IMAGE: %w", err)
    return result
}
```

#### Step 4: Container Execution (`pkg/sandbox/container.go`)

**Configure container** (Line 58-75):
```go
containerConfig := &container.Config{
    Image:      cfg.Image,
    Cmd:        strslice.StrSlice{"sh", "-c", cfg.Command},
    WorkingDir: "/workspace",
    User:       "1000:1000",
}

// Enable stdin if provided
if cfg.Stdin != "" {
    containerConfig.OpenStdin = true
    containerConfig.AttachStdin = true
    containerConfig.StdinOnce = true
}
```

**Security settings** (Line 77-106):
```go
hostConfig := &container.HostConfig{
    NetworkMode: "none",  // No network access
    Resources: container.Resources{
        Memory:   parseMemoryLimit(cfg.MemoryLimit),
        NanoCPUs: int64(cfg.CPULimit) * 1000000000,
    },
    Mounts: []mount.Mount{
        {
            Type:     mount.TypeBind,
            Source:   cfg.RepoRoot,
            Target:   "/workspace",
            ReadOnly: true,  // Read-only access
        },
        {
            Type:   mount.TypeBind,
            Source: tempDir,
            Target: "/tmp/workspace",
        },
    },
    CapDrop:        strslice.StrSlice{"ALL"},  // Drop all capabilities
    SecurityOpt:    []string{"no-new-privileges"},
    ReadonlyRootfs: true,  // Read-only root filesystem
    Tmpfs: map[string]string{
        "/tmp":    "exec",
        "/.cache": "",
        "/go":     "",
    },
}
```

**Create and start** (Line 108-117):
```go
resp, err := cli.ContainerCreate(ctx, containerConfig, hostConfig, nil, nil, "")
defer cli.ContainerRemove(ctx, resp.ID, types.ContainerRemoveOptions{Force: true})

// Handle stdin if provided
if cfg.Stdin != "" {
    hijackedResp, err = cli.ContainerAttach(ctx, resp.ID, attachOpts)
    defer hijackedResp.Close()
}

err := cli.ContainerStart(ctx, resp.ID, types.ContainerStartOptions{})
```

**Write stdin** (Line 125-131):
```go
if cfg.Stdin != "" {
    _, err = hijackedResp.Conn.Write([]byte(cfg.Stdin))
    hijackedResp.CloseWrite()
}
```

**Wait with timeout** (Line 133-147):
```go
statusCh, errCh := cli.ContainerWait(ctx, resp.ID, container.WaitConditionNotRunning)
select {
case err := <-errCh:
    if err != nil {
        return result, fmt.Errorf("error waiting for container: %w", err)
    }
case status := <-statusCh:
    result.ExitCode = int(status.StatusCode)
case <-ctx.Done():
    result.ExitCode = 124  // Timeout
    return result, fmt.Errorf("command timed out after %v", cfg.Timeout)
}
```

**Collect logs** (Line 149-163):
```go
logReader, err := cli.ContainerLogs(ctx, resp.ID, types.ContainerLogsOptions{
    ShowStdout: true,
    ShowStderr: true,
})
defer logReader.Close()

var stdout, stderr strings.Builder
if err := demuxLogs(logReader, &stdout, &stderr); err != nil {
    return result, fmt.Errorf("failed to read container logs: %w", err)
}

result.Stdout = stdout.String()
result.Stderr = stderr.String()
```

#### Step 5: Result Formatting (`internal/app/app.go`)

**Line 108-121**:
```go
case "exec":
    fmt.Fprintf(output, "=== EXEC SUCCESSFUL: %s ===\n", cmd.Argument)
    fmt.Fprintf(output, "Exit code: %d\n", result.ExitCode)
    fmt.Fprintf(output, "Duration: %.3fs\n", result.ExecutionTime.Seconds())
    if result.Result != "" {
        fmt.Fprint(output, "Output:\n")
        fmt.Fprint(output, result.Result)
    }
    fmt.Fprint(output, "=== END EXEC ===\n")
```

---

## 4. SEARCH Command - Semantic Code Search

### User Input
```
<search authentication logic>
```

### Code Flow

#### Step 1: Scanner Parsing (`pkg/scanner/scanner.go`)

**Detects `<search`** (Line 72-77):
```go
if strings.HasPrefix(buffered, "<search") {
    s.startCommand("search")
    s.transitionTo(StateSearch)
}
```

**Collects query** (Line 175-185):
```go
case StateSearch:
    if ch == '>' {
        s.currentCmd.Argument = strings.TrimSpace(s.buffer.String())
        return cmd
    }
```

#### Step 2: Search Engine Initialization (`pkg/evaluator/search.go`)

**Check if enabled** (Line 10-18):
```go
if searchCfg == nil || !searchCfg.Enabled {
    result.Error = fmt.Errorf("SEARCH_DISABLED: search feature is not enabled")
    return result
}
```

**Initialize engine** (Line 20-28):
```go
searchEngine, err := search.NewSearchEngine(searchCfg, cfg.RepositoryRoot)
if err != nil {
    result.Error = fmt.Errorf("SEARCH_INIT_FAILED: %w", err)
    return result
}
defer searchEngine.Close()
```

**NewSearchEngine** (`internal/search/engine.go` line 14-39):
```go
func NewSearchEngine(cfg *SearchConfig, repoRoot string) (*SearchEngine, error) {
    if !cfg.Enabled {
        return nil, fmt.Errorf("search is not enabled")
    }
    
    // Initialize database
    db, err := InitSearchDB(cfg.VectorDBPath)
    
    return &SearchEngine{
        db:       db,
        config:   cfg,
        repoRoot: repoRoot,
    }, nil
}
```

#### Step 3: Database Schema (`internal/search/database.go`)

**InitSearchDB** (Line 21-46):
```go
func InitSearchDB(dbPath string) (*sql.DB, error) {
    db, err := sql.Open("sqlite3", dbPath)
    
    schema := `
    CREATE TABLE IF NOT EXISTS embeddings (
        filepath TEXT PRIMARY KEY,
        content_hash TEXT NOT NULL,
        embedding BLOB NOT NULL,
        last_modified INTEGER NOT NULL,
        file_size INTEGER NOT NULL,
        indexed_at INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_hash ON embeddings(content_hash);
    CREATE INDEX IF NOT EXISTS idx_modified ON embeddings(last_modified);
    `
    
    _, err := db.Exec(schema)
    return db, nil
}
```

#### Step 4: Generate Query Embedding (`internal/search/engine.go`)

**Check Ollama** (Line 49-52):
```go
if err := checkOllamaAvailability(se.config.OllamaURL); err != nil {
    return nil, fmt.Errorf("Ollama not available: %w", err)
}
```

**checkOllamaAvailability** (Line 110-120):
```go
func checkOllamaAvailability(ollamaURL string) error {
    resp, err := http.Get(ollamaURL + "/api/tags")
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("Ollama responded with status %d", resp.StatusCode)
    }
    return nil
}
```

**Generate embedding** (Line 54-58):
```go
queryEmbedding, err := generateEmbedding(se.config.OllamaURL, query)
if err != nil {
    return nil, fmt.Errorf("failed to generate query embedding: %w", err)
}
```

**generateEmbedding** (`internal/search/embedding.go` line 19-66):
```go
func generateEmbedding(ollamaURL string, text string) ([]float32, error) {
    // Prepare request
    reqBody := OllamaEmbeddingRequest{
        Model:  "nomic-embed-text",
        Prompt: text,
    }
    
    jsonData, err := json.Marshal(reqBody)
    
    // Make HTTP request to Ollama
    resp, err := http.Post(ollamaURL+"/api/embeddings", "application/json", bytes.NewBuffer(jsonData))
    defer resp.Body.Close()
    
    // Parse response
    var ollamaResp OllamaEmbeddingResponse
    json.NewDecoder(resp.Body).Decode(&ollamaResp)
    
    // Convert []float64 to []float32
    embedding := make([]float32, embeddingDimensions)
    for i, v := range ollamaResp.Embedding {
        embedding[i] = float32(v)
    }
    
    return embedding, nil
}
```

#### Step 5: Similarity Search (`internal/search/engine.go`)

**Query database** (Line 60-64):
```go
rows, err := se.db.Query("SELECT filepath, embedding, file_size FROM embeddings")
defer rows.Close()

var results []SearchResult
```

**Calculate similarity** (Line 66-84):
```go
for rows.Next() {
    var filePath string
    var embeddingBytes []byte
    var fileSize int64
    
    rows.Scan(&filePath, &embeddingBytes, &fileSize)
    
    // Deserialize embedding
    fileEmbedding := deserializeEmbedding(embeddingBytes)
    
    // Calculate similarity
    score := cosineSimilarity(queryEmbedding, fileEmbedding)
    
    // Filter by minimum score
    if score < float32(se.config.MinSimilarityScore) {
        continue
    }
    
    results = append(results, SearchResult{...})
}
```

**Cosine similarity** (`internal/search/similarity.go` line 10-26):
```go
func cosineSimilarity(a, b []float32) float32 {
    var dotProduct, normA, normB float32
    for i := range a {
        dotProduct += a[i] * b[i]
        normA += a[i] * a[i]
        normB += b[i] * b[i]
    }
    
    if normA == 0 || normB == 0 {
        return 0.0
    }
    
    return dotProduct / (float32(math.Sqrt(float64(normA))) * float32(math.Sqrt(float64(normB))))
}
```

#### Step 6: Rank and Return

**Rank results** (Line 86-93):
```go
rankSearchResults(results)

// Limit results
if se.config.MaxResults > 0 && len(results) > se.config.MaxResults {
    results = results[:se.config.MaxResults]
}

return results, nil
```

**rankSearchResults** (`internal/search/results.go` line 47-51):
```go
func rankSearchResults(results []SearchResult) {
    sort.Slice(results, func(i, j int) bool {
        return results[i].Score > results[j].Score
    })
}
```

#### Step 7: Format Output (`pkg/evaluator/search.go`)

**formatSearchOutput** (Line 53-95):
```go
func formatSearchOutput(query string, results []SearchResult, maxResults int, duration time.Duration) string {
    var output strings.Builder
    
    output.WriteString(fmt.Sprintf("=== SEARCH: %s ===\n", query))
    output.WriteString(fmt.Sprintf("=== SEARCH RESULTS (%.2fs) ===\n", duration.Seconds()))
    
    if len(results) == 0 {
        output.WriteString("No files found matching query.\n")
        return output.String()
    }
    
    for i, result := range results {
        output.WriteString(fmt.Sprintf("%d. %s (score: %.2f)\n",
            i+1, result.FilePath, result.Score*100))
        
        output.WriteString(fmt.Sprintf("   Lines: %d | Size: %s",
            result.LineCount, formatFileSizeForSearch(result.FileSize)))
        output.WriteString("\n")
        
        if result.Preview != "" {
            output.WriteString(fmt.Sprintf("   Preview: \"%s\"\n", result.Preview))
        }
        output.WriteString("\n")
    }
    
    output.WriteString("=== END SEARCH ===\n")
    return output.String()
}
```

---

## Configuration System

### Loading Configuration (`internal/cli/config.go`)

**buildConfig** (Line 15-62):
```go
func buildConfig() (*config.Config, error) {
    cfg := &config.Config{
        RepositoryRoot:      viper.GetString("root"),
        MaxFileSize:         viper.GetInt64("max-size"),
        MaxWriteSize:        viper.GetInt64("max-write-size"),
        ExcludedPaths:       viper.GetStringSlice("exclude"),
        Interactive:         viper.GetBool("interactive"),
        // ... many more fields
    }
    
    // Parse timeout durations
    execTimeoutStr := viper.GetString("exec-timeout")
    execTimeout, err := time.ParseDuration(execTimeoutStr)
    cfg.ExecTimeout = execTimeout
    
    return cfg, nil
}
```

### Default Values (`internal/config/defaults.go`)

**SetViperDefaults** (Line 19-87):
```go
func SetViperDefaults() {
    // Repository defaults
    viper.SetDefault("repository.root", ".")
    viper.SetDefault("repository.excluded_paths", []string{".git", ".env"})
    
    // Command defaults - Open
    viper.SetDefault("commands.open.enabled", true)
    viper.SetDefault("commands.open.max_file_size", 1048576)
    
    // Command defaults - Write
    viper.SetDefault("commands.write.enabled", true)
    viper.SetDefault("commands.write.backup_before_write", true)
    
    // Command defaults - Exec
    viper.SetDefault("commands.exec.enabled", false)
    viper.SetDefault("commands.exec.timeout_seconds", 30)
    viper.SetDefault("commands.exec.whitelist", []string{"go test", "make"})
    
    // Search defaults
    viper.SetDefault("commands.search.enabled", false)
    viper.SetDefault("commands.search.ollama_url", "http://localhost:11434")
}
```

---

## Session and Audit Logging

### Session Management (`internal/session/session.go`)

**NewSession** (Line 17-32):
```go
func NewSession(cfg *config.Config) *Session {
    sessionID := fmt.Sprintf("%d", time.Now().UnixNano())
    
    // Setup audit logging
    auditFile, err := os.OpenFile("audit.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
    auditLogger := log.New(auditFile, "", 0)
    
    return &Session{
        ID:          sessionID,
        Config:      cfg,
        StartTime:   time.Now(),
        AuditLogger: auditLogger,
    }
}
```

**LogAudit** (Line 34-48):
```go
func (s *Session) LogAudit(command, argument string, success bool, errorMsg string) {
    status := "success"
    if !success {
        status = "failed"
    }
    
    logEntry := fmt.Sprintf("%s|session:%s|%s|%s|%s|%s",
        time.Now().Format(time.RFC3339),
        s.ID,
        command,
        argument,
        status,
        errorMsg,
    )
    
    s.AuditLogger.Println(logEntry)
}
```

---

## Search Index Management

### Indexing Files (`internal/search/indexing.go`)

**IndexRepository** (Line 15-76):
```go
func IndexRepository(db *sql.DB, cfg *SearchConfig, repoRoot string, 
                    excludedPaths []string, showProgress bool, reindexAll bool) (*IndexStats, error) {
    
    stats := &IndexStats{StartTime: time.Now()}
    
    // Walk through repository
    err := filepath.Walk(repoRoot, func(path string, info os.FileInfo, err error) error {
        if info.IsDir() {
            return nil
        }
        
        stats.TotalFiles++
        
        relPath, _ := filepath.Rel(repoRoot, path)
        
        // Check if file should be indexed
        if !shouldIndexFile(relPath, cfg.IndexExtensions, excludedPaths) {
            stats.SkippedFiles++
            return nil
        }
        
        // Check file size and type
        if info.Size() > cfg.MaxFileSize || !isTextFile(path) {
            stats.SkippedFiles++
            return nil
        }
        
        // Check if needs indexing
        needsIndexing, _ := fileNeedsIndexing(db, relPath, info, reindexAll)
        if !needsIndexing {
            stats.SkippedFiles++
            return nil
        }
        
        // Index the file
        if err := indexFile(db, cfg, repoRoot, relPath, info); err != nil {
            stats.ErrorFiles++
            return nil
        }
        
        stats.IndexedFiles++
        stats.BytesIndexed += info.Size()
        
        return nil
    })
    
    stats.EndTime = time.Now()
    return stats, err
}
```

**indexFile** (Line 171-203):
```go
func indexFile(db *sql.DB, cfg *SearchConfig, repoRoot string, 
              filePath string, info os.FileInfo) error {
    
    // Read file content
    fullPath := filepath.Join(repoRoot, filePath)
    content, err := os.ReadFile(fullPath)
    
    // Calculate content hash
    contentHash := fmt.Sprintf("%x", content)
    
    // Generate embedding
    truncated := truncateText(string(content), 200)
    embedding, err := generateEmbedding(cfg.OllamaURL, truncated)
    
    // Create file info
    fileInfo := &FileInfo{
        FilePath:     filePath,
        ContentHash:  contentHash,
        Embedding:    embedding,
        LastModified: info.ModTime().Unix(),
        FileSize:     info.Size(),
        IndexedAt:    time.Now().Unix(),
    }
    
    // Store in database
    return storeFileInfo(db, fileInfo)
}
```

---

## Summary

This tool provides a complete system for LLMs to interact with code:

1. **Open**: Securely reads files with path validation
2. **Write**: Creates/modifies files with backups and formatting
3. **Exec**: Runs commands in isolated Docker containers
4. **Search**: Semantic code search using embeddings

All operations are:
- **Secure**: Path traversal protection, sandboxing, resource limits
- **Audited**: Complete logging of all operations
- **Configurable**: YAML config and CLI flags
- **Containerized**: Optional Docker isolation for I/O

Key security features:
- Path validation and exclusion lists
- Extension whitelisting for writes
- Command whitelisting for exec
- Read-only mounts and capability dropping
- Network isolation and resource limits
