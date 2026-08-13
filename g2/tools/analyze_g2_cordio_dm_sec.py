#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio security manager."""

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
READINESS_MANIFEST = ROOT / "research/readiness/dm-sec/SHA256SUMS"
READINESS_BYTES = 1_288
READINESS_SHA256 = "df7e710c606536b1b18e5a3f4c905543228ff4143d8510d248d58c787bd4b167"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-sec-function-map.tsv": "e2a961f69dd7fd8210005233c15739959b62e9155e54859a03a29d0eb861a18c",
    ROOT / "tools/manifests/packetcraft-cordio-dm-sec-provenance.tsv": "146a9fbac8e20b8c04b05c88c7c0982248bee67ccb116764e7faf509e9fbfc52",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-build-results.tsv": "3cd5b299dc638f3624127852cb74689b0f6b58a316b11e8d09c36426a89125a8",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-closure-results.tsv": "bcc7f6ea6610cfbfde7330ae78d0642e544ec68d8f31e74f54d2411dd646d942",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-include-closure.tsv": "6ccf15ab6bd982c0a64e22139c845e512db2655b8e89d8e29c97875b8a5c4b7b",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-r441-input-identities.tsv": "317175c5bd6536da9744322baf47d22fa1b1e6373f232ab4ad5e4e78b51d6247",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-source-identities.tsv": "f442001ba9f234af239f565cf07289657710bff626f42e198a667aebc1f2b319",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-undefined-providers.tsv": "657d813380f5b04731a073216a161a55afddfea08ed95fbb86cfb6fa73dee00d",
}

FUNCTIONS = {
    "dmSecHciHandler": (0x004D2364, 0x004D2440, "0487ba4b9d4d93d5d414c875b37afcaf6a9fa2628fa6193fa979f282678a1024"),
    "dmSecMsgHandler": (0x004D2440, 0x004D24A8, "e81d46f26d7abdc37bfd9591456c899b262f48cbe9e29b5b103191461d343968"),
    "DmSmpCbackExec": (0x004D24A8, 0x004D24D4, "744f27bf06671b3daa10125b6ca65a9fbc9333f6754ee728f79a014c91567e41"),
    "DmSecAuthRsp": (0x004D24D4, 0x004D250C, "96dbb0ebe2c014b420b5d911b1b8b6cd6b17791676309aa571825fe123357c32"),
    "DmSecInit": (0x004D250C, 0x004D251E, "1d080174ce4ee0342e3ef23e4265aa5016db7fa494fdb0d973c58003fe2c001c"),
    "DmSecGetLocalCsrk": (0x004D251E, 0x004D2524, "3e78c4337c3095a014bf862ea720d3f84c41c3a62a44088f983d2933d25faf6d"),
    "DmSecGetLocalIrk": (0x004D2524, 0x004D252A, "c6eec40909bef313a6287d7f0213790f6fb54ed7ea6141d584eb5cf3fef975ae"),
    "dmSecReset": (0x004D2544, 0x004D254C, "a0cc5ec9827b16bf9b816684f01caa1b05cf224b58b137a4f335339a08f90320"),
}
BODY_CONCAT_SHA256 = "e0d03ccd38c94624504eb3b2b7580038cb38c9206623f36ad0cc9b04ca20e4c3"
PHYSICAL = (0x004D2364, 0x004D254C)
PHYSICAL_SHA256 = "4107b2f66ec33b888a5b4927b654ac6f69ac8ae29545bbfdfb0b2af211fba75f"
GAP = (0x004D252A, 0x004D2544)
GAP_SHA256 = "c4344eab6518385818a52118876c3738f279e0c4c72743cd251dae478fa7abfe"
POOL_WORDS = [0x20073B78, 0x007856B0, 0x200712A4, 0x0078A898, 0x20000694, 0x20074114]
INTERFACE = (0x0078A898, 0x0078A8A4)
INTERFACE_SHA256 = "480092e342ed56020f154b848f6f5b49b0ddcfbb3ed7f89e8366f979e8cf0403"
INTERFACE_WORDS = [0x004D2545, 0x004D2365, 0x004D2441]
CALLERS = {
    "dmSecHciHandler": [],
    "dmSecMsgHandler": [],
    "DmSmpCbackExec": [0x004D2426, 0x00537A54, 0x0056E670, 0x0056E870, 0x0056E9CA, 0x0056EDA2, 0x0056EDEA, 0x0056EDFC, 0x0056EE5C, 0x005E2AF6, 0x005E2C0C, 0x005E2D5A, 0x005E2DAC, 0x005E31D0, 0x005E3A72],
    "DmSecAuthRsp": [0x004BB01C],
    "DmSecInit": [0x004B8026],
    "DmSecGetLocalCsrk": [0x0056EB34],
    "DmSecGetLocalIrk": [0x004794F0, 0x004BB1F4, 0x00504030, 0x00504042, 0x0056EAD8],
    "dmSecReset": [],
}
EXPECTED_STORED = {
    0x0078A898: 0x004D2545,
    0x0078A89C: 0x004D2365,
    0x0078A8A0: 0x004D2441,
}
SOURCE_ONLY = ["dmSecApiLtkMsg", "DmSecCancelReq", "DmSecSetLocalCsrk", "DmSecSetLocalIrk"]


