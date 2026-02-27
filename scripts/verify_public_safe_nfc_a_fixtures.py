#!/usr/bin/env python3
import hashlib
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "v0.1.1"

EXPECTED = {
    "unicode_nfc_composed.json": ("PASS", "fc4ed13d8980ceabd15bb8bc0ecae3d8d33175ac015479344908e35ee311188a", ""),
    "unicode_nfc_decomposed.json": ("PASS", "fc4ed13d8980ceabd15bb8bc0ecae3d8d33175ac015479344908e35ee311188a", ""),
    "num_integer_ok.json": ("PASS", "ed7f8f6cc2a76f126ddb11b59724594bce62eb4c814c647f00445e9cd3646025", ""),
    "num_float_forbidden.json": ("FAIL_CLOSED", "", "ERR_NUM_FLOAT_FORBIDDEN"),
    "num_scientific_forbidden.json": ("FAIL_CLOSED", "", "ERR_NUM_SCIENTIFIC_NOTATION"),
    "num_negative_zero_forbidden.raw.json": ("FAIL_CLOSED", "", "ERR_NUM_NEGATIVE_ZERO"),
    "unknown_field_forbidden.json": ("FAIL_CLOSED", "", "ERR_UNKNOWN_FIELD"),
}

ALLOWED_TOP_LEVEL = {"spec_version", "event_type", "payload"}

class FailClosed(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code

def parse_event_fail_closed(raw: str):
    def parse_int(s: str):
        if s == "-0":
            raise FailClosed("ERR_NUM_NEGATIVE_ZERO")
        return int(s)

    def parse_float(s: str):
        if "e" in s or "E" in s:
            raise FailClosed("ERR_NUM_SCIENTIFIC_NOTATION")
        raise FailClosed("ERR_NUM_FLOAT_FORBIDDEN")

    def object_pairs_hook(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise FailClosed("ERR_JSON_DUPLICATE_KEYS")
            obj[k] = v
        return obj

    try:
        obj = json.loads(raw, parse_int=parse_int, parse_float=parse_float, object_pairs_hook=object_pairs_hook)
    except FailClosed as e:
        return ("FAIL_CLOSED", None, e.code)
    except Exception:
        return ("FAIL_CLOSED", None, "ERR_JSON_PARSE")

    if not isinstance(obj, dict):
        return ("FAIL_CLOSED", None, "ERR_TOPLEVEL_NOT_OBJECT")

    if set(obj.keys()) - ALLOWED_TOP_LEVEL:
        return ("FAIL_CLOSED", None, "ERR_UNKNOWN_FIELD")

    for k in ("spec_version", "event_type", "payload"):
        if k not in obj:
            return ("FAIL_CLOSED", None, "ERR_MISSING_REQUIRED_FIELD")

    if not isinstance(obj["spec_version"], str) or not isinstance(obj["event_type"], str):
        return ("FAIL_CLOSED", None, "ERR_TYPE")

    return ("PASS", obj, "")

def canonicalize(x):
    if isinstance(x, dict):
        return {k: canonicalize(x[k]) for k in sorted(x.keys())}
    if isinstance(x, list):
        return [canonicalize(v) for v in x]
    if isinstance(x, str):
        return unicodedata.normalize("NFC", x)
    return x

def scope_hash_sha256(event_obj) -> str:
    can = canonicalize(event_obj)
    s = json.dumps(can, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main() -> int:
    ok = 0
    bad = 0

    for name, (exp_outcome, exp_hash, exp_err) in EXPECTED.items():
        p = FIX / name
        if not p.exists():
            print(f"[FAIL] missing: {p}")
            bad += 1
            continue

        raw = p.read_text(encoding="utf-8")
        outcome, obj, err = parse_event_fail_closed(raw)

        if outcome != exp_outcome:
            print(f"[FAIL] {name}: outcome={outcome} expected={exp_outcome} err={err}")
            bad += 1
            continue

        if outcome == "PASS":
            h = scope_hash_sha256(obj)
            if h != exp_hash:
                print(f"[FAIL] {name}: hash={h} expected={exp_hash}")
                bad += 1
            else:
                print(f"[OK]   {name}: PASS hash={h}")
                ok += 1
        else:
            if err != exp_err:
                print(f"[FAIL] {name}: err={err} expected={exp_err}")
                bad += 1
            else:
                print(f"[OK]   {name}: FAIL_CLOSED err={err}")
                ok += 1

    print(f"\nSummary: ok={ok} bad={bad}")
    return 0 if bad == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
