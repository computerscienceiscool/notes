# Collab-Editor Promise Implementation Guide

## Implementing Promise Theory Economics in the Collaborative Text Editor

*Document prepared: November 30, 2025*
 

---

## Overview

This document outlines how to implement Promise Theory-based economics in the collab-editor application. The collab-editor will eventually run on PromiseGrid, but can prototype these concepts now using mocked/placeholder PromiseGrid messages.

The goal is to create a working demonstration of:
- Promises as trackable events
- Tokens generated from kept promises
- Reputation-based voluntary enforcement

---

## Core Concept: The Promise Lifecycle

Every user action in the collab-editor can be modeled as a promise:

```
┌─────────────────┐
│  User Action    │  (edit, format, commit, review)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Promise Made   │  Logged with timestamp, user, action type
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Evaluation     │  Did the promise get kept?
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ Kept  │ │Broken │
└───┬───┘ └───┬───┘
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│ Token │ │  No   │
│Created│ │ Token │
└───────┘ └───────┘
```

---

## What Counts as a Promise in Collab-Editor

### Content Promises

| Action | Promise Implicit | Kept When |
|--------|------------------|-----------|
| Insert text | "I'm adding value to this document" | Content persists without revert |
| Delete text | "This removal improves the document" | Deletion persists without undo |
| Format text | "This formatting enhances readability" | Formatting persists |

### Review Promises

| Action | Promise Implicit | Kept When |
|--------|------------------|-----------|
| Accept edit | "I vouch for this change" | Accepted edit persists |
| Request review | "I will respond to feedback" | Response provided |
| Complete review | "I reviewed this thoroughly" | Review submitted |

### Structural Promises

| Action | Promise Implicit | Kept When |
|--------|------------------|-----------|
| Restructure document | "This reorganization helps" | Structure persists |
| Create section | "This section is needed" | Section remains |
| Merge content | "This consolidation makes sense" | Merge persists |

### Commitment Promises

| Action | Promise Implicit | Kept When |
|--------|------------------|-----------|
| Commit/save | "This version is stable" | No immediate issues |
| Export | "This output is ready" | Export completes |
| Share | "Others should see this" | Recipients can access |

---

## "Kept" Criteria: Implementation Options

Since we're uncertain about exact criteria, implement configurable options:

### Option A: Time-Based Persistence

```javascript
const KEPT_THRESHOLD_MS = 10 * 60 * 1000; // 10 minutes

function evaluatePromise(promise) {
  const elapsed = Date.now() - promise.timestamp;
  if (elapsed > KEPT_THRESHOLD_MS && !promise.reverted) {
    return 'kept';
  } else if (promise.reverted) {
    return 'broken';
  } else {
    return 'pending';
  }
}
```

### Option B: Peer Acceptance

```javascript
function evaluatePromise(promise) {
  const acceptances = promise.peerReactions.filter(r => r.type === 'accept');
  const rejections = promise.peerReactions.filter(r => r.type === 'reject');
  
  if (acceptances.length > rejections.length) {
    return 'kept';
  } else if (rejections.length > 0) {
    return 'broken';
  } else {
    return 'pending';
  }
}
```

### Option C: Hybrid (Recommended for Prototype)

```javascript
function evaluatePromise(promise) {
  const elapsed = Date.now() - promise.timestamp;
  const hasExplicitAccept = promise.peerReactions.some(r => r.type === 'accept');
  const hasExplicitReject = promise.peerReactions.some(r => r.type === 'reject');
  
  if (hasExplicitReject || promise.reverted) {
    return 'broken';
  } else if (hasExplicitAccept) {
    return 'kept';
  } else if (elapsed > KEPT_THRESHOLD_MS) {
    return 'kept'; // Implicit acceptance via persistence
  } else {
    return 'pending';
  }
}
```

---

## Token Generation

When a promise is evaluated as "kept", generate a token:

### Token Structure

```javascript
const token = {
  id: generateUniqueId(),           // Unique token identifier
  type: 'kept_promise',             // Token type
  promiseId: promise.id,            // Reference to original promise
  promiseType: promise.actionType,  // What kind of promise (edit, review, etc.)
  agentId: promise.userId,          // Who earned this token
  timestamp: Date.now(),            // When token was generated
  roomId: currentRoom,              // Context where earned
  
  // Optional metadata
  contentHash: hashContent(promise.content),  // What was promised
  witnesses: getActiveUsers(),                 // Who was present
};
```

### Token Storage (Local Prototype)

For now, store tokens locally per session:

```javascript
// In-memory store (will be replaced by PromiseGrid later)
const tokenStore = {
  byAgent: {},      // agentId -> [tokens]
  byRoom: {},       // roomId -> [tokens]
  all: [],          // All tokens
};

function storeToken(token) {
  tokenStore.all.push(token);
  
  if (!tokenStore.byAgent[token.agentId]) {
    tokenStore.byAgent[token.agentId] = [];
  }
  tokenStore.byAgent[token.agentId].push(token);
  
  if (!tokenStore.byRoom[token.roomId]) {
    tokenStore.byRoom[token.roomId] = [];
  }
  tokenStore.byRoom[token.roomId].push(token);
}
```

