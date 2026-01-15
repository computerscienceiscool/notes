# nv + Diff Workflow Cheatsheet

## Quick Reference Commands

### Opening Diffs
```
\dv          Open diff view (shows uncommitted changes)
\dh          Show git history with diffs
```

### Navigating Changes
```
]c           Jump to next change
[c           Jump to previous change
```

### Managing Views
```
\dc          Close diff view
\b           Toggle file browser (left panel)
```

### Git History Navigation
```
↑/↓          Select commits in history
Enter        View selected commit's diff
```

---

## Complete Workflow Walkthrough

### Step 1: Make Changes
Either manually edit files or let Claude/Codex make changes for you.

### Step 2: Open File in nv
```bash
nv filename.js
```
Or if you already have nv running with a shada file:
```bash
nv
```

### Step 3: View What Changed
**From within nv:**
```
\dv
```
This opens a side-by-side diff showing:
- **Left side**: Original file (committed version)
- **Right side**: Your changes (working copy)

### Step 4: Review the Diff
**Navigate through changes:**
- `]c` - Jump to next change
- `[c` - Jump to previous change

**Toggle file browser:**
- `\b` - Show/hide file list on left
  - Arrow through files
  - Press Enter to view that file's diff

**Move between panes:**
- `Ctrl-w w` - Switch between left/right panes

### Step 5: Close Diff View
```
\dc
```
Returns you to normal editing mode.

### Step 6: Commit Changes
Exit nv and commit, or use Claude/Codex to commit:
```bash
# In Claude/Codex CLI
commit
```

---

## Advanced: Viewing Git History

### View Past Commits
```
\dh
```
Opens git log with commit list in bottom panel.

**Navigate history:**
- `↑/↓` - Move through commits
- `Enter` - View that commit's diff
- `\b` - Toggle file browser to see changed files

**Jump between panels:**
- `Ctrl-w w` - Move cursor between panels

### Close History View
```
\dc
```

---

## Common Scenarios

### Scenario 1: Claude Just Made Changes
```
1. \dv              # See what Claude changed
2. ]c / [c          # Review each change
3. \dc              # Close when satisfied
4. Tell Claude: "commit"
```

### Scenario 2: Review Your Manual Edits
```
1. Edit file in nv
2. :w               # Save
3. \dv              # View your changes
4. Review
5. \dc              # Close
6. Exit and git commit
```

### Scenario 3: Multiple Files Changed
```
1. \dv              # Open diff view
2. \b               # Show file browser
3. ↑/↓              # Navigate file list
4. Enter            # View that file's diff
5. \b               # Hide browser for clean view
6. Repeat for other files
7. \dc              # Close when done
```

### Scenario 4: Check What Changed Yesterday
```
1. \dh              # Open git history
2. ↑/↓              # Find yesterday's commits
3. Enter            # View that diff
4. \b               # Toggle file list
5. \dc              # Close history view
```

---

## Tips

- **Always review diffs before committing** - Catch mistakes early
- **Use `\b` frequently** - Toggle file browser on/off as needed
- **Jump between changes with `]c`/`[c`** - Don't scroll manually
- **`Ctrl-w w` switches panes** - No mouse needed
- **`\dc` always closes** - Gets you back to normal mode

---

## File Locations
- Script: `~/bin/nv`
- Shada files: `nv.shada` at project root
- Example: `~/lab/myproject/nv.shada`
