# MDAB v0.1 — Key Policy (Minimal)

This document is **normative** for HighAssurance (HA) Telemetry verification.

- Keys are identified by `key_id` and rotated regularly (recommended <= 12 months).
- Only **ed25519** is permitted in v0.1.
- Signatures cover **raw digest bytes** of `event_hash` (32 bytes), not the textual JSON form.
- Verifiers MUST reject:
  - unknown `key_id`
  - revoked keys
  - keys outside the `[not_before_utc, not_after_utc]` validity window
  - invalid signatures (fail-closed)
