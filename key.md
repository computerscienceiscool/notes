# Key Choices for PromiseGrid

## Short recommendation

For native PromiseGrid use:

- **Ed25519** for signatures.
- **X25519** for encryption/key agreement when confidentiality is needed.
- **Separate keys** for signing and encryption.
- **GPG/OpenPGP** only when PromiseGrid must interoperate with people or systems
  that already use OpenPGP.

The key rule is: do not share a person's private key with an agent or an LLM.

## What each option is for

| Option | Good for | Why it is not sufficient alone |
|---|---|---|
| Ed25519 | Signing Grid messages and approvals | It does not encrypt secrets. |
| X25519 | Encrypting a secret or data key for a recipient | It does not sign messages or prove who sent them. |
| Ed25519 + X25519 | Native PromiseGrid signing plus confidentiality | This is the recommended combination. Each key has one clear job. |
| GPG | Human-operated OpenPGP signing and encryption | It adds the larger OpenPGP keyring, packet, identity, and compatibility system. |
| GopenPGP | A Go library for processing OpenPGP messages | It is still OpenPGP, so it is best for compatibility rather than normal Grid messages. |
| `cv25519` | GnuPG/OpenPGP name for Curve25519 encryption | It is an OpenPGP-specific name, not a third general PromiseGrid key type. Native Go code should use X25519. |

## Why native PromiseGrid should not use GPG/OpenPGP for every message

GPG and GopenPGP work. The issue is not that they are broken; they solve a
different problem.

PromiseGrid already has its own machine-readable message format: CBOR Grid
envelopes, CIDs, pCIDs, and local capability checks. Using OpenPGP around every
Grid message would add a second message format and a second key-management
system.

OpenPGP is useful for exchanging signed or encrypted files with existing GPG
users. It can use Ed25519 for signatures and `cv25519`/X25519 for encryption.
That does not make OpenPGP the best native format for a Grid agent's ordinary
messages.

The simple defensible position is:

> PromiseGrid uses Ed25519 for native signatures and X25519 when it needs
> confidentiality. It keeps signing and encryption keys separate. GPG/OpenPGP
> remains an interoperability bridge for people and existing systems, rather
> than the native PromiseGrid message, identity, or permission system.

## Important distinctions

- **GPG** is a program people use to create and manage OpenPGP keys.
- **GopenPGP** is a Go library that reads and writes OpenPGP data.
- **Ed25519** is a signing algorithm.
- **X25519** is an encryption/key-agreement algorithm.
- **`cv25519`** is GnuPG/OpenPGP terminology for the Curve25519 encryption
  side of an OpenPGP key setup.

An OpenPGP key may contain both an Ed25519 signing key and a `cv25519`
encryption key. Therefore, “GPG versus Ed25519” is not a direct choice between
two equivalent things: GPG is a tool and format that can use Ed25519.

## Agents, people, and keys

A person and an agent should have separate keys.

- A **person** makes important approvals and sets policy.
- An **agent** is software that works on the Grid and makes its own promises.
- An **LLM** is usually a tool the agent uses to reason, summarize, or draft. It
  is not automatically a person or an authorized Grid agent.

For example, Olivia is the human operations owner. She approves a policy that
lets Sam, a synchronization agent, read invoices and prepare drafts. Sam uses
an LLM to help classify an invoice. The LLM can make a recommendation, but it
cannot approve a payment or use Olivia's private key. If Sam needs to change an
external system, the system checks whether Olivia's policy gave Sam that exact
permission.

There are always two different questions:

1. **Did the agent do this?** The agent's Ed25519 signature answers this.
2. **Was the agent allowed to do this for the person or organization?** A
   separate approval or permission record answers this.

The permission should say who approved it, which agent receives it, what it may
do, when it expires, and whether human approval is required for each action.

For high-risk actions—sending money, changing accounting records, unlocking
secrets, or controlling equipment—a human should normally approve the action
near the time it occurs. If the result is uncertain, the agent must check what
happened before trying again.

## Recommended key layout

