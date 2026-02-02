# Storm Installation Guide

Complete guide for installing and running Storm on a Linux machine with goenv.

## Prerequisites

- Linux machine (tested on Ubuntu)
- goenv installed and configured
- Go 1.24.0 or later
- OpenAI API key
- Git

## Installation Steps

### 1. Set Up Go Environment

**Check your Go version:**
```bash
go version
```

You need Go 1.24.0 or later. If using goenv:

```bash
# Check available versions
goenv versions

# If 1.24.0+ isn't installed, install it
goenv install 1.24.0

# Set it as the local version in your grokker directory
cd ~/lab/grokker/x/storm
goenv local 1.24.0

# Refresh your shell to pick up correct GOPATH
eval "$(goenv init -)"

# Verify GOPATH points to correct version
echo $GOPATH
# Should show: /home/youruser/go/1.24.0
```

### 2. Set Environment Variables

**Set your OpenAI API key:**
```bash
export OPENAI_API_KEY=your-actual-api-key-here
```

**Make it permanent** by adding to your `~/.bashrc`:
```bash
echo 'export OPENAI_API_KEY=your-actual-api-key-here' >> ~/.bashrc
```

**Fix Go toolchain setting:**
```bash
export GOTOOLCHAIN=auto
```

Add to `~/.bashrc`:
```bash
echo 'export GOTOOLCHAIN=auto' >> ~/.bashrc
```

Reload your shell:
```bash
source ~/.bashrc
```

### 3. Clone Grokker Repository

```bash
cd ~/lab
git clone https://github.com/stevegt/grokker.git
cd grokker
```

### 4. Initialize Grokker

Storm depends on grokker's LLM core. Initialize it:

```bash
cd ~/lab/grokker
grok init
```

**Set the default LLM model:**
```bash
grok model gpt-4o
```

### 5. Build and Install Storm

```bash
cd ~/lab/grokker/x/storm
make install
```

This will:
- Download dependencies
- Compile Storm
- Install the `storm` binary to your GOPATH bin directory

**Verify installation:**
```bash
which storm
# Should show: /home/youruser/.goenv/shims/storm

storm version
# Should show: storm dev-XXXXXX
```

### 6. Start Storm Server

```bash
storm serve
```

You should see:
```
storm dev-XXXXXX
migrating from X.X.XX to X.X.XX
Server starting on :8080
```

**Open your browser:**
- Main UI: http://localhost:8080
- API docs: http://localhost:8080/docs

### 7. Create Your First Project

Open a **new terminal** (keep Storm running in the first), then:

```bash
storm project add my-project ~/path/to/your/code ~/path/to/chat.md
```

Example:
```bash
storm project add test-project ~/lab/grokker ~/lab/grokker/test-chat.md
```

**Refresh your browser** - you should see your project listed!

### 8. Add Files to Project (Optional)

```bash
storm file add --project my-project /path/to/file1.go /path/to/file2.py
```

## Troubleshooting

### Issue: "go: go.mod requires go >= 1.24"

**Cause:** Your Go version is too old or GOTOOLCHAIN is set to 'local'

**Fix:**
```bash
export GOTOOLCHAIN=auto
eval "$(goenv init -)"
echo $GOPATH  # Verify correct version
go version    # Should show 1.24.0+
```

### Issue: "failed to load LLM core: open : no such file or directory"

**Cause:** Grokker not initialized

**Fix:**
```bash
cd ~/lab/grokker
grok init
grok model gpt-4o
```

### Issue: "model not found"

**Cause:** Default model not set in grokker

**Fix:**
```bash
grok model gpt-4o
```

### Issue: GOPATH points to wrong version

**Cause:** goenv not refreshed after setting local version

**Fix:**
```bash
eval "$(goenv init -)"
echo $GOPATH  # Should show correct version now
```

### Issue: "storm: command not found"

**Cause:** GOPATH bin not in PATH or goenv shims not set up

**Fix:**
```bash
# Check if goenv shims are in PATH
echo $PATH | grep goenv

# If not, ensure goenv is initialized in .bashrc
echo 'eval "$(goenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Reinstall storm
cd ~/lab/grokker/x/storm
make install
```

### Issue: Can't connect to OpenAI API

**Cause:** API key not set or invalid

