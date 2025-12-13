# Phase 3: Container-Only Refactor - Complete Guide

## Analysis Results

I've analyzed all the uploaded files. Here are the **exact changes** needed:

---

## KEY FINDINGS

### Files with `IOContainerized` or `ExecEnabled` checks:

1. **pkg/evaluator/open.go** (Lines 58-83)
   - Has `if cfg.IOContainerized` branching
   - Contains both containerized and direct filesystem read paths

2. **pkg/evaluator/write.go** (Lines 158-210)
   - Has `if cfg.IOContainerized` branching  
   - Contains both containerized and direct filesystem write paths

3. **pkg/evaluator/exec.go** (Lines 19-23)
   - Has `if !cfg.ExecEnabled` validation check
   - Needs to be removed (exec always enabled in container-only mode)

4. **pkg/sandbox/exec_validation.go** (Lines 10-11)
   - Validates `ExecEnabled` flag
   - Needs simplification

---

## STEP-BY-STEP EXECUTION PLAN

I'll walk you through each change with precise grep/sed commands. Let's do non-test files first, then tests.

---

# PART 1: NON-TEST FILES (.go files)

## Step 1: pkg/evaluator/open.go - Remove Direct Filesystem Path

### Current Code (Lines 58-83):
```go
// Read the file (containerized or direct)
var content []byte
if cfg.IOContainerized {
    // Use containerized I/O
    contentStr, err := sandbox.ReadFileInContainer(
        safePath,
        cfg.RepositoryRoot,
        cfg.IOContainerImage,
        cfg.IOTimeout,
        cfg.IOMemoryLimit,
        cfg.IOCPULimit,
    )
    if err != nil {
        result.Success = false
        result.Error = fmt.Errorf("READ_CONTAINER: %w", err)
        result.ExecutionTime = time.Since(startTime)
        if auditLog != nil {
            auditLog("open", filepath, false, result.Error.Error())
        }
        return result
    }
    content = []byte(contentStr)
} else {
    // Direct file read on host
    content, err = os.ReadFile(safePath)
    if err != nil {
        result.Success = false
        result.Error = fmt.Errorf("READ_ERROR: %w", err)
        result.ExecutionTime = time.Since(startTime)
        if auditLog != nil {
            auditLog("open", filepath, false, result.Error.Error())
        }
        return result
    }
}
```

### Changes Needed:
**Remove the entire `if/else` block and keep only the containerized path.**

### Sed Command:
```bash
sed -i '58,83d' pkg/evaluator/open.go
```

### Then Insert Simplified Code:
```bash
cat >> /tmp/open_replacement.txt << 'EOF'
	// Read the file using containerized I/O (always)
	contentStr, err := sandbox.ReadFileInContainer(
		safePath,
		cfg.RepositoryRoot,
		cfg.IOContainerImage,
		cfg.IOTimeout,
		cfg.IOMemoryLimit,
		cfg.IOCPULimit,
	)
	if err != nil {
		result.Success = false
		result.Error = fmt.Errorf("READ_CONTAINER: %w", err)
		result.ExecutionTime = time.Since(startTime)
		if auditLog != nil {
			auditLog("open", filepath, false, result.Error.Error())
		}
		return result
	}
	content := []byte(contentStr)
EOF

sed -i '57 r /tmp/open_replacement.txt' pkg/evaluator/open.go
```

---

## Step 2: pkg/evaluator/write.go - Remove Direct Filesystem Path

