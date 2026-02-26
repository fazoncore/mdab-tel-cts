# Issue template — Envelope checkpoints for system‑level invariants (PUBLIC‑SAFE)

**Title:** Envelope checkpoints: transaction determinism vs system coherence (profile‑level)

## Problem statement
MDAB v0.1 provides deterministic replay and conformance at the **transaction/decision** layer. In chained/stateful deployments, a composed sequence can be locally conformant while violating a higher‑order constraint (budget, rate limit, conserved quantity, safety envelope) that is not committed locally.

## Goal
Define a review‑friendly “envelope checkpoint” profile (or add‑on) that:
- makes system‑level invariants auditable by committing invariant declarations and boundary state digests, and
- produces discrete audit surfaces (checkpoint boundaries) suitable for external review/certification.

## Proposed approach
- Add an invariant declaration artefact type (profile‑level): **versioned, immutable**, with its own identity and hash.
- Add an envelope checkpoint result record type (profile‑level).
- Require checkpoint result records to reference the invariant artefact by `invariant_hash` and to commit: `checkpoint_id`, `invariant_hash`, `state_digest`, `evaluation_outcome`, and optional checkpoint chaining fields.
- Treat checkpoint FAIL as NONCONFORMANT / FAIL‑CLOSED at the envelope layer.

## Deliverables
- Profile spec (minimal fields + canonicalization rules)
- CTS fixtures:
  - locally conformant decision sequence
  - checkpoint boundary FAIL on composed invariant
  - invariant declaration artefact + hash reference correctness
- Documentation note explaining scope boundary and claims language.

## Acceptance criteria
- Reviewers can locate invariant failure at a named boundary without auditing a rolling stream.
- Invariant declarations are stable and diffable as immutable artefacts.
- Offline replay remains deterministic for the decision layer.
- Envelope evaluation is fail‑closed and verifiable.
