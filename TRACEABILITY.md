# MDAB-TEL v0.1 — Traceability Matrix (Normative)

This document maps normative requirements (RQ-*) to:
- the concrete test cases / fixtures that verify the requirement, and
- the reproduction commands used to validate conformance.

A conforming implementation (IUT) MUST satisfy all P0 requirements below for the claimed profile.

## Profiles
- Core: deterministic evaluation + canonicalization + hashes + fail-closed verifier behavior.
- Audit: Core + chain verification (prev_event_hash/seq) + checkpoints (block_hash) where applicable.
- HighAssurance (HA): Audit + signature verification over signed fixtures/events (optional in v0.1 unless explicitly claimed).

---

## Reproduction commands (offline)

### Install
```bash
python3 -m pip install -r telemetry_cts/requirements.txt
