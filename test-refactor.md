# Test Fixing Prompt: llm-runtime Post-Refactoring

## Context

I recently refactored the llm-runtime codebase to consolidate duplicate code. The build passes but tests need updating. Test files are temporarily stored in `temp_tests/` and need to be fixed to work with the new package structure.

## The 6 Refactoring Phases

### Phase 1: Identify Duplicates
Discovered the same code existed in both `internal/` and `pkg/` directories:
- Parser/scanner code in both `internal/command/` and `pkg/scanner/`
- Security code in both `internal/security/` and `pkg/sandbox/`
- Docker code in both `internal/docker/` and `pkg/sandbox/`

### Phase 2: Choose Canonical Locations
Decided to keep `pkg/` versions (public API) and delete `internal/` duplicates:
- `pkg/scanner/` - command parsing (kept)
- `pkg/sandbox/` - security + Docker (kept)
- `pkg/evaluator/` - command execution (kept)

### Phase 3: Delete Duplicate Files
Removed from `internal/`:
- `internal/command/parser.go` → kept `pkg/scanner/parser.go`
- `internal/command/types.go` → kept `pkg/scanner/types.go`
- `internal/security/path.go` → kept `pkg/sandbox/path.go`
- `internal/security/extension.go` → kept `pkg/sandbox/extension.go`
- `internal/security/exec_validation.go` → kept `pkg/sandbox/exec_validation.go`
- `internal/security/audit.go` → kept `pkg/sandbox/audit.go`
- `internal/docker/client.go` → kept `pkg/sandbox/client.go`
- `internal/docker/container.go` → kept `pkg/sandbox/container.go`
- `internal/cli/scanner.go` → kept `pkg/scanner/scanner.go`
- `internal/cli/process.go` → dead code, removed entirely

### Phase 4: Update Imports
Changed imports in `pkg/evaluator/*.go`:
```go
// Before
import (
    "github.com/computerscienceiscool/llm-runtime/internal/docker"
    "github.com/computerscienceiscool/llm-runtime/internal/security"
)

// After
import (
    "github.com/computerscienceiscool/llm-runtime/pkg/sandbox"
)
```

### Phase 5: Fix Bugs Found During Refactor
- **Parser ordering bug**: Commands were grouped by type instead of execution order. Fixed by adding `sort.Slice()` by `StartPos`.
- **Unused function**: Removed `isCommandStart()` from `internal/cli/interactive.go` (dead code)

### Phase 6: Move Test Files
Moved test files to `temp_tests/` for later fixing:
```
temp_tests/
├── cli/
│   ├── process_test.go
│   └── scanner_test.go
├── command/
│   └── parser_test.go
├── docker/
│   └── container_test.go
└── security/
    ├── path_test.go
    └── exec_validation_test.go
```

---

## Directory Structure

### Before Refactoring
```
llm-runtime/
├── cmd/llm-runtime/
│   └── main.go
├── internal/
│   ├── app/
│   ├── cli/
│   │   ├── flags.go
│   │   ├── interactive.go
│   │   ├── process.go          # DUPLICATE - dead code
│   │   └── scanner.go          # DUPLICATE of pkg/scanner/
│   ├── command/                 # DUPLICATE of pkg/scanner/
│   │   ├── parser.go
│   │   ├── parser_test.go
│   │   └── types.go
│   ├── config/
│   ├── docker/                  # DUPLICATE of pkg/sandbox/
│   │   ├── client.go
│   │   ├── container.go
│   │   └── container_test.go
│   ├── infrastructure/
│   ├── search/
│   ├── security/                # DUPLICATE of pkg/sandbox/
│   │   ├── audit.go
│   │   ├── exec_validation.go
│   │   ├── exec_validation_test.go
│   │   ├── extension.go
│   │   ├── path.go
│   │   └── path_test.go
│   └── session/
├── pkg/
│   ├── evaluator/
│   │   ├── exec.go              # imported internal/docker, internal/security
│   │   ├── executor.go
│   │   ├── open.go              # imported internal/security
│   │   ├── search.go
│   │   └── write.go             # imported internal/security
│   ├── sandbox/
│   │   ├── audit.go
│   │   ├── client.go
│   │   ├── container.go
│   │   ├── exec_validation.go
│   │   ├── extension.go
│   │   ├── io_container.go
│   │   └── path.go
│   └── scanner/
│       ├── parser.go
│       ├── scanner.go
│       └── types.go
└── docs/
```