class AuditError(RuntimeError):
    """Raised when authenticated DM-security evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_sec_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES or _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei dm_sec readiness artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned dm_sec input changed: {path}")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = _slice(blob, start, end)
        if _sha256(data) != expected:
            raise AuditError(f"stock dm_sec body changed: {name}")
        bodies.append(data)
    if _sha256(b"".join(bodies)) != BODY_CONCAT_SHA256:
        raise AuditError("dm_sec body concatenation changed")
    if _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("dm_sec physical interval changed")
    gap = _slice(blob, *GAP)
    if _sha256(gap) != GAP_SHA256 or gap[:2] != b"\0\0" or list(struct.unpack("<6I", gap[2:])) != POOL_WORDS:
        raise AuditError("dm_sec alignment/literal gap changed")
    interface = _slice(blob, *INTERFACE)
    if _sha256(interface) != INTERFACE_SHA256 or list(struct.unpack("<3I", interface)) != INTERFACE_WORDS:
        raise AuditError("dm_sec interface table changed")

    decoder = _load_decoder()
    starts = {start: name for name, (start, _, _) in FUNCTIONS.items()}
    callers = {name: [] for name in FUNCTIONS}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            callers[starts[target]].append(address)
    if callers != CALLERS:
        raise AuditError("dm_sec direct caller closure changed")

    entries = set(starts)
    interiors = set()
    for start, end, _ in FUNCTIONS.values():
        interiors.update(range(start + 2, end, 2))
    stored = {}
    interior_pointers = []
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", _slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in entries:
            stored[address] = value
        elif target in interiors:
            interior_pointers.append((address, value))
    if stored != EXPECTED_STORED or interior_pointers:
        raise AuditError("dm_sec stored entry/interior pointer closure changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "source_inventory_functions": 12, "source_only_functions": SOURCE_ONLY,
            "direct_bl_ingress_sites": sum(len(v) for v in callers.values()),
            "registered_function_pointers": len(stored),
            "strict_interior_pointers": len(interior_pointers),
        },
        "architecture": {
            "security_component_id": 5, "lesc_component_id": 8,
            "security_message_events": [0x28, 0x29], "lesc_message_events": [0x40, 0x41],
            "message_ordinal_mask": 7,
            "lesc_nonzero_ediv_rand_negative_reply": True,
        },
        "abi": {
            "dm_sec_cb": 0x20074114, "dm_sec_cb_bytes": 8,
            "dm_cb": 0x20073B78, "dm_conn_cb": 0x200712A4,
            "calc128_zeros": 0x007856B0,
        },
        "lineage": {
            "selected_source_interval": "Packetcraft r20.05 through r20.05c / AmbiqSuite R4.4.1",
            "selected_blob": "7d66f73b3246b7735a07a5a7c4572c0f6d82cfcb",
            "selected_sha256": "88ff7fdfac976a70eaa3e3457d8c7123675a39311ddb21480d6699d939ffa241",
            "historical_generating_commit_resolved": False, "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST), "archive_sha256": READINESS_SHA256,
            "compiler_profiles": 2, "source_functions_built": 12,
            "provider_seams": 22, "valid_non_vacuous_closure_profiles": 2,
            "linked_unresolved_symbols": 0,
        },
        "production": {"source_owned_bytes_added": 0, "stock_bytes_replaced": 0},
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
        module = report["module"]
        print(f"Cordio dm_sec closed: {module['linked_function_count']} linked / {len(module['source_only_functions'])} source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
