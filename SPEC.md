# MDAB-TEL v0.1 — Normative Quick Reference

This is a quick reference. The normative sources are:
- `telemetry_cts/SPEC/terminology.md`
- `telemetry_cts/SPEC/chain_verifier.md`
- `telemetry_cts/schemas/*.schema.json`

## Fail-closed parsing
Implementations MUST fail (verification FAIL) on:
- invalid JSON
- duplicate keys
- forbidden number forms (e.g., floats/exponents/NaN/Inf) when not allowed by the profile
- schema violations

## Hash primitive and format
- SHA-256 is the only digest primitive in v0.1.
- Hash strings use: `sha256:<64 lowercase hex>`.

## decision_hash
`decision_hash = SHA256(canon(decision_core))`
- `decision_core` MUST conform to `telemetry_cts/schemas/decision_core.schema.json`.
- Any mismatch MUST fail: `E_DECISION_HASH_MISMATCH`.
- Interop note: `decision_digest` MAY be accepted only as an ingestion alias; conformance uses `decision_hash`.

## event_hash
`event_hash = SHA256(canon(event_core))`
- `event_core` is the event object excluding: `event_hash` and `signature`.
- Any mismatch MUST fail: `E_HASH_MISMATCH`.

## Chain integrity (per emitter stream)
Per `emitter.instance_id`:
- `seq` MUST be strictly increasing.
- `prev_event_hash` MUST equal the previous `event_hash` (or null for genesis).
- Any break MUST fail: `E_CHAIN_BREAK` / `E_SEQ_NON_MONOTONIC`.

## Checkpoints (if present)
Checkpoint block hashing is defined in `telemetry_cts/SPEC/chain_verifier.md`.
- Any mismatch MUST fail: `E_BLOCKHASH_MISMATCH`.

## HighAssurance signatures (HA profile)
- Algorithm: `ed25519`.
- Signature covers the raw 32-byte digest bytes of `event_hash` (not the text string).
- Unknown/revoked/expired key MUST fail.
- Invalid signature MUST fail: `E_SIG_INVALID`.

## Reproduce
See `REPRODUCIBILITY.md`.
