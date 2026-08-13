#!/usr/bin/env python3
"""Fail-closed boundary and ingress audit for confirmed G2 IAR runtime code."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x0043_7FE0

SPANS = (
    ("__aeabi_memmove", 0x0043_9710, 0x0043_97A6, "31caf15ad676c4a99eace5673e1fe46b818b64d901707c461074e8acc5474b28"),
    ("sqrtf", 0x0043_97A8, 0x0043_97C4, "f7003725d19bfa0d3c7727692b5c7016e23a9f109d5d799dcde22e11ac1f7dd8"),
    ("__aeabi_memcpy", 0x0043_9BE4, 0x0043_9C8A, "8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd"),
    ("domain_error_setter", 0x0043_9CA4, 0x0043_9CB2, "c8f0b7b877865ce0f05883d06ee187d144d96194bffe3bf1acdd06487da88d21"),
    ("range_error_setter", 0x0043_9CB2, 0x0043_9CC4, "49f0244f79bf9886dcc3c9fdae846695936595a3215241bf8172c7c6e20cac6f"),
    ("errno_address", 0x0043_9CC4, 0x0043_9CD0, "7b7994948ecea72e56a7893548fddcd9b681182c1bb4c7df5926ee7185d11f83"),
    ("runtime_literals", 0x0043_9CD0, 0x0043_9CE0, "0d441527b2ae7b59077c4bf26520f57704ef2c60c91719c900279c3f3fcfc222"),
)

# Count and SHA-256 of sorted little-endian caller addresses.  This keeps the
# 790-entry memcpy topology fail-closed without embedding a noisy address list.
INGRESS = {
    (0x0043_9710, "bl"): (12, "a3650e0944f51e2216357bcf8aceaee7ce3308f63a7e0bc8377d03d39839196b"),
    (0x0043_97A8, "bl"): (68, "b6bbb3a5e38098347f11a79bd308bb424a52dae9f55a1d5b3c4b6db1a3fc2de1"),
    (0x0043_9BE4, "bl"): (790, "57c4b4ee9b87378cbf17bd1e3241d0953fff6058540f1eee968218aa70341c0e"),
    (0x0043_9BE4, "bw"): (1, "d9fef51d9409daf2defc0a66d246d5bba18fa8cfe307e12b55a8be31f6863165"),
    (0x0043_9CA4, "bw"): (2, "50f4cd724d4a28d6b6a97ae5d8561371ee66e011c0c6a8522df3860108732e89"),
    (0x0043_9CB2, "bl"): (6, "b9ea2b26794cdc23d9e4f08bfb6cdab0787b703493c6d0be464b064135c4c9a8"),
    (0x0043_9CB2, "bw"): (2, "edf5f12505fe0599504bd18e9ef7bb4444e3a5c1ad6ae5d584f70e827ff62864"),
    (0x0043_9CC4, "bl"): (29, "31421e39d5c150df27f3c5134014bec1bd14d93d21b38b7c967927057868e8b9"),
}
INTERNAL_INGRESS = {
    (0x0043_9C04, "bl"): (597, "150840e78264efb86706a5f10f436ecce01a2226bcf3b15d48b03b443e0058ad"),
}

# Three independent application build banners.  The date/time fields occupy
# fixed 12-byte slots in the stock string table and were produced within 22
# seconds of one another.  They are stronger temporal evidence than the
# unrelated 2025 component-version string elsewhere in the image.
BUILD_BANNERS = (
    (0x0078_A3AC, "Jul  6 2026", "21:37:47"),
    (0x0078_B594, "Jul  6 2026", "21:37:52"),
    (0x0078_B984, "Jul  6 2026", "21:37:30"),
)


class AuditError(RuntimeError):
    """Raised when an authenticated compiler-runtime invariant changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def wide_branch_target(address: int, first: int, second: int, *, link: bool) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        sign << 24
        | (1 ^ (j1 ^ sign)) << 23
        | (1 ^ (j2 ^ sign)) << 22
        | (first & 0x03FF) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def scan_ingress(blob: bytes) -> dict[tuple[int, str], tuple[int, str]]:
    wanted = {key for key in INGRESS} | {key for key in INTERNAL_INGRESS}
    found: dict[tuple[int, str], list[int]] = {key: [] for key in wanted}
    for offset in range(0, len(blob) - 3, 2):
        address = LOAD_BASE + offset
        first, second = struct.unpack_from("<HH", blob, offset)
        for kind, link in (("bl", True), ("bw", False)):
            target = wide_branch_target(address, first, second, link=link)
            key = (target, kind)
            if key in found:
                found[key].append(address)
    return {
        key: (len(addresses), sha256(b"".join(a.to_bytes(4, "little") for a in addresses)))
        for key, addresses in found.items()
    }


