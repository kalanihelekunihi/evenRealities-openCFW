#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio common advertising module."""

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
READINESS_MANIFEST = ROOT / "research/readiness/dm-adv/SHA256SUMS"
READINESS_BYTES = 1_175
READINESS_SHA256 = "69a9f55db18e329a8038ce756a0c6ad8a522ff2e3ce56f5efae2ea0246725b89"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-adv-function-map.tsv": "54e908660de2c61d9852efab17af3f0e8c34ed1a149d2f22c4962e5fb84cea38",
    ROOT / "tools/manifests/packetcraft-cordio-dm-adv-provenance.tsv": "0749854360957aa52abc49563bb77ccde1508006caa6d26ce8bfd8bbebadd4a9",
    ROOT / "tools/manifests/readiness-cordio-dm-adv-build-results.tsv": "3351c6913259286e3f580f4a5a055d88ba097a1b54ee54537152ad20f410139f",
    ROOT / "tools/manifests/readiness-cordio-dm-adv-closure-results.tsv": "ca1a0aab6fd04abdb5052672ee185236071e535d8543d04e1d3081e213eaa8b3",
    ROOT / "tools/manifests/readiness-cordio-dm-adv-source-identities.tsv": "ffbef55abaf4a48365c30a99306afcdc0221d74f023d6e1cd93d3092bda05cfc",
    ROOT / "tools/manifests/readiness-cordio-dm-adv-undefined-providers.tsv": "1abc9cae4ada5d70ea6069b373cb31307ace8f38b04f58867b06de7a5057ddbc",
}

FUNCTIONS = [
    ("dmAdvCbInit", 0x004B3098, 0x004B30E4, "aefaf5db89e1246258ba18bb4672584b4396f0ae73133f9a3275b53108f4a0a1", [0x004B30EE]),
    ("dmAdvInit", 0x004B30E4, 0x004B310A, "916c841e53ffb9c86fbe2374a5bdb9a36dcb7f2ade6389d2bf8eaaa296892fb0", [0x004BA48A, 0x004BAC38]),
    ("dmAdvGenConnCmpl", 0x004B310A, 0x004B3166, "7278efc0ef64092bf864eafdd23dbcb0eb55733a8fb584d9738afe2593ad8886", [0x004BA690]),
    ("DmAdvConfig", 0x004B3166, 0x004B319E, "cdff558439309661431dc31f66185fd2f77a7971de126ed18527d4c8e558b850", [0x004B438A]),
    ("DmAdvSetData", 0x004B319E, 0x004B31EA, "30644465fe7726d858b5a3295ff702730d72c0b232627431583cad876b624581", [0x004B34B6]),
    ("DmAdvStart", 0x004B31EA, 0x004B3250, "7726c2e021841b599517727d376a0565fc0c391864114aa5f656769213d13be1", [0x004B43CA]),
    ("DmAdvStop", 0x004B3250, 0x004B3292, "26bbea80de4adeb0fbcb0e3c47ac6ca47570de7c0a40cad71db9d64cabe34be2", [0x004B4464, 0x004B45A2]),
    ("DmAdvSetInterval", 0x004B3292, 0x004B32B8, "95c597db37c6cc3e5379b964dd4e80ca63e6f9f71e00a8eab8efecf6d241f641", [0x004B4352]),
    ("DmAdvSetAddrType", 0x004B32B8, 0x004B32CA, "69fba7669a16927974c2f118d08d78410b6bf255f254476b929c18056cd9ebbb", [0x0046DC02]),
]
TU_SPAN = (0x004B3098, 0x004B32D4)
TU_SHA256 = "602b39c3a5562ff91272adf5f5db48b27663df6a7c350bce5a4dbbd3fe175b71"
BODY_SHA256 = "8bdd4ede90b244542c72f39a10c26c0b4a8926b1d807c5d482446b4258b768cc"
LITERAL_POOL = (0x004B32CA, 0x004B32D4)
LITERAL_POOL_SHA256 = "d7ff04799cb39fd9c800b5446f5068a8033122edfb91cf493f0db48c52a3866e"
LITERAL_POOL_BYTES = bytes.fromhex("000094330720783b0720")
CALLEES = {
    "dmAdvCbInit": [],
    "dmAdvInit": [(0x004B30EE, 0x004B3098)],
    "dmAdvGenConnCmpl": [(0x004B311A, 0x0043C0E4), (0x004B3158, 0x004D293C), (0x004B315E, 0x004D29C2)],
    "DmAdvConfig": [(0x004B3174, 0x004BF99E), (0x004B318C, 0x004D293C), (0x004B3196, 0x004BF9BA)],
    "DmAdvSetData": [(0x004B31B2, 0x004BF99E), (0x004B31D8, 0x00439BE4), (0x004B31E2, 0x004BF9BA)],
    "DmAdvStart": [(0x004B31F6, 0x004BF99E), (0x004B324A, 0x004BF9BA)],
    "DmAdvStop": [(0x004B3258, 0x004BF99E), (0x004B328C, 0x004BF9BA)],
    "DmAdvSetInterval": [(0x004B329A, 0x0052B8C8), (0x004B32B2, 0x0052B8D0)],
    "DmAdvSetAddrType": [(0x004B32BC, 0x0052B8C8), (0x004B32C4, 0x0052B8D0)],
}
SOURCE_ONLY = [
    "DmAdvRemoveAdvSet", "DmAdvClearAdvSets", "DmAdvSetRandAddr",
    "DmAdvSetChannelMap", "DmAdvSetAdValue", "DmAdvSetName",
]


