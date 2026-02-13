# mob-consensus: Beginner's Guide

## What is mob-consensus?

`mob-consensus` is a tool for collaborative coding where multiple people work on parallel branches and merge their work together frequently. Think of it like Google Docs for code - everyone has their own version, and you regularly sync up by merging each other's changes.

---

## The Basic Concept

### Branch Naming Convention

Everyone works on branches named: `<your-name>/<feature-name>`

For example, if three people are working on a "login" feature:
- Alice works on: `alice/login`
- Bob works on: `bob/login`
- Carol works on: `carol/login`

The part before the `/` is your username (from your git email).
The part after the `/` is the "twig" - the shared feature name.

---

## Step-by-Step Walkthrough: 3 Users Working Together

Let's walk through a realistic scenario with Alice, Bob, and Carol all working on a "dashboard" feature.

---

### Step 0: Prerequisites (Everyone)

Everyone needs:
1. Git configured with their email:
   ```bash
   git config user.email "alice@example.com"
   ```
2. `mob-consensus` installed:
   ```bash
   go install github.com/stevegt/mob-consensus@latest
   ```
3. Access to a shared remote repository (like GitHub)

---

### Step 1: Alice Starts the Feature (First Person)

**Alice's situation:** She's starting a new feature called "dashboard" from the `main` branch.

**What Alice does:**

```bash
# Make sure you're on main and it's up to date
git checkout main
git pull

# Create the shared twig branch locally
git switch -c dashboard

# Create your personal branch from the twig
mob-consensus -b dashboard
```

**What happens:**
- `mob-consensus` reads Alice's email: `alice@example.com`
- Extracts username: `alice`
- Creates branch: `alice/dashboard`
- Switches to `alice/dashboard`

**Output Alice sees:**
```
Next: push your branch when you're ready.
  git push -u origin alice/dashboard
```

**Alice pushes her branch:**
```bash
git push -u origin alice/dashboard
```

**What Alice has now:**
- Local branch: `alice/dashboard` (where she's working)
- Remote branch: `origin/alice/dashboard` (backed up on GitHub)

---

### Step 2: Alice Does Some Work

**What Alice does:**
```bash
# Edit files
vim src/dashboard.go

# Regular git workflow
git add src/dashboard.go
git commit -m "Add dashboard skeleton"

# Push her changes
git push
```

**What Alice has now:**
- Her code is on `alice/dashboard` both locally and remotely

---

### Step 3: Bob Joins the Feature (Second Person)

**Bob's situation:** He heard Alice is working on "dashboard" and wants to join.

**What Bob does:**

```bash
# Fetch all remote branches
git fetch origin

# Get the shared twig branch
git switch -c dashboard origin/dashboard

# OR if dashboard doesn't exist on remote, start from main:
# git checkout main
# git switch -c dashboard

# Create his personal branch
mob-consensus -b dashboard
```

**What happens:**
- `mob-consensus` reads Bob's email: `bob@example.com`
- Extracts username: `bob`
- Creates branch: `bob/dashboard`
- Switches to `bob/dashboard`

**Bob pushes his branch:**
```bash
git push -u origin bob/dashboard
```

**What Bob has now:**
- Local branch: `bob/dashboard` (where he's working)
- Remote branch: `origin/bob/dashboard` (backed up on GitHub)

---

### Step 4: Bob Does Some Work

**What Bob does:**
```bash
# Edit files (different part of the codebase)
vim src/widgets.go

# Regular git workflow
git add src/widgets.go
git commit -m "Add widget components"
git push
```

---

### Step 5: Carol Joins (Third Person)

**Carol's situation:** She's joining the dashboard team.

**What Carol does:**
```bash
# Fetch latest
git fetch origin

# Get the twig branch
git switch -c dashboard origin/dashboard
# OR: git checkout main && git switch -c dashboard

# Create her personal branch
mob-consensus -b dashboard
```

**What happens:**
- Creates `carol/dashboard`
- Carol is now on her own branch

**Carol pushes:**
```bash
git push -u origin carol/dashboard
```

---

### Step 6: Alice Wants to See What Everyone Is Doing (Discovery)

**Alice's situation:** She wants to check if Bob and Carol are ahead of her.

**What Alice does:**
```bash
# Make sure you're on your branch
git checkout alice/dashboard

# Run discovery mode (no arguments)
mob-consensus
```

**What happens:**
- Fetches latest from remote
- Shows all branches ending in `/dashboard`

**Output Alice sees:**
```
Related branches and their diffs (if any):

                        bob/dashboard is ahead: 2 files changed, 45 insertions(+)
                      carol/dashboard is synced
```

**What this means:**
- Bob has changes Alice doesn't have (45 new lines)
- Carol is synced (same as Alice, or no changes yet)

---

### Step 7: Alice Merges Bob's Work (Consensus!)

**Alice's situation:** She wants Bob's widget code merged into her branch.

**What Alice does:**
```bash
mob-consensus bob/dashboard
```

**What happens (step by step):**

1. **Branch resolution:** mob-consensus checks if `bob/dashboard` exists locally. If not, it uses `origin/bob/dashboard`

2. **Merge starts:** Runs `git merge --no-commit --no-ff origin/bob/dashboard`

3. **Conflicts?**
   - **If NO conflicts:** Merge succeeds, staged changes ready
   - **If conflicts exist:** Opens `vimdiff` to resolve conflicts
     - Alice sees split screen: her version vs Bob's version
     - She manually resolves conflicts
     - Saves and exits vimdiff
     - mob-consensus stages the resolved files

4. **Review changes:** Opens `git difftool` so Alice can review ALL changes about to be committed
   - Alice reviews every change Bob made
   - Exits when satisfied

5. **Commit:** Opens editor with pre-filled merge message:
   ```
   mob-consensus merge from bob/dashboard onto alice/dashboard

   Co-authored-by: Bob Smith <bob@example.com>
   ```
   - Alice can edit the message
   - Saves and closes editor
   - Commit is created

6. **Push:** Automatically pushes to `origin/alice/dashboard`

**What Alice has now:**
- Her branch `alice/dashboard` contains both her work AND Bob's work
- Bob is credited as co-author in the merge commit

---

### Step 8: Bob Merges Alice's Work Back

**Bob's situation:** Alice just merged his code, so now she's ahead. He wants her latest work.

**What Bob does:**
```bash
git checkout bob/dashboard
mob-consensus alice/dashboard
```

**What happens:**
- Same process as Step 7
- Bob merges Alice's changes (which include his own previous work, plus Alice's new work)
- Creates merge commit with Alice as co-author
- Pushes to `bob/dashboard`

**What Bob has now:**
- His branch is now in sync with Alice's

---

### Step 9: Carol Does Her First Merge

**Carol's situation:** She's been working independently and wants to sync with Alice and Bob.

**What Carol does:**
```bash
git checkout carol/dashboard

# See who's ahead
mob-consensus

# Merge Alice's work
mob-consensus alice/dashboard

# Merge Bob's work
mob-consensus bob/dashboard
```

**What happens:**
- Carol gets all of Alice's work (including Bob's changes that Alice merged)
- Then Carol gets Bob's latest direct work
- Carol's branch now has everyone's contributions