### Current Code (Lines 158-210):
```go
// Write file (containerized or direct)
if cfg.IOContainerized {
    // Use containerized I/O
    err = sandbox.WriteFileInContainer(
        safePath,
        formattedContent,
        cfg.RepositoryRoot,
        cfg.IOContainerImage,
        cfg.IOTimeout,
        cfg.IOMemoryLimit,
        cfg.IOCPULimit,
    )
    if err != nil {
        result.Success = false
        result.Error = fmt.Errorf("WRITE_CONTAINER: %w", err)
        result.ExecutionTime = time.Since(startTime)
        if auditLog != nil {
            auditLog("write", filePath, false, result.Error.Error())
        }
        return result
    }
} else {
    // Direct atomic write on host
    // Create directory if it doesn't exist
    dir := filepath.Dir(safePath)
    if err := os.MkdirAll(dir, 0755); err != nil {
        result.Success = false
        result.Error = fmt.Errorf("DIRECTORY_CREATION_FAILED: %w", err)
        result.ExecutionTime = time.Since(startTime)
        if auditLog != nil {
            auditLog("write", filePath, false, result.Error.Error())
        }
        return result
    }

    tempPath := safePath + ".tmp." + strconv.FormatInt(time.Now().UnixNano(), 10)
    err = os.WriteFile(tempPath, []byte(formattedContent), 0644)
    if err != nil {
        result.Success = false
        result.Error = fmt.Errorf("WRITE_ERROR: %w", err)
        result.ExecutionTime = time.Since(startTime)
        if auditLog != nil {
            auditLog("write", filePath, false, result.Error.Error())
        }
        return result
    }
    err = os.Rename(tempPath, safePath)
    if err != nil {
        os.Remove(tempPath)
        result.Success = false
        result.Error = fmt.Errorf("RENAME_ERROR: %w", err)
        result.ExecutionTime = time.Since(startTime)
        if auditLog != nil {
            auditLog("write", filePath, false, result.Error.Error())
        }
        return result
    }
}
```

### Sed Command:
```bash
sed -i '158,210d' pkg/evaluator/write.go
```

### Insert Simplified Code:
```bash
cat >> /tmp/write_replacement.txt << 'EOF'
	// Write file using containerized I/O (always)
	err = sandbox.WriteFileInContainer(
		safePath,
		formattedContent,
		cfg.RepositoryRoot,
		cfg.IOContainerImage,
		cfg.IOTimeout,
		cfg.IOMemoryLimit,
		cfg.IOCPULimit,
	)
	if err != nil {
		result.Success = false
		result.Error = fmt.Errorf("WRITE_CONTAINER: %w", err)
		result.ExecutionTime = time.Since(startTime)
		if auditLog != nil {
			auditLog("write", filePath, false, result.Error.Error())
		}
		return result
	}
EOF

sed -i '157 r /tmp/write_replacement.txt' pkg/evaluator/write.go
```

### Remove Unnecessary Imports:
```bash
# Remove strconv import (no longer needed)
sed -i '/^[[:space:]]*"strconv"$/d' pkg/evaluator/write.go
```

---

## Step 3: pkg/evaluator/exec.go - Remove ExecEnabled Check

### Current Code (Lines 19-28):
```go
// Validate command
if err := sandbox.ValidateExecCommand(cmd.Argument, cfg.ExecEnabled, cfg.ExecWhitelist); err != nil {
    result.Success = false
    result.Error = fmt.Errorf("EXEC_VALIDATION: %w", err)
    result.ExecutionTime = time.Since(startTime)
    if auditLog != nil {
        auditLog("exec", cmd.Argument, false, result.Error.Error())
    }
    return result
}
```

### Changes:
The validation function signature needs to change. We'll update this in the sandbox package.

---

## Step 4: pkg/sandbox/exec_validation.go - Simplify Validation

### Current Code:
```go
func ValidateExecCommand(command string, execEnabled bool, whitelist []string) error {
	if !execEnabled {
		return fmt.Errorf("exec command is disabled")
	}

	if len(whitelist) == 0 {
		return fmt.Errorf("no commands are whitelisted")
	}
	// ... rest of validation
}
```

### Simplified Version:
```bash
cat > /tmp/exec_validation_new.go << 'EOF'
package sandbox

import (
	"fmt"
	"strings"
)

// ValidateExecCommand checks if the command is allowed to execute
// Note: Exec is always enabled in container-only mode
func ValidateExecCommand(command string, whitelist []string) error {
	if len(whitelist) == 0 {
		return fmt.Errorf("no commands are whitelisted")
	}

	commandParts := strings.Fields(command)
	if len(commandParts) == 0 {
		return fmt.Errorf("empty command")
	}

	baseCommand := commandParts[0]

	// Check against whitelist
	for _, allowed := range whitelist {
		if allowed == baseCommand || strings.HasPrefix(command, allowed) {
			return nil
		}
	}

	return fmt.Errorf("command not in whitelist: %s", baseCommand)
}
EOF

cp /tmp/exec_validation_new.go pkg/sandbox/exec_validation.go
```