| Owner | Key | Purpose |
|---|---|---|
| Person | Separate approval/signing key | Approves policies, delegations, and high-risk actions. |
| Grid agent | Separate Ed25519 signing key | Signs the agent's own Grid promises and records. |
| Grid agent or secret service | Separate X25519 encryption key | Receives encrypted data keys or confidential material. |
| Existing GPG user or system | Optional OpenPGP key | Interoperability with OpenPGP files and signatures. |

An agent's key does not give it unlimited authority. It proves which agent made
a statement. The person or organization still decides what the agent is allowed
to do.

## Decision table: what to use and what not to use

The ratings below are for **native PromiseGrid messages and agent operations**.
They are not ratings of whether the underlying technology is good in its own
proper setting.

| Option | Native PromiseGrid rating | Decision | Reason |
|---|---:|---|---|
| Separate Ed25519 signing key per person and agent | 5/5 | Use | It directly proves who signed a Grid promise. cdint-grid already uses it in experiments. |
| Separate X25519 encryption key where confidentiality is required | 5/5 | Use | It is the right separate tool for encrypting a data key to a recipient. |
| Ed25519 plus X25519, with different keys | 5/5 | Use | Provides both signatures and confidentiality without mixing purposes. |
| GPG/OpenPGP for a human-facing file, release, or existing PGP user | 5/5 for interoperability | Use when needed | It is well suited to working with existing OpenPGP users and tools. |
| GPG/OpenPGP around every ordinary Grid message | 2/5 | Do not make it the default | It works technically but duplicates Grid's CBOR message format, identity work, and permission model. |
| GopenPGP for required OpenPGP interoperability in Go | 4/5 for interoperability | Conditional use | It is a maintained OpenPGP library, but still adds OpenPGP machinery not needed by native Grid messages. |
| `golang.org/x/crypto/openpgp` | 0/5 | Do not use | Its maintainers say it is unsafe by design, has known security issues, and is unmaintained. |
| Ed25519 alone when the requirement includes secrecy | 2/5 | Not enough alone | It signs but cannot encrypt. |
| X25519 alone when the requirement includes proof of sender | 1/5 | Not enough alone | It supports key agreement/encryption but cannot sign. |
| Reusing or converting one Ed25519 key for X25519 encryption | 1/5 | Do not use | It mixes two security purposes and makes key rotation, compromise response, and audit harder. Generate separate keys. |
| `cv25519` as a separate native Grid key type | 1/5 | Do not use | It is GnuPG/OpenPGP terminology for Curve25519 encryption, not an additional native Grid capability. Use X25519 in Go. |
| Giving an agent or LLM a person's private key | 0/5 | Never use | It destroys the ability to distinguish a human approval from an agent action. |
| Treating a valid key or signature as permission | 0/5 | Never use | A key proves control of a key. Permission must come from a separate, scoped approval or capability. |

## What does not work

Some choices do not work at all for their intended job:

- X25519 cannot make a digital signature, so it cannot prove an agent sent a
  promise.
- Ed25519 cannot encrypt a secret for a recipient, so it cannot provide
  confidentiality by itself.
- A signature alone cannot show that an agent was allowed to spend money,
  access a secret, or change an external system.
- An LLM using a person's private key cannot be distinguished from that person;
  that is unacceptable for approvals and audit.

Other choices work but are a poor default:

- GPG/OpenPGP works well for PGP interoperability, but is unnecessarily large
  and overlapping for ordinary native Grid traffic.
- `cv25519` works inside OpenPGP contexts, but native Go software should use the
  modern X25519 interface directly.
- A single reused key might be convenient, but creates a larger failure: one
  compromise then affects both signatures and encryption.

## Current cdint-grid status

cdint-grid currently uses real Ed25519 signatures in its experiments. It also
requires signing keys to remain separate from repository data-encryption keys.

The final production design remains open for:

- durable AgentID method;
- key rotation, recovery, and revocation rules;
- final capability-token encoding; and
- long-term identity and credential storage.

Those open questions do not change the basic recommendation: separate people
from agents, separate signing from encryption, and use explicit permission for
access to real-world resources.
