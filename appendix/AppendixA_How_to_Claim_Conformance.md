# Appendix A — How to Claim Conformance (MDAB v0.1)

## Purpose
Provide a minimal, reproducible method to claim conformance to **MDAB v0.1** using deterministic hashes + executable test cases.

## A0. Hash naming (normative)
Conformance bundles MUST use **`*_hash`** naming for SHA-256 outputs.

- `policy_hash = SHA-256(canon(policy))`
- `decision_hash` is the normative name for the decision binding hash.

**Compatibility alias (allowed only for ingestion tooling):**
- `decision_digest` MAY be accepted as an alias for `decision_hash`.
- If both fields appear, they MUST be identical; otherwise the record is INVALID.
- Conformance claims MUST emit and reference **`decision_hash`**.

## A1. Conformance profiles
| Profile | Minimum requirements (summary) |
|---|---|
| **MDAB-System-Core-0.1** | Authority-before-execution via ATKN; deterministic `canon()` + `decision_hash`; Enforcer fail-closed; EER emitted for every attempt. |
| **MDAB-System-Audit-0.1** | Core + Verifier replay: EER chain validation; `decision_hash` recomputation; `policy_hash` verification (when policy available); policy replay (outcome + reason_code[0]). |
| **MDAB-System-HighAssurance-0.1** | Audit + signatures (boundary/enforcer or telemetry signer) and tamper-resistance; WORM/append-only storage; atomic anti-replay for one-time tokens. |

## A2. Evidence bundle (required artifacts)
A conformance claim MUST be accompanied by an evidence bundle (repo URL or archive). Include these files and their SHA-256 checksums:

### A2.1 Core boundary conformance artifacts (MDAB)
| Artifact | Path | Purpose |
|---|---|---|
| Policy (canonical JSON) | `policy/mdab.core-0.1.0.json` | Reference policy; input to `policy_hash`. |
| Policy hash | `policy/mdab.core-0.1.0.sha256` | Golden `SHA-256(canon(policy))`. |
| Golden vectors (10) | `vectors/tv01-10.jsonl` | TIC+AT inputs with expected outcome/reason/rule + `decision_hash`. |
| CT index | `ct/CT-INDEX.md` | Normative test definitions + pass/fail rules. |
| CT runner | `ct/run_ct.py` | Reproduces `policy_hash`, `decision_hash`, evaluator replay. |
| Negative fixtures (recommended) | `fixtures/**` + `ct/run_ct_neg.py` | Fail-closed and strict parsing evidence. |
| Verifier fixtures (recommended) | `fixtures/eer/*.jsonl` + `ct/run_vfy_ct.py` | EER chain + replay examples (valid + tampered). |

### A2.2 Telemetry CTS artifacts (MDAB-TEL v0.1)
| Artifact | Path | Purpose |
|---|---|---|
| Terminology | `SPEC/terminology.md` | Normative naming: `decision_hash` and SHA-256 conventions. |
| JSON Schemas | `schemas/*.schema.json` | Telemetry event schemas (DECISION/CHECKPOINT) and overlays for HA. |
| Requirements | `ct/REQUIREMENTS.md` | Normative RQ list (P0/P1/P2) by profile. |
| Traceability | `ct/TRACEABILITY.md` | RQ→SPEC→CT→Evidence mapping. |
| Schema validator | `ct/validate_schema.py` | Offline schema validation step (pre-verification). |
| Chain verifier | `ct/run_chain_verifier.py` | Normative chain + hash + checkpoint verification. |
| Tamper fixtures | `fixtures/tel/*.jsonl` | Valid + tampered + gap + reorder fixtures. |
| Key bundle (HA) | `keys/*` | Public keys + key policy for signature verification. |

| Architecture diagram (optional) | `FAZON_MDAB_Architecture_v0.1.svg` | Non-normative overview for reviewers. |

## A3. Reference procedure (how to produce evidence)
Run the following commands and capture stdout verbatim in `RESULTS.md`. All failures MUST be treated as NONCONFORMANT.

**Commands (MDAB core):**
```text
python3 ct/run_ct.py
python3 ct/run_ct_neg.py  # recommended
python3 ct/run_vfy_ct.py --profile audit fixtures/eer/eer-stream-valid.jsonl  # for Audit+ profiles
```

**Commands (Telemetry CTS):**
```text
python3 ct/validate_schema.py
python3 ct/run_chain_verifier.py --profile audit fixtures/tel/tel-stream-valid.jsonl
python3 ct/run_chain_verifier.py --profile ha fixtures/tel/tel-stream-signed-valid.jsonl  # for HighAssurance
```

**Golden policy_hash (SHA-256(canon(policy))):**  
`f2d4239831f71aad992a7a21c6f9e87627fe39d387bf201ab633c511d3c635d3`

## A4. Minimal conformance claim (template)
- **Implementation:** <name> / <version> (commit/hash optional)  
- **Claim date:** <YYYY-MM-DD>  
- **Claimed profile(s):** MDAB-System-{Core|Audit|HighAssurance}-0.1  
- **Policy reference:** `policy/mdab.core-0.1.0.json`  
- **policy_hash:** `f2d4239831f71aad992a7a21c6f9e87627fe39d387bf201ab633c511d3c635d3`  
- **Vectors:** `vectors/tv01-10.jsonl` (TV01..TV10)  
- **Test execution:** `ct/run_ct.py` -> PASS (and optional runs as applicable)  
- **Telemetry CTS:** `ct/run_chain_verifier.py` -> PASS (Audit/HA as claimed)  
- **Evidence bundle:** repo URL or archive checksum + `SHA256SUMS.txt` + `RESULTS.md`

## A5. Packaging checklist
Include:  
(1) `SHA256SUMS.txt` for every artifact,  
(2) `RESULTS.md` with runner outputs,  
(3) `MANIFEST.md` describing file purpose,  
(4) optional diagram.  
Avoid external dependencies; reviewers should reproduce results offline.
