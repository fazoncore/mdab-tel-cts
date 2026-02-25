# Security Policy (mdab-tel-cts)

## Reporting a vulnerability
Please DO NOT open public GitHub issues for security vulnerabilities.

Preferred channel:
- GitHub: Security tab → “Report a vulnerability” (Private Vulnerability Reporting)

Fallback:
- Email: fazon@fazoncore.org
- Subject: [mdab-tel-cts] Security report
- Include: affected version/tag, impact, minimal repro/PoC, and suggested fix (if any)

## In scope
- Verifier correctness bypass (PASS where FAIL expected)
- Signature verification flaws (HA profile / signed fixtures)
- Canonicalization ambiguity causing cross-implementation hash mismatches
- Hash-chain integrity verification bypass (prev_event_hash / seq / checkpoint)
- Schema validation bypass affecting verifier correctness

## Out of scope
- Compromised host/OS, stolen keys, insider threats
- Pure DoS without a correctness bypass
- Third-party dependency vulnerabilities (please report upstream)

## Disclosure
Coordinated disclosure on a best-effort basis. No SLA is guaranteed.
