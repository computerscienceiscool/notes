# LLM Runtime Tool - Practical Demo Guide

## Prerequisites

1. **Build the tool**:
   ```bash
   make build
   ```

2. **For exec commands** (optional):
   ```bash
   docker pull ubuntu:22.04
   ```

3. **For search** (optional):
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull embedding model
   ollama pull nomic-embed-text
   
   # Build search index
   ./llm-runtime reindex
   ```

---

## Demo 1: Reading Files (OPEN Command)

### Basic File Read

**Command**:
```bash
echo "<open README.md>" | ./llm-runtime
```

**What happens**:
1. Scanner detects `<open README.md>`
2. ValidatePath checks:
   - No path traversal (`..`)
   - Not in excluded paths
   - Within repository root
3. File is read (either direct or containerized)
4. Content is returned

**Expected output**:
```
=== LLM TOOL START ===
=== COMMAND: <open README.md> ===
=== FILE: README.md ===
[contents of README.md]
=== END FILE ===
=== END COMMAND ===
=== LLM TOOL COMPLETE ===
Commands executed: 1
Time elapsed: 0.03s
=== END ===
```

### Multiple Files

**Command**:
```bash
cat > multi_read.txt << 'EOF'
<open go.mod>
<open Makefile>
<open cmd/llm-runtime/main.go>
EOF

./llm-runtime --input multi_read.txt
```

**Result**: Each file is read and output sequentially

### Reading with Containerized I/O

**Command**:
```bash
echo "<open README.md>" | ./llm-runtime --io-containerized
```

**What's different**:
- File read happens inside a Docker container
- Extra security layer
- Slightly slower due to container overhead

**To see it work**:
```bash
# Build the I/O container image first
make build-io-image

# Test containerized read
echo "<open README.md>" | ./llm-runtime --io-containerized
```

### Security Test: Path Traversal Prevention

**Command**:
```bash
echo "<open ../../../etc/passwd>" | ./llm-runtime
```

**Expected**: Error message about path traversal detected

**Command**:
```bash
echo "<open .env>" | ./llm-runtime
```

**Expected**: Error message about excluded path

---

## Demo 2: Writing Files (WRITE Command)

### Create a New File

**Command**:
```bash
cat > create_file.txt << 'EOF'
<write hello.txt>
Hello from the LLM Runtime Tool!
This file was created at runtime.

Current features:
- Open files
- Write files
- Execute commands
- Search code
</write>
EOF

./llm-runtime --input create_file.txt
```

**What happens**:
1. Scanner accumulates content between `<write>` and `</write>`
2. Path validation
3. Extension check (.txt is allowed)
4. Size check (must be under MaxWriteSize)
5. Atomic write (temp file + rename)
6. File created: `hello.txt`

**Verify**:
```bash
cat hello.txt
```

### Update with Backup

**Command**:
```bash
cat > update_file.txt << 'EOF'
<write hello.txt>
Hello from the LLM Runtime Tool!
This file was UPDATED at runtime.

Features demonstrated:
- Atomic writes
- Automatic backups
- Content formatting
</write>
EOF

./llm-runtime --input update_file.txt --backup
```

**What happens**:
1. Detects file exists
2. Creates backup: `hello.txt.bak.1234567890`
3. Writes new content
4. Returns backup path

**Verify**:
```bash
ls -la hello.txt*
cat hello.txt
cat hello.txt.bak.*
```

### Write Go Code (with Formatting)

**Command**:
```bash
cat > write_go.txt << 'EOF'
<write test_program.go>
package main
import "fmt"
func main() {
fmt.Println("Hello, World!")
x:=42
y:=100
fmt.Printf("Sum: %d\n",x+y)
}
</write>
EOF

./llm-runtime --input write_go.txt
```

**What happens**:
1. Content is written
2. FormatContent detects `.go` extension
3. Runs `go/format.Source()` to format code
4. Properly formatted Go code is saved

**Verify**:
```bash
cat test_program.go
# Should see properly formatted code with correct indentation
```

### Write JSON (with Formatting)

**Command**:
```bash
cat > write_json.txt << 'EOF'
<write config.json>
{"name":"test","version":"1.0.0","features":["open","write","exec","search"],"limits":{"maxFileSize":1048576,"maxWriteSize":102400}}
</write>
EOF

