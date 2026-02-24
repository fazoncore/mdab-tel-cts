# Contributing

## Ground rules
- Keep changes deterministic and reproducible.
- Any change that affects hashes/vectors MUST update fixtures and CTS expectations.
- Prefer small PRs with explicit rationale.

## Development
1) Install deps:
```bash
python3 -m pip install -r telemetry_cts/requirements.txt
```
2) Run CTS:
```bash
python3 telemetry_cts/ct/validate_schema.py
python3 telemetry_cts/ct/run_chain_verifier.py --profile audit telemetry_cts/fixtures/tel/tel-stream-valid.jsonl
python3 telemetry_cts/ct/run_chain_verifier.py --profile ha telemetry_cts/fixtures/tel/tel-stream-signed-valid.jsonl
```
