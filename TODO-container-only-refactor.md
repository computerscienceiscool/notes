# TODO: Container-Only Refactor

## Overview
Simplify security model by making Docker containers the only execution path. Remove host-based path validation and let the container namespace be the security boundary.

---

## 1. Remove IOContainerized Flag & Non-Containerized I/O Path

### 1.1 Remove flag from config
- [ ] `internal/config/types.go`: Delete `IOContainerized bool` field from `Config` struct
- [ ] `internal/config/types.go`: Delete `IOContainerImage string` field
- [ ] `internal/config/types.go`: Delete `IOTimeout time.Duration` field
- [ ] `internal/config/types.go`: Delete `IOMemoryLimit string` field
- [ ] `internal/config/types.go`: Delete `IOCPULimit int` field

### 1.2 Remove flags from CLI
- [ ] `internal/cli/root.go`: Delete `--io-containerized` flag
- [ ] `internal/cli/root.go`: Delete `--io-image` flag
- [ ] `internal/cli/root.go`: Delete `--io-timeout` flag
- [ ] `internal/cli/root.go`: Delete `--io-memory` flag
- [ ] `internal/cli/root.go`: Delete `--io-cpu` flag

### 1.3 Remove from config defaults
- [ ] `internal/config/defaults.go`: Remove all IO-related viper defaults in `SetViperDefaults()`

### 1.4 Simplify open.go - Always use container
- [ ] `pkg/evaluator/open.go`: Delete lines with `if cfg.IOContainerized` conditional
- [ ] `pkg/evaluator/open.go`: Delete entire `else` block (direct `os.ReadFile` path)
- [ ] `pkg/evaluator/open.go`: Keep only `sandbox.ReadFileInContainer()` call
- [ ] `pkg/evaluator/open.go`: Use `ExecContainerImage` instead of `IOContainerImage`
- [ ] `pkg/evaluator/open.go`: Use `ExecTimeout` instead of `IOTimeout`
- [ ] `pkg/evaluator/open.go`: Use `ExecMemoryLimit` instead of `IOMemoryLimit`
- [ ] `pkg/evaluator/open.go`: Use `ExecCPULimit` instead of `IOCPULimit`

### 1.5 Simplify write.go - Always use container
- [ ] `pkg/evaluator/write.go`: Delete lines with `if cfg.IOContainerized` conditional
- [ ] `pkg/evaluator/write.go`: Delete entire `else` block (direct write + `os.MkdirAll` path)
- [ ] `pkg/evaluator/write.go`: Keep only `sandbox.WriteFileInContainer()` call
- [ ] `pkg/evaluator/write.go`: Use `ExecContainerImage` instead of `IOContainerImage`
- [ ] `pkg/evaluator/write.go`: Use `ExecTimeout` instead of `IOTimeout`
- [ ] `pkg/evaluator/write.go`: Use `ExecMemoryLimit` instead of `IOMemoryLimit`
- [ ] `pkg/evaluator/write.go`: Use `ExecCPULimit` instead of `IOCPULimit`

### 1.6 Rename io_container.go
- [ ] `pkg/sandbox/io_container.go`: Rename file to `io.go`
- [ ] Update all imports referencing this file

### 1.7 Update io.go to use exec container settings
- [ ] `pkg/sandbox/io.go`: Remove separate IO container image parameter
- [ ] `pkg/sandbox/io.go`: Update `ReadFileInContainer()` signature - use exec settings
- [ ] `pkg/sandbox/io.go`: Update `WriteFileInContainer()` signature - use exec settings

### 1.8 Remove IO-specific functions
- [ ] `pkg/sandbox/io.go`: Delete `EnsureIOContainerImage()` (use exec image check instead)
- [ ] `pkg/sandbox/io.go`: Delete `ValidateIOContainer()` (use exec validation instead)
- [ ] `pkg/sandbox/io.go`: Delete `parseMemoryLimitIO()` (use exec version)

### 1.9 Update bootstrap
- [ ] `internal/app/bootstrap.go`: Remove IO config loading
- [ ] `internal/app/bootstrap.go`: Add Docker availability check on startup
- [ ] `internal/app/bootstrap.go`: Add exec container image check on startup
- [ ] `internal/app/bootstrap.go`: Fail fast with clear error if Docker unavailable

