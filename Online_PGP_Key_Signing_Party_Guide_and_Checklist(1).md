# Online PGP Key Signing Party Guide and Checklist

## Purpose

This guide is for organizing a small online PGP key signing party, such as a five-person video meeting.

The goal is simple: each person confirms that a particular PGP public key belongs to them, and the other participants can then sign that key.

## PGP in Very Simple Terms

Think of a PGP key like a special digital ID.

Each person has two parts:

- **Public key** — safe to share with other people.
- **Private key** — must stay private and should never be shared.

A public key also has a long identifier called a **fingerprint**.

The fingerprint is what people compare during a key signing party.

## Before the Meeting

Participants can either:

- Create a new PGP key before the meeting.
- Create a new PGP key during the meeting.
- Bring an existing PGP key they already use.

People do **not** need to create a new key just for the party if they already have one they want verified.

A common tool for creating and managing PGP keys is **GnuPG (GPG)**.

## What Each Participant Should Have

Before verification, each participant should have:

- Their name.
- Their email address associated with the key, if applicable.
- Their public PGP key.
- Their full PGP key fingerprint.
- Access to the private key so they can use the key later.

Never share the private key.

## Suggested Online Meeting Flow

### 1. Welcome and Explain the Process

Tell everyone that the meeting is for confirming ownership of PGP public keys.

Explain that the important thing being compared is the key fingerprint.

### 2. Create Keys if Needed

Anyone who does not already have a PGP key can generate one during the meeting.

Anyone who already has a key can use their existing key.

### 3. Post Fingerprints in the Group Chat

Each person posts something like:

```text
JJ
jj@example.com
Fingerprint: ABCD 1234 EFGH 5678 IJKL 9012 MNOP 3456 QRST 7890
```

Use the **full fingerprint**, not only a short key ID.

### 4. Confirm the Fingerprint Out Loud

Each participant reads or verbally confirms their fingerprint.

For example:

> "I'm JJ, and the fingerprint I posted in the chat is my PGP key fingerprint."

The other participants compare what they hear with what appears in the group chat.

### 5. Mark the Person as Verified

Once the information matches, each participant can mark that person as verified on their checklist.

### 6. Sign the Public Keys

After verification, participants can sign the verified public keys.

Signing someone's public key means, in effect:

> "I checked this key and believe it belongs to this person."

The signing can be done during the meeting or afterward.

## Verification Options

For a small, informal group, the simplest method is:

1. Post the full fingerprint in the group chat.
2. Confirm it verbally on the video call.
3. Have everyone compare the two.

For stronger verification, participants can also use another trusted method, such as:

- Confirming through a previously known email address.
- Confirming through Signal or another messaging account already known to the group.
- Checking government-issued identification, if the group specifically wants identity verification.

The group should decide in advance how strict the verification should be.

## Organizer Checklist

### Before the Meeting

- [ ] Schedule the online meeting.
- [ ] Invite participants.
- [ ] Explain that this is a PGP key signing party.
- [ ] Tell participants they may bring an existing key.
- [ ] Tell beginners they can create a key during the meeting.
- [ ] Ask participants to install or have access to a PGP tool such as GPG.
- [ ] Remind everyone never to share their private key.

### During the Meeting

- [ ] Explain public keys, private keys, and fingerprints.
- [ ] Help beginners generate keys if needed.
- [ ] Have each person post their name and full fingerprint in group chat.
- [ ] Have each person verbally confirm their fingerprint.
- [ ] Have everyone compare the spoken fingerprint with the chat entry.
- [ ] Mark each verified participant on the checklist.
- [ ] Explain how participants will sign the verified keys.

### After the Meeting

- [ ] Sign only the keys you personally verified.
- [ ] Double-check the full fingerprint before signing.
- [ ] Keep your private key private.
- [ ] Export or distribute signed public keys if the group has agreed on a method.

## Five-Person Verification Sheet

| Participant | Email | Full Fingerprint | Posted in Chat | Confirmed Verbally | Verified | Signed |
|---|---|---|---|---|---|---|
| 1. | | | [ ] | [ ] | [ ] | [ ] |
| 2. | | | [ ] | [ ] | [ ] | [ ] |
| 3. | | | [ ] | [ ] | [ ] | [ ] |
| 4. | | | [ ] | [ ] | [ ] | [ ] |
| 5. | | | [ ] | [ ] | [ ] | [ ] |

## Simple Invitation Text

```text
We're holding a small online PGP key signing party.

You do not need prior PGP experience.

If you already have a PGP key, bring the public key and full fingerprint.
If you do not have one, we can create one during the meeting.

During the call, each person will post their public-key fingerprint in the group chat and confirm it verbally. The group will compare the information, and participants can then sign the keys they verified.

Important: Never share your private key.
```

## Important Safety Rules