---

### Step 10: The Cycle Continues

**Throughout the day:**

1. **Everyone works independently** on their own branches
   ```bash
   # Edit, commit, push on your own branch
   git add .
   git commit -m "My changes"
   git push
   ```

2. **Regularly check status**
   ```bash
   mob-consensus
   ```

3. **Merge others' work frequently**
   ```bash
   mob-consensus alice/dashboard
   mob-consensus bob/dashboard
   ```

4. **Keep working**
   - Your branch accumulates everyone's merged work
   - Everyone's branch evolves independently
   - Through frequent merges, you reach "consensus"

---

## Common Scenarios

### Scenario: I Have Uncommitted Changes

**What you see:**
```bash
mob-consensus bob/dashboard
# Output: you have uncommitted changes
# Error: working tree is dirty (use -c to commit)
```

**Solution 1: Commit them first**
```bash
git add .
git commit -m "Work in progress"
mob-consensus bob/dashboard
```

**Solution 2: Use -c flag to auto-commit**
```bash
mob-consensus -c bob/dashboard
# Will show diff, open editor for commit message, then proceed with merge
```

---

### Scenario: I Want to Skip the Auto-Push

**Use case:** You want to review commits locally before pushing.

**What you do:**
```bash
mob-consensus -n alice/dashboard
```

The `-n` flag means "no push". You'll need to manually `git push` later.

---

### Scenario: Branch Not Found

**What you see:**
```bash
mob-consensus dave/dashboard
# Error: branch "dave/dashboard" not found locally or as "origin/dave/dashboard"
```

**What this means:**
- Dave hasn't pushed his branch yet, or
- You mistyped the name, or
- Dave isn't working on "dashboard" (wrong twig name)

**Solution:**
```bash
# Check what branches exist
mob-consensus
# Shows all branches ending in /dashboard
```

---

### Scenario: Merge Conflicts

**What happens:**
```bash
mob-consensus bob/dashboard
# Git tries to merge
# Output: CONFLICT (content): Merge conflict in src/dashboard.go
# vimdiff opens automatically
```

**What you see in vimdiff:**
- Left side: Your version
- Right side: Bob's version
- You navigate and choose which changes to keep