---

## 2. Remove ValidatePath Completely

### 2.1 Delete ValidatePath function
- [ ] `pkg/sandbox/path.go`: Delete entire file

### 2.2 Remove ValidatePath from open.go
- [ ] `pkg/evaluator/open.go`: Delete `ValidatePath()` call
- [ ] `pkg/evaluator/open.go`: Remove `safePath` variable
- [ ] `pkg/evaluator/open.go`: Use `filepath` directly instead of `safePath`
- [ ] `pkg/evaluator/open.go`: Remove error handling for path validation

### 2.3 Remove ValidatePath from write.go
- [ ] `pkg/evaluator/write.go`: Delete `ValidatePath()` call
- [ ] `pkg/evaluator/write.go`: Remove `safePath` variable
- [ ] `pkg/evaluator/write.go`: Use `filePath` directly instead of `safePath`
- [ ] `pkg/evaluator/write.go`: Remove error handling for path validation

### 2.4 Remove ExcludedPaths from config
- [ ] `internal/config/types.go`: Delete `ExcludedPaths []string` field
- [ ] `internal/cli/root.go`: Delete `--exclude` flag
- [ ] `internal/config/defaults.go`: Remove `excluded_paths` defaults
- [ ] `llm-runtime.config.yaml`: Remove `excluded_paths` section
- [ ] `llm-runtime.yaml`: Remove `excluded_paths` section

### 2.5 Update imports
- [ ] Remove `pkg/sandbox` import from files that only used `ValidatePath()`

---

## 3. Allow Symlinks

### 3.1 Remove any symlink restrictions
- [ ] Search codebase for `filepath.EvalSymlinks` - remove defensive checks
- [ ] Search codebase for `os.Lstat` vs `os.Stat` - use `os.Stat` (follows symlinks)
- [ ] Search for symlink-related comments - remove warnings

### 3.2 Update config if symlink restrictions exist
- [ ] Check `llm-runtime.config.yaml` for symlink settings - remove if present
- [ ] Check `internal/config/types.go` for symlink fields - remove if present

---

## 4. Let LLM Manage Symlinks via Exec

### 4.1 Add symlink commands to default whitelist
- [ ] `internal/config/defaults.go`: Add to `commands.exec.whitelist`:
  - `ln`
  - `ln -s`
  - `readlink`
  - `unlink`

### 4.2 Update config files
- [ ] `llm-runtime.config.yaml`: Add symlink commands to `whitelist` section
- [ ] `llm-runtime.yaml`: Add symlink commands to `whitelist` section

### 4.3 Verify ls is already whitelisted
- [ ] Confirm `ls` and `ls -la` are in default whitelist

---

## 5. Simplify Threat Model - Remove Security Validation

### 5.1 Remove file extension validation
- [ ] `pkg/evaluator/write.go`: Delete `ValidateWriteExtension()` call
- [ ] `pkg/evaluator/write.go`: Remove error handling for extension validation
- [ ] `pkg/sandbox/extension.go`: Delete entire file

### 5.2 Remove exec command whitelist validation
- [ ] `pkg/evaluator/exec.go`: Delete `ValidateExecCommand()` call
- [ ] `pkg/evaluator/exec.go`: Remove error handling for whitelist validation
- [ ] `pkg/sandbox/exec_validation.go`: Delete entire file

### 5.3 Remove extension restrictions from config
- [ ] `internal/config/types.go`: Delete `AllowedExtensions []string` field
- [ ] `internal/cli/root.go`: Delete `--allowed-extensions` flag
- [ ] `internal/config/defaults.go`: Remove `allowed_extensions` defaults
- [ ] `llm-runtime.config.yaml`: Remove `allowed_extensions` section
- [ ] `llm-runtime.yaml`: Remove `allowed_extensions` section

### 5.4 Remove whitelist from config
- [ ] `internal/config/types.go`: Delete `ExecWhitelist []string` field
- [ ] `internal/cli/root.go`: Delete `--exec-whitelist` flag
- [ ] `internal/config/defaults.go`: Remove `whitelist` defaults
- [ ] `llm-runtime.config.yaml`: Remove `whitelist` section
- [ ] `llm-runtime.yaml`: Remove `whitelist` section

