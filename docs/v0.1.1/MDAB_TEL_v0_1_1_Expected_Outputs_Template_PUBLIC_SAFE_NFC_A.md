# MDAB‑TEL — v0.1.1 Expected Outputs Template (PUBLIC‑SAFE)

**Purpose:** make reproducibility auditable in ≤ 5 steps.

---

## 1) Repro steps (≤ 5 commands)
1. `tool --version`  → record tool version
2. `tool verify fixtures/v0.1.1/<fixture>` → record outcome
3. (optional) `tool canonicalize <fixture>` → record canonical bytes digest
4. (optional) `tool hash-scope <fixture>` → record scope hash
5. (optional) `tool verify-chain <chainfile>` → record chain outcome

---

## 2) Expected outputs table (fill in)

| Fixture ID     | File(s)                                      | Expected outcome | Expected scope_hash_sha256 | Expected error/reason |
|---------------|----------------------------------------------|------------------|----------------------------|-----------------------|
| F-UNICODE-01  | unicode_nfc_composed.json                     | PASS             | <FILL>                     |                       |
| F-UNICODE-01  | unicode_nfc_decomposed.json                   | PASS             | <FILL>                     |                       |
| F-NUM-02      | num_float_forbidden.json                      | FAIL_CLOSED      |                            | <FILL>                |
| F-JSON-01     | dup_keys_forbidden.raw.json                   | FAIL_CLOSED      |                            | <FILL>                |
| F-SCOPE-01    | scope_event_type_A.json / scope_event_type_B.json | PASS         | <FILL / <FILL>>            |                       |
| F-CHAIN-01    | chain_missing_middle.jsonl                    | FAIL_CLOSED      |                            | <FILL>                |

---

## 3) STOP conditions (normative workflow rule)
- If any fixture outcome differs from expected → STOP (do not proceed).
- If any PASS fixture hash differs from expected → STOP.
- If any FAIL fixture passes → STOP and treat as a verifier regression.

---