- Never share your private key.
- Never paste your private key into meeting chat.
- Use the **full fingerprint** when verifying a key.
- Do not sign a key unless you are satisfied that you verified it.
- A key signature represents your own verification, not the group's verification.

## Quick Vocabulary

**PGP**  
A system for encryption and digital signatures.

**GPG / GnuPG**  
A common free tool used to work with PGP keys.

**Public key**  
The part of the key that can be shared.

**Private key**  
The secret part of the key. Never share it.

**Fingerprint**  
A long identifier used to verify that you have the correct public key.

**Key signing**  
Adding your digital signature to another person's public key after verifying it.

**Web of trust**  
A trust model in which people verify and sign one another's keys.

## The Entire Process in One Sentence

Create or bring a PGP key, share the full public-key fingerprint, confirm that fingerprint through the meeting, verify the other participants, and then sign only the keys you personally verified.

# OpenPGP Certificate Packet Structure - Visual Explanation

An OpenPGP public-key certificate is not one indivisible object. It is a **sequence of packets** stored one after another.

A common certificate looks like this:

```text
OPENPGP CERTIFICATE

[ Public-Key Packet ]                  Tag 6
        |
        |  This is the primary public key.
        |
        +--------------------------------------------------+
        |                                                  |
        v                                                  v
[ User ID Packet ]                   Tag 13       [ Public-Subkey Packet ]   Tag 14
"JJ <jj@example.com>"                              helper public key
        |                                                  |
        v                                                  v
[ Signature Packet ]                  Tag 2        [ Signature Packet ]       Tag 2
self-certification                                  subkey-binding signature
"The primary key approves                          "The primary key says this
 this User ID."                                     subkey belongs to it."
```

The most important pattern is:

```text
THING YOU WANT TO ATTACH
          +
SIGNATURE THAT BINDS IT TO THE PRIMARY KEY
```

For a User ID:

```text
Primary Key
    |
    +-- User ID
           |
           +-- Self-Certification Signature
```

For a subkey:

```text
Primary Key
    |
    +-- Public Subkey
           |
           +-- Subkey-Binding Signature
```

## What the Bytes Look Like Conceptually

On disk or over the network, the certificate is simply packet after packet:

```text
+----------------------+----------------------+----------------------+
| Public-Key Packet    | User ID Packet       | Signature Packet     |
+----------------------+----------------------+----------------------+
| Public-Subkey Packet | Signature Packet     | ...                  |
+----------------------+----------------------+----------------------+
```

Each packet has the same basic idea:

```text
+----------------+----------------+------------------------------+
| Packet header  | Length         | Packet body                  |
+----------------+----------------+------------------------------+
       |                                |
       |                                +-- the actual key, name,
       |                                    signature, etc.
       |
       +-- tells OpenPGP what kind of packet follows
```

## Four Packet Types to Learn First

| Packet | Tag | Plain-English meaning |
|---|---:|---|
| Public-Key Packet | 6 | "Here is my primary public key." |
| User ID Packet | 13 | "Here is the identity label I want associated with it." |
| Signature Packet | 2 | "Here is a cryptographic statement approving or certifying something." |
| Public-Subkey Packet | 14 | "Here is another public key attached to my primary key for a particular job." |

## One Important Detail About Signature Packets

A **Signature Packet** does not have only one meaning. The packet type is always "Signature Packet," but a field *inside* it says what kind of signature it is.

Examples include:

```text
Signature Packet
    |
    +-- certification signature
    |      "I certify this User ID."
    |
    +-- subkey-binding signature
    |      "I bind this subkey to my primary key."
    |
    +-- key-revocation signature
    |      "This key should no longer be used."
    |
    +-- certification-revocation signature
           "I withdraw an earlier certification."
```

So do not memorize "Signature Packet = self-signature."

Instead remember:

> **Signature Packet = a container for a cryptographic signature plus information describing what that signature means.**

## The Memory Hook

For the simplest useful mental model:

```text
KEY  ->  NAME  ->  STAMP
```

Which translates to:

```text
Public-Key Packet
        -> User ID Packet
                -> Signature Packet
```

The "stamp" is the self-certification signature made by the primary key.

Then later you can add:

```text
KEY  ->  HELPER KEY  ->  STAMP
```

Which translates to:

```text
Public-Key Packet
        -> Public-Subkey Packet
                -> Signature Packet
```

That second stamp is a **subkey-binding signature**.

## A More Complete Certificate Can Contain More Packets

A real certificate may also contain:

- several User ID packets;
- several certification signatures;
- signatures made by other people;
- several public subkeys;
- subkey-binding signatures;
- revocation signatures;
- direct-key signatures;
- User Attribute packets, such as an image attribute.

But the four packet types above are the right place to start.

## The One Sentence to Remember

**An OpenPGP certificate is a sequence of packets, and signatures are what cryptographically connect claims such as identities and subkeys to the primary key.**