### 5.5 Remove ExecEnabled flag (always enabled)
- [ ] `internal/config/types.go`: Delete `ExecEnabled bool` field
- [ ] `internal/cli/root.go`: Delete `--exec-enabled` flag
- [ ] `internal/config/defaults.go`: Remove `exec.enabled` default
- [ ] `pkg/evaluator/exec.go`: Remove check for `cfg.ExecEnabled`
- [ ] `llm-runtime.config.yaml`: Remove `enabled: true` from exec section
- [ ] `llm-runtime.yaml`: Remove `enabled: true` from exec section

### 5.6 Keep resource limits (prevent DoS)
- [ ] **KEEP**: `MaxFileSize` - prevent reading huge files
- [ ] **KEEP**: `MaxWriteSize` - prevent writing huge files
- [ ] **KEEP**: `ExecTimeout` - prevent infinite loops
- [ ] **KEEP**: `ExecMemoryLimit` - prevent memory exhaustion
- [ ] **KEEP**: `ExecCPULimit` - prevent CPU hogging

### 5.7 Keep container security settings
- [ ] **KEEP**: `NetworkMode: "none"` - no network access
- [ ] **KEEP**: `CapDrop: "ALL"` - no capabilities
- [ ] **KEEP**: `SecurityOpt: "no-new-privileges"` - no privilege escalation
- [ ] **KEEP**: `ReadonlyRootfs: true` - read-only root filesystem
- [ ] **KEEP**: `User: "1000:1000"` - non-root user

---

## 6. Cleanup Obsolete Code

### 6.1 Delete files
- [ ] Delete `pkg/sandbox/path.go`
- [ ] Delete `pkg/sandbox/extension.go`
- [ ] Delete `pkg/sandbox/exec_validation.go`

### 6.2 Rename files for clarity
- [ ] Rename `pkg/sandbox/io_container.go` → `pkg/sandbox/io.go`
- [ ] Rename `pkg/sandbox/container.go` → `pkg/sandbox/exec.go`
- [ ] Update all imports

### 6.3 Remove unused imports
- [ ] Search for `sandbox.ValidatePath` - remove imports
- [ ] Search for `sandbox.ValidateWriteExtension` - remove imports
- [ ] Search for `sandbox.ValidateExecCommand` - remove imports

---

## 7. Update Startup Behavior

### 7.1 Require Docker on startup
- [ ] `internal/app/bootstrap.go`: Add `sandbox.CheckDockerAvailability()` at start
- [ ] `internal/app/bootstrap.go`: Return clear error if Docker not available
- [ ] Error message: "Docker is required. Install: https://docs.docker.com/get-docker/"

### 7.2 Verify container image on startup
- [ ] `internal/app/bootstrap.go`: Check exec container image exists
- [ ] `internal/app/bootstrap.go`: Pull image if missing (or fail with instruction)

### 7.3 Update help text
- [ ] `internal/cli/root.go`: Update command description to mention Docker requirement
- [ ] `internal/cli/root.go`: Add note: "Requires Docker to be installed and running"

---

## 8. Update Documentation

### 8.1 Update code walkthrough
- [ ] `llm-runtime-walkthrough.md`: Remove sections about non-containerized I/O
- [ ] `llm-runtime-walkthrough.md`: Remove path validation sections
- [ ] `llm-runtime-walkthrough.md`: Update security model section
- [ ] `llm-runtime-walkthrough.md`: Explain container-only approach

### 8.2 Update demo guide
- [ ] `llm-runtime-demo-guide.md`: Remove `--io-containerized` flag examples
- [ ] `llm-runtime-demo-guide.md`: Remove path traversal security tests
- [ ] `llm-runtime-demo-guide.md`: Remove extension validation tests
- [ ] `llm-runtime-demo-guide.md`: Add symlink examples
- [ ] `llm-runtime-demo-guide.md`: Update prerequisites (Docker required)

### 8.3 Update architecture docs
- [ ] `llm-runtime-architecture.md`: Remove path validation layer from diagrams
- [ ] `llm-runtime-architecture.md`: Simplify security layers diagram
- [ ] `llm-runtime-architecture.md`: Update to show container-only flow

