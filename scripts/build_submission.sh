#!/usr/bin/env bash
set -euo pipefail

# build_submission.sh
# Builds a standard-grade submission bundle from the repo:
#  - creates dist/<BUNDLE_DIR>/ with selected artifacts
#  - generates SHA256SUMS.txt (for files inside the bundle)
#  - produces a deterministic ZIP (stable ordering + fixed timestamps)
#  - generates ZIP .sha256
#  - writes DAY_CLOSE_YYYYMMDD.txt into dist/PROOF (external proof summary)

# Usage:
#   ./scripts/build_submission.sh [v0.1.0]
# Env overrides:
#   VERSION, DOI, ZENODO_RECORD_URL, RELEASE_URL, TRACKING_NUMBER

VERSION="${1:-${VERSION:-v0.1.0}}"

DOI="${DOI:-10.5281/zenodo.18763066}"
ZENODO_RECORD_URL="${ZENODO_RECORD_URL:-https://zenodo.org/records/18763066}"
RELEASE_URL="${RELEASE_URL:-https://github.com/fazoncore/mdab-tel-cts/releases/tag/${VERSION}}"

# Try to detect repo root
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# Build UTC date stamp
DATE_UTC="$(date -u +%Y%m%d 2>/dev/null || python3 - <<'PY'
import datetime
print(datetime.datetime.utcnow().strftime("%Y%m%d"))
PY
)"

# Git metadata (best-effort)
GIT_COMMIT="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo "unknown")"
GIT_ORIGIN="$(git -C "$ROOT" config --get remote.origin.url 2>/dev/null || echo "unknown")"
GIT_DESCRIBE="$(git -C "$ROOT" describe --tags --dirty --always 2>/dev/null || echo "unknown")"

# Tracking number: env > file > empty
TRACKING_NUMBER="${TRACKING_NUMBER:-}"
if [[ -z "${TRACKING_NUMBER}" && -f "$ROOT/TRACKING_NUMBER.txt" ]]; then
  TRACKING_NUMBER="$(tr -d '\r\n' < "$ROOT/TRACKING_NUMBER.txt" || true)"
fi

BASENAME="MDAB-TEL_${VERSION#v}_submission_${DATE_UTC}"
DIST_DIR="$ROOT/dist"
OUTDIR="$DIST_DIR/$BASENAME"
PROOF_DIR="$DIST_DIR/PROOF"
ARCHIVE_ZIP="$DIST_DIR/${BASENAME}.zip"
ARCHIVE_SHA="$ARCHIVE_ZIP.sha256"

mkdir -p "$DIST_DIR"
rm -rf "$OUTDIR"
mkdir -p "$OUTDIR"

# Helper: copy if exists
copy_path () {
  local src="$1"
  local dst="$2"
  if [[ -e "$src" ]]; then
    mkdir -p "$(dirname "$dst")"
    # shellcheck disable=SC2086
    cp -R "$src" "$dst"
  fi
}

cd "$ROOT"

# ---- Required top-level docs (copy only if present) ----
copy_path "$ROOT/README.md"              "$OUTDIR/README.md"
copy_path "$ROOT/SPEC.md"                "$OUTDIR/SPEC.md"
copy_path "$ROOT/REPRODUCIBILITY.md"     "$OUTDIR/REPRODUCIBILITY.md"
copy_path "$ROOT/NON_GOALS_v0.1.md"      "$OUTDIR/NON_GOALS_v0.1.md"
copy_path "$ROOT/RELEASE.md"             "$OUTDIR/RELEASE.md"
copy_path "$ROOT/MANIFEST.md"            "$OUTDIR/MANIFEST.md"
copy_path "$ROOT/SECURITY.md"            "$OUTDIR/SECURITY.md"
copy_path "$ROOT/CONTRIBUTING.md"        "$OUTDIR/CONTRIBUTING.md"
copy_path "$ROOT/LICENSE"                "$OUTDIR/LICENSE"
copy_path "$ROOT/NOTICE"                 "$OUTDIR/NOTICE"
copy_path "$ROOT/CITATION.cff"           "$OUTDIR/CITATION.cff"

# ---- Core repo folders ----
copy_path "$ROOT/appendix"               "$OUTDIR/appendix"
copy_path "$ROOT/telemetry_cts"          "$OUTDIR/telemetry_cts"

# ---- Standardization packet (optional) ----
copy_path "$ROOT/docs/standardization"   "$OUTDIR/docs/standardization"

