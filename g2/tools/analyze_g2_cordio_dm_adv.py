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
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_dm_adv.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_dm_adv.h"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
SOURCE_SHA256 = "d6fe9bb4a957495b0716a8e5e21d9dfbde904a1b6f8944790f08cf9e507a788b"
HEADER_SHA256 = "207706e8411b2d3fb124e20354f24e438864eb88ef685568743295f4303d8cfb"
OVERLAY_SIZE = 380_444
OVERLAY_SHA256 = "21095c67c3376be1010a7bea19156bae8b1b67bb471525d196c1135d0894f622"
COMPONENT_SIZE = 3_956_672
COMPONENT_SHA256 = "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6"
PACKAGE_SIZE = 4_750_780
PACKAGE_SHA256 = "1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771"
FLASH_PLAN_SIZE = 5_485_925
FLASH_PLAN_SHA256 = "d931ff83e416a91a87f40690c1ed2dc65cee4ee7b1bdc8fb37eaf9cd2cf624ef"
PRODUCTION_FUNCTIONS = [
    "open_cfw_cordio_dm_adv_control_block_initialize",
    "open_cfw_cordio_dm_adv_initialize",
    "open_cfw_cordio_dm_adv_generate_connection_complete",
    "open_cfw_cordio_dm_adv_configure",
    "open_cfw_cordio_dm_adv_set_data",
    "open_cfw_cordio_dm_adv_start",
    "open_cfw_cordio_dm_adv_stop",
    "open_cfw_cordio_dm_adv_set_interval",
    "open_cfw_cordio_dm_adv_set_address_type",
]
PRODUCTION_METRICS = [
    (286212, 70, 0), (286284, 40, 2), (286332, 160, 1),
    (286492, 90, 2), (286584, 142, 2), (286728, 160, 2),
    (286892, 384, 2), (287276, 50, 2), (287328, 26, 2),
]
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


def _verify_production() -> dict[str, Any]:
    if _sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise AuditError("common advertising production source changed")
    if _sha256(HEADER.read_bytes()) != HEADER_SHA256:
        raise AuditError("common advertising production header changed")
    report = json.loads(REPORT.read_text())
    config = json.loads(CONFIG.read_text())
    manifest = json.loads(MANIFEST.read_text())
    leaves = [
        row for row in report["relocated_leaves"]
        if row.get("source", {}).get("path", "").endswith(SOURCE.name)
    ]
    leaves.sort(key=lambda row: row["pins"]["offset"])
    if len(leaves) != len(PRODUCTION_FUNCTIONS):
        raise AuditError("common advertising production leaf count changed")
    for row, function, expected in zip(
        leaves, PRODUCTION_FUNCTIONS, PRODUCTION_METRICS
    ):
        observed = (
            row["pins"]["offset"], row["extraction"]["size"],
            row["extraction"]["relocation_count"],
        )
        if row["extraction"]["function"] != function or observed != expected:
            raise AuditError(f"common advertising production leaf changed: {function}")
    sites = {
        row["name"]: row for row in config["patch_sites"]
        if row["name"].startswith("replace_cordio_dm_adv_")
        and not row["name"].startswith("replace_cordio_dm_adv_leg_")
    }
    if len(sites) != len(PRODUCTION_FUNCTIONS):
        raise AuditError("common advertising production route count changed")
    for index, ((_, start, end, expected_hash, _), function) in enumerate(
        zip(FUNCTIONS, PRODUCTION_FUNCTIONS), 1
    ):
        site = sites.get(f"replace_cordio_dm_adv_{index:02d}")
        if (
            site is None or site["branch"] != "b_w"
            or site["target_function"] != function
            or site["runtime_address"] != start
            or site["expected_size"] != end - start
            or site["expected_sha256"] != expected_hash
        ):
            raise AuditError(f"common advertising production route changed: {function}")
    override = manifest["component_overrides"]["apollo_main"]
    if (
        report["overlay"]["size"] != OVERLAY_SIZE
        or report["overlay"]["sha256"] != OVERLAY_SHA256
        or report["component"]["size"] != COMPONENT_SIZE
        or report["component"]["sha256"] != COMPONENT_SHA256
        or override["provider"].get("size") != COMPONENT_SIZE
        or override["provider"].get("sha256") != COMPONENT_SHA256
        or len([row for row in override["regions"]
                if row["name"].startswith("cordio_dm_adv_")
                and not row["name"].startswith("cordio_dm_adv_leg_")]) != 24
    ):
        raise AuditError("common advertising component/manifest ownership changed")
    if (
        PACKAGE.stat().st_size != PACKAGE_SIZE
        or _sha256(PACKAGE.read_bytes()) != PACKAGE_SHA256
    ):
        raise AuditError("common advertising deterministic package changed")
    flash = json.loads(FLASH_PLAN.read_text())
    if (
        FLASH_PLAN.stat().st_size != FLASH_PLAN_SIZE
        or _sha256(FLASH_PLAN.read_bytes()) != FLASH_PLAN_SHA256
        or (len(flash["flash_regions"]), len(flash["unresolved_flash_regions"]),
            len(flash["container_only_regions"]), len(flash["protected_regions"]))
            != (7822, 0, 8, 6)
    ):
        raise AuditError("common advertising flash plan changed")
    return {
        "status": "routed",
        "linked_functions": len(PRODUCTION_FUNCTIONS),
        "source_functions": 15,
        "source_only_functions": SOURCE_ONLY,
        "stock_bytes_replaced": 562,
        "compiled_text_bytes": sum(row[1] for row in PRODUCTION_METRICS),
        "source_owned_bytes_added": sum(row[1] for row in PRODUCTION_METRICS),
        "alignment_bytes": sum(row["placement"]["padding_before"] for row in leaves),
        "strict_relocations": sum(row[2] for row in PRODUCTION_METRICS),
        "guarded_redirects": len(PRODUCTION_FUNCTIONS),
        "inline_payload_abi": "eight-byte fixed header followed by copied payload",
        "hardening": [
            "advertising handle and set count bounds",
            "required pointer and allocation checks",
            "data location and maximum length checks",
            "advertising-element shape and buffer bounds",
            "interval ordering and channel-map validation",
        ],
        "hardware_validation": (
            "blocked by unavailable physical evidence; future qualification requires authorized responsive G2/EM9305 and BLE peer evidence"
        ),
    }


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
        "production": _verify_production(),
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
