#!/usr/bin/env python3
"""Clean-room inclusion and ABI audit for Ambiq Cordio's stock HCI event port."""

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
FUNCTION_MAP = ROOT / "tools/manifests/ambiq-cordio-hci-evt-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiq-cordio-hci-evt-provenance.tsv"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_evt.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_hci_evt.h"
RUNTIME_TEST = ROOT / "tests/test_runtime_cordio_hci_evt.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINNED_INPUTS = {
    FUNCTION_MAP: "190704aa275a90eeec26c7d5a57b1e5115757c10d7f1eee02468344604b40702",
    PROVENANCE: "a1f5b2844e6d724dedd0bdbf749a077729d3d2de003337d3913083ed690bc90f",
}
PRODUCTION_FILES = {
    SOURCE: (58_413, "1e7af7d4fbf35dba4edf0a75289233136caae70d29301bd6548794f24f3fa405"),
    HEADER: (681, "e189fb11195331f706d371b214ff9bd44a43133082a56dad0295214a216aae7d"),
    RUNTIME_TEST: (6_973, "996425610123154b7a13f90e2505ce1d9cced5d827346bcafac628f473911428"),
}
PRODUCTION_OVERLAY = (429_058, "0e3a5f42548a24be9c6be90f9d6a60031af69b6570e7d212815f6671bb6d7bcd")
PRODUCTION_COMPONENT = (3_952_454, "d72288b5831087acaff95fc3aaadb9e178b755ee8ce3b64a17be24af1bfd3dcb")
PRODUCTION_PACKAGE = (4_745_526, "4eb4b7f409e6c7023cffa70b21b2b3646a20f1bf305333cdc57b556b5fc32934")
PRODUCTION_FLASH_PLAN = (4_643_183, "9618a0d0f2ad5dfb572479320d8ec8e15a011a600edcd8d9bbd542c3625c4d66")
CONFIG_LEAF_CONTRACT_SHA256 = "f463cea41362a6a57f4be5444512b1b279cd24e87ff7bbd7da6389f4656b6214"
BUILD_LEAF_CONTRACT_SHA256 = "4f7eacb14000f3e6c77523795584126144a640a3b64b633d4a67507cc1fa9218"
ROUTE_CONTRACT_SHA256 = "b8b57cfab05c0b5e8c6b800380beb360a001fa5ab38c15d46bf88214da3dc377"

MODULE_START = 0x00569D4C
MODULE_END = 0x0056B7EC
MODULE_SHA256 = "4d7dfa091432416e0eab04bedee540929d97fd640295906f64ce36ea71d85b2d"
BODY_BYTES = 6_718
BODY_SHA256 = "4fc280002f216e5ee787f8b98f126a9f4ab2af8d7f17e0fc8796d28b6b44b9f6"
GAPS = (
    (0x0056A902, 0x0056A908, "de4dc1c462645865014cce37cf7bea0aae0eb2ea6899daca9f70422d1cf2fe7e"),
    (0x0056ABCE, 0x0056ABD4, "de4dc1c462645865014cce37cf7bea0aae0eb2ea6899daca9f70422d1cf2fe7e"),
    (0x0056B13E, 0x0056B150, "a1ec7967dd10ae7e007976f9df8b46c91abf233337b56b341d291ead2dd0f78b"),
    (0x0056B37C, 0x0056B390, "a6de6587d8861d9abca7d2e8c0ed6792d72edd6d1b3862af936217ba3ca71417"),
    (0x0056B7BC, 0x0056B7EC, "9253ed73aa101889993fe96f6cf3ddeb803b3911773ca261e9c7ea2e98bd8dcc"),
)
GAP_BYTES = 98
GAP_SHA256 = "d382d6b4650a892647a6eceb5ef21dbfcfb01b5fcd96b6a3a5ce35ea0b8d313d"

PARSE_TABLE = (0x006C910C, 0x006C9260)
PARSE_TABLE_SHA256 = "b61db5479706fbe355d1173a5636c7ed8c4cb2e91f48bf3ab96add02a6e3fb60"
CALLBACK_LENGTH_TABLE = (0x006E3720, 0x006E3775)
CALLBACK_LENGTH_SHA256 = "72451d4e8b3cd63e6a1bf880cd3a651083250b66a00485064a8f222538213ef8"
CALLBACK_LENGTHS = [
    4, 36, 36, 10, 14, 6, 28, 10, 14, 8, 14, 16, 8, 8, 8, 10, 16,
    6, 136, 6, 6, 6, 6, 6, 12, 12, 6, 22, 14, 8, 8, 10, 6, 8, 14,
    14, 14, 70, 38, 8, 6, 10, 6, 10, 36, 4, 10, 12, 22, 16, 6, 4,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 28, 4, 8, 8, 8, 8, 40, 10, 10,
    10, 40, 6, 6, 6, 6, 44, 32, 16, 60, 6, 56, 6, 6, 28,
]

PATH_ADDRESS = 0x006E0518
PATH_POINTER_CELLS = [0x0056B37C, 0x0056B7E4]
PATH_BYTES = (
    b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host"
    b"\\sources\\hci\\ambiq\\hci_evt.c\x00"
)
PATH_SHA256 = "1087f0b585b360c33cacba43c868180811c5e2d594e016562d75f7a78e8ee7eb"

HCI_CB = 0x20073870
HCI_EVT_STATS = 0x20073BC0
TAIL_WORDS = {
    0x0056B7C8: HCI_CB,
    0x0056B7CC: CALLBACK_LENGTH_TABLE[0],
    0x0056B7D0: PARSE_TABLE[0],
    0x0056B7D4: HCI_EVT_STATS,
    0x0056B7E4: PATH_ADDRESS,
}

DIRECT_CALL_EDGES = [
    (0x00530CCE, 0x0056B390),
    (0x0056B174, 0x0056B100),
    (0x0056B3F6, 0x0056B150),
    (0x0056B40C, 0x0056B182),
    (0x0056B4E0, 0x0056A398),
    (0x0056B518, 0x0056AB50),
    (0x0056B546, 0x0056A430),
    (0x0056B56A, 0x0056A5BE),
    (0x0056B57C, 0x0056A63E),
    (0x0056B672, 0x0056A908),
]
DIRECT_CALL_DIGEST = "a7adf7dd9a05f3073bc57e933a939a287023a7538f613a443379d626e8ffba5b"
STORED_ENTRY_DIGEST = "98e42ec1193f836cec36969dfe2e1a77f1749cfcaf5943f41d80fd1aa40632a3"