def analyze(image: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo-main image identity mismatch")

    segments = []
    for name, start, end, digest in SPANS:
        body = image_slice(blob, start, end)
        if sha256(body) != digest:
            raise AuditError(f"{name} boundary changed")
        if name == "runtime_literals":
            state = "classified_retained_data"
        else:
            state = "source_recreated_redirected"
        segments.append({
            "name": name,
            "start": start,
            "end": end,
            "size": len(body),
            "sha256": digest,
            "state": state,
        })

    observed = scan_ingress(blob)
    expected = {**INGRESS, **INTERNAL_INGRESS}
    if observed != expected:
        raise AuditError(f"runtime ingress topology changed: {observed!r}")

    literal_words = struct.unpack("<IIII", image_slice(blob, 0x0043_9CD0, 0x0043_9CE0))
    if literal_words != (0, 0x2007_4F14, 0x2007_4F14, 0):
        raise AuditError("errno literal island changed")
    if image_slice(blob, 0x0043_97A8, 0x0043_97B8).hex() != "b5eec00af1ee10fa02d4b1eec00a7047":
        raise AuditError("sqrtf VFP fast path changed")
    if image_slice(blob, 0x0043_9CAA, 0x0043_9CC0).hex() != "c0460949212205e00fb581b00020c046064922224250":
        raise AuditError("EDOM/ERANGE setter seam changed")

    build_banners = []
    for address, expected_date, expected_time in BUILD_BANNERS:
        observed_date = image_slice(blob, address, address + 12).rstrip(b"\0").decode("ascii")
        observed_time = image_slice(blob, address + 12, address + 24).rstrip(b"\0").decode("ascii")
        if (observed_date, observed_time) != (expected_date, expected_time):
            raise AuditError(f"application build banner changed at 0x{address:08X}")
        build_banners.append({
            "address": address,
            "date": observed_date,
            "time": observed_time,
        })

    def ingress_record(key: tuple[int, str], value: tuple[int, str]) -> dict[str, Any]:
        return {
            "target": key[0],
            "kind": key[1],
            "count": value[0],
            "caller_address_sha256": value[1],
        }

    return {
        "identity": {
            "toolchain_family": "IAR DLIB/compiler runtime",
            "exact_release_proven": False,
            "release_hypothesis": "EWARM 9.20+ practical Cortex-M55 floor; 9.60.2 leading compatibility candidate; exact release unknown",
            "archive_comparison_priority": ("9.60.2", "9.60.3", "9.70.x", "9.50.x"),
            "archive_family_hypotheses": {
                "math": "m7M_tl{v|s}.a",
                "runtime": "rt7M_tl.a",
                "dlib_c": "dl7M_tl{n|f}.a",
            },
            "unresolved_options": ("full_vs_single_precision_vfp", "normal_vs_full_dlib"),
            "errno_address": 0x2007_4F14,
        },
        "application_build_banners": build_banners,
        "segments": segments,
        "ingress": [ingress_record(key, value) for key, value in sorted(INGRESS.items())],
        "interior_entries": [
            {
                "name": "__aeabi_memcpy_aligned",
                **ingress_record(key, value),
            }
            for key, value in sorted(INTERNAL_INGRESS.items())
        ],
        "recovery": {
            "confirmed_runtime_code_units": 10,
            "source_recreated_units": 10,
            "production_integrated_units": 10,
            "retained_runtime_code_units": 0,
            "retained_units_with_qualified_source_candidates": 0,
            "retained_runtime_code_bytes": 0,
            "classified_runtime_literal_bytes": 16,
            "known_unit_boundary_abi_percent": 100,
            "estimated_broader_runtime_identification_percent": "40-50",
            "production_integration_percent_for_new_six": 100,
        },
        "readiness_confirmation": {
            "ghidra": "12.1.2",
            "jdk": "21.0.12",
            "shards": 16,
            "candidate_entries": 35,
            "result_root": "/var/tmp/opencfw-iar-runtime-JDR5ne",
            "note": "raw byte and ingress facts are reproduced locally; remote project/log paths are not provenance",
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("G2 IAR runtime census: PASS")
        print(json.dumps(report["recovery"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