### Update exec.go to use new signature:
```bash
sed -i 's/sandbox.ValidateExecCommand(cmd.Argument, cfg.ExecEnabled, cfg.ExecWhitelist)/sandbox.ValidateExecCommand(cmd.Argument, cfg.ExecWhitelist)/' pkg/evaluator/exec.go
```

---

## Step 5: Update pkg/config/types.go - Remove Flags

### Find and Remove Lines:
```bash
# Remove IOContainerized field
sed -i '/IOContainerized[[:space:]]*bool/d' pkg/config/types.go

# Remove ExecEnabled field  
sed -i '/ExecEnabled[[:space:]]*bool/d' pkg/config/types.go
```

---

## Step 6: Update pkg/cli/root.go - Remove CLI Flags

### Search for the flags:
```bash
grep -n "io-containerized\|exec-enabled" pkg/cli/root.go
```

### Remove flag definitions (you'll need to manually identify line numbers):
```bash
# These are examples - adjust line numbers based on your grep output
sed -i '/rootCmd.PersistentFlags().Bool("io-containerized"/d' pkg/cli/root.go
sed -i '/rootCmd.PersistentFlags().Bool("exec-enabled"/d' pkg/cli/root.go
```

---

## Step 7: Update pkg/cli/config.go - Remove Config Assignments

```bash
# Remove IOContainerized assignment
sed -i '/IOContainerized:/d' pkg/cli/config.go

# Remove ExecEnabled assignment
sed -i '/ExecEnabled:/d' pkg/cli/config.go
```

---

## Step 8: Update pkg/config/defaults.go - Remove Defaults

```bash
# Remove default values for removed fields
sed -i '/IOContainerized:[[:space:]]*false,/d' pkg/config/defaults.go
sed -i '/ExecEnabled:[[:space:]]*false,/d' pkg/config/defaults.go
```

---

# PART 2: TEST FILES (*_test.go)

Now let's update all the test files to remove references to the deleted fields.

## Step 9: Update pkg/evaluator/exec_test.go

### Find test cases checking ExecEnabled:
```bash
grep -n "ExecEnabled" pkg/evaluator/exec_test.go
```

### Tests to update:
1. `TestExecuteExec_Disabled` - Delete entirely (exec can't be disabled)
2. `TestExecuteExec_EmptyWhitelist` - Keep (still valid)
3. Update any test that sets `ExecEnabled: false`

```bash
# Remove the entire TestExecuteExec_Disabled test
sed -i '/func TestExecuteExec_Disabled/,/^}/d' pkg/evaluator/exec_test.go

# Update all instances of ExecEnabled: false to remove that line
sed -i '/ExecEnabled:[[:space:]]*false,/d' pkg/evaluator/exec_test.go

# Update all instances of ExecEnabled: true to remove that line (always true now)
sed -i '/ExecEnabled:[[:space:]]*true,/d' pkg/evaluator/exec_test.go
```

---

## Step 10: Update pkg/evaluator/open_test.go

### Remove any references to IOContainerized:
```bash
grep -n "IOContainerized" pkg/evaluator/open_test.go

# If found, remove those lines
sed -i '/IOContainerized:/d' pkg/evaluator/open_test.go
```

---

## Step 11: Update pkg/evaluator/write_test.go

```bash
# Remove IOContainerized references
sed -i '/IOContainerized:/d' pkg/evaluator/write_test.go
```

---

## Step 12: Update pkg/sandbox/exec_validation_test.go

### Update function signature in tests:
```bash
# Replace old function calls with new signature
sed -i 's/ValidateExecCommand(\([^,]*\), true, /ValidateExecCommand(\1, /g' pkg/sandbox/exec_validation_test.go
sed -i 's/ValidateExecCommand(\([^,]*\), false, /ValidateExecCommand(\1, /g' pkg/sandbox/exec_validation_test.go
```

### Remove tests that check execEnabled:
```bash
# Remove test for "exec disabled"
sed -i '/name:[[:space:]]*"exec disabled"/,/},/d' pkg/sandbox/exec_validation_test.go
```

---

# EXECUTION SCRIPT

Here's a complete bash script to run all changes at once:

