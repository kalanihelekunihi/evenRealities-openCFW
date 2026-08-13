#!/usr/bin/env python3
"""Fail-closed audit for the two linked G2 Cordio WSF string helpers."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

REVERSE_COPY = (0x0056D8C4, 0x0056D8F0, "249d9f2b812108c61c554f67936ae7cd01ac1029b475f21deb49f55cf27e6b94")
REVERSE = (0x0056D8F0, 0x0056D93A, "dd319dbd967e39a1da26a2e1393cc42aed30fcc0a96b4e43c326490b801e20a7")
AGGREGATE_SHA256 = "61177a461ed16699f591cd6a4052af43503cba745d3daf8665c4f9213a73cef2"
MATRIX_MANIFEST = ROOT / "research/readiness/wstr/SHA256SUMS"

REVERSE_COPY_CALLERS = [
    0x005363BE, 0x005363C8, 0x005366F0, 0x005366FE, 0x0053672A,
    0x005367A8, 0x005367B4, 0x0056D022, 0x0056D034, 0x0056D088,
    0x0056D0DC, 0x0056D130, 0x005E26B2, 0x005E26C4, 0x005E26E4,
    0x005E26F6, 0x005E2736, 0x005E2748, 0x005E2768, 0x005E277A,
    0x005E2B80, 0x005E2B90, 0x005E2FF8, 0x005E34DE, 0x005E351C,
    0x005E359A, 0x005E35AA, 0x005E35FA, 0x005E3652, 0x005E37A4,
    0x005E37CC, 0x005E3DB8, 0x005E3DC8, 0x005E3E66, 0x005E3EA8,
    0x005E3F58, 0x005E401A, 0x005E40FA, 0x005E4138,
]
REVERSE_CALLERS = [0x00534D8A, 0x005362AA]

PINNED_INPUTS = {
    ROOT / "components/shared/cordio/runtime_cordio_wstr_candidate.c": "f535a0cc5d1ddc94ad8a6eaf31264140523071dd59f89500adaa0cf9f19e665b",
    ROOT / "components/shared/cordio/runtime_cordio_wstr_candidate.h": "50f7ac6408223869df5476beb919edcd6cee6433fef6d707bd85478a0da2be96",
    ROOT / "tools/manifests/cordio-wstr-provenance.tsv": "6a633ceaab0b7d589eb28530433af3eb7417d0c9058a3d44bda2080f61500a5f",
    ROOT / "tools/manifests/cordio-wstr-function-map.tsv": "080cc1d9857ecd1a9fe8afb2547ef8c7abb7ca97035431399dea8dc9a5008750",
    MATRIX_MANIFEST: "50e389afa187f8e8ae1bdd2b53a115b9c6df2eec294988a0dc3e041aae586c48",
}


class AuditError(RuntimeError):
    """Raised when closed WSF string-helper evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("wsf_wstr_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _callers(blob: bytes, decoder: Any, target: int) -> list[int]:
    return [
        address
        for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2)
        if decoder._thumb_bl_target(blob, address) == target
    ]


def _verify_no_stored_pointers(blob: bytes) -> None:
    targets = {
        address | thumb
        for start, end, _ in (REVERSE_COPY, REVERSE)
        for address in range(start, end, 2)
        for thumb in (0, 1)
    }
    for offset in range(0, len(blob) - 3):
        if struct.unpack_from("<I", blob, offset)[0] in targets:
            raise AuditError(
                f"unexpected stored WSF string-helper pointer at 0x{LOAD_BASE + offset:08x}"
            )


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned WSF string-helper input changed: {path.name}")
    for start, end, expected in (REVERSE_COPY, REVERSE):
        if _sha256(_slice(blob, start, end)) != expected:
            raise AuditError(f"WSF string-helper stock span changed at 0x{start:08x}")
    if _sha256(_slice(blob, REVERSE_COPY[0], REVERSE[1])) != AGGREGATE_SHA256:
        raise AuditError("WSF string-helper aggregate changed")

    decoder = _load_decoder()
    callers = {
        "WStrReverseCpy": _callers(blob, decoder, REVERSE_COPY[0]),
        "WStrReverse": _callers(blob, decoder, REVERSE[0]),
    }
    if callers["WStrReverseCpy"] != REVERSE_COPY_CALLERS:
        raise AuditError("WStrReverseCpy direct caller closure changed")
    if callers["WStrReverse"] != REVERSE_CALLERS:
        raise AuditError("WStrReverse direct caller closure changed")
    _verify_no_stored_pointers(blob)

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": REVERSE_COPY[0], "end_exclusive": REVERSE[1],
            "size": REVERSE[1] - REVERSE_COPY[0], "sha256": AGGREGATE_SHA256,
            "functions": [
                {"name": "WStrReverseCpy", "start": REVERSE_COPY[0], "end_exclusive": REVERSE_COPY[1], "size": 44, "sha256": REVERSE_COPY[2], "direct_bl_callers": callers["WStrReverseCpy"], "direct_callees": []},
                {"name": "WStrReverse", "start": REVERSE[0], "end_exclusive": REVERSE[1], "size": 74, "sha256": REVERSE[2], "direct_bl_callers": callers["WStrReverse"], "direct_callees": []},
            ],
            "stored_entry_or_interior_pointers": 0,
            "external_interior_branches": 0,
        },
        "lineage": {
            "exact_public_definition_route": "Packetcraft Apache-2.0 r19.02 through r20.05c",
            "ambiq_source_family": "R2.4.2 through at least R4.4.1",
            "release_discriminator": False,
            "proprietary_source_copied": False,
        },
        "source_inventory": {
            "linked": ["WStrReverseCpy", "WStrReverse"],
            "dead_stripped": ["WstrnCpy"],
            "dead_strip_reason": "all upstream WstrnCpy consumers are in absent WDXS",
        },
        "candidate": {
            "production": "excluded", "functions": 2, "stock_bytes": 118,
        },
        "compiler_matrix": {
            "archive": str(MATRIX_MANIFEST),
            "archive_sha256": PINNED_INPUTS[MATRIX_MANIFEST],
            "compiler_profiles": 13,
            "comparison_rows": 26,
            "linked_unresolved_symbols": 0,
            "raw_matches": 0,
            "strict_normalized_matches": 0,
            "best_common_profile": "O1",
            "best_common_absolute_size_delta": 10,
            "wall_seconds": 2.152592560,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("WSF wstr audit: 2 functions / 118 bytes, 39+2 direct callers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