./llm-runtime --input write_json.txt
```

**Result**: JSON is automatically pretty-printed

**Verify**:
```bash
cat config.json
# Should see formatted JSON with indentation
```

### Security Test: Extension Block

**Command**:
```bash
echo '<write malware.exe>binary content</write>' | ./llm-runtime
```

**Expected**: Error about file extension not allowed

### Security Test: Size Limit

**Command**:
```bash
# Create a file larger than MaxWriteSize (100KB default)
python3 << 'EOF'
content = "A" * 200000  # 200KB
print(f"<write large.txt>\n{content}\n</write>")
EOF | ./llm-runtime
```

**Expected**: Error about content too large

---

## Demo 3: Executing Commands (EXEC Command)

### Simple Command

**Command**:
```bash
echo "<exec ls -la>" | ./llm-runtime --exec-enabled
```

**What happens**:
1. Command validated against whitelist
2. Docker container created with:
   - Read-only mount of repository
   - No network access
   - Limited memory/CPU
   - All capabilities dropped
3. Command executed
4. Output collected

**Expected output**:
```
=== LLM TOOL START ===
=== COMMAND: <exec ls -la> ===
=== EXEC SUCCESSFUL: ls -la ===
Exit code: 0
Duration: 0.523s
Output:
total 48
drwxr-xr-x 1 llmuser llmuser  4096 Dec 12 10:30 .
drwxr-xr-x 1 root    root     4096 Dec 12 10:30 ..
-rw-r--r-- 1 llmuser llmuser  1234 Dec 12 10:30 README.md
...
=== END EXEC ===
=== END COMMAND ===
=== LLM TOOL COMPLETE ===
```

### Run Tests

**Command**:
```bash
echo "<exec go test -v ./...>" | ./llm-runtime --exec-enabled
```

**What happens**:
- Go tests run inside container
- Test output is captured
- Exit code indicates pass/fail

### Execute with Stdin (Multi-line)

**Command**:
```bash
cat > exec_stdin.txt << 'EOF'
<exec python3>
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
</exec>
EOF

./llm-runtime --input exec_stdin.txt --exec-enabled
```

**What happens**:
1. Scanner detects multi-line exec
2. Content between `<exec>` and `</exec>` is stdin
3. Container is configured with `OpenStdin: true`
4. Python code is piped to python3 interpreter

**Expected output**:
```
=== EXEC SUCCESSFUL: python3 ===
Exit code: 0
Duration: 0.234s
Output:
fib(0) = 0
fib(1) = 1
fib(2) = 1
fib(3) = 2
fib(4) = 3
fib(5) = 5
fib(6) = 8
fib(7) = 13
fib(8) = 21
fib(9) = 34
=== END EXEC ===
```

### Timeout Test

**Command**:
```bash
cat > timeout_test.txt << 'EOF'
<exec python3>
import time
print("Starting long operation...")
time.sleep(60)  # Exceeds default 30s timeout
print("Done!")
</exec>
EOF

./llm-runtime --input timeout_test.txt --exec-enabled
```

**Expected**: Timeout after 30 seconds with exit code 124

### Security Test: Network Isolation

**Command**:
```bash
cat > network_test.txt << 'EOF'
<exec python3>
import urllib.request
try:
    urllib.request.urlopen('http://google.com')
    print("Network access!")
except Exception as e:
    print(f"Network blocked: {e}")
</exec>
EOF

./llm-runtime --input network_test.txt --exec-enabled
```

**Expected**: Network connection fails (no network in container)

### Security Test: Whitelist

**Command**:
```bash
echo "<exec rm -rf />" | ./llm-runtime --exec-enabled
```

**Expected**: Error - command not in whitelist

**To allow it**:
```bash
echo "<exec rm -rf />" | ./llm-runtime --exec-enabled --exec-whitelist="rm"
```

**But still safe**: Read-only root filesystem prevents deletion

---

## Demo 4: Semantic Search

### Prerequisites

**Start Ollama**:
```bash
ollama serve &
ollama pull nomic-embed-text
```

**Build Search Index**:
```bash
./llm-runtime reindex
```

**What happens during indexing**:
1. Walks repository directory tree
2. Filters files by extension (.go, .py, .js, .md, etc.)
3. Reads file contents
4. Generates embeddings via Ollama
5. Stores in SQLite database

### Basic Search

**Command**:
```bash
echo "<search authentication logic>" | ./llm-runtime
```

**What happens**:
1. Query embedding generated via Ollama
2. All file embeddings retrieved from database
3. Cosine similarity calculated for each
4. Results ranked by score
5. Top N results returned

**Expected output**:
```
=== LLM TOOL START ===
=== COMMAND: <search authentication logic> ===
=== SEARCH: authentication logic ===
=== SEARCH RESULTS (0.45s) ===
1. internal/session/session.go (score: 78.23)
   Lines: 48 | Size: 1.2 KB
   Preview: "Session manages authentication..."