**How to resolve:**
1. In vimdiff, navigate with arrow keys
2. Choose changes: `:diffget` or `:diffput`
3. Save and exit: `:wqa`
4. mob-consensus continues automatically

**If you panic:**
```bash
# Abort the merge
git merge --abort
# You're back to before the merge started
```

---

### Scenario: I Want to Start Fresh from Main

**Use case:** Feature is done, starting a new one.

**What you do:**
```bash
git checkout main
git pull
mob-consensus -b new-feature
# Creates alice/new-feature from main
git push -u origin alice/new-feature
```

---

## Quick Reference

### Commands

| Command | What it does |
|---------|--------------|
| `mob-consensus` | Show related branches and their status (discovery) |
| `mob-consensus alice/feature` | Merge alice/feature into your current branch |
| `mob-consensus -b main` | Create your personal branch from main |
| `mob-consensus -c alice/feature` | Auto-commit dirty changes before merging |
| `mob-consensus -n alice/feature` | Merge but don't auto-push |
| `mob-consensus -h` | Show help |

### Branch Names

- **Twig:** The shared feature name (e.g., `dashboard`)
- **Your branch:** `<you>/<twig>` (e.g., `alice/dashboard`)
- **Others' branches:** `<them>/<twig>` (e.g., `bob/dashboard`)

### Workflow

1. **Start:** `mob-consensus -b <base-branch>`
2. **Work:** Regular git add/commit/push
3. **Check:** `mob-consensus` (see who's ahead)
4. **Sync:** `mob-consensus <other-branch>`
5. **Repeat:** Steps 2-4 throughout the day

---

## Philosophy

**Why merge so often?**
- Catch conflicts early (easier to resolve)
- Share knowledge (see what everyone's doing)
- Build consensus gradually (not one big merge at the end)
- Co-authorship credit (everyone's contributions are tracked)

**Why personal branches?**
- Freedom to experiment without breaking others' work
- Each person controls when to integrate changes
- Clear ownership and attribution
- Parallel work without blocking

**The "consensus" part:**
- Through repeated merging, all branches converge
- No single "correct" version - everyone's branch is valid
- Consensus emerges from collaboration, not imposed

---

## Troubleshooting

### "fatal: not something we can merge"
- The branch doesn't exist
- Check spelling: `mob-consensus` (no args) lists available branches

### "you aren't on a 'alice/' branch"
- You're not on your personal branch
- Fix: `git checkout alice/dashboard` (or use `-F` to force)

### "working tree is dirty"
- You have uncommitted changes
- Fix: Commit them or use `-c` flag

### vimdiff is confusing
- Alternative: Configure your preferred merge tool in git config
- Or: Accept the merge as-is and fix conflicts manually after

### Push failed
- Your upstream might not be set (should auto-fix now with smartPush)
- Or: Someone force-pushed (rare)
- Try: `git push -u origin <your-branch>`

---

## Example Full Session (Alice's Perspective)

```bash
# === MORNING ===

# Start new feature
git checkout main
git pull
mob-consensus -b main  # Creates alice/dashboard from main
git push -u origin alice/dashboard

# Do some work
vim src/dashboard.go
git add src/dashboard.go
git commit -m "Add dashboard layout"
git push

# === LUNCHTIME ===

# Check what others are doing
mob-consensus
# Output:
#   bob/dashboard is ahead: 3 files changed
#   carol/dashboard is synced

# Merge Bob's work
mob-consensus bob/dashboard
# Reviews changes in difftool
# Edits commit message
# Auto-pushed

# === AFTERNOON ===

# More work
vim src/dashboard.go
git commit -am "Add widgets to dashboard"
git push

# Check again
mob-consensus
# Output:
#   bob/dashboard is ahead: 1 file changed
#   carol/dashboard is behind: 5 files changed

# Carol is behind me, she needs to merge my stuff
# Let's get Bob's latest
mob-consensus bob/dashboard

# === END OF DAY ===

# Final sync with everyone
mob-consensus
mob-consensus carol/dashboard  # Get Carol's work if she pushed any
git push

# All done! Branch has everyone's contributions.
```

---

## Tips for Success

1. **Merge often** - At least 2-3 times per day
2. **Push regularly** - After every significant commit
3. **Communicate** - Tell teammates when you push something big
4. **Small commits** - Easier to review in difftool
5. **Run discovery** - `mob-consensus` with no args to check status
6. **Trust the process** - The tool handles the git complexity

---

## What You've Learned

- ✅ How to create your personal branch
- ✅ How to discover what others are doing
- ✅ How to merge others' work into yours
- ✅ How merge conflicts are handled
- ✅ How co-authorship works
- ✅ The mob programming workflow

**You're ready to mob!** 🎉
