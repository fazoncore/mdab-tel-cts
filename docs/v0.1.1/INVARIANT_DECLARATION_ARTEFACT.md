# Invariant declaration artefact (PUBLIC‑SAFE note)

**Purpose:** make system‑level constraints auditable **without** changing transaction‑level conformance semantics.

MDAB‑TEL v0.1 conformance is decision/transaction‑scoped. In chained/stateful deployments, higher‑order constraints (“constraint envelopes”) must be **explicitly committed** to be enforceable and reviewable.

This note describes a review‑friendly pattern: treat invariants as a **versioned, immutable artefact** with its own identity and hash. Checkpoint results then reference the invariant by hash.

## Why split invariants from checkpoint results
Splitting improves:
- **Diffability:** rule changes are explicit (new invariant version) rather than hidden in checkpoint payloads.
- **Boundary localization:** checkpoint results remain discrete audit surfaces.
- **Certification trails:** auditors can reference a stable rule artefact and evaluate discrete results.
- **Drift resistance:** reduces the risk of subtle invariant drift via bundled envelope updates.

## Minimal requirements (profile‑level / roadmap)

### Invariant declaration artefact (stable rule)
An invariant declaration artefact SHOULD:
- be **versioned** (e.g., semantic version or monotonically increasing integer)
- be treated as **immutable** once published
- be canonicalized deterministically (same canonicalization discipline as other artefacts)
- produce a stable `invariant_hash` computed over the canonical declaration

Minimal fields (illustrative):
- `invariant_id` — stable identifier
- `invariant_version` — version label
- `invariant_spec` — normalized/canonical representation of the rule
- `invariant_hash` — digest of the canonical declaration (algorithm identified)

### Checkpoint result record (discrete evaluation)
A checkpoint result record SHOULD:
- reference the invariant artefact by `invariant_hash`
- commit a `state_digest` of the relevant boundary state/summary
- record `evaluation_outcome` (PASS/FAIL) and optional `reason_code`

Minimal fields (illustrative):
- `checkpoint_id`
- `invariant_hash`
- `state_digest`
- `evaluation_outcome`
- `reason_code` (optional)
- `prev_checkpoint_hash` (optional, if checkpoint chaining is used)

## Claims language (PUBLIC‑SAFE)
- If an invariant is **not** committed as an artefact and referenced by hash, it is **out of scope** for conformance claims.
- If a checkpoint evaluation FAILs, the envelope layer MUST be treated as **NONCONFORMANT / FAIL‑CLOSED** at that boundary, even if individual decisions remain conformant.

