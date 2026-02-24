#!/usr/bin/env python3
# MDAB v0.1 — Telemetry Chain Verifier (CTS runner, fail-fast)
#
# Profiles:
#   core   : schema + decision_hash checks
#   audit  : core + event_hash + chain + checkpoint verification
#   ha     : audit + ed25519 signature + key validity (signature required)
#
# Exit codes:
#   0 PASS
#   1 FAIL (verification error)
#   2 FAIL (usage / IO)

import argparse
import base64
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class DuplicateKeyError(Exception):
    pass


def fail(code: str, line_no: int, detail: str = "") -> int:
    if detail:
        print("=== RESULT: FAIL ===")
        print(f"[FAIL] line={line_no} {code} ({detail})")
    else:
        print("=== RESULT: FAIL ===")
        print(f"[FAIL] line={line_no} {code}")
    return 1


def loads_strict(s: str) -> Any:
    # Reject duplicate keys using object_pairs_hook.
    def hook(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise DuplicateKeyError(k)
            obj[k] = v
        return obj

    return json.loads(s, object_pairs_hook=hook)


def canon(obj: Any) -> str:
    # JCS-like canonical JSON serialization
    return json.dumps(
        obj,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_prefixed_from_canon(obj: Any) -> str:
    return "sha256:" + sha256_hex(canon(obj).encode("utf-8"))


def parse_ts_utc(s: str) -> datetime:
    if not s.endswith("Z"):
        raise ValueError("timestamp must end with Z")
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def contains_float(x: Any) -> bool:
    if isinstance(x, float):
        return True
    if isinstance(x, dict):
        return any(contains_float(v) for v in x.values())
    if isinstance(x, list):
        return any(contains_float(v) for v in x)
    return False


def validate_int_ranges(x: Any) -> None:
    # Reject bools (subclass of int) and enforce int64 for all integers encountered.
    if isinstance(x, bool):
        raise ValueError("bool-forbidden")
    if isinstance(x, int):
        if x < -(2**63) or x > (2**63 - 1):
            raise ValueError("int64-out-of-range")
    elif isinstance(x, dict):
        for v in x.values():
            validate_int_ranges(v)
    elif isinstance(x, list):
        for v in x:
            validate_int_ranges(v)


@dataclass
class KeyInfo:
    key_id: str
    alg: str
    pub: Ed25519PublicKey
    not_before: datetime
    not_after: datetime
    status: str
    revoked_at: Optional[datetime]


def load_key_bundle(path: Path) -> Dict[str, KeyInfo]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("version") != "MDAB-KEYS-0.1":
        raise ValueError("bad key bundle version")

    revoked_map: Dict[str, datetime] = {}
    for r in (doc.get("revocations", []) or []):
        revoked_map[r["key_id"]] = parse_ts_utc(r["revoked_at_utc"])

    out: Dict[str, KeyInfo] = {}
    for k in (doc.get("keys", []) or []):
        key_id = k["key_id"]
        alg = k["alg"]
        pub_b64 = k["public_key_b64"]
        pub_bytes = base64.b64decode(pub_b64)
        pub = Ed25519PublicKey.from_public_bytes(pub_bytes)

        nb = parse_ts_utc(k["not_before_utc"])
        na = parse_ts_utc(k["not_after_utc"])
        status = k["status"]
        revoked_at = revoked_map.get(key_id)

        out[key_id] = KeyInfo(
            key_id=key_id,
            alg=alg,
            pub=pub,
            not_before=nb,
            not_after=na,
            status=status,
            revoked_at=revoked_at,
        )
    return out


def build_registry(schema_dir: Path) -> Registry:
    registry = Registry()
    for p in schema_dir.glob("*.schema.json"):
        schema = json.loads(p.read_text(encoding="utf-8"))
        sid = schema.get("$id")
        if sid:
            registry = registry.with_resource(sid, Resource.from_contents(schema))
    return registry


def load_schema(schema_dir: Path, name: str) -> Dict[str, Any]:
    return json.loads((schema_dir / name).read_text(encoding="utf-8"))


def schema_error(validator: Draft202012Validator, instance: Any) -> Optional[str]:
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if not errors:
        return None
    e = errors[0]
    path = ".".join([str(p) for p in e.path])
    return f"{path}: {e.message}" if path else e.message


def verify_signature(ev: Dict[str, Any], keyinfo: KeyInfo, ts: datetime) -> Optional[str]:
    sig = ev.get("signature")
    if not isinstance(sig, dict):
        return "E_SIG_MISSING"

    if sig.get("alg") != "ed25519":
        return "E_SIG_INVALID"

    if keyinfo.status != "ACTIVE":
        return "E_KEY_REVOKED"

    if ts < keyinfo.not_before or ts > keyinfo.not_after:
        return "E_KEY_EXPIRED"

    if keyinfo.revoked_at is not None and ts >= keyinfo.revoked_at:
        return "E_KEY_REVOKED"

    eh = ev.get("event_hash", "")
    if not isinstance(eh, str) or not eh.startswith("sha256:"):
        return "E_HASH_MISMATCH"

    digest_bytes = bytes.fromhex(eh.split("sha256:", 1)[1])
    try:
        sig_bytes = base64.b64decode(sig.get("sig_b64", ""))
        keyinfo.pub.verify(sig_bytes, digest_bytes)
        return None
    except Exception:
        return "E_SIG_INVALID"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=["core", "audit", "ha"], default="audit")
    ap.add_argument("--keys", default="keys/verifier_keys.json")
    ap.add_argument("stream", type=str)
    args = ap.parse_args()

    profile = args.profile
    stream_path = Path(args.stream)

    root = Path(__file__).resolve().parents[1]
    schema_dir = root / "schemas"
    keys_path = root / args.keys

    # Validators
    registry = build_registry(schema_dir)

    dec_schema = load_schema(schema_dir, "decision_event.ha.schema.json" if profile == "ha" else "decision_event.schema.json")
    chk_schema = load_schema(schema_dir, "checkpoint_event.ha.schema.json" if profile == "ha" else "checkpoint_event.schema.json")

    dec_val = Draft202012Validator(dec_schema, registry=registry)
    chk_val = Draft202012Validator(chk_schema, registry=registry)

    # Keys
    keys = None
    if profile == "ha":
        try:
            keys = load_key_bundle(keys_path)
        except Exception as e:
            print(f"[FAIL] key bundle load error: {e}")
            return 2

    # Per-emitter state: expected seq + prev hash, and decision hashes for checkpoints
    state: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
    dec_hashes: Dict[Tuple[str, str, str, str], Dict[int, str]] = {}

    try:
        lines = [l for l in stream_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    except Exception as e:
        print(f"[FAIL] IO_ERROR: {e}")
        return 2

    for line_no, line in enumerate(lines, start=1):
        # Parse strict
        try:
            ev = loads_strict(line)
        except DuplicateKeyError:
            return fail("E_DUPLICATE_KEY", line_no)
        except Exception:
            return fail("E_PARSE_ERROR", line_no)

        # Numeric policy
        if contains_float(ev):
            return fail("E_FLOAT_FORBIDDEN", line_no)
        try:
            validate_int_ranges(ev)
        except Exception:
            return fail("E_INT_RANGE", line_no)

        etype = ev.get("event_type")
        if etype not in ("DECISION", "CHECKPOINT"):
            return fail("E_SCHEMA_INVALID", line_no)

        # Schema validation
        msg = schema_error(dec_val if etype == "DECISION" else chk_val, ev)
        if msg is not None:
            return fail("E_SCHEMA_INVALID", line_no, msg)

        # decision_hash check (DECISION)
        if etype == "DECISION":
            dc = ev["decision"]["decision_core"]
            calc_dh = sha256_prefixed_from_canon(dc)
            got = ev["decision"].get("decision_hash")
            # optional alias support
            if got is None and "decision_digest" in ev["decision"]:
                got = ev["decision"]["decision_digest"]
            if got != calc_dh:
                return fail("E_DECISION_HASH_MISMATCH", line_no)

        # event_hash + chain + checkpoint (AUDIT/HA)
        emitter = ev["emitter"]
        ek = (emitter["service"], emitter["instance_id"], emitter["env"], emitter["region"])

        if ek not in state:
            state[ek] = {"expected_seq": 0, "prev_hash": None}
            dec_hashes[ek] = {}

        if profile in ("audit", "ha"):
            # event_hash
            core = dict(ev)
            core.pop("event_hash", None)
            core.pop("signature", None)
            calc_eh = sha256_prefixed_from_canon(core)
            if ev["event_hash"] != calc_eh:
                return fail("E_HASH_MISMATCH", line_no)

            # chain
            st = state[ek]
            seq = ev["seq"]
            prev = ev["prev_event_hash"]

            exp_seq = st["expected_seq"]
            if seq < exp_seq:
                return fail("E_SEQ_NON_MONOTONIC", line_no)
            if seq > exp_seq:
                return fail("E_SEQ_GAP", line_no)

            exp_prev = st["prev_hash"]
            if exp_seq == 0:
                if prev is not None:
                    return fail("E_CHAIN_BREAK", line_no)
            else:
                if prev != exp_prev:
                    return fail("E_CHAIN_BREAK", line_no)

            st["expected_seq"] = exp_seq + 1
            st["prev_hash"] = ev["event_hash"]

            # store decision event hashes
            if etype == "DECISION":
                dec_hashes[ek][seq] = ev["event_hash"]

            # checkpoint verify
            if etype == "CHECKPOINT":
                cp = ev["checkpoint"]
                start = cp["range_start_seq"]
                end = cp["range_end_seq"]
                if start > end:
                    return fail("E_BLOCKHASH_MISMATCH", line_no)

                # gather hashes
                hashes: List[str] = []
                for s in range(start, end + 1):
                    if s not in dec_hashes[ek]:
                        return fail("E_BLOCKHASH_MISMATCH", line_no)
                    hashes.append(dec_hashes[ek][s])

                material = "MDAB-BLOCK-0.1\n" + "\n".join(hashes) + "\n"
                calc_bh = "sha256:" + sha256_hex(material.encode("utf-8"))
                if cp["block_hash"] != calc_bh:
                    return fail("E_BLOCKHASH_MISMATCH", line_no)
                if cp["last_event_hash"] != hashes[-1]:
                    return fail("E_BLOCKHASH_MISMATCH", line_no)

        # signature (HA, or if present)
        sig_present = "signature" in ev
        if profile == "ha" or sig_present:
            if keys is None:
                try:
                    keys = load_key_bundle(keys_path)
                except Exception:
                    return fail("E_KEY_UNKNOWN", line_no)

            sig = ev.get("signature")
            key_id = sig.get("key_id") if isinstance(sig, dict) else None
            if key_id not in keys:
                return fail("E_KEY_UNKNOWN", line_no)

            ts = parse_ts_utc(ev["ts_utc"])
            code = verify_signature(ev, keys[key_id], ts)
            if code is not None:
                return fail(code, line_no)

    print("=== RESULT: PASS ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
