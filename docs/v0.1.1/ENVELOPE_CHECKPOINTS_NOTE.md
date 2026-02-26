# System‑level invariants via periodic envelope checkpoints (PUBLIC‑SAFE note)

**Why this exists:** deterministic replay and transaction‑level conformance are necessary but not sufficient for **system‑level coherence** in chained/stateful deployments. A sequence can be locally conformant per decision while violating a higher‑order constraint that is not encoded locally.

**Reviewability goal:** external reviewers generally prefer **discrete audit surfaces** over auditing a continuous stream.

## Recommended pattern (review‑facing)
Introduce periodic **envelope checkpoints** (roadmap / profile‑level) that commit:
- `checkpoint_id` (boundary/window identifier)
- `invariant_hash` (hash of a **versioned, immutable invariant declaration artefact**)
- `state_digest` (hash of the relevant state snapshot or conserved summary)
- `evaluation_outcome` (PASS/FAIL) and optional reason code
- `prev_checkpoint_hash` if you chain checkpoints (optional)

**Interpretation:** if `evaluation_outcome = FAIL`, the envelope layer is NONCONFORMANT / FAIL‑CLOSED at that boundary, even if the individual decisions remain conformant.

## Packaging (roadmap) — recommended: split

### 1) Invariant declaration artefact (stable rule)
Treat the invariant declaration as a **versioned, immutable artefact** with its own identity and hash.

Minimal fields (illustrative):
- `invariant_id`
- `invariant_version`
- `invariant_spec` (normalized / canonical form)
- `invariant_hash` (hash over the canonical invariant declaration)

### 2) Checkpoint result record (discrete evaluation)
Each checkpoint result references the invariant artefact by `invariant_hash`, and commits:
- `checkpoint_id`
- `invariant_hash`
- `state_digest`
- `evaluation_outcome` (PASS/FAIL)
- (optional) `reason_code`

**Why split:** bundling is compact, but splitting is audit‑legible. It improves diffability, boundary localization, and certification trails, and reduces the risk of subtle invariant drift being introduced via bundled updates.
