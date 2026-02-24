# MDAB v0.1 — Telemetry Chain Verifier (Normative)

This document specifies the **normative** verification procedure for MDAB Telemetry
DecisionEvent and CheckpointEvent streams (MDAB-TEL-0.1).

## Inputs
- A JSONL stream containing events.
- Schemas under `schemas/`.
- (HA) A key bundle `keys/verifier_keys.json`.

## Verification algorithm (fail-closed)

For each line in the JSONL stream:

1) **Parse (strict)**  
   - Duplicate keys are forbidden and MUST raise an error.  
   - Floats/exponent-form numbers are forbidden and MUST raise an error.

2) **Schema validation**  
   - If `event_type == "DECISION"` validate against `schemas/decision_event.schema.json`
     (or `decision_event.ha.schema.json` in HA profile).
   - If `event_type == "CHECKPOINT"` validate against `schemas/checkpoint_event.schema.json`
     (or `checkpoint_event.ha.schema.json` in HA profile).

3) **decision_hash**  
   - Compute `calc_decision_hash = sha256:<hex>` where `<hex> = SHA-256(canon(decision_core))`.
   - Require `calc_decision_hash == decision.decision_hash`.
   - (Optional ingestion alias) `decision_digest` MAY be accepted as an alias for `decision_hash`
     but conformance streams MUST use `decision_hash`.

4) **event_hash**  
   - Construct `event_core = event` with fields `event_hash` and `signature` removed.
   - Compute `calc_event_hash = sha256:<hex>` where `<hex> = SHA-256(canon(event_core))`.
   - Require `calc_event_hash == event.event_hash`.

5) **Chain integrity (per emitter stream)**  
   Emitter stream key is the tuple `(service, instance_id, env, region)`.

   For each emitter stream:
   - `seq` MUST start at 0 and increment by 1 with no gaps.
   - `prev_event_hash` MUST equal prior `event_hash` (genesis uses null).

6) **Checkpoint verification (AUDIT/HA)**  
   For each CheckpointEvent:
   - Gather DECISION `event_hash` values for the same emitter in the inclusive range
     `[range_start_seq..range_end_seq]` in ascending `seq`.
   - Compute:
     `block_hash = SHA-256("MDAB-BLOCK-0.1\n" + join(event_hashes,"\n") + "\n")`
     encoded as `sha256:<hex>`.
   - Require it equals `checkpoint.block_hash`.
   - Require `checkpoint.last_event_hash` equals the DECISION event_hash at `range_end_seq`.

7) **Signature verification (HA profile, or if signature present)**  
   - Resolve `signature.key_id` in `keys/verifier_keys.json`.
   - Reject unknown / revoked / non-ACTIVE / time-invalid keys.
   - Signature algorithm MUST be `ed25519`.
   - Verify signature over the **raw 32-byte digest** represented by `event_hash`
     (i.e., bytes of the hex after `sha256:`).

Any failure MUST produce **FAIL** with explicit error code(s).

## Error codes (minimum)
- `E_DUPLICATE_KEY`
- `E_FLOAT_FORBIDDEN`
- `E_SCHEMA_INVALID`
- `E_DECISION_HASH_MISMATCH`
- `E_HASH_MISMATCH`
- `E_CHAIN_BREAK`
- `E_SEQ_GAP`
- `E_SEQ_NON_MONOTONIC`
- `E_BLOCKHASH_MISMATCH`
- `E_SIG_MISSING` (HA only)
- `E_KEY_UNKNOWN`
- `E_KEY_REVOKED`
- `E_KEY_EXPIRED`
- `E_SIG_INVALID`
