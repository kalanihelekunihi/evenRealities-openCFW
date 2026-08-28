#!/usr/bin/env python3
"""Clean-room inclusion and ABI audit for Ambiq Cordio's HCI platform shim."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/ambiq-cordio-hci-core-ps-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiq-cordio-hci-core-ps-provenance.tsv"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_core_ps.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_hci_core_ps.h"
RUNTIME_TEST = ROOT / "tests/test_runtime_cordio_hci_core_ps.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINNED_INPUTS = {
    FUNCTION_MAP: "c629580d4e48aaf60f9af6c1c654df0d8b344cb0e9cd757ab4f5a6a0a829aa45",
    PROVENANCE: "cccd010ccbc4a9230d4248e42c56a1d1428ce4e5b510c92edd93482bca524c3e",
}
PRODUCTION_FILES = {
    SOURCE: (11_302, "0438bb30f3eacf0908f319cd5bafa252cedb3515df9b122493004a471976c1a0"),
    HEADER: (1_634, "946bfa113cf1657c7d236b2a922ce087a170963d2a5f03aa48c7f13bbc864cdb"),
    RUNTIME_TEST: (10_563, "b1e7118e2f9f41fd22ec195014963e3d523370d94d4e22f9337b9f9bc2dbe5eb"),
}
PRODUCTION_OVERLAY = (429_058, "0e3a5f42548a24be9c6be90f9d6a60031af69b6570e7d212815f6671bb6d7bcd")
PRODUCTION_COMPONENT = (3_952_454, "d72288b5831087acaff95fc3aaadb9e178b755ee8ce3b64a17be24af1bfd3dcb")
PRODUCTION_PACKAGE = (4_745_526, "4eb4b7f409e6c7023cffa70b21b2b3646a20f1bf305333cdc57b556b5fc32934")
PRODUCTION_FLASH_PLAN = (4_643_183, "9618a0d0f2ad5dfb572479320d8ec8e15a011a600edcd8d9bbd542c3625c4d66")

MODULE_START = 0x00530C00
MODULE_END = 0x00530D74
MODULE_SHA256 = "af477f877f3e5fff17af792d0e5cb5ac459bdbb84b784725d701bd911bfed904"
BODY_BYTES = 360
BODY_SHA256 = "2ed7114bc4a26f3ef70c1cc230ca031567fbb537290e90af0360eac0af34d9c0"
LITERAL_POOL = (0x00530D68, 0x00530D74)
LITERAL_POOL_SHA256 = "960d7b2734426f4a19a4a5469fc95148b7e92f971d4723ee47b053b3e8ad47a6"

HCI_CORE_CB = 0x20071478
HCI_CB = 0x20073870
HCI_BD_ADDR = 0x200714E0
TAIL_WORDS = {
    0x00530D68: HCI_CORE_CB,
    0x00530D6C: HCI_CB,
    0x00530D70: HCI_BD_ADDR,
}

DIRECT_CALL_EDGES = [
    (0x004B51A4, 0x00530D4C),
    (0x004B5290, 0x00530D4C),
    (0x004B52AA, 0x00530D4C),
    (0x004B6416, 0x00530D30),
    (0x004BB1DC, 0x00530D54),
    (0x004D29E0, 0x00530D4C),
    (0x0052A858, 0x00530D34),
    (0x0052A8C2, 0x00530D34),
    (0x0052A8D2, 0x00530D34),
    (0x0052AC64, 0x00530C00),
    (0x0052AD5A, 0x00530D34),
    (0x005301DA, 0x00530C88),
    (0x005302AC, 0x00530D4C),
    (0x00531370, 0x00530D4C),
    (0x0053138A, 0x00530D4C),
    (0x00536818, 0x00530CB2),
    (0x0056B414, 0x00530C08),
    (0x0056C864, 0x00530D4C),
    (0x0056C87E, 0x00530D4C),
    (0x0056E534, 0x00530D3C),
    (0x0056EAFE, 0x00530D30),
]
DIRECT_CALL_DIGEST = "93c65a4f2ad6085c5e7ff5fadf7f43eb4876b575e57dd32e08e386d60a586db6"


class AuditError(RuntimeError):
    """Raised when authenticated HCI platform-shim evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first >= last:
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def occurrences(blob: bytes, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    return [BASE + offset for offset in range(len(blob) - 3)
            if blob[offset:offset + 4] == needle]


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("hci_core_ps_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def packed_pairs_digest(pairs: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def verify_file(path: Path, expected: tuple[int, str], label: str) -> None:
    data = path.read_bytes()
    if (len(data), sha256(data)) != expected:
        raise AuditError(f"{label} changed")


def verify_production() -> dict:
    for path, expected in PRODUCTION_FILES.items():
        verify_file(path, expected, f"HCI platform production input {path.name}")
    config = json.loads(CONFIG.read_text())
    expected = config["expected"]
    if (
        (expected["overlay_size"], expected["overlay_sha256"]) != PRODUCTION_OVERLAY
        or (expected["component_size"], expected["component_sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI platform production aggregate pins changed")

    leaf_contract = {
        "hciCoreInit": (4, 1, 2),
        "hciCoreNumCmplPkts": (168, 2, 0),
        "hciCoreRecv": (60, 3, 0),
        "HciCoreHandler": (142, 7, 0),
        "HciGetBdAddr": (10, 0, 2),
        "HciGetBufSize": (12, 0, 2),
        "HciGetLeSupFeat": (88, 0, 0),
        "HciGetMaxRxAclLen": (12, 0, 0),
        "HciLeAdvExtSupported": (18, 0, 0),
    }
    leaves = [
        row for row in config["relocated_leaves"]
        if row.get("source", {}).get("path")
        == "components/shared/cordio/runtime_cordio_hci_core_ps.c"
    ]
    if {row["function"] for row in leaves} != set(leaf_contract):
        raise AuditError("HCI platform production leaf inventory changed")
    for row in leaves:
        size, relocations, _padding = leaf_contract[row["function"]]
        if (
            row["expected"]["size"] != size
            or len(row["relocations"]) != relocations
            or row.get("strict_relocation_contract") is not True
            or row.get("allow_discarded_alloc_sections") is not True
        ):
            raise AuditError(f"HCI platform leaf contract changed: {row['function']}")

    sites = [
        row for row in config["patch_sites"]
        if row["name"].startswith("replace_cordio_hci_core_ps_")
    ]
    if len(sites) != 9 or sum(row["expected_size"] for row in sites) != BODY_BYTES:
        raise AuditError("HCI platform production routes changed")
    if any(row["branch"] != "b_w" for row in sites):
        raise AuditError("HCI platform route is not a guarded redirect")

    report = json.loads(BUILD_REPORT.read_text())
    built = {
        row["extraction"]["function"]: row
        for row in report["relocated_leaves"]
        if row["extraction"]["function"] in leaf_contract
    }
    if set(built) != set(leaf_contract):
        raise AuditError("HCI platform production build inventory changed")
    for function, (size, relocations, padding) in leaf_contract.items():
        row = built[function]
        if (
            row["extraction"]["size"] != size
            or row["extraction"]["relocation_count"] != relocations
            or row["placement"]["padding_before"] != padding
        ):
            raise AuditError(f"HCI platform production build changed: {function}")
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
        != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI platform production build aggregate changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (
        override["provider"].get("size"), override["provider"].get("sha256")
    ) != PRODUCTION_COMPONENT:
        raise AuditError("HCI platform production provider changed")
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_hci_core_ps_")
    ]
    if len(regions) != 21:
        raise AuditError("HCI platform production manifest regions changed")
    verify_file(PACKAGE, PRODUCTION_PACKAGE, "HCI platform package")
    verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN, "HCI platform flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (6671, 0, 6, 6):
        raise AuditError("HCI platform flash-plan counts changed")
    return {
        "status": "production-routed",
        "stock_bytes_replaced": BODY_BYTES,
        "source_owned_bytes_added": sum(row[0] for row in leaf_contract.values()),
        "alignment_bytes_added": sum(row[2] for row in leaf_contract.values()),
        "strict_relocations": sum(row[1] for row in leaf_contract.values()),
        "source_only_functions_compiled": 11,
        "manifest_regions": len(regions),
        "flash_plan_counts": counts,
        "proprietary_source_copied": False,
        "public_behavior_license": "Apache-2.0",
        "completed_count_underflow_hardened": True,
        "unknown_receive_type_hardened": True,
        "extended_advertising_uses_num_sets": True,
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned HCI platform input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row for row in rows if row["stock_status"] == "source_only"]
    expected_source_only = [
        "HciGetWhiteListSize", "HciGetAdvTxPwr", "HciGetNumBufs",
        "HciGetSupStates", "HciGetResolvingListSize", "HciLlPrivacySupported",
        "HciGetMaxAdvDataLen", "HciGetNumSupAdvSets", "HciGetPerAdvListSize",
        "HciGetLocalVerInfo", "HciGetLeSupFeat32",
    ]
    if len(rows) != 20 or len(linked) != 9:
        raise AuditError("R4 hci_core_ps.c source inventory changed")
    if [row["function"] for row in source_only] != expected_source_only:
        raise AuditError("HCI platform source-only classification changed")

    bodies = []
    starts: dict[int, str] = {}
    interiors: set[int] = set()
    for row in linked:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        starts[start] = row["function"]
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("HCI platform body concatenation changed")
    if sha256(image_slice(blob, MODULE_START, MODULE_END)) != MODULE_SHA256:
        raise AuditError("HCI platform physical interval changed")

    literal_raw = image_slice(blob, *LITERAL_POOL)
    if sha256(literal_raw) != LITERAL_POOL_SHA256:
        raise AuditError("HCI platform literal pool changed")
    for cell, expected in TAIL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"HCI platform literal changed at 0x{cell:08x}")

    decoder = load_decoder()
    edges = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            edges.append((address, target))
    if edges != DIRECT_CALL_EDGES or packed_pairs_digest(edges) != DIRECT_CALL_DIGEST:
        raise AuditError("HCI platform direct-call closure changed")

    stored_entries = []
    stored_interiors = []
    for address in range(BASE, BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if stored_entries or stored_interiors:
        raise AuditError("stored HCI platform entry/interior pointer appeared")

    if occurrences(blob, HCI_CORE_CB) != [0x0052AE14, 0x00530D68, 0x00569D28]:
        raise AuditError("hciCoreCb reference closure changed")
    if occurrences(blob, HCI_CB) != [
        0x0052AE18, 0x0052B6B8, 0x00530D6C, 0x00536810,
        0x00569D48, 0x0056B140, 0x0056B7C8,
    ]:
        raise AuditError("hciCb reference closure changed")
    if occurrences(blob, HCI_BD_ADDR) != [0x00530D70, 0x00569D40]:
        raise AuditError("HCI BD-address reference closure changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "module": {
            "start": MODULE_START,
            "end_exclusive": MODULE_END,
            "physical_bytes": MODULE_END - MODULE_START,
            "linked_function_count": len(linked),
            "linked_function_bytes": BODY_BYTES,
            "source_inventory_functions": len(rows),
            "source_only_functions": expected_source_only,
            "literal_bytes": len(literal_raw),
            "direct_bl_ingress_sites": len(edges),
            "stored_entry_pointers": 0,
            "strict_interior_pointers": 0,
        },
        "abi": {
            "hci_core_cb": HCI_CORE_CB,
            "hci_cb": HCI_CB,
            "bd_addr": HCI_BD_ADDR,
            "bd_addr_offset": 0x68,
            "le_feature_bits": 64,
            "iso_callback_offset_in_hci_cb": 0x18,
            "resetting_offset_in_hci_cb": 0x21,
        },
        "behavior": {
            "iso_receive_dispatch": True,
            "completed_packet_flow_reenable": True,
            "connection_parameter_feature_masked": True,
            "source_only_getters": len(source_only),
        },
        "lineage": {
            "selected_oracle": "AmbiqSuite R4.4.1 later official import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "863085f75f368ac8ad2a8b741dd51231bffcabcf",
            "selected_sha256": "dca9e769828eedab03b15d99ffd0e1e726d8935af2e22eaa901bb897e05853cd",
            "r25_source_functions": 18,
            "r44_source_functions": 20,
            "historical_generating_commit_resolved": False,
            "license": "Arm Cordio proprietary SLA",
        },
        "production": verify_production(),
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
        print("HCI core platform production-routed: 9 linked / 11 source-only; Apache behavior + G2 ABI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
