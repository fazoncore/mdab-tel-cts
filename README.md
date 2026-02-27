[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18763066.svg)](https://doi.org/10.5281/zenodo.18763066)
# MDAB v0.1 — Telemetry Event Schema & CTS (GitHub-ready)
Zenodo DOI: https://doi.org/10.5281/zenodo.18763066
This repository provides a **deterministic telemetry event schema (MDAB-TEL v0.1)**,
plus a **Chain Verifier** and **Conformance Test Suite (CTS)** with **valid / tamper / signed (HA)** fixtures.

It is designed to be:
- **offline-reproducible** (no network calls by the verifier)
- **fail-closed** (any parse/schema/hash error => FAIL)
- **deterministic** (canonical JSON + SHA-256)

## Quick start
```bash
python3 -m pip install -r telemetry_cts/requirements.txt
python3 telemetry_cts/ct/validate_schema.py
python3 telemetry_cts/ct/run_chain_verifier.py --profile audit telemetry_cts/fixtures/tel/tel-stream-valid.jsonl
python3 telemetry_cts/ct/run_chain_verifier.py --profile ha telemetry_cts/fixtures/tel/tel-stream-signed-valid.jsonl
```

## What to submit (NIST-style evidence)
- Appendix A (PDF): `appendix/AppendixA_Conformance_2p_v2.pdf`
- Telemetry CTS folder: `telemetry_cts/`
- Integrity: `telemetry_cts/SHA256SUMS.txt`

> Note: Appendix A includes a broader *system* conformance template (MDAB Core + Telemetry).
> This repository focuses on **Telemetry CTS**. If you want a single monorepo that also includes
> MDAB Core vectors/policy/CT, add them alongside `telemetry_cts/` and keep the same hash rules.

## Repository layout
- `telemetry_cts/` — schemas, requirements, traceability, verifier, fixtures, keys
- `appendix/` — Appendix A (MD + PDF) and patch file

## License
Apache-2.0 (see `LICENSE`).