### After Refactoring
```
llm-runtime/
├── cmd/llm-runtime/
│   └── main.go
├── internal/
│   ├── app/
│   │   ├── app.go
│   │   └── bootstrap.go
│   ├── cli/
│   │   ├── flags.go
│   │   └── interactive.go       # MODIFIED: uses pkg/scanner
│   ├── config/
│   ├── infrastructure/
│   ├── search/                  # Ollama integration
│   └── session/
├── pkg/
│   ├── evaluator/
│   │   ├── exec.go              # MODIFIED: imports pkg/sandbox
│   │   ├── executor.go
│   │   ├── open.go              # MODIFIED: imports pkg/sandbox
│   │   ├── search.go
│   │   └── write.go             # MODIFIED: imports pkg/sandbox
│   ├── sandbox/                 # CANONICAL: security + Docker
│   │   ├── audit.go
│   │   ├── client.go
│   │   ├── container.go
│   │   ├── exec_validation.go
│   │   ├── extension.go
│   │   ├── io_container.go
│   │   └── path.go
│   └── scanner/                 # CANONICAL: parsing
│       ├── parser.go            # MODIFIED: sort by StartPos
│       ├── scanner.go
│       └── types.go
├── temp_tests/                  # Tests needing fixes
│   ├── cli/
│   ├── command/
│   ├── docker/
│   └── security/
└── docs/
```

---

## Test Files That Need Fixing

### 1. `temp_tests/command/parser_test.go`
**Issues:**
- Package declaration: `package command` → `package scanner`
- Import path: was testing `internal/command`, now test `pkg/scanner`
- Some tests may expect mid-line command matching (old behavior)

**Fix approach:**
```go
// Change package
package scanner

// Update test expectations for HasPrefix behavior
// Commands must start at line beginning (after whitespace)
```

### 2. `temp_tests/security/path_test.go`
**Issues:**
- Package declaration: `package security` → `package sandbox`
- Import path changes

**Fix approach:**
```go
package sandbox
// Tests should work after package rename
```

### 3. `temp_tests/security/exec_validation_test.go`
**Issues:**
- Package declaration: `package security` → `package sandbox`

### 4. `temp_tests/docker/container_test.go`
**Issues:**
- Package declaration: `package docker` → `package sandbox`
- May reference types that moved

### 5. `temp_tests/cli/scanner_test.go`
**Issues:**
- Was testing `internal/cli` scanner, now lives in `pkg/scanner`
- May be redundant with `pkg/scanner` tests

### 6. `temp_tests/cli/process_test.go`
**Issues:**
- Tests dead code (`process.go` was removed)
- **Likely delete entirely**

---

## Task

Please help me fix these test files:

1. **For each test file in `temp_tests/`:**
   - Update package declaration
   - Update import paths
   - Fix any test expectations that don't match new behavior
   - Move to correct location in `pkg/` or `internal/`

2. **Delete tests for removed code:**
   - `process_test.go` - tests dead code

3. **Verify all tests pass:**
   ```bash
   go test ./...
   ```

4. **Clean up:**
   - Remove `temp_tests/` directory after tests are fixed
   - Ensure no duplicate test files

---

## Current Package Mapping

| Old Location | New Location | Package Name |
|--------------|--------------|--------------|
| `internal/command/` | `pkg/scanner/` | `scanner` |
| `internal/security/` | `pkg/sandbox/` | `sandbox` |
| `internal/docker/` | `pkg/sandbox/` | `sandbox` |
| `internal/cli/scanner.go` | `pkg/scanner/` | `scanner` |
| `internal/cli/process.go` | DELETED | - |

## Import Path Changes

```go
// Old
"github.com/computerscienceiscool/llm-runtime/internal/command"
"github.com/computerscienceiscool/llm-runtime/internal/security"
"github.com/computerscienceiscool/llm-runtime/internal/docker"

// New
"github.com/computerscienceiscool/llm-runtime/pkg/scanner"
"github.com/computerscienceiscool/llm-runtime/pkg/sandbox"
```

---

## Additional Context

- Build currently passes: `go build ./...` ✅
- Tests currently fail (files in wrong locations)
- Search functionality moved from Python to Ollama (no `PythonPath` config field)
- Parser now sorts commands by `StartPos` to preserve execution order
