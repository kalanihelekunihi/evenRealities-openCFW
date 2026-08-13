#!/usr/bin/env python3
"""Correlate the complete GR551x SDK 1.7.0 source tree with G2 strings."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
DEFAULT_SDK = Path("/var/tmp/opencfw-goodix-v170/GR551x_SDK_V1.7.0")
SELECTED_COMMIT = "854c43e0b96a24051ffce4c06ff629255aa56c59"
MANIFEST = ROOT / "tools/manifests/goodix-gr551x-v170-firmware-string-overlap.tsv"
MANIFEST_SHA256 = "930c6dd01cfc1f0b54b1ce627abf94e78433343a1b2f467f5488e23d1f629f0d"
SOURCE_PATHS = 2167
UNIQUE_SOURCE_BLOBS = 1681
MIN_LITERAL_LENGTH = 12
MIN_MULTI_HIT = 3
STRING_RE = re.compile(r'(?<![A-Za-z0-9_])("(?:\\.|[^"\\])*")')


class AuditError(RuntimeError):
    """Raised when the selected SDK tree or correlation changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _matching_literals(source: bytes, firmware: bytes) -> set[str]:
    matches: set[str] = set()
    for token in STRING_RE.findall(source.decode("utf-8", "ignore")):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                value = ast.literal_eval(token)
        except (SyntaxError, ValueError):
            continue
        if not isinstance(value, str) or len(value) < MIN_LITERAL_LENGTH:
            continue
        try:
            encoded = value.encode("utf-8")
        except UnicodeEncodeError:
            continue
        if encoded in firmware:
            matches.add(value)
    return matches


def _overlap_digest(matches: set[str]) -> str:
    return _sha256(("\n".join(sorted(matches)) + "\n").encode("utf-8"))


def _git_head(sdk: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(sdk.parent), "rev-parse", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise AuditError(f"cannot authenticate selected SDK checkout: {error}") from error


def analyze(sdk: Path = DEFAULT_SDK, image: Path = IMAGE) -> dict[str, object]:
    firmware = image.read_bytes()
    if _sha256(firmware) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    if not MANIFEST.is_file() or _sha256(MANIFEST.read_bytes()) != MANIFEST_SHA256:
        raise AuditError("source-overlap classification manifest changed")
    if not sdk.is_dir() or _git_head(sdk) != SELECTED_COMMIT:
        raise AuditError("selected GR551x SDK 1.7.0 checkout unavailable or changed")

    paths = sorted(path for path in sdk.rglob("*") if path.suffix.lower() in {".c", ".h"})
    blobs: dict[str, tuple[bytes, list[str]]] = {}
    for path in paths:
        data = path.read_bytes()
        digest = _sha256(data)
        if digest not in blobs:
            blobs[digest] = (data, [])
        blobs[digest][1].append(str(path.relative_to(sdk)))
    if len(paths) != SOURCE_PATHS or len(blobs) != UNIQUE_SOURCE_BLOBS:
        raise AuditError("complete SDK C/header tree census changed")

    observed: dict[str, dict[str, object]] = {}
    for digest, (data, carriers) in blobs.items():
        matches = _matching_literals(data, firmware)
        if len(matches) >= MIN_MULTI_HIT:
            observed[digest] = {
                "bytes": len(data),
                "source_paths": carriers,
                "matching_literals": len(matches),
                "matching_literal_bytes": sum(map(len, matches)),
                "overlap_digest": _overlap_digest(matches),
            }

    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        expected_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(expected_rows) != 4 or set(observed) != {row["sha256"] for row in expected_rows}:
        raise AuditError(f"multi-string SDK overlap set changed: {set(observed)!r}")
    for row in expected_rows:
        item = observed[row["sha256"]]
        if (
            int(row["bytes"]) != item["bytes"]
            or int(row["matching_literals_ge12"]) != item["matching_literals"]
            or int(row["matching_literal_bytes"]) != item["matching_literal_bytes"]
            or row["overlap_digest"] != item["overlap_digest"]
            or row["source_path"] not in item["source_paths"]
        ):
            raise AuditError(f"source overlap changed for {row['source_path']}")

    util = _load(ROOT / "tools/analyze_g2_util_error_check.py", "goodix_overlap_util").analyze(image)
    cm_module = _load(ROOT / "tools/analyze_g2_cmbacktrace_version.py", "goodix_overlap_cmbacktrace")
    cm = cm_module.audit(firmware)
    nanopb_module = _load(ROOT / "tools/analyze_g2_nanopb_point_release.py", "goodix_overlap_nanopb")
    nanopb = nanopb_module.audit_image(firmware)
    if util["goodix_source_lineage"]["exact_source_snapshot_version"] != "1.7.0":
        raise AuditError("Goodix app_error exact-source result changed")
    if cm["component"] != "armink/CmBacktrace" or cm["identity"]["print_info_entries"] != 39:
        raise AuditError("CmBacktrace collision classification changed")
    if nanopb["discriminators"]["pb_read_saturating_clamp"]["introduced"] != "0.4.7":
        raise AuditError("nanopb lower-bound discriminator changed")

    decode_path = sdk / expected_rows[2]["source_path"]
    decode = decode_path.read_text(encoding="utf-8")
    if (
        "#define NANOPB_VERSION nanopb-0.4.2" not in (decode_path.parent / "pb.h").read_text()
        or "stream->bytes_left -= count;" not in decode
        or "if (stream->bytes_left < count)\n            stream->bytes_left = 0;" in decode
    ):
        raise AuditError("SDK-bundled nanopb 0.4.2 behavior changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only source/string correlation; no signing, flashing, erase, or hardware operation",
        "sdk": {
            "version": "GR551x SDK 1.7.0",
            "selected_public_carrier_commit": SELECTED_COMMIT,
            "c_header_paths": len(paths),
            "unique_source_blobs": len(blobs),
            "multi_string_overlap_blobs": len(observed),
            "literal_threshold": MIN_LITERAL_LENGTH,
            "multi_hit_threshold": MIN_MULTI_HIT,
        },
        "classifications": {
            "new_exact_goodix_source": ["components/libraries/app_error/app_error.c"],
            "known_cmbacktrace_shared_ancestry": ["components/libraries/app_error/cortex_backtrace.c"],
            "known_nanopb_non_discriminating_or_excluded": [
                "projects/ble/ble_peripheral/ble_app_ags/Src/gadgets/script/pb_decode.c",
                "projects/ble/ble_peripheral/ble_app_ags/Src/gadgets/script/pb_encode.c",
            ],
            "new_dependency_families_beyond_goodix_app_error": [],
        },
        "cross_checks": {
            "goodix_app_error_exact_version": "1.7.0",
            "cmbacktrace_stock_print_info_entries": cm["identity"]["print_info_entries"],
            "goodix_cortex_backtrace_exact_stock_source": False,
            "sdk_nanopb_version": "0.4.2",
            "stock_nanopb_pristine_lower_bound": "0.4.7",
            "sdk_nanopb_0_4_2_excluded_by_stock_pb_read": True,
        },
        "overlaps": expected_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", type=Path, default=DEFAULT_SDK)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.sdk_root, args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        sdk = report["sdk"]
        print(
            "G2 / Goodix SDK 1.7.0 source-overlap audit: PASS "
            f"({sdk['unique_source_blobs']} unique source blobs, "
            f"{sdk['multi_string_overlap_blobs']} multi-string overlaps)"
        )
        print("new dependency families beyond the copied app_error utility: 0")
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
