# MDAB v0.1 — Standard Telemetry CTS Bundle (MANIFEST)

This bundle contains a **standard** set of normative artifacts for:
- naming / terminology (`decision_hash` unification)
- JSON Schemas (DecisionEvent, CheckpointEvent, decision_core, key bundle)
- requirements + traceability
- normative chain verifier + tamper fixtures (including signed)

## Top-level
- `SPEC/terminology.md` — normative terminology and hash naming.
- `SPEC/chain_verifier.md` — normative verification algorithm and error codes.
- `schemas/` — JSON Schemas (draft 2020-12).
- `ct/` — CTS runners and indexes.
- `fixtures/tel/` — telemetry streams (valid + tampered + signed).
- `keys/` — key bundle + key policy (for HA signature verification).
- `SHA256SUMS.txt` — SHA-256 checksums for all files in this bundle.
- `FAZON_MDAB_Architecture_v0.1.svg` — optional architecture diagram.

## Running CTS
```bash
python3 ct/validate_schema.py
python3 ct/run_chain_verifier.py --profile audit fixtures/tel/tel-stream-valid.jsonl
python3 ct/run_chain_verifier.py --profile ha    fixtures/tel/tel-stream-signed-valid.jsonl
```
