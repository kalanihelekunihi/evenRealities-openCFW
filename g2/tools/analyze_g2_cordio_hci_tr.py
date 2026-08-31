#!/usr/bin/env python3
"""Clean-room inclusion, ownership, and ABI audit for Ambiq Cordio hci_tr.c."""

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
FUNCTION_MAP = ROOT / "tools/manifests/ambiq-cordio-hci-tr-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiq-cordio-hci-tr-provenance.tsv"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_tr.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_hci_tr.h"
RUNTIME_TEST = ROOT / "tests/test_runtime_cordio_hci_tr.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINNED_INPUTS = {
    FUNCTION_MAP: "d62f968c8aeb2e8a5fe2b26b842ad14df3186b7e2d5a88592baba2f8360be0ea",
    PROVENANCE: "783817eb0c6d353dfa01109348ecc8a644ac9296ce1b920651fbd00ccde7ace2",
}
PRODUCTION_FILES = {
    SOURCE: (8_296, "0648c687458298cd2f54f874212b829a992aa0c7f642d6c773f7b0b499f0bef3"),
    HEADER: (586, "c4e82cf7c9f9cbcc8fc3039d43afae41e8a8f5462c0c551f951f238b19dbbb70"),
    RUNTIME_TEST: (9_249, "afe88cac80f073208e1299b70e06869c28d2191da8b015446121cc806afdce8a"),
}
PRODUCTION_OVERLAY = (362_272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae")
PRODUCTION_COMPONENT = (3_885_668, "898d5efb1430dc0c3e0b8b7e26823a653952114ffeab0d3ae6e89d8925301ef5")
PRODUCTION_PACKAGE = (4_678_740, "d569793138c6bc2ee456536daee59dcef0bb6051034ed966f7144083790a777a")
PRODUCTION_FLASH_PLAN = (4_595_610, "b217e924841c0fda423dfc7727d76d31499f8057aade7339e4bc3b338104c127")

MODULE_START = 0x0053013C
MODULE_END = 0x00530364
MODULE_SHA256 = "89831c5be3644e40fe6007f24df12f2929d7ffe4ae525ab190e28e7d9e9fc069"
BODY_BYTES = 524
BODY_SHA256 = "d217aa89caa7a78189e74d3513eccaee24eda36191bda2abb082f946cb03908f"
LITERAL_POOL = (0x00530348, 0x00530364)
LITERAL_POOL_SHA256 = "46a5db920b131ce56c0ca1c85324be54e0c33aef5cb7284cd022f2c5ed8f4d59"

P_DATA_RX = 0x20074654
I_RX = 0x20074F30
RECEIVING_PACKET = 0x20074FCD
P_PKT_RX = 0x20074650
PKT_IND_RX = 0x20074FCF
STATE_RX = 0x20074FCE
HDR_RX = 0x2007464C
TAIL_WORDS = {
    0x00530348: P_DATA_RX,
    0x0053034C: I_RX,
    0x00530350: RECEIVING_PACKET,
    0x00530354: P_PKT_RX,
    0x00530358: PKT_IND_RX,
    0x0053035C: STATE_RX,
    0x00530360: HDR_RX,
}

DIRECT_CALL_EDGES = [
    (0x004B4AF8, 0x00530186),
    (0x004B4BD8, 0x00530186),
    (0x0052A772, 0x0053013C),
    (0x0052AEA2, 0x00530166),
]
DIRECT_CALL_DIGEST = "7cf80c2270a14cba953dc948f83844bf192981c0c0f4b0b923fba1e26ab6d9f1"
DIRECT_CALLEE_EDGES = [
    (0x00530150, 0x004B4A02),
    (0x00530174, 0x004B4A02),
    (0x005301DA, 0x00530C88),
    (0x005302AC, 0x00530D4C),
    (0x005302C0, 0x004BF990),
    (0x005302E2, 0x004BF99E),
]
DIRECT_CALLEE_DIGEST = "71090b8b69c1739ae7dc91e5cecad54b9dac349fd80305995c61536c3f4d86c2"


class AuditError(RuntimeError):
    """Raised when authenticated HCI transport evidence changes."""


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
    spec = importlib.util.spec_from_file_location("hci_tr_thumb", path)
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
        verify_file(path, expected, f"HCI transport production input {path.name}")

    config = json.loads(CONFIG.read_text())
    expected = config["expected"]
    if (
        (expected["overlay_size"], expected["overlay_sha256"]) != PRODUCTION_OVERLAY
        or (expected["component_size"], expected["component_sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI transport production aggregate pins changed")
    leaves = [
        row for row in config["relocated_leaves"]
        if row.get("source", {}).get("path")
        == "components/shared/cordio/runtime_cordio_hci_tr.c"
    ]
    expected_leaves = {
        "hciTrSendAclData": (52, 1),
        "hciTrSendCmd": (32, 1),
        "hciTrSerialRxIncoming": (370, 4),
    }
    if {row["function"] for row in leaves} != set(expected_leaves):
        raise AuditError("HCI transport production leaf inventory changed")
    for row in leaves:
        size, relocations = expected_leaves[row["function"]]
        if (
            row["expected"]["size"] != size
            or len(row["relocations"]) != relocations
            or row.get("strict_relocation_contract") is not True
            or row.get("allow_discarded_alloc_sections") is not True
        ):
            raise AuditError(f"HCI transport leaf contract changed: {row['function']}")

    sites = sorted(
        (row for row in config["patch_sites"]
         if row["name"].startswith("replace_cordio_hci_tr_")),
        key=lambda row: row["runtime_address"],
    )
    if [
        (row["runtime_address"], row["expected_size"], row["target_function"])
        for row in sites
    ] != [
        (0x0053013C, 42, "hciTrSendAclData"),
        (0x00530166, 32, "hciTrSendCmd"),
        (0x00530186, 450, "hciTrSerialRxIncoming"),
    ] or any(row["branch"] != "b_w" for row in sites):
        raise AuditError("HCI transport production routes changed")

    report = json.loads(BUILD_REPORT.read_text())
    built = {
        row["extraction"]["function"]: row
        for row in report["relocated_leaves"]
        if row["extraction"]["function"] in expected_leaves
    }
    if set(built) != set(expected_leaves):
        raise AuditError("HCI transport production build inventory changed")
    for function, (size, relocations) in expected_leaves.items():
        row = built[function]
        if (
            row["extraction"]["size"] != size
            or row["extraction"]["relocation_count"] != relocations
            or row["placement"]["padding_before"] != 0
        ):
            raise AuditError(f"HCI transport production build changed: {function}")
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
        != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI transport production build aggregate changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (
        override["provider"].get("size"), override["provider"].get("sha256")
    ) != PRODUCTION_COMPONENT:
        raise AuditError("HCI transport production provider changed")
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_hci_tr_")
    ]
    if len(regions) != 6:
        raise AuditError("HCI transport production manifest regions changed")

    verify_file(PACKAGE, PRODUCTION_PACKAGE, "HCI transport package")
    verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN, "HCI transport flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (6588, 0, 6, 6):
        raise AuditError("HCI transport flash-plan counts changed")
    return {
        "status": "production-routed",
        "stock_bytes_replaced": BODY_BYTES,
        "source_owned_bytes_added": sum(value[0] for value in expected_leaves.values()),
        "alignment_bytes_added": 0,
        "strict_relocations": sum(value[1] for value in expected_leaves.values()),
        "source_only_functions_compiled": 1,
        "manifest_regions": len(regions),
        "flash_plan_counts": counts,
        "proprietary_source_copied": False,
        "failure_state_reset_hardened": True,
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned HCI transport input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row for row in rows if row["stock_status"] == "source_only"]
    if len(rows) != 4 or len(linked) != 3:
        raise AuditError("R4 hci_tr.c source inventory changed")
    if [row["function"] for row in source_only] != ["hciTrReceivingPacket"]:
        raise AuditError("HCI transport source-only classification changed")

    bodies = []
    starts: dict[int, str] = {}
    interiors: set[int] = set()
    body_ranges = []
    for row in linked:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        body_ranges.append((start, end))
        starts[start] = row["function"]
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("HCI transport body concatenation changed")
    if sha256(image_slice(blob, MODULE_START, MODULE_END)) != MODULE_SHA256:
        raise AuditError("HCI transport physical interval changed")

    literal_raw = image_slice(blob, *LITERAL_POOL)
    if sha256(literal_raw) != LITERAL_POOL_SHA256:
        raise AuditError("HCI transport literal pool changed")
    for cell, expected in TAIL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"HCI transport literal changed at 0x{cell:08x}")
        if occurrences(blob, expected) != [cell]:
            raise AuditError(f"HCI transport state reference closure changed at 0x{cell:08x}")

    decoder = load_decoder()
    ingress = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            ingress.append((address, target))
    if ingress != DIRECT_CALL_EDGES or packed_pairs_digest(ingress) != DIRECT_CALL_DIGEST:
        raise AuditError("HCI transport direct-call ingress changed")

    callees = []
    for start, end in body_ranges:
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                callees.append((address, target))
    if callees != DIRECT_CALLEE_EDGES or packed_pairs_digest(callees) != DIRECT_CALLEE_DIGEST:
        raise AuditError("HCI transport provider-call closure changed")

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
        raise AuditError("stored HCI transport entry/interior pointer appeared")

    for start in starts:
        if occurrences(blob, start) or occurrences(blob, start | 1):
            raise AuditError("unaligned stored HCI transport entry pointer appeared")

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
            "source_only_functions": ["hciTrReceivingPacket"],
            "literal_bytes": len(literal_raw),
            "direct_bl_ingress_sites": len(ingress),
            "direct_provider_calls": len(callees),
            "stored_entry_pointers": 0,
            "strict_interior_pointers": 0,
        },
        "abi": {
            "p_data_rx": P_DATA_RX,
            "i_rx": I_RX,
            "receiving_packet": RECEIVING_PACKET,
            "p_pkt_rx": P_PKT_RX,
            "pkt_ind_rx": PKT_IND_RX,
            "state_rx": STATE_RX,
            "hdr_rx": HDR_RX,
            "acl_header_bytes": 4,
            "event_header_bytes": 2,
            "event_parameter_limit": 255,
        },
        "behavior": {
            "acl_send_returns_length_or_zero": True,
            "command_send_returns_success": True,
            "transport_does_not_complete_tx_buffers": True,
            "invalid_packet_type_is_discarded": True,
            "acl_length_checked_against_controller_limit": True,
            "receive_returns_consumed_length": True,
        },
        "lineage": {
            "selected_oracle": "AmbiqSuite R4.4.1 later official import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "2fab7d10b369ff14d90339f75eda614a66239735",
            "selected_sha256": "81461dd10e01fac253df692f163f62e2174899e2e51f68c48f15b0cd07c9a6fd",
            "r25_send_ownership": "transport completes/frees successful sends",
            "r44_send_ownership": "caller completes/frees after return status",
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
        print("Ambiq hci_tr production-routed: 3 linked / 1 source-only; clean-room hardened RX")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
