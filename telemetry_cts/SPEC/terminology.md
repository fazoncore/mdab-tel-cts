# MDAB v0.1 — Terminology and Naming

This document is **normative** for MDAB v0.1 packages and CTS artifacts.

## Normative keywords
The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL**
are to be interpreted as described in RFC 2119 and RFC 8174.

## Digest primitive and naming unification

MDAB v0.1 uses **SHA-256** as the sole digest primitive.

All normative documents and schemas MUST use the suffix **`_hash`** (not `_digest`)
for SHA-256 derived identifiers.

### Canonical names

- **`policy_hash`** = `SHA-256(canon(policy_json))`
- **`input_hash`** = `SHA-256(canon(input_json))`
- **`decision_hash`** = `SHA-256(canon(decision_core))`
- **`event_hash`** = `SHA-256(canon(event_core))`
- **`block_hash`** = `SHA-256("MDAB-BLOCK-0.1\n" + join(event_hashes, "\n") + "\n")`

All hashes in telemetry MUST be encoded as strings: `sha256:<lowercase-hex>`.

### Backward-compatibility alias (ingestion only)

Some implementations may emit **`decision_digest`**. For interoperability:

- Telemetry ingestion and verification tools MAY accept `decision_digest`
  as an alias for `decision_hash`.
- If both `decision_hash` and `decision_digest` are present, they MUST be identical;
  otherwise the record is INVALID.

Conformance claims MUST emit and reference only `decision_hash`.

## Core terms (MDAB)
- **Policy**: a canonical JSON document defining deterministic rule evaluation.
- **Input**: the canonical JSON object evaluated under a profile (CORE/TIMEAWARE).
- **decision_core**: the minimal, stable JSON object used to compute `decision_hash`.
- **DecisionEvent**: an append-only telemetry event emitted for each decision.
- **CheckpointEvent**: a telemetry event summarizing a contiguous range of DecisionEvents.
- **CTS**: Conformance Test Suite (tests + vectors + fixtures + manifests).
- **IUT**: Implementation Under Test.

## Canonical JSON (canon)

MDAB v0.1 uses a JCS-like canonicalization function:

- UTF-8 JSON serialization
- object keys are sorted lexicographically
- separators are `,` and `:`
- no whitespace outside JSON strings
- arrays preserve order
- NaN/Infinity are forbidden

### Parser constraints (normative)
Because JSON Schema cannot detect duplicate keys:

- JSON parsers used for conformance MUST reject duplicate keys (fail-closed).
- Numeric policy: only integer JSON numbers are permitted for conformance artifacts.
  Floats and exponent forms (e.g., `1.5`, `1e3`) are INVALID.
