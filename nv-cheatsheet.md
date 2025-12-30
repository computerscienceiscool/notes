# nv Script Cheatsheet

## What It Does
Manages per-project Neovim sessions. Each project gets its own `nv.shada` file that remembers cursor positions, open files, and marks.

## Setup
```bash
nvim ~/bin/nv          # Paste script here
chmod +x ~/bin/nv      # Make executable
```

## Usage
```bash
nv                     # Open with project session
nv file.txt            # Open file with session
nv file1 file2         # Open multiple files
nv -c                  # Force current directory (ignore parents)
```

## How It Works
1. Searches UP from current dir for existing `nv.shada`
2. Stops at project root, `$HOME`, or `/`
3. Creates `nv.shada` in current dir if none found
4. Opens nvim and restores last session

## Neovim Buffer Commands
```
:ls                    # List all open buffers
:bn                    # Next buffer
:bp                    # Previous buffer
:b2                    # Jump to buffer 2
:bd                    # Close current buffer
Ctrl-^                 # Toggle last two buffers
```

## Neovim Split Commands
```
:split file            # Horizontal split
:vsplit file           # Vertical split
Ctrl-w w              # Switch between splits
Ctrl-w q              # Close current split
```

## Troubleshooting

**Q: I opened multiple files but only see one**
A: All files are loaded as buffers. Use `:bn` or `:ls` to see them.

**Q: Where is my shada file?**
A: Run `find . -name "nv.shada"` from project root.

**Q: Wrong session restored**
A: Check which `nv.shada` was used. Script walks UP to find nearest one.

**Q: Want fresh session**
A: Use `nv -c` to create new shada in current directory, or delete existing `nv.shada`.

**Q: Script not found**
A: Verify `~/bin` is in PATH: `echo $PATH`

**Q: Permission denied**
A: Run `chmod +x ~/bin/nv`

## File Locations
- Script: `~/bin/nv`
- Shada files: `nv.shada` at root of each project
- Example: `~/lab/myproject/nv.shada`
