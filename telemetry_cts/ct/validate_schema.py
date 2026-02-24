#!/usr/bin/env python3
# MDAB v0.1 — Schema validation helper (CTS)
#
# Validates that:
#  1) local schemas can be loaded and referenced
#  2) fixtures which are intended to be schema-valid validate against their schema
#
# Note:
#  - parse-level negative fixtures (duplicate keys) are expected to fail strict parsing
#  - numeric-policy negative fixtures (floats) are expected to fail before schema
# Therefore, those are skipped here and exercised via ct/run_chain_verifier.py.

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
FIX = ROOT / "fixtures" / "tel"

SKIP_FILES = {
    "tel-stream-dupkeys.jsonl",
    "tel-stream-float.jsonl",
}

def build_registry(schema_dir: Path) -> Registry:
    registry = Registry()
    for p in schema_dir.glob("*.schema.json"):
        schema = json.loads(p.read_text(encoding="utf-8"))
        sid = schema.get("$id")
        if sid:
            registry = registry.with_resource(sid, Resource.from_contents(schema))
    return registry


def load_schema(name: str):
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def validate_one(schema, registry, instance):
    v = Draft202012Validator(schema, registry=registry)
    errs = sorted(v.iter_errors(instance), key=lambda e: e.path)
    if errs:
        e = errs[0]
        path = ".".join([str(p) for p in e.path])
        msg = f"{path}: {e.message}" if path else e.message
        return False, msg
    return True, ""


def main() -> int:
    registry = build_registry(SCHEMAS)

    dec = load_schema("decision_event.schema.json")
    chk = load_schema("checkpoint_event.schema.json")
    dec_ha = load_schema("decision_event.ha.schema.json")
    chk_ha = load_schema("checkpoint_event.ha.schema.json")

    failures = 0

    for fp in sorted(FIX.glob("*.jsonl")):
        if fp.name in SKIP_FILES:
            continue

        lines = [l for l in fp.read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, line in enumerate(lines, start=1):
            obj = json.loads(line)  # non-strict is sufficient for schema check
            et = obj.get("event_type")

            if et == "DECISION":
                ok, msg = validate_one(dec, registry, obj)
                if not ok:
                    print(f"[FAIL] {fp.name}:{i} decision_event.schema.json {msg}")
                    failures += 1
                if "signature" in obj:
                    ok, msg = validate_one(dec_ha, registry, obj)
                    if not ok:
                        print(f"[FAIL] {fp.name}:{i} decision_event.ha.schema.json {msg}")
                        failures += 1

            elif et == "CHECKPOINT":
                ok, msg = validate_one(chk, registry, obj)
                if not ok:
                    print(f"[FAIL] {fp.name}:{i} checkpoint_event.schema.json {msg}")
                    failures += 1
                if "signature" in obj:
                    ok, msg = validate_one(chk_ha, registry, obj)
                    if not ok:
                        print(f"[FAIL] {fp.name}:{i} checkpoint_event.ha.schema.json {msg}")
                        failures += 1

            else:
                print(f"[FAIL] {fp.name}:{i} unknown event_type")
                failures += 1

    if failures == 0:
        print("=== SCHEMA RESULT: PASS ===")
        return 0

    print(f"=== SCHEMA RESULT: FAIL ({failures}) ===")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