### PromiseGrid CBOR Message (For Future Integration)

Generate a PromiseGrid message for each token:

```javascript
function createTokenMessage(token) {
  return {
    protocol_hash: "QmPromiseGridProtocolV1",
    tag: 0x67726964, // 'grid'
    payload: {
      message_type: "token_generated",
      token: {
        id: token.id,
        agent_id: token.agentId,
        promise_type: token.promiseType,
        promise_id: token.promiseId,
        timestamp: token.timestamp,
        room_id: token.roomId,
        content_hash: token.contentHash,
      },
      // Signature would go here in real implementation
    }
  };
}
```

---

## Reputation Calculation

An agent's reputation = their accumulated kept-promise tokens.

### Simple Count

```javascript
function getReputation(agentId) {
  const tokens = tokenStore.byAgent[agentId] || [];
  return tokens.length;
}
```

### Weighted by Promise Type

```javascript
const PROMISE_WEIGHTS = {
  'content_addition': 1.0,
  'content_deletion': 0.5,
  'formatting': 0.2,
  'review_completed': 1.5,
  'structural_change': 2.0,
  'commit': 0.5,
};

function getWeightedReputation(agentId) {
  const tokens = tokenStore.byAgent[agentId] || [];
  return tokens.reduce((sum, token) => {
    const weight = PROMISE_WEIGHTS[token.promiseType] || 1.0;
    return sum + weight;
  }, 0);
}
```

### With Decay (Optional)

```javascript
const DECAY_HALF_LIFE_MS = 30 * 24 * 60 * 60 * 1000; // 30 days

function getDecayedReputation(agentId) {
  const tokens = tokenStore.byAgent[agentId] || [];
  const now = Date.now();
  
  return tokens.reduce((sum, token) => {
    const age = now - token.timestamp;
    const decayFactor = Math.pow(0.5, age / DECAY_HALF_LIFE_MS);
    const weight = PROMISE_WEIGHTS[token.promiseType] || 1.0;
    return sum + (weight * decayFactor);
  }, 0);
}
```

---

## Voluntary Enforcement

Enforcement is NOT automatic blocking. It's information that helps users make choices.

### Display Reputation in UI

```javascript
// In user list display
function renderUserBadge(user) {
  const reputation = getReputation(user.id);
  const trustLevel = getTrustLevel(reputation);
  
  return `
    <div class="user-badge" style="border-color: ${user.color}">
      <span class="user-name">${user.name}</span>
      <span class="user-reputation" title="${reputation} kept promises">
        ${trustLevel.icon} ${reputation}
      </span>
    </div>
  `;
}

function getTrustLevel(reputation) {
  if (reputation >= 50) return { icon: '⭐', label: 'Trusted' };
  if (reputation >= 20) return { icon: '✓', label: 'Established' };
  if (reputation >= 5)  return { icon: '○', label: 'New' };
  return { icon: '?', label: 'Unknown' };
}
```

### Personal Threshold Settings

Let each user set their own thresholds:

```javascript
// User preferences (stored in localStorage)
const userPreferences = {
  // Minimum reputation to auto-accept edits
  autoAcceptThreshold: 20,
  
  // Minimum reputation to skip review prompt
  skipReviewThreshold: 50,
  
  // Show warning for users below this
  warningThreshold: 5,
};

function shouldPromptForReview(incomingUser) {
  const reputation = getReputation(incomingUser.id);
  return reputation < userPreferences.skipReviewThreshold;
}

function shouldShowWarning(incomingUser) {
  const reputation = getReputation(incomingUser.id);
  return reputation < userPreferences.warningThreshold;
}
```

### Enforcement UI Examples

**Low-reputation user makes an edit:**

```
┌──────────────────────────────────────────┐
│  ⚠️ Edit from New User                   │
├──────────────────────────────────────────┤
│                                          │
│  Carol (reputation: 2) made an edit.     │
│                                          │
│  Your threshold for auto-accept: 20      │
│                                          │
│  [ View Edit ]  [ Accept ]  [ Reject ]   │
│                                          │
└──────────────────────────────────────────┘
```

**Threshold settings panel:**

```
┌──────────────────────────────────────────┐
│  🛡️ Trust Settings                       │
├──────────────────────────────────────────┤
│                                          │
│  Auto-accept edits from users with       │
│  reputation ≥ [  20  ] ▼                 │
│                                          │
│  Show warning for users with             │
│  reputation < [   5  ] ▼                 │
│                                          │
│  [ Save ]  [ Reset to Defaults ]         │
│                                          │
└──────────────────────────────────────────┘
```

---

## Promise Log Integration

Extend the existing Promise Log Panel to show token generation:

```
📜 Promise Log
─────────────────────────────────────────────
[14:32:01] Alice promises: insert "Introduction" at position 0
[14:42:01] ✓ Alice's promise KEPT → Token #47 generated
[14:33:15] Bob promises: bold formatting on "Introduction"
[14:43:15] ✓ Bob's promise KEPT → Token #12 generated
[14:35:22] Carol promises: restructure section 2
[14:36:45] ✗ Carol's promise BROKEN (reverted by Bob)
[14:38:00] Bob promises: review Alice's paragraph
[14:39:30] ✓ Bob's promise KEPT (review completed) → Token #13 generated
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Actions                              │
│  (typing, formatting, reviewing, committing)                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Promise Logger                               │
│  - Captures action as promise                                    │
│  - Assigns promise ID and timestamp                              │
│  - Logs to Promise Log Panel                                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Promise Evaluator                              │
│  - Monitors pending promises                                     │
│  - Checks kept criteria (time, acceptance, persistence)          │
│  - Marks as kept/broken/pending                                  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    Token Generator      │     │    No Token             │
│  - Creates token        │     │  (promise broken)       │
│  - Stores in tokenStore │     │                         │
│  - Generates CBOR msg   │     │                         │
└───────────┬─────────────┘     └─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Reputation Calculator                           │
│  - Aggregates tokens per agent                                   │
│  - Applies weights and decay                                     │
│  - Provides reputation scores                                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     UI Components                                │
│  - User badges with reputation                                   │
│  - Trust threshold warnings                                      │
│  - Personal preference controls                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Files to Create/Modify

### New Files

| File | Purpose |
|------|---------|
| `src/promises/promiseLogger.js` | Capture user actions as promises |
| `src/promises/promiseEvaluator.js` | Evaluate kept/broken status |
| `src/promises/tokenGenerator.js` | Generate tokens for kept promises |
| `src/promises/tokenStore.js` | Store and query tokens |
| `src/promises/reputationCalculator.js` | Calculate reputation scores |
| `src/ui/reputationBadge.js` | Display reputation in user list |
| `src/ui/trustSettings.js` | Personal threshold preferences |

### Modified Files

| File | Changes |
|------|---------|
| `src/ui/promiseLog.js` | Add token generation events |
| `src/ui/userList.js` | Add reputation badges |
| `src/setup/yjsSetup.js` | Hook into Yjs for action tracking |
| `src/export/handlers.js` | Generate CBOR messages for tokens |
| `index.html` | Add trust settings panel |
| `style.css` | Styles for reputation UI |

---

## Implementation Phases

### Phase 1: Promise Tracking (Visibility Only)

- [ ] Implement `promiseLogger.js` to capture all actions
- [ ] Display promises in Promise Log Panel
- [ ] No evaluation yet — just logging

### Phase 2: Token Generation

- [ ] Implement `promiseEvaluator.js` with time-based "kept" criteria
- [ ] Implement `tokenGenerator.js` to create tokens
- [ ] Implement `tokenStore.js` for local storage
- [ ] Show token events in Promise Log

### Phase 3: Reputation Display

- [ ] Implement `reputationCalculator.js`
- [ ] Add reputation badges to user list
- [ ] Show reputation in tooltips

### Phase 4: Voluntary Enforcement

- [ ] Implement `trustSettings.js` for personal thresholds
- [ ] Add warning prompts for low-reputation users
- [ ] Add auto-accept for high-reputation users

### Phase 5: PromiseGrid Integration (Future)

- [ ] Replace local tokenStore with PromiseGrid storage
- [ ] Generate real CBOR messages (not mocked)
- [ ] Sync reputation across grid nodes

---

## Configuration Options

Make these configurable for experimentation:

```javascript
// config/promiseConfig.js

export const PROMISE_CONFIG = {
  // Time before a promise is evaluated as "kept" (if not reverted)
  keptThresholdMs: 10 * 60 * 1000, // 10 minutes
  
  // Weights for different promise types
  promiseWeights: {
    content_addition: 1.0,
    content_deletion: 0.5,
    formatting: 0.2,
    review_completed: 1.5,
    structural_change: 2.0,
    commit: 0.5,
  },
  
  // Decay settings (null = no decay)
  decayHalfLifeMs: null, // Set to enable decay
  
  // Default user thresholds
  defaultThresholds: {
    autoAccept: 20,
    skipReview: 50,
    warning: 5,
  },
  
  // Enable/disable features
  features: {
    tokenGeneration: true,
    reputationDisplay: true,
    voluntaryEnforcement: true,
    decayEnabled: false,
  },
};
```

---

## Questions to Resolve Before Implementation

1. **Exact "kept" criteria** — Time-based? Peer acceptance? Hybrid?
2. **Token persistence** — Session only? LocalStorage? Backend?
3. **Cross-room reputation** — Does reputation carry across documents?
4. **Broken promise handling** — Just no token? Or active penalty?
5. **Initial reputation** — Do new users start at 0? Or bootstrap amount?

---

## Success Metrics

How do we know this is working?

- Users understand their reputation (can explain why it's X)
- Users adjust behavior based on reputation visibility
- Low-reputation edits get more scrutiny (measured in review rates)
- High-reputation users experience less friction
- No complaints about unfair enforcement (it's voluntary!)

---

*This document will be updated as design decisions are made with the PromiseGrid team.*