class AuditError(RuntimeError):
    """Raised when authenticated common advertising evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_adv_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _all_callers(blob: bytes, decoder: Any) -> dict[int, list[int]]:
    callers = {start: [] for _, start, _, _, _ in FUNCTIONS}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in callers:
            callers[target].append(address)
    return callers


def _verify_callees(blob: bytes, decoder: Any) -> None:
    for name, expected in CALLEES.items():
        observed = []
        start = next(item[1] for item in FUNCTIONS if item[0] == name)
        end = next(item[2] for item in FUNCTIONS if item[0] == name)
        for address in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                observed.append((address, target))
        if observed != expected:
            raise AuditError(f"common advertising callee closure changed for {name}")


def _verify_aligned_pointers(blob: bytes) -> None:
    values = {
        value
        for _, start, end, _, _ in FUNCTIONS
        for address in range(start, end, 2)
        for value in (address, address | 1)
    }
    found = []
    for offset in range(0, len(blob) - 3, 4):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in values:
            found.append((LOAD_BASE + offset, value))
    if found:
        raise AuditError("common advertising gained stored entry/interior pointers")


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES:
        raise AuditError("Lorelei common advertising artifact size changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei common advertising artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned common advertising input changed: {path}")

    decoder = _load_decoder()
    callers = _all_callers(blob, decoder)
    reports = []
    bodies = []
    for name, start, end, expected_hash, expected_callers in FUNCTIONS:
        body = _slice(blob, start, end)
        if _sha256(body) != expected_hash:
            raise AuditError(f"common advertising stock span changed at 0x{start:08x}")
        if callers[start] != expected_callers:
            raise AuditError(f"common advertising caller closure changed for {name}")
        bodies.append(body)
        reports.append({
            "name": name, "start": start, "end_exclusive": end,
            "size": end - start, "sha256": expected_hash,
            "direct_bl_callers": expected_callers,
            "direct_bl_callees": CALLEES[name],
        })
    if _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("common advertising concatenated bodies changed")
    if _sha256(_slice(blob, *TU_SPAN)) != TU_SHA256:
        raise AuditError("common advertising translation-unit interval changed")
    pool = _slice(blob, *LITERAL_POOL)
    if pool != LITERAL_POOL_BYTES or _sha256(pool) != LITERAL_POOL_SHA256:
        raise AuditError("common advertising literal pool changed")
    _verify_callees(blob, decoder)
    _verify_aligned_pointers(blob)

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "tu_start": TU_SPAN[0], "tu_end_exclusive": TU_SPAN[1],
            "tu_bytes": TU_SPAN[1] - TU_SPAN[0], "tu_sha256": TU_SHA256,
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for _, start, end, _, _ in FUNCTIONS),
            "concatenated_body_sha256": BODY_SHA256,
            "literal_pool_bytes": LITERAL_POOL[1] - LITERAL_POOL[0],
            "literal_pool_sha256": LITERAL_POOL_SHA256,
            "functions": reports,
            "source_only_dead_stripped": SOURCE_ONLY,
            "direct_bl_ingress_sites": sum(len(item[-1]) for item in FUNCTIONS),
            "registered_function_entries": 0,
            "unexpected_aligned_entry_or_interior_pointers": 0,
        },
        "abi": {
            "dm_num_adv_sets": 2,
            "dmAdvCb_address": 0x20073394,
            "dmCb_address": 0x20073B78,
            "set_data_message_header_bytes": 8,
            "set_data_payload_offset": 8,
            "set_data_allocation": "sizeof(dmAdvApiSetData_t) + len",
            "set_data_layout": "Ambiq flexible-array pData[]; Packetcraft pointer ABI rejected",
        },
        "lineage": {
            "selected_exact_source": "AmbiqSuite R2.4.2/R2.5.1 dm_adv.c blob 49be7fa0b651753aa7e13e170d5a6819d46b8196",
            "selected_source_sha256": "449c64cce932d729ccd165e3dfd8085b9301e5f3b4b0a87b3e4ce0604ca34df5",
            "public_dependency_tree": "Packetcraft r20.05c commit 3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "public_near_oracle_qualification": "fourteen bodies exact; pointer-bearing DmAdvSetData rejected",
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST), "archive_sha256": READINESS_SHA256,
            "source_inventory_functions": 15, "linked_functions": 9,
            "compiler_profiles": 2, "provider_seams": 11,
            "linked_unresolved_symbols": 0,
        },
        "production": {
            "status": "stock-retained; exact Apache source/ABI identified; IAR placement not promoted",
            "source_owned_bytes_added": 0,
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
        module = report["module"]
        print(
            "Cordio common advertising evidence authenticated: "
            f"{module['linked_function_count']} linked functions / "
            f"{module['linked_function_bytes']} code bytes"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
