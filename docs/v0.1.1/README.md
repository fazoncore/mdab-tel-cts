# MDAB‑TEL v0.1.1 — Public‑Safe Clarification Pack (NFC_A)

This folder contains:
- Spec clarifications (determinism hardening):
  - Unicode: normalize all strings to NFC prior to canonical serialization
  - Unknown fields: FAIL‑CLOSED in v0.1.x
  - Numbers: strict FAIL‑CLOSED for float/scientific/-0/etc.
  - Duplicate keys: FAIL‑CLOSED
  - Hash scope + chain semantics: explicit

- Scope boundary clarification (system coherence):
  - v0.1 conformance is transaction‑scoped (deterministic replay per decision)
  - system‑level invariants are out‑of‑scope unless explicitly committed
  - for external review, periodic envelope checkpoints are the recommended pattern (roadmap)
  - audit‑legible packaging: split (a) invariant declaration artefact (versioned, immutable, hashed) and (b) checkpoint result records referencing the invariant hash

- Invariant declaration artefact note (why/how to split invariants from checkpoint evaluations)

- Fixtures manifest (what to add under fixtures/v0.1.1/)
- Expected outputs template (fill AFTER running CTS/verifier)
- Release notes template (copy into GitHub Release for v0.1.1)

NOTE: v0.1.1 is clarifications + fixtures only. v0.1.0 remains immutable.
