#!/usr/bin/env python3
"""Fail-closed exclusion audit for optional Cordio device privacy on stock G2."""

from __future__ import annotations

import argparse
import hashlib
import importlib
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
SOURCE=ROOT/"components/shared/cordio/runtime_cordio_dm_dev_priv.c"
HEADER=ROOT/"components/shared/cordio/runtime_cordio_dm_dev_priv.h"
TEST=ROOT/"tests/test_runtime_cordio_dm_dev_priv.py"
SOURCE_PIN=(9053,"4bda14da5fb346939c64b62cf6b29ad852a4da534c8d0482740e00e0cc01fb2a")
HEADER_PIN=(4241,"e1453b60d02906c2b2494666bea17fe11a5a3fea161b92c6d694f571fa27ac0d")
TEST_PIN=(3640,"7b45ce4b118a53f3e3829a274b7bafb2803a4b34c8698bfa9689e37ab58b6ffb")
READINESS_MANIFEST = ROOT / "research/readiness/dm-dev-priv/SHA256SUMS"
READINESS_BYTES = 1_116
READINESS_SHA256 = "2fc8d4436075e4c7248adf2d61e78e6a420a250e0155df8cad809815ecb941e8"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-dev-priv-function-map.tsv":
        "dcd31e0fdc1f4d385df5439772e20a5afcd9752d946118a9392c12b37193fa68",
    ROOT / "tools/manifests/packetcraft-cordio-dm-dev-priv-provenance.tsv":
        "edc7d3ee5e19873960f3b6657993e1e52def596190a2e1178c6425bdae3ee8d0",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-priv-build-results.tsv":
        "7b16556f0220fc626d9ecc25b344e78da7692bf3d12899fb1740365ffb1d10ae",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-priv-closure-results.tsv":
        "b77dd44eec50788ce40900897acf655c849ae1210b933caa3ae0b33ed3264538",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-priv-include-closure.tsv":
        "250ee94f007d36c2b9b32fb2b2471c61bb1a74b04cb96f092c322dc2a52120b9",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-priv-source-identities.tsv":
        "3d3b4989180754d0bd4659603c6f41bb9c4cd8731304c16bf88aaa27bcebccd5",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-priv-undefined-providers.tsv":
        "73376c1000329f6767828ee3f27b484467092967849da16fdbc4d425a2d3fb1f",
}

DM_FCN_IF_TABLE = 0x20000694
DM_DEV_PRIV_SLOT = DM_FCN_IF_TABLE + 4
DM_NUM_IDS = 21
DM_DEFAULT_IF = (0x0078A850, 0x0078A85C)
DM_DEFAULT_IF_SHA256 = "203372a811e7881325fe55a1ef19871303192cfda3e2d76d8d08db14afb459ef"
DM_EMPTY_BODIES = (0x004D29BE, 0x004D29C2)
DM_EMPTY_BODIES_SHA256 = "fd7165fc6672b624f26b42214654f5e37cadfc0f97f94634045b87ad1f4a4704"
DM_DEFAULT_VALUES = [0x004D29BF, 0x004D29C1, 0x004D29C1]
DM_FCN_IF_BOOT_SHA256 = "590f6b5e0e6e2075ecf65176a09eed976c145138f6d486d69e808165c06bdeac"
DM_FCN_IF_BOOT_VALUES = [0x0078A850] * DM_NUM_IDS
DM_FCN_IF_BOOT_VALUES[7] = 0x0078A844

TABLE_BASE_LITERAL_CELLS = [
    0x004B3070, 0x004B7438, 0x004BACC0, 0x004C5870, 0x004D253C,
    0x004D2930, 0x004D2AEC, 0x00534988, 0x00536A24,
]
TABLE_BASE_LITERAL_CELLS_SHA256 = (
    "ca17515d6103f75737af401bb52b850ca987204d09d45b87bdb5180a81db67f4"
)