2. pkg/sandbox/audit.go (score: 72.15)
   Lines: 67 | Size: 2.1 KB
   Preview: "AuditLogger handles audit logging..."

3. internal/cli/config.go (score: 65.89)
   Lines: 89 | Size: 3.4 KB
   Preview: "buildConfig constructs configuration..."

[Showing top 10 results]
=== END SEARCH ===
=== END COMMAND ===
=== LLM TOOL COMPLETE ===
```

### Search for Error Handling

**Command**:
```bash
echo "<search error handling patterns>" | ./llm-runtime
```

**Result**: Files with error handling logic ranked by relevance

### Search for Specific Function

**Command**:
```bash
echo "<search container resource limits>" | ./llm-runtime
```

**Result**: Finds `pkg/sandbox/container.go` and related files

### Search Management Commands

**Check Index Status**:
```bash
./llm-runtime search-status
```

**Output**:
```
Search Index Status
==================
Total files indexed: 42
Total size: 156789 bytes
Oldest index: 2025-12-12 10:30:00
Newest index: 2025-12-12 10:35:00
```

**Validate Index**:
```bash
./llm-runtime search-validate
```

**Update Index** (incremental):
```bash
./llm-runtime search-update
```

**Clean Up** (remove deleted files):
```bash
./llm-runtime search-cleanup
```

**Full Reindex**:
```bash
./llm-runtime reindex
```

---

## Demo 5: Combined Operations

### Read, Analyze, Write

**Scenario**: Read a file, extract information, write a summary

**Command**:
```bash
cat > combined_demo.txt << 'EOF'
<open README.md>

Now let me create a summary:

<write README_SUMMARY.md>
# README Summary

This document summarizes the main features of the LLM Runtime Tool.

## Key Features
1. File operations (read/write)
2. Command execution (sandboxed)
3. Semantic code search
4. Security controls

## Use Cases
- LLM-assisted coding
- Automated code analysis
- Safe command execution
- Repository exploration
</write>
EOF

./llm-runtime --input combined_demo.txt
```

### Search, Read, Execute

**Scenario**: Search for test files, read one, run tests

**Command**:
```bash
cat > search_test_demo.txt << 'EOF'
<search unit test examples>

<open pkg/scanner/scanner_test.go>

<exec go test -v ./pkg/scanner>
EOF

./llm-runtime --input search_test_demo.txt --exec-enabled
```

### Complex Workflow

**Command**:
```bash
cat > complex_workflow.txt << 'EOF'
Step 1: Search for configuration files
<search configuration yaml>

Step 2: Read the main config
<open llm-runtime.config.yaml>

Step 3: Create a test config
<write test_config.yaml>
repository:
  root: "./test"
  excluded_paths:
    - ".git"

commands:
  open:
    enabled: true
    max_file_size: 10240
  
  write:
    enabled: true
    backup_before_write: true
</write>

