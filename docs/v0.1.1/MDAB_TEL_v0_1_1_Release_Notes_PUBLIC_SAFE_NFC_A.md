# MDAB‑TEL v0.1.1 — Release Notes (PUBLIC‑SAFE)

**Type:** clarification + fixtures only (no changes to v0.1.0 artifacts)

## Summary
This release tightens determinism and auditability by:
- making Unicode and numeric handling explicit,
- enforcing fail‑closed semantics for ambiguous JSON constructs,
- defining hash scope inclusion/exclusion rules,
- adding fixtures that detect equivocation, replay‑style truncation, and parser drift.

## Changes (high‑signal)
- Canonicalization: Unicode strings (keys + values) are NFC‑normalized prior to canonical serialization; key collisions after normalization FAIL‑CLOSED (deterministic).
- Numbers: restricted to signed integers; floats/scientific/-0 forbidden.
- JSON: duplicate keys forbidden; unknown fields forbidden (v0.1.x).
- Hash scope: explicit domain separation (version + event_type/schema_id) and exclusions.
- Chain semantics: continuity required; missing links fail.
- Scope boundary: clarified transaction determinism vs system‑level coherence; recommended periodic envelope checkpoints for external review (roadmap).
- Audit legibility note: recommended **split** between (a) a versioned invariant declaration artefact (immutable, hashed) and (b) discrete checkpoint result records referencing the invariant hash.
- Fixtures: added a minimal negative suite for determinism and scope integrity.
- Documentation: expected outputs template + STOP conditions.

## Non‑goals
- Does not claim endorsement/approval.
- Does not change v0.1.0.
- Does not widen format for extensions (reserved for future versions).

---