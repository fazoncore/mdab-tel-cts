# fixtures/v0.1.1

Add v0.1.1 fixtures here according to:
docs/v0.1.1/MDAB_TEL_v0_1_1_Fixtures_Manifest_PUBLIC_SAFE_NFC_A.md

Recommended workflow:
1) Copy an existing minimal PASS fixture from v0.1.0
2) Modify exactly one factor per fixture (Unicode form, number format, unknown field, duplicate keys, chain link)
3) Run CTS/verifier, then record PASS/FAIL and hashes into:
docs/v0.1.1/MDAB_TEL_v0_1_1_Expected_Outputs_Template_PUBLIC_SAFE_NFC_A.md

Optional roadmap:
- If you later add an “envelope checkpoint” profile, use periodic checkpoints to create discrete audit surfaces
  for system‑level invariants (see fixtures manifest P2 section).