### 8.4 Create new security documentation
- [ ] Create `SECURITY.md`: Document container-based threat model
- [ ] `SECURITY.md`: Explain what containers protect against
- [ ] `SECURITY.md`: Explain what containers DON'T protect against
- [ ] `SECURITY.md`: Document resource limits
- [ ] `SECURITY.md`: Note: LLM has full filesystem access within container

---

## 9. Update Configuration Files

### 9.1 Simplify llm-runtime.config.yaml
- [ ] Remove `io-containerized` settings
- [ ] Remove `excluded_paths`
- [ ] Remove `allowed_extensions`
- [ ] Remove `exec.enabled`
- [ ] Remove `exec.whitelist`
- [ ] Keep resource limits
- [ ] Add comment: "Docker required - all operations run in containers"

### 9.2 Simplify llm-runtime.yaml
- [ ] Same changes as above

---

## 10. Verification Steps

### 10.1 Build
- [ ] `make clean`
- [ ] `make build`
- [ ] Verify no compilation errors

### 10.2 Test Docker requirement
- [ ] Stop Docker daemon
- [ ] Run `./llm-runtime`
- [ ] Verify clear error message about Docker being required
- [ ] Start Docker daemon

### 10.3 Test read operations
- [ ] `echo '<open README.md>' | ./llm-runtime`
- [ ] Verify file contents displayed
- [ ] Check Docker container was created/removed

### 10.4 Test write operations
- [ ] `echo '<write test.txt>hello</write>' | ./llm-runtime`
- [ ] Verify file created
- [ ] `cat test.txt` - verify contents
- [ ] `rm test.txt`

### 10.5 Test nested directory creation
- [ ] `echo '<write a/b/c/deep.txt>nested</write>' | ./llm-runtime`
- [ ] Verify directories and file created
- [ ] `rm -rf a/`

### 10.6 Test exec operations
- [ ] `echo '<exec ls -la>' | ./llm-runtime`
- [ ] Verify directory listing shown

### 10.7 Test symlink creation
- [ ] `echo '<exec ln -s README.md link.md>' | ./llm-runtime`
- [ ] `echo '<open link.md>' | ./llm-runtime`
- [ ] Verify symlink works (shows README contents)
- [ ] `rm link.md`

### 10.8 Test symlink management
- [ ] `echo '<exec ls -la link.md>' | ./llm-runtime`
- [ ] `echo '<exec readlink link.md>' | ./llm-runtime`
- [ ] `echo '<exec unlink link.md>' | ./llm-runtime`

### 10.9 Test previously-restricted operations now work
- [ ] Write to "forbidden" extension: `echo '<write test.exe>content</write>' | ./llm-runtime`
- [ ] Write to "forbidden" path: `echo '<write .env>secret</write>' | ./llm-runtime`
- [ ] Run "forbidden" command: `echo '<exec curl example.com>' | ./llm-runtime` (should fail - no network)
- [ ] Clean up: `rm test.exe .env`

### 10.10 Verify resource limits still work
- [ ] Test timeout: `echo '<exec sleep 60>' | ./llm-runtime` (should timeout)
- [ ] Test large file: Create 2MB file, try to read (should fail if MaxFileSize < 2MB)

---

## Expected Result

### Before
- Mixed execution: Host or container based on `--io-containerized` flag
- Path validation prevents certain operations
- Extension whitelist prevents certain file writes
- Command whitelist prevents certain exec commands
- Complex security model with multiple layers

### After
- All operations run in containers
- No path validation - LLM has full filesystem access in container
- No extension restrictions - LLM can write any file type
- No command whitelist - LLM can run any command
- Simple security model: Container namespace is the boundary
- Resource limits prevent DoS attacks

### Security Boundary
- **Before**: Path validation + extension checks + command whitelist + containers
- **After**: Containers only (with resource limits)

### Trade-offs
- ✅ Simpler code
- ✅ More flexible for LLM
- ✅ Clearer threat model
- ⚠️ Requires Docker (not optional)
- ⚠️ LLM has more freedom (intentional)