# Every stock component-interface install that reaches the table through one of
# the authenticated literal cells.  Exact instruction bytes pin the installed
# offsets: 0, 0x24, 0x14, 0x18/0x3c, 0x20, and 8.  None writes slot +4.
INSTALL_WINDOWS = {
    (0x004BAC32, 0x004BAC38): "6f8dadd23a2bfd12f9144c3f59f6cd88fb0d5994e47d1598ef50c0e6581663d9",
    (0x004C5850, 0x004C5856): "0e37f5de9552e863a4ff7339b114936924ee2da5c311f1256ca0afdebec9e87b",
    (0x004D250C, 0x004D2512): "043febcd4c7b02ec7129bb27ad920e66ad7ce9608c60307d32334dd16483cd67",
    (0x004D27E6, 0x004D27F0): "be8f8f0f50b6c0ca44bb49a8a6ccc8ddb072b206ad38b89847f06916974fb57e",
    (0x0053496A, 0x00534970): "db7e3836b4fb3ea73b61bd8e6c2118f57dfe8ba961da06f8eb78ec7efaa85446",
    (0x005369F0, 0x005369F6): "2867b7ed57ebee0a7fba530547df7a1397d4f4ff82a18b76bcdb46b57987d091",
}
INSTALL_OFFSETS = [0x00, 0x08, 0x14, 0x18, 0x20, 0x24, 0x3C]

WSF_MSG_ALLOC = 0x004BF99E
WSF_MSG_ALLOC_CALL_COUNT = 69
WSF_MSG_ALLOC_CALLER_SHA256 = (
    "a370b08f3cfaeab9f47af159b79bd2acdf9784cc6723b59e7791b42724467219"
)
ABSENT_STRINGS = (b"dm_dev_priv.c", b"dmDevPriv", b"DmDevPriv")
SOURCE_FUNCTIONS = [
    "dmDevPrivAdvertising", "dmDevPrivTimerStart", "dmDevPrivAddrCalc",
    "dmDevPrivSetRpa", "dmDevPrivSetPendingRpa", "dmDevPrivActStart",
    "dmDevPrivActStop", "dmDevPrivActTimeout", "dmDevPrivActAesCmpl",
    "dmDevPrivActRpaStart", "dmDevPrivActRpaStop", "dmDevPrivActCtrl",
    "dmDevPrivHciHandler", "dmDevPrivMsgHandler", "dmDevPrivReset",
    "DmDevPrivInit", "DmDevPrivStart", "DmDevPrivStop",
]


