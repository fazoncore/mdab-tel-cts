# MDAB‑TEL — v0.1.1 Clarification Pack (PUBLIC‑SAFE)
**Purpose:** tighten determinism, hash scope clarity, and fail‑closed semantics without changing v0.1.0 artifacts.

> This document is intended as a drop‑in **normative addendum** you can copy into your spec (or use as `SPEC_ADDENDUM_v0_1_1.md`).
> It contains **MUST / MUST NOT** rules and is intentionally minimal.

## 0. Scope & versioning discipline (v0.1.1)
1. This addendum defines **v0.1.1** conformance requirements and does **not** retroactively modify any v0.1.0 canonical artifacts.
2. Implementations MUST treat the version identifier included in hash scope (e.g., `spec_version`) as a protocol boundary:
   - v0.1.1 artifacts MUST identify as v0.1.1 (or equivalent), and
   - validators MUST FAIL‑CLOSED on version mismatch (do not accept v0.1.1 objects as v0.1.0).

---
## 1. Canonical JSON Input Requirements

### 1.1 Encoding
1. Inputs MUST be valid UTF‑8.
2. Inputs MUST NOT contain invalid Unicode scalar values (e.g., unpaired surrogates). If detected, the verifier MUST FAIL‑CLOSED.

### 1.2 JSON parsing
1. Inputs MUST be valid JSON per RFC 8259.
2. Object member names MUST be unique. Duplicate keys MUST trigger FAIL‑CLOSED (no “last‑wins” semantics).
3. Numbers MUST be handled as specified in Section 2.3 (restricted numeric domain). Any deviation MUST FAIL‑CLOSED.
4. Any parse ambiguity MUST trigger FAIL‑CLOSED.

---

## 2. Canonicalization Determinism

### 2.1 Deterministic serialization
Canonicalization MUST be deterministic across platforms, runtimes, and language implementations.

### 2.2 Strings (Unicode normalization policy — NFC inside)

To prevent cross‑implementation drift from visually‑equivalent Unicode strings:

1. Prior to canonical serialization, **all JSON strings MUST be normalized to Unicode NFC**, including:
   - object member names (keys), and
   - string values.
2. If NFC normalization cannot be performed due to invalid Unicode scalar values, the verifier MUST FAIL‑CLOSED.
3. After NFC normalization, **object member names MUST remain unique** within each object. If two keys become equal after NFC normalization, the verifier MUST FAIL‑CLOSED (treat as a duplicate key error).
4. After NFC normalization, serialization MUST proceed deterministically.


### 2.3 Numbers (restricted domain)
To prevent cross‑implementation drift, the numeric domain is restricted as follows:

1. Only **signed integers** are permitted.
2. Integers MUST be represented without leading zeros (except the literal `0`).
3. Floating point numbers are forbidden (`1.0`, `1e3`, `-0.0`), as are NaN/Infinity representations (even if a parser accepts them).
4. `-0` MUST FAIL‑CLOSED.
5. If a value cannot be represented as an integer in the chosen domain, the verifier MUST FAIL‑CLOSED.

*(If you need broader numeric support later, define a v0.2 numeric profile; do not widen v0.1.x.)*

### 2.4 Unknown members / forward compatibility (v0.1.x)
To prevent equivocation and “shadow semantics”:

- Any JSON object member not explicitly defined by the schema MUST cause FAIL‑CLOSED.

*(Forward‑compat should be introduced only via an explicit, namespaced extension container in a future version.)*

---

## 3. Hash Scope — explicit and non‑ambiguous

### 3.1 Scope MUST include (domain separation)
The hash scope MUST include, at minimum:

1. `spec_version` (or equivalent version identifier)
2. `schema_id` / `event_type` (domain separation between object types)
3. canonical payload bytes (the output of canonicalization)
4. hash algorithm identifier (e.g., `sha256`)
5. `prev_hash` (for chained records; omit only for genesis where explicitly defined)

### 3.2 Scope MUST exclude
The scope MUST NOT include:

- filesystem paths, build paths, runtime environment strings
- timestamps that are not part of the logical payload
- comments, whitespace, or transport metadata
- the signature bytes themselves (avoid circular dependence)

### 3.3 Equivocation test
If any two records differ in `schema_id/event_type` or canonical payload, their scope hash MUST differ.

---

## 4. Chain Semantics (if hash‑chain is used)

1. Each non‑genesis record MUST include `prev_hash` equal to the scope hash of the immediately prior record.
2. Verifiers MUST validate chain continuity (no gaps, no reorder).
3. Any missing link, mismatch, or truncation MUST FAIL‑CLOSED.

---

## 5. Signature Semantics (if signatures are used)

1. The signature MUST authenticate **the scope hash** (recommended) or the canonical payload bytes; choose ONE and specify it.
2. Signature verification metadata (key id, algorithm id) MUST be defined as verification inputs.
3. The signature bytes MUST NOT be included in the bytes being signed (no circularity).
4. Any signature mismatch MUST FAIL‑CLOSED.

---

## 6. Reproducibility contract (documentation level)

1. Repro steps MUST be ≤ 5 commands/steps.
2. Expected outputs MUST include at least:
   - PASS/FAIL outcome
   - resulting scope hash (or digest)
   - tool/version identifier used for the run
3. Any mismatch in expected outputs MUST STOP the workflow (FAIL‑CLOSED).

## 7. Transaction conformance vs system coherence (envelope checkpoints)

### 7.1 Scope statement (v0.1.x)
MDAB‑TEL v0.1 conformance is intentionally **transaction‑scoped**: a verifier can prove deterministic replay and integrity for a single decision attempt (e.g., `policy_hash` + `decision_hash` binding) and enforce a fail‑closed posture.

In **chained/stateful** deployments, higher‑order constraints (“constraint envelopes”) may exist above any single decision scope (budgets, rate limits, conserved quantities, safety envelopes, sequence invariants, etc.). These **system‑level invariants are out‑of‑scope unless explicitly committed** into the auditable record.

- Implementations MUST treat uncommitted system‑level invariants as out‑of‑scope for conformance claims.
- Implementations MUST NOT claim system‑level invariant conformance unless the invariant declaration and the relevant state/summary are committed in a verifiable form.

### 7.2 Review‑friendly pattern (recommended): periodic envelope checkpoints
For external review (independent auditors, regulators, adversarial testing), prefer **periodic envelope checkpoints** over per‑step rolling state digests.

A checkpoint creates a discrete “audit surface” where you can say:
- individual decisions are locally conformant under Audit, but
- the composed invariant fails at **boundary X**.

A checkpoint envelope result record SHOULD commit, at minimum:
1. `checkpoint_id` (boundary/window identifier)
2. `invariant_hash` (hash of a **versioned, immutable invariant declaration artefact**)
3. `state_digest` (hash of the relevant state snapshot or conserved summary at the boundary)
4. `evaluation_outcome` (PASS/FAIL) and (optionally) a reason code
5. `prev_checkpoint_hash` (if checkpoint chaining is used; omit only for genesis when explicitly defined)

If checkpoint evaluation fails, the envelope result MUST be treated as **NONCONFORMANT** (or FAIL‑CLOSED) at the envelope layer, even if each individual decision remains conformant.

### 7.3 Rolling state digests (internal option)
Rolling per‑step state digests can be useful internally for drift detection, but they increase cognitive load for reviewers and make boundary‑localization harder. For governance artifacts, optimize for **inspectability over continuity**.

### 7.4 Split invariants from checkpoint results (recommended)
To maximize audit legibility and reduce invariant drift risk, treat invariants and their evaluations as separate artefacts:

1. **Invariant declaration artefact (stable rule):** versioned and immutable once published, producing an `invariant_hash` over its canonical form.
2. **Checkpoint result record (discrete evaluation):** references `invariant_hash` and commits `state_digest` + PASS/FAIL outcome.

Bundling is compact; splitting is audit‑legible. For review‑facing posture, optimize for legibility.

---