class AuditError(RuntimeError):
    """Raised when authenticated HCI event-port evidence changes."""


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
    spec = importlib.util.spec_from_file_location("hci_evt_thumb", path)
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
        verify_file(path, expected, f"HCI event input {path.name}")

    config = json.loads(CONFIG.read_text())
    expected = config["expected"]
    if (
        (expected["overlay_size"], expected["overlay_sha256"]) != PRODUCTION_OVERLAY
        or (expected["component_size"], expected["component_sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI event aggregate pins changed")
    source_path = "components/shared/cordio/runtime_cordio_hci_evt.c"
    leaves = [
        row for row in config["relocated_leaves"]
        if row.get("source", {}).get("path") == source_path
    ]
    if len(leaves) != 79 or any(
        row.get("strict_relocation_contract") is not True
        or row.get("allow_discarded_alloc_sections") is not True
        for row in leaves
    ):
        raise AuditError("HCI event leaf inventory or strict policy changed")
    config_contract = sorted(
        (row["function"], row["expected"]["size"], len(row["relocations"]))
        for row in leaves
    )
    if sha256(json.dumps(config_contract, separators=(",", ":")).encode()) \
            != CONFIG_LEAF_CONTRACT_SHA256:
        raise AuditError("HCI event leaf configuration changed")

    sites = [
        row for row in config["patch_sites"]
        if row["name"].startswith("replace_cordio_hci_evt_")
    ]
    if len(sites) != 79 or sum(row["expected_size"] for row in sites) != BODY_BYTES:
        raise AuditError("HCI event routes changed")
    copies = [row for row in sites if row["branch"] == "copy"]
    if len(copies) != 1 or copies[0]["target_function"] != "hciEvtParseLeScanTimeout" \
            or any(row["branch"] not in ("b_w", "copy") for row in sites):
        raise AuditError("HCI event route policy changed")
    route_contract = sorted(
        (row["target_function"], row["expected_size"], row["branch"])
        for row in sites
    )
    if sha256(json.dumps(route_contract, separators=(",", ":")).encode()) \
            != ROUTE_CONTRACT_SHA256:
        raise AuditError("HCI event route contract changed")

    report = json.loads(BUILD_REPORT.read_text())
    built = {
        row["extraction"]["function"]: row
        for row in report["relocated_leaves"]
        if row.get("source", {}).get("path") == source_path
    }
    if len(built) != 79:
        raise AuditError("HCI event production inventory changed")
    build_contract = sorted(
        (function, row["extraction"]["size"],
         row["extraction"]["relocation_count"], row["placement"]["padding_before"])
        for function, row in built.items()
    )
    if sha256(json.dumps(build_contract, separators=(",", ":")).encode()) \
            != BUILD_LEAF_CONTRACT_SHA256:
        raise AuditError("HCI event production build changed")
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
        != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI event build aggregate changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (override["provider"].get("size"), override["provider"].get("sha256")) \
            != PRODUCTION_COMPONENT:
        raise AuditError("HCI event provider changed")
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_hci_evt_")
    ]
    if len(regions) != 161:
        raise AuditError("HCI event manifest regions changed")
    verify_file(PACKAGE, PRODUCTION_PACKAGE, "HCI event package")
    verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN, "HCI event flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (6671, 0, 6, 6):
        raise AuditError("HCI event flash-plan counts changed")
    return {
        "status": "production-routed",
        "redirected_stock_functions": 79,
        "redirected_stock_bytes": BODY_BYTES,
        "source_owned_bytes_added": 23_590,
        "alignment_bytes_added": 30,
        "strict_relocations": 52,
        "source_only_functions_compiled": 1,
        "manifest_regions": len(regions),
        "flash_plan_counts": counts,
        "remaining_unrouted_linked_functions": 0,
        "remaining_source_only_functions": 0,
        "full_event_layer_complete": True,
        "proprietary_source_copied": False,
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned HCI event input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 80:
        raise AuditError("R4 hci_evt.c source inventory changed")
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row for row in rows if row["stock_status"] == "source_only"]
    if len(linked) != 79 or [row["function"] for row in source_only] != ["hciEvtGetStats"]:
        raise AuditError("HCI event function inclusion changed")

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
        raise AuditError("HCI event body concatenation changed")
    if sha256(image_slice(blob, MODULE_START, MODULE_END)) != MODULE_SHA256:
        raise AuditError("HCI event physical interval changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(blob, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"HCI event gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != GAP_BYTES or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("HCI event gap concatenation changed")

    parse_raw = image_slice(blob, *PARSE_TABLE)
    length_raw = image_slice(blob, *CALLBACK_LENGTH_TABLE)
    if sha256(parse_raw) != PARSE_TABLE_SHA256 or sha256(length_raw) != CALLBACK_LENGTH_SHA256:
        raise AuditError("HCI event lookup tables changed")
    parse_values = list(struct.unpack("<85I", parse_raw))
    if len(parse_values) != 85 or sum(value != 0 for value in parse_values) != 74:
        raise AuditError("HCI parse table shape changed")
    parser_starts = {
        int(row["stock_start"], 0) for row in linked
        if row["ingress"].startswith("parse table index")
    }
    if {value & ~1 for value in parse_values if value} != parser_starts or len(parser_starts) != 69:
        raise AuditError("HCI parse table target closure changed")
    if list(length_raw) != CALLBACK_LENGTHS:
        raise AuditError("HCI callback structure lengths changed")

    for cell, expected in TAIL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"HCI tail literal changed at 0x{cell:08x}")
    if image_slice(blob, PATH_ADDRESS, PATH_ADDRESS + len(PATH_BYTES)) != PATH_BYTES:
        raise AuditError("retained hci_evt.c path changed")
    if sha256(PATH_BYTES) != PATH_SHA256 or occurrences(blob, PATH_ADDRESS) != PATH_POINTER_CELLS:
        raise AuditError("retained hci_evt.c path-pointer closure changed")

    decoder = load_decoder()
    edges = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            edges.append((address, target))
    if edges != DIRECT_CALL_EDGES or packed_pairs_digest(edges) != DIRECT_CALL_DIGEST:
        raise AuditError("HCI event direct-call closure changed")

    stored_entries = []
    stored_interiors = []
    for address in range(BASE, BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if len(stored_entries) != 74 or packed_pairs_digest(stored_entries) != STORED_ENTRY_DIGEST:
        raise AuditError("HCI event stored-entry closure changed")
    if stored_interiors:
        raise AuditError("strict-interior HCI event pointer appeared")

    if occurrences(blob, HCI_EVT_STATS) != [0x0056B7D4]:
        raise AuditError("HCI statistics-object reference closure changed")
    if occurrences(blob, HCI_CB) != [
        0x0052AE18, 0x0052B6B8, 0x00530D6C, 0x00536810,
        0x00569D48, 0x0056B140, 0x0056B7C8,
    ]:
        raise AuditError("hciCb reference closure changed")

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
            "source_only_functions": ["hciEvtGetStats"],
            "inline_and_tail_data_bytes": GAP_BYTES,
            "direct_bl_ingress_sites": len(edges),
            "registered_parser_pointer_cells": len(stored_entries),
            "unique_registered_parsers": len(parser_starts),
            "strict_interior_pointers": 0,
        },
        "tables": {
            "parse_table": PARSE_TABLE,
            "parse_entries": len(parse_values),
            "parse_nonnull_entries": sum(value != 0 for value in parse_values),
            "callback_length_table": CALLBACK_LENGTH_TABLE,
            "callback_length_entries": len(length_raw),
        },
        "abi": {
            "hci_cb": HCI_CB,
            "hci_evt_stats": HCI_EVT_STATS,
            "hci_evt_stats_references": 1,
            "transport_callback_site": 0x00530CCE,
        },
        "lineage": {
            "selected_oracle": "AmbiqSuite R4.4.1 later official import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "d2b2648587b2c8e89852f9d99555b35148e4d6ca",
            "selected_sha256": "5bee4484a94968be22cf59b60aa1d40441a824f26fe657edc58ca3e190037f24",
            "r25_parse_entries": 67,
            "r44_parse_entries": 85,
            "stock_parse_entries": 85,
            "diagnostic_lines": [1625, 1629, 1680, 2831],
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
        print(
            "Ambiq hci_evt production-routed: 79 linked / 1 source-only API; "
            "exact R4 85-entry layout"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
