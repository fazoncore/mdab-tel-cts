# Release checklist (v0.1.x)

1) Run CTS locally:
```bash
python3 -m pip install -r telemetry_cts/requirements.txt
python3 telemetry_cts/ct/validate_schema.py
python3 telemetry_cts/ct/run_chain_verifier.py --profile audit telemetry_cts/fixtures/tel/tel-stream-valid.jsonl
python3 telemetry_cts/ct/run_chain_verifier.py --profile ha telemetry_cts/fixtures/tel/tel-stream-signed-valid.jsonl
```

2) Update version references if needed:
- `telemetry_cts/MANIFEST.md`
- `CITATION.cff`

3) Tag and push:
```bash
git tag v0.1.0
git push origin v0.1.0
```

4) Attach artifacts to GitHub Release:
- `MDAB_v0.1_Appendix_Conformance_2p_v2.pdf`
- (optional) a zip of `telemetry_cts/`
