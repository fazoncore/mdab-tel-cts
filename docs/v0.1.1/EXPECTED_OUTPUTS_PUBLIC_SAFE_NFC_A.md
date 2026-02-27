# MDAB-TEL v0.1.1 — Expected outputs (PUBLIC_SAFE_NFC_A)

Hash rule:
scope_hash_sha256 = SHA256( UTF-8( canonical_json(event) ) )

canonical_json:
- key sort
- compact JSON (no extra whitespace)
- Unicode NFC normalization for all strings
- FAIL_CLOSED on: floats, scientific notation, -0, duplicate keys, unknown top-level fields

## Expected

PASS:
- fixtures/v0.1.1/unicode_nfc_composed.json     => fc4ed13d8980ceabd15bb8bc0ecae3d8d33175ac015479344908e35ee311188a
- fixtures/v0.1.1/unicode_nfc_decomposed.json   => fc4ed13d8980ceabd15bb8bc0ecae3d8d33175ac015479344908e35ee311188a
- fixtures/v0.1.1/num_integer_ok.json           => ed7f8f6cc2a76f126ddb11b59724594bce62eb4c814c647f00445e9cd3646025

FAIL_CLOSED:
- fixtures/v0.1.1/num_float_forbidden.json              => ERR_NUM_FLOAT_FORBIDDEN
- fixtures/v0.1.1/num_scientific_forbidden.json         => ERR_NUM_SCIENTIFIC_NOTATION
- fixtures/v0.1.1/num_negative_zero_forbidden.raw.json  => ERR_NUM_NEGATIVE_ZERO
- fixtures/v0.1.1/unknown_field_forbidden.json          => ERR_UNKNOWN_FIELD
