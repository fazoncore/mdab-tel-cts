# MDAB v0.1 — Requirements (Telemetry CTS)

This document is **normative** for the Telemetry CTS bundle.

## Legend
- **Priority**: P0 (mandatory), P1 (strongly recommended), P2 (optional)
- **Profiles**: CORE, AUDIT, HIGHASSURANCE (HA)

---

## Canonical JSON and parsing

**RQ-01 (P0, CORE/AUDIT/HA)** — Canonicalization  
Implementations MUST implement `canon(x)` as a deterministic, JCS-like canonical JSON serialization:
- UTF-8
- lexicographic object key sort
- separators `,` and `:`
- no whitespace outside JSON strings
- arrays preserve order
- NaN/Infinity forbidden

**RQ-02 (P0, CORE/AUDIT/HA)** — Duplicate keys forbidden  
Parsers used for conformance MUST reject duplicate keys (fail-closed).

**RQ-03 (P0, CORE/AUDIT/HA)** — Numeric policy  
Conformance artifacts MUST NOT contain floats or exponent-form numbers. Only integers are permitted.

---

## Hash naming and computation

**RQ-10 (P0, CORE/AUDIT/HA)** — `decision_hash` computation  
`decision_hash` MUST equal `sha256:<hex>` where `<hex>` is `SHA-256(canon(decision_core))`.

**RQ-11 (P1, CORE/AUDIT/HA)** — `decision_digest` alias (ingestion only)  
Verification tools MAY accept `decision_digest` as an alias for `decision_hash`.  
If both exist, they MUST be identical; otherwise INVALID.

**RQ-20 (P0, AUDIT/HA)** — `event_hash` computation  
`event_hash` MUST equal `sha256:<hex>` where `<hex>` is `SHA-256(canon(event_core))` and  
`event_core` is the event with fields `event_hash` and `signature` removed.

**RQ-21 (P0, AUDIT/HA)** — Chain integrity  
For each emitter stream:
- `seq` MUST start at 0 and increment by 1 (no gaps)
- `prev_event_hash` MUST equal the prior event's `event_hash` (genesis uses null)

**RQ-22 (P1, AUDIT/HA)** — Checkpoint correctness  
For each checkpoint:
- `block_hash` MUST equal `SHA-256("MDAB-BLOCK-0.1\n" + join(event_hashes,"\n") + "\n")`
  over the DECISION `event_hash` values in `[range_start_seq..range_end_seq]` (inclusive).
- `last_event_hash` MUST match the DECISION event_hash at `range_end_seq`.

---

## Signatures and keys (HighAssurance)

**RQ-30 (P0, HA)** — Signature verification  
If HA profile is claimed, DecisionEvent and CheckpointEvent MUST include `signature`, and verifiers
MUST validate ed25519 signatures over the **raw 32-byte** digest represented by `event_hash`.

**RQ-31 (P0, HA)** — Key bundle validation  
Verifiers MUST:
- resolve `signature.key_id` in `keys/verifier_keys.json`
- reject unknown, revoked, or time-invalid keys
- reject signatures that do not verify (fail-closed)