**Fix:**
```bash
# Check if set
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY=your-actual-key
echo 'export OPENAI_API_KEY=your-actual-key' >> ~/.bashrc
```

### Issue: "Uncommitted changes found" during make

**Cause:** You have uncommitted changes in git (this is just a warning)

**Not an error!** This is informational. The build will continue. If you want to silence it, commit your changes:
```bash
git add .
git commit -m "Local modifications"
```

## Architecture Notes

### Directory Structure
```
~/lab/grokker/
├── v3/                    # Grokker v3 core
│   ├── core/             # LLM core library
│   ├── client/           # API client
│   └── cmd/grok/         # Grok CLI tool
└── x/
    └── storm/            # Storm application
        ├── main.go       # Main server
        ├── api.go        # REST API
        ├── cli.go        # CLI commands
        ├── project.go    # Project management
        └── db/           # Database layer
```

### Key Components

1. **Grokker Core** (`~/lab/grokker/v3/core/`)
   - Handles LLM communication
   - Stores model configuration in `~/.grok`
   - Manages chat history and context

2. **Storm Server** (`~/lab/grokker/x/storm/`)
   - Multi-project management
   - WebSocket-based real-time chat
   - File authorization and tracking
   - SQLite database in `~/.storm/data.db`

3. **Database Files**
   - Grokker config: `~/.grok`
   - Storm data: `~/.storm/data.db`

### How Storm Uses Grokker

1. Storm imports grokker's `core` package
2. On startup, Storm calls `core.Load("", true)` to:
   - Find the `~/.grok` file (walks up directories)
   - Load the default LLM model
   - Get read-only access
3. Storm uses grokker's API to:
   - Send queries to LLM
   - Extract code from responses
   - Count tokens
   - Manage embeddings

## Common Workflows

### Daily Development

**Terminal 1 (Storm server):**
```bash
cd ~/lab/grokker/x/storm
storm serve
```

**Terminal 2 (Commands):**
```bash
# Add files to project
storm file add --project my-project src/main.go

# View project info
storm project info my-project

# Use the web UI for chat
# Open http://localhost:8080
```

### Updating Storm

```bash
cd ~/lab/grokker/x/storm
git pull
make install
```

### Changing Default LLM

```bash
# See available models
grok models

# Switch model
grok model gpt-4-turbo
```

## Configuration Files

### Storm Config
Location: Built into binary, no config file needed

Default settings:
- Port: 8080
- Database: `~/.storm/data.db`

Override with flags:
```bash
storm serve --port 3000 --db-path /custom/path/db
```

### Grokker Config
Location: `~/.grok`

This is a JSON file managed by grokker. Don't edit manually.

To change settings, use `grok` commands:
```bash
grok model gpt-4o        # Change model
grok init                # Reinitialize
```

## Security Notes

- Your OpenAI API key is stored in environment variables
- All data sent to Storm goes through OpenAI's API
- Review OpenAI's data usage policies for sensitive content
- Storm's database (`~/.storm/data.db`) is stored locally with 0600 permissions
- WebSocket connections are local-only by default (localhost:8080)

## Performance Tips

- **Token limits:** Adjust in web UI per query (default 8192)
- **File selection:** Only add files you need as context
- **Cache hits:** Storm caches recent queries in discussion history
- **Database size:** The `~/.grok` file grows with embeddings; periodically `grok init` to reset

## Next Steps

1. **Learn the web UI:**
   - Create projects
   - Select input/output files
   - Send queries to LLM
   - Manage unexpected files

2. **Explore CLI commands:**
   ```bash
   storm --help
   storm project --help
   storm file --help
   ```

3. **Read the full docs:**
   - Storm README: `~/lab/grokker/x/storm/README.md`
   - Grokker README: `~/lab/grokker/README.md`

4. **Try advanced features:**
   - Multi-round conversations
   - Code extraction to files
   - AGENTS.md project instructions
   - Vector database queries

## Support

- **Storm Issues:** https://github.com/stevegt/grokker/issues
- **Grokker Docs:** ~/lab/grokker/README.md
- **Storm Docs:** ~/lab/grokker/x/storm/README.md

## License

See LICENSE file in grokker repository.

---

**Installation completed!** Storm should now be running at http://localhost:8080
