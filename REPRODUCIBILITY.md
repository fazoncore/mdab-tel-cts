# Reproducibility (Offline)

## Goal
The CTS/verifier is designed to be:
- offline-reproducible (no network calls required)
- fail-closed (any parse/schema/hash/signature error => FAIL)
- deterministic (canonical JSON + SHA-256)
- tamper-evident (event_hash + hash-chain; optional signed HA fixtures)

## Quickstart
```bash
python3 -m pip install -r telemetry_cts/requirements.txt
python3 telemetry_cts/ct/validate_schema.py
python3 telemetry_cts/ct/run_chain_verifier.py --profile audit telemetry_cts/fixtures/tel/tel-stream-valid.jsonl
python3 telemetry_cts/ct/run_chain_verifier.py --profile ha telemetry_cts/fixtures/tel/tel-stream-signed-valid.jsonl
