# Phase 3: Quick Reference Card

Use this for quick grep/sed commands during refactoring.

---

## FINDING THINGS

### Find all references to removed fields:
```bash
grep -rn "IOContainerized" pkg/ --include="*.go"
grep -rn "ExecEnabled" pkg/ --include="*.go"
```

### Find specific patterns:
```bash
# Find if/else blocks with IOContainerized
grep -A 5 "if cfg.IOContainerized" pkg/evaluator/*.go

# Find validation calls
grep -n "ValidateExecCommand" pkg/evaluator/exec.go

# Find config field definitions
grep -n "IOContainerized\|ExecEnabled" pkg/config/types.go
```

---

## AUTOMATED FIXES

### Remove IOContainerized from config:
```bash
sed -i '/IOContainerized[[:space:]]*bool/d' pkg/config/types.go
```

### Remove ExecEnabled from config:
```bash
sed -i '/ExecEnabled[[:space:]]*bool/d' pkg/config/types.go
```

### Remove from test configs:
```bash
sed -i '/IOContainerized:/d' pkg/evaluator/*_test.go
sed -i '/ExecEnabled:/d' pkg/evaluator/*_test.go
```

### Update ValidateExecCommand calls:
```bash
sed -i 's/ValidateExecCommand(\([^,]*\), cfg\.ExecEnabled, /ValidateExecCommand(\1, /' pkg/evaluator/exec.go
```

### Update ValidateExecCommand test calls:
```bash
sed -i 's/ValidateExecCommand(\([^,]*\), true, /ValidateExecCommand(\1, /g' pkg/sandbox/exec_validation_test.go
sed -i 's/ValidateExecCommand(\([^,]*\), false, /ValidateExecCommand(\1, /g' pkg/sandbox/exec_validation_test.go
```

---

## VERIFICATION COMMANDS

### Check build:
```bash
go build ./...
```

### Check for remaining references:
```bash
grep -r "IOContainerized" pkg/ --include="*.go" | grep -v ".bak" | grep -v "REMOVED"
grep -r "ExecEnabled" pkg/ --include="*.go" | grep -v ".bak" | grep -v "REMOVED"
```

### Run tests:
```bash
go test ./... -v
```

### Check specific packages:
```bash
go test ./pkg/evaluator/... -v
go test ./pkg/sandbox/... -v
```

---

## FILE-SPECIFIC QUICK FIXES

### open.go - Remove entire if/else block:
```bash
# Lines 58-83
sed -i '58,83d' pkg/evaluator/open.go
```

### write.go - Remove entire if/else block:
```bash
# Lines 158-210
sed -i '158,210d' pkg/evaluator/write.go
```

### write.go - Remove strconv import:
```bash
sed -i '/^[[:space:]]*"strconv"$/d' pkg/evaluator/write.go
```

---

## BACKUP COMMANDS

### Create backups before changes:
```bash
cp pkg/evaluator/open.go pkg/evaluator/open.go.bak
cp pkg/evaluator/write.go pkg/evaluator/write.go.bak
cp pkg/evaluator/exec.go pkg/evaluator/exec.go.bak
cp pkg/sandbox/exec_validation.go pkg/sandbox/exec_validation.go.bak
```

### Restore from backup:
```bash
cp pkg/evaluator/open.go.bak pkg/evaluator/open.go
```

---

## DIFF COMMANDS

### See what changed:
```bash
git diff pkg/evaluator/open.go
git diff pkg/evaluator/write.go
git diff pkg/sandbox/exec_validation.go
```

### See all changes:
```bash
git diff pkg/
```

---

## COMMON ERRORS AND FIXES

### Error: "IOContainerized undefined"
```bash
# Find it:
grep -rn "IOContainerized" pkg/

# Remove it:
sed -i '/IOContainerized:/d' <filename>
```

### Error: "ExecEnabled undefined"
```bash
# Find it:
grep -rn "ExecEnabled" pkg/

# Remove it:
sed -i '/ExecEnabled:/d' <filename>
```

### Error: "too many arguments to ValidateExecCommand"
```bash
# Find the call:
grep -n "ValidateExecCommand" pkg/evaluator/exec.go

# Fix it (remove ExecEnabled parameter):
sed -i 's/ValidateExecCommand(cmd\.Argument, cfg\.ExecEnabled, cfg\.ExecWhitelist)/ValidateExecCommand(cmd.Argument, cfg.ExecWhitelist)/' pkg/evaluator/exec.go
```

---

## ONE-LINER VERIFICATION

After all changes, run this:
```bash
go build ./... && \
go test ./... && \
echo "✓ Build and tests passed" || \
echo "✗ Something failed - check output above"
```

---

## FILES TO MODIFY (CHECKLIST)

Core Files:
- [ ] pkg/evaluator/open.go
- [ ] pkg/evaluator/write.go
- [ ] pkg/evaluator/exec.go
- [ ] pkg/sandbox/exec_validation.go
- [ ] pkg/config/types.go
- [ ] pkg/cli/root.go (if exists)
- [ ] pkg/cli/config.go (if exists)
- [ ] pkg/config/defaults.go (if exists)

Test Files:
- [ ] pkg/evaluator/exec_test.go
- [ ] pkg/evaluator/open_test.go
- [ ] pkg/evaluator/write_test.go
- [ ] pkg/sandbox/exec_validation_test.go

---

## LINES TO DELETE

Quick reference for major deletions:

| File | Lines | What |
|------|-------|------|
| open.go | 58-83 | if/else block for IOContainerized |
| write.go | 158-210 | if/else block for IOContainerized |
| types.go | ~XX | IOContainerized bool line |
| types.go | ~XX | ExecEnabled bool line |

Use `grep -n "IOContainerized\|ExecEnabled"` to find exact line numbers.

---

## POST-REFACTORING

After completing changes:

1. **Build:** `go build ./...`
2. **Test:** `go test ./...`
3. **Verify:** `grep -r "IOContainerized\|ExecEnabled" pkg/`
4. **Commit:** `git add -A && git commit -m "Phase 3: Remove non-containerized paths"`