# ---- Issue templates / workflows are optional; keep out of submission by default ----
# copy_path "$ROOT/.github"              "$OUTDIR/.github"

# ---- Scripts (include so auditors can reproduce packaging) ----
copy_path "$ROOT/scripts"                "$OUTDIR/scripts"

# ---- Add minimal evidence metadata file ----
cat > "$OUTDIR/EVIDENCE_BUNDLE.md" <<EOF
# Evidence bundle (submission)

- Bundle: ${BASENAME}
- Version: ${VERSION}
- Built (UTC): ${DATE_UTC}

## Immutable references
- Git origin: ${GIT_ORIGIN}
- Git commit: ${GIT_COMMIT}
- Git describe: ${GIT_DESCRIBE}
- GitHub release: ${RELEASE_URL}

## Archive reference
- Zenodo record: ${ZENODO_RECORD_URL}
- DOI: ${DOI}

## Verification
1) Verify bundle file integrity:
   - use SHA256SUMS.txt (included)
2) Run reproducibility commands:
   - see REPRODUCIBILITY.md (included)
EOF

# ---- Generate SHA256SUMS.txt for ALL files inside OUTDIR ----
python3 - <<'PY' "$OUTDIR"
import hashlib, pathlib, sys

root = pathlib.Path(sys.argv[1])
out = root / "SHA256SUMS.txt"

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

files = sorted([p for p in root.rglob("*") if p.is_file() and p.name != "SHA256SUMS.txt"])
with out.open("w", newline="\n") as f:
    for p in files:
        rel = p.relative_to(root).as_posix()
        f.write(f"{sha256_file(p)}  {rel}\n")
PY

# ---- Build deterministic ZIP (stable ordering + fixed timestamps) ----
rm -f "$ARCHIVE_ZIP" "$ARCHIVE_SHA"

python3 - <<'PY' "$OUTDIR" "$ARCHIVE_ZIP"
import pathlib, zipfile, sys

src = pathlib.Path(sys.argv[1])
zip_path = pathlib.Path(sys.argv[2])

# Fixed timestamp to avoid machine-dependent mtimes
FIXED_DT = (2026, 2, 24, 0, 0, 0)

files = sorted([p for p in src.rglob("*") if p.is_file()])

with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for p in files:
        rel = p.relative_to(src).as_posix()
        data = p.read_bytes()
        info = zipfile.ZipInfo(rel, date_time=FIXED_DT)
        info.compress_type = zipfile.ZIP_DEFLATED
        # -rw-r--r--
        info.external_attr = (0o644 << 16)
        z.writestr(info, data)
PY

# ---- Compute ZIP sha256 ----
python3 - <<'PY' "$ARCHIVE_ZIP" "$ARCHIVE_SHA"
import hashlib, os, pathlib, sys

p = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])

h = hashlib.sha256()
with p.open("rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
        h.update(chunk)

out.write_text(f"{h.hexdigest()}  {p.name}\n", newline="\n")
print(h.hexdigest())
PY

ZIP_SHA256="$(cut -d' ' -f1 < "$ARCHIVE_SHA" | tr -d '\r\n')"

# ---- DAY_CLOSE proof summary (external; not inside the ZIP) ----
mkdir -p "$PROOF_DIR"
DAY_CLOSE_FILE="$PROOF_DIR/DAY_CLOSE_${DATE_UTC}.txt"

cat > "$DAY_CLOSE_FILE" <<EOF
DAY_CLOSE ${DATE_UTC} (UTC)

TRACKING_NUMBER: ${TRACKING_NUMBER:-<none>}
VERSION: ${VERSION}

GIT_ORIGIN: ${GIT_ORIGIN}
GIT_COMMIT: ${GIT_COMMIT}
GIT_DESCRIBE: ${GIT_DESCRIBE}

GITHUB_RELEASE: ${RELEASE_URL}

ZENODO_RECORD: ${ZENODO_RECORD_URL}
DOI: ${DOI}

SUBMISSION_ZIP: $(basename "$ARCHIVE_ZIP")
SUBMISSION_ZIP_SHA256: ${ZIP_SHA256}

NOTE: Bundle internal checksums are in SHA256SUMS.txt inside the ZIP.
EOF

echo ""
echo "OK"
echo "Bundle dir:   $OUTDIR"
echo "ZIP:         $ARCHIVE_ZIP"
echo "ZIP sha256:  $ARCHIVE_SHA"
echo "DAY_CLOSE:   $DAY_CLOSE_FILE"