Step 4: Validate the config syntax
<exec python3>
import yaml
with open('test_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print("Config is valid!")
    print(f"Root: {config['repository']['root']}")
</exec>
EOF

./llm-runtime --input complex_workflow.txt --exec-enabled
```

---

## Interactive Mode Demo

### Start Interactive Session

**Command**:
```bash
./llm-runtime --interactive
```

**What happens**:
- Tool waits for input
- You can enter commands one at a time
- Press Ctrl+D after each command to execute
- Tool continues running for more commands

### Example Session

```
LLM Tool - Interactive Mode
Waiting for input (send EOF with Ctrl+D to process)...
Supports commands: <open filepath>, <write filepath>content</write>, <exec command args>, <search query>

<open go.mod>
[Press Ctrl+D]

=== LLM TOOL START ===
=== COMMAND: <open go.mod> ===
=== FILE: go.mod ===
module github.com/computerscienceiscool/llm-runtime
go 1.21
...
=== END FILE ===
=== END COMMAND ===
=== LLM TOOL COMPLETE ===

Waiting for more input...

<search docker container>
[Press Ctrl+D]

=== LLM TOOL START ===
=== COMMAND: <search docker container> ===
[search results...]
=== END COMMAND ===
=== LLM TOOL COMPLETE ===

Waiting for more input...

[Press Ctrl+D to exit]
```

---

## Monitoring and Debugging

### Verbose Mode

**Command**:
```bash
echo "<open README.md>" | ./llm-runtime --verbose
```

**Additional output**:
```
Repository root: /path/to/llm-runtime
Max file size: 1048576 bytes
Max write file size: 102400 bytes
Allowed extensions: [.go .py .js .md .txt .json .yaml .yml .toml]
Excluded paths: [.git .env *.key *.pem]
Backup enabled: true
Exec enabled: false
```

### Audit Log

**View audit log**:
```bash
tail -f audit.log
```

**Format**:
```
2025-12-12T10:30:15Z|session:1234567890|open|README.md|success|
2025-12-12T10:30:20Z|session:1234567890|write|hello.txt|success|hash:abc123,bytes:456,action:created
2025-12-12T10:30:25Z|session:1234567890|exec|ls -la|success|exit_code:0,duration:0.523s,status:completed
2025-12-12T10:30:30Z|session:1234567890|search|authentication|success|results:5,duration:0.450s
```

### Error Logs

**View error log**:
```bash
tail -f llm-runtime.log
```

---

## Performance Testing

### Benchmark File Operations

**Read performance**:
```bash
time for i in {1..100}; do 
  echo "<open README.md>" | ./llm-runtime > /dev/null
done
```

**Write performance**:
```bash
time for i in {1..100}; do 
  echo "<write test_$i.txt>test content $i</write>" | ./llm-runtime > /dev/null
done
```

### Benchmark Search

**Search performance**:
```bash
time for i in {1..10}; do 
  echo "<search authentication logic>" | ./llm-runtime > /dev/null
done
```

---

## Troubleshooting

### Docker Not Available

**Error**: `DOCKER_UNAVAILABLE: Docker not available`

**Fix**:
```bash
# Check Docker
docker --version

# Start Docker
sudo systemctl start docker

# Test Docker
docker run hello-world
```

### Ollama Not Available

**Error**: `Ollama not available at http://localhost:11434`

**Fix**:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve &

# Pull model
ollama pull nomic-embed-text

# Test
curl http://localhost:11434/api/tags
```

### Path Security Error

**Error**: `PATH_SECURITY: path traversal detected`

**Cause**: Trying to access files outside repository

**Fix**: Use paths relative to repository root

### Extension Denied

**Error**: `EXTENSION_DENIED: file extension not allowed: .exe`

**Fix**: Only write to allowed extensions (configure in config file)

---

## Advanced Configuration

### Custom Config File

**Create `llm-runtime.config.yaml`**:
```yaml
repository:
  root: "."
  excluded_paths:
    - ".git"
    - "node_modules"

commands:
  open:
    enabled: true
    max_file_size: 2097152  # 2MB

  write:
    enabled: true
    max_file_size: 204800  # 200KB
    backup_before_write: true

  exec:
    enabled: true
    timeout_seconds: 60
    memory_limit: "1g"
    cpu_limit: 2
    whitelist:
      - "go test"
      - "npm test"
      - "python3"
      - "make"

  search:
    enabled: true
    max_results: 15
    min_similarity_score: 0.4
```

### Environment Variables

**Set via environment**:
```bash
export LLM_ROOT="/path/to/repo"
export LLM_EXEC_ENABLED=true
export LLM_EXEC_WHITELIST="go test,npm test,python3"

./llm-runtime
```

---

## Cleanup

### Remove Test Files

```bash
rm -f hello.txt hello.txt.bak.*
rm -f test_program.go
rm -f config.json
rm -f README_SUMMARY.md
rm -f test_config.yaml
rm -f test_*.txt
```

### Clean Search Index

```bash
rm -f embeddings.db
```

### Clean Logs

```bash
rm -f audit.log
rm -f llm-runtime.log
```

---

## Summary

This tool provides a complete interface for LLMs to:

1. **Read files** securely with path validation
2. **Write files** with atomic operations and backups
3. **Execute commands** in isolated containers
4. **Search code** using semantic embeddings

All operations are:
- Logged for audit
- Validated for security
- Configurable via YAML or flags
- Optionally containerized for extra isolation
