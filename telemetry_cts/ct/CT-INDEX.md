# MDAB v0.1 — Telemetry CTS Index (CT-INDEX)

This CTS validates **Telemetry Event Schema v0.1** (DecisionEvent + CheckpointEvent),
hash-chain tamper evidence, and (optionally) ed25519 signatures for HighAssurance.

## 0) Quick start

```bash
python3 ct/validate_schema.py
python3 ct/run_chain_verifier.py --profile audit fixtures/tel/tel-stream-valid.jsonl
python3 ct/run_chain_verifier.py --profile audit fixtures/tel/tel-stream-tampered-field.jsonl
python3 ct/run_chain_verifier.py --profile ha    fixtures/tel/tel-stream-signed-valid.jsonl
```

## 1) Test cases

### CT-TEL-001 — Valid stream (AUDIT) passes
- Command: `python3 ct/run_chain_verifier.py --profile audit fixtures/tel/tel-stream-valid.jsonl`
- Expected: PASS

### CT-TEL-002 — Tampered field (hash not updated) fails
- Expected code: `E_HASH_MISMATCH`

### CT-TEL-003 — Tampered hash string fails
- Expected code: `E_HASH_MISMATCH`

### CT-TEL-004 — Sequence gap fails
- Expected code: `E_SEQ_GAP` (or `E_CHAIN_BREAK`)

### CT-TEL-005 — Reordered / non-monotonic seq fails
- Expected code: `E_SEQ_GAP` (first event is not genesis)

### CT-TEL-006 — Bad checkpoint fails
- Expected code: `E_BLOCKHASH_MISMATCH`

### CT-TEL-007 — Signed valid stream (HA) passes
- Command: `python3 ct/run_chain_verifier.py --profile ha fixtures/tel/tel-stream-signed-valid.jsonl`
- Expected: PASS

### CT-TEL-008 — Bad signature fails
- Expected code: `E_SIG_INVALID`

### CT-TEL-009 — Expired key fails
- Expected code: `E_KEY_EXPIRED`

### CT-TEL-010 — Duplicate keys rejected (fail-closed)
- Expected code: `E_DUPLICATE_KEY`

### CT-TEL-011 — Float rejected (fail-closed)
- Expected code: `E_FLOAT_FORBIDDEN`

## 2) Profiles

- **CORE**: schema + decision_hash checks (no chain required)
- **AUDIT**: CORE + event_hash + chain + checkpoint verification
- **HA**: AUDIT + signature and key validation (ed25519)

## 3) Artifacts

- Schemas: `schemas/*.schema.json`
- Keys: `keys/verifier_keys.json`
- Fixtures: `fixtures/tel/*.jsonl`
- Requirements: `ct/REQUIREMENTS.md`
- Traceability: `ct/TRACEABILITY.md`
