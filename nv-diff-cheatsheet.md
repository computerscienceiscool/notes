# nv + Diff View Cheatsheet

## nv Script - Project Session Manager

### Setup
```bash
nvim ~/bin/nv          # Paste script here
chmod +x ~/bin/nv      # Make executable
```

### Usage
```bash
nv                     # Open with project session
nv file.txt            # Open file with session
nv file1 file2         # Open multiple files
nv -c                  # Force current directory (ignore parents)
```

### How It Works
1. Searches UP from current dir for existing `nv.shada`
2. Stops at project root, `$HOME`, or `/`
3. Creates `nv.shada` in current dir if none found
4. Opens nvim and restores last session

---

## Neovim Diff View

### Opening Diffs
```
:diffsplit file        # Horizontal diff split
:vert diffsplit file   # Vertical diff split (recommended)
nv file1 file2 -d      # Open two files in diff mode
nvim -d file1 file2    # Direct diff mode
```

### Navigating Changes
```
]c                     # Jump to next change
[c                     # Jump to previous change
```

### Applying Changes
```
do                     # Diff obtain (pull changes from other file)
dp                     # Diff put (push changes to other file)
:diffget               # Get changes from other buffer
:diffput               # Put changes to other buffer
```

### Diff Controls
```
:diffupdate            # Refresh diff highlighting
:diffoff               # Turn off diff mode
:diffoff!              # Turn off diff in all windows
:set diffopt+=iwhite   # Ignore whitespace
zo                     # Open folded section
zc                     # Close folded section
```

---

## Buffer & Split Commands

### Buffers
```
:ls                    # List all open buffers
:bn                    # Next buffer
:bp                    # Previous buffer
:b2                    # Jump to buffer 2
:bd                    # Close current buffer
Ctrl-^                 # Toggle last two buffers
```

### Splits
```
:split file            # Horizontal split
:vsplit file           # Vertical split
Ctrl-w w               # Switch between splits
Ctrl-w q               # Close current split
Ctrl-w =               # Make splits equal size
Ctrl-w |               # Maximize width
Ctrl-w _               # Maximize height
```

---

## Quick Workflows

### Compare Two Files
```bash
nv file1.txt file2.txt -d
# Then use ]c/[c to navigate, do/dp to sync changes
```

### Compare Current File with Git Version
```bash
:vert diffsplit HEAD:%    # Compare with committed version
:vert diffsplit @~1:%     # Compare with previous commit
```

### Compare Buffers
```
:windo diffthis        # Turn current windows into diff
:windo diffoff         # Turn off diff in all windows
```

---

## Troubleshooting

**Multiple files loaded but only see one?**
→ Files are in buffers. Use `:ls` then `:bn` to navigate.

**Which shada file is active?**
→ Run `find . -name "nv.shada"` from project root.

**Want fresh session?**
→ Use `nv -c` or delete existing `nv.shada`.

**Diff not updating?**
→ Run `:diffupdate` to refresh.

**Script not found?**
→ Verify `~/bin` in PATH: `echo $PATH`

---

## File Locations
- Script: `~/bin/nv`
- Shada files: `nv.shada` at project root
- Example: `~/lab/myproject/nv.shada`
