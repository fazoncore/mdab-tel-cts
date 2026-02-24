# MDAB v0.1 — Traceability Matrix (Telemetry CTS)

This document maps normative requirements (RQ-xx) to conformance tests (CT-TEL-xxx)
and concrete fixtures.

## How to run
See `ct/CT-INDEX.md`.

---

## Traceability table

| RQ ID | Priority | Profile(s) | Requirement (summary) | Tests | Fixtures |
|---:|:---:|:---:|---|---|---|
| RQ-01 | P0 | CORE/AUDIT/HA | Deterministic canon(x) | CT-TEL-001..009 | all streams (hash checks depend on canon) |
| RQ-02 | P0 | CORE/AUDIT/HA | Duplicate keys rejected | CT-TEL-010 | `fixtures/tel/tel-stream-dupkeys.jsonl` |
| RQ-03 | P0 | CORE/AUDIT/HA | Integer-only numbers | CT-TEL-011 | `fixtures/tel/tel-stream-float.jsonl` |
| RQ-10 | P0 | CORE/AUDIT/HA | decision_hash = SHA256(canon(decision_core)) | CT-TEL-001 | `tel-stream-valid.jsonl` |
| RQ-20 | P0 | AUDIT/HA | event_hash = SHA256(canon(event_core)) | CT-TEL-001..006 | valid + tamper fixtures |
| RQ-21 | P0 | AUDIT/HA | chain seq+prev hash integrity | CT-TEL-004..005 | gap/reordered fixtures |
| RQ-22 | P1 | AUDIT/HA | checkpoint block_hash correctness | CT-TEL-006 | `tel-stream-bad-checkpoint.jsonl` |
| RQ-30 | P0 | HA | ed25519 signature verify | CT-TEL-007..008 | signed fixtures |
| RQ-31 | P0 | HA | key validity/revocation | CT-TEL-009 | expired-key fixture |