class AuditError(RuntimeError):
    """Raised when authenticated device-privacy exclusion evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _verify_maintained_source() -> None:
    for path,expected,label in ((SOURCE,SOURCE_PIN,"source"),(HEADER,HEADER_PIN,"header"),(TEST,TEST_PIN,"test")):
        data=path.read_bytes()
        if (len(data),_sha256(data))!=expected:
            raise AuditError(f"maintained dm_dev_priv {label} changed")


def _slice(blob: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or first >= last or last > len(blob):
        raise AuditError(f"span [0x{start:08x},0x{end:08x}) is outside image")
    return blob[first:last]


def _occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [LOAD_BASE + i for i in range(len(blob) - 3) if blob[i:i + 4] == packed]


def _load_thumb_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_dev_priv_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _initialized_sram(blob: bytes) -> bytes:
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    module = importlib.import_module("analyze_g2_flashdb")
    return module._decode_initialized_sram(blob)


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    _verify_maintained_source()
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES:
        raise AuditError("Lorelei dm_dev_priv readiness size changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei dm_dev_priv readiness artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned dm_dev_priv input changed: {path}")

    default_if = _slice(blob, *DM_DEFAULT_IF)
    if _sha256(default_if) != DM_DEFAULT_IF_SHA256:
        raise AuditError("dmFcnDefault table changed")
    if list(struct.unpack("<3I", default_if)) != DM_DEFAULT_VALUES:
        raise AuditError("dmFcnDefault entries changed")
    if _sha256(_slice(blob, *DM_EMPTY_BODIES)) != DM_EMPTY_BODIES_SHA256:
        raise AuditError("dmEmptyReset/dmEmptyHandler bodies changed")

    literal_cells = _occurrences(blob, DM_FCN_IF_TABLE)
    if literal_cells != TABLE_BASE_LITERAL_CELLS:
        raise AuditError("dmFcnIfTbl literal-cell closure changed")
    packed_cells = b"".join(struct.pack("<I", value) for value in literal_cells)
    if _sha256(packed_cells) != TABLE_BASE_LITERAL_CELLS_SHA256:
        raise AuditError("dmFcnIfTbl literal-cell digest changed")
    if _occurrences(blob, DM_DEV_PRIV_SLOT):
        raise AuditError("unexpected direct literal for dmFcnIfTbl[DM_ID_DEV_PRIV]")
    for bounds, expected in INSTALL_WINDOWS.items():
        if _sha256(_slice(blob, *bounds)) != expected:
            raise AuditError(f"component install changed at 0x{bounds[0]:08x}")

    sram = _initialized_sram(blob)
    offset = DM_FCN_IF_TABLE - 0x20000000
    boot_table = sram[offset:offset + DM_NUM_IDS * 4]
    if _sha256(boot_table) != DM_FCN_IF_BOOT_SHA256:
        raise AuditError("boot dmFcnIfTbl bytes changed")
    boot_values = list(struct.unpack(f"<{DM_NUM_IDS}I", boot_table))
    if boot_values != DM_FCN_IF_BOOT_VALUES:
        raise AuditError("boot dmFcnIfTbl values changed")
    if boot_values[1] != DM_DEFAULT_IF[0]:
        raise AuditError("device-privacy slot is no longer default-routed")

    for needle in ABSENT_STRINGS:
        if needle in blob:
            raise AuditError(f"unexpected device-privacy marker appeared: {needle!r}")

    decoder = _load_thumb_decoder()
    msg_alloc_callers = []
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        if decoder._thumb_bl_target(blob, address) == WSF_MSG_ALLOC:
            msg_alloc_callers.append(address)
    caller_bytes = b"".join(struct.pack("<I", value) for value in msg_alloc_callers)
    if len(msg_alloc_callers) != WSF_MSG_ALLOC_CALL_COUNT:
        raise AuditError("WsfMsgAlloc direct-call census changed")
    if _sha256(caller_bytes) != WSF_MSG_ALLOC_CALLER_SHA256:
        raise AuditError("WsfMsgAlloc direct-call ledger changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "classification": "not_linked_or_dead_stripped",
            "linked_function_count": 0,
            "linked_function_bytes": 0,
            "source_inventory_functions": len(SOURCE_FUNCTIONS),
            "source_only_functions": SOURCE_FUNCTIONS,
            "retained_path_anchors": 0,
            "semantic_body_anchors": 0,
        },
        "default_routing": {
            "dm_function_interface_table": DM_FCN_IF_TABLE,
            "component_slots": DM_NUM_IDS,
            "device_privacy_component_id": 1,
            "device_privacy_slot": DM_DEV_PRIV_SLOT,
            "boot_slot_value": boot_values[1],
            "default_interface": DM_DEFAULT_IF[0],
            "default_reset": DM_DEFAULT_VALUES[0],
            "default_hci_handler": DM_DEFAULT_VALUES[1],
            "default_message_handler": DM_DEFAULT_VALUES[2],
            "table_base_literal_cells": literal_cells,
            "component_install_offsets": INSTALL_OFFSETS,
            "device_privacy_installations": 0,
        },
        "corroboration": {
            "retained_name_or_path_markers": 0,
            "wsf_msg_alloc_direct_calls_reviewed": len(msg_alloc_callers),
            "start_alloc6_event8_pattern": False,
            "stop_alloc4_event9_pattern": False,
            "privacy_action_table": False,
            "privacy_interface_table": False,
        },
        "lineage": {
            "selected_optional_source": "Packetcraft r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "fe1af93bc232a888f564513282b4da3c56acbee5",
            "selected_sha256": "aae3783dc9adce996027fc7b4505bde8399c3c8630ea6ecb79bf8905683cc475",
            "stock_body_version_discriminated": False,
            "compatibility_basis": "surrounding r20 shift-three DM ABI with product DM_NUM_ADV_SETS=2",
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "compiler_profiles": 2,
            "source_functions_built": 18,
            "provider_seams": 24,
            "valid_non_vacuous_closure_profiles": 2,
            "linked_unresolved_symbols": 0,
            "minimum_retained_text": 1422,
            "retained_bss": 5416,
            "maintained_source_functions": 18,
            "local_target_profiles": 1,
        },
        "production": {
            "status": "configuration-excluded",
            "reason": "official component slot remains default-routed; no stock entry exists to replace",
            "source_owned_bytes_added": 0,
            "stock_bytes_replaced": 0,
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
            "Cordio dm_dev_priv excluded: "
            f"{module['linked_function_count']} linked / "
            f"{module['source_inventory_functions']} source-only functions"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
