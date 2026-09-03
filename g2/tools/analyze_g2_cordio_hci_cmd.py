#!/usr/bin/env python3
"""Clean-room inclusion and queue-ABI audit for Ambiq Cordio hci_cmd.c."""

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
FUNCTION_MAP = ROOT / "tools/manifests/ambiq-cordio-hci-cmd-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiq-cordio-hci-cmd-provenance.tsv"
CLOSURE = ROOT / "tools/manifests/ambiq-cordio-hci-cmd-closure.tsv"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_cmd.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_hci_cmd.h"
RUNTIME_TEST = ROOT / "tests/test_runtime_cordio_hci_cmd_core.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINNED_INPUTS = {
    FUNCTION_MAP: "e303eb2280777c82cda209d48f05301f4b56a14d49577909afbfd065b23a887d",
    PROVENANCE: "462d7f2ed0c8f34bde8f175fe5415f808d442b3b3650676aab56a3add86496c8",
    CLOSURE: "7899866f45ab1c748d515b3f811c2b9c90e4762c8c36f9cb79cdf7e2ea89aee2",
}
PRODUCTION_FILES = {
    SOURCE: (22_577, "7852655ec8e29b68a6de88ab75e7a02621a37b816211f593ce191d814a0beb53"),
    HEADER: (6_193, "f3c731af23e2db762344caae77fe8e6cffd87a57143b6f214cab84132911a826"),
    RUNTIME_TEST: (7_754, "08f5c0ef4e953e08700112e8ba6a9097b01e7246e7b3ee0fa9e527bec662ffea"),
}
PRODUCTION_OVERLAY = (362_272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae")
PRODUCTION_COMPONENT = (3_956_672, "79323dd5ae9211e9d1c393f26593c98c96c53d928c44c4447c946e67ef0fbeef")
PRODUCTION_PACKAGE = (4_750_780, "49c61010614d5db51c9e97f3ca549e47644a32805411d0ff5dc96ea7445d3e27")
PRODUCTION_FLASH_PLAN = (4_961_300, "f2625775d8a7b3c81c8862db00979cdcf4965eeb003e4b6b84e8cb2d8c1293b9")
CONFIG_LEAF_CONTRACT_SHA256 = "48f8f665bc34c29cb0abd2061286cc0f38fc39a831d0bd49a6eed092dcbf6583"
BUILD_LEAF_CONTRACT_SHA256 = "96e15d2840bbe09221a8859ae955be520c919faf5178ff7a1222a6fff7d4adf3"
ROUTE_CONTRACT_SHA256 = "f95204934ead6d0799758732f008414ef10c9ca5b296de97ead52b61e59dc4bd"

MODULE_START = 0x0052AE38
MODULE_END = 0x0052B8A4
MODULE_SHA256 = "dc34dc1f11085b6c7e8748c7edebf2e1b4dbc1568774dd8352b7fc064ca15119"
BODY_BYTES = 2_654
BODY_SHA256 = "cab0777a869c367127b83c0f51c76bb8c7fec32582d7b3f634f8e4f157ccecc1"
LITERAL_ISLAND = (0x0052B6AE, 0x0052B6BC)
LITERAL_ISLAND_SHA256 = "f68646989009779d7d768ce66f33d6b64840a54198ac3d03e6e4d814d174907c"
LITERAL_WORDS = {
    0x0052B6B0: 0x20073AA0,
    0x0052B6B4: 0x20073A90,
    0x0052B6B8: 0x20073870,
}
DIRECT_CALL_COUNT = 156
DIRECT_CALL_DIGEST = "af3562ba738d194152c84607bfa487699037fe1b459428f67db29bb8b093e57e"
BODY_CALL_COUNT = 127
BODY_CALL_DIGEST = "104e66103d9d8f30c9074d632616557d9e6dc23c7f55fee81ce2fe7bc507fec3"
ACCIDENTAL_INTERIOR_WORDS = [(0x006317C0, 0x0052B5EF)]
SOURCE_ONLY = [
    "HciLeAddDevWhiteListCmd",
    "HciLeClearWhiteListCmd",
    "HciLeReadDefDataLen",
    "HciLeReadAdvTXPowerCmd",
    "HciLeReadChanMapCmd",
    "HciLeRemoveDevWhiteListCmd",
    "HciLeSetHostChanClassCmd",
    "HciReadLocalSupFeatCmd",
    "HciReadLocalVerInfoCmd",
    "HciReadRemoteVerInfoCmd",
    "HciReadTxPwrLvlCmd",
    "HciReadAuthPayloadTimeout",
    "HciLeReadPeerResolvableAddr",
    "HciLeReadLocalResolvableAddr",
    "HciLeSetResolvablePrivateAddrTimeout",
    "HciLeReceiverTestCmd",
    "HciLeTransmitterTestCmd",
    "HciLeTestEndCmd",
    "HciLeReceiverTestCmdV3",
    "HciLeTransmitterTestCmdV3",
    "HciLeReadBufSizeCmdV2",
    "HciLeSetHostFeatureCmd",
]


class AuditError(RuntimeError):
    """Raised when authenticated HCI-command evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first >= last:
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("hci_cmd_thumb", path)
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
        verify_file(path, expected, f"HCI command-core input {path.name}")

    config = json.loads(CONFIG.read_text())
    expected = config["expected"]
    if (
        (expected["overlay_size"], expected["overlay_sha256"]) != PRODUCTION_OVERLAY
        or (expected["component_size"], expected["component_sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI command-core aggregate pins changed")
    leaves = [
        row for row in config["relocated_leaves"]
        if row.get("source", {}).get("path")
        == "components/shared/cordio/runtime_cordio_hci_cmd.c"
    ]
    if len(leaves) != 50:
        raise AuditError("HCI command-core leaf inventory changed")
    if any(
        row.get("strict_relocation_contract") is not True
        or row.get("allow_discarded_alloc_sections") is not True
        for row in leaves
    ):
        raise AuditError("HCI command leaf strict-routing policy changed")
    config_contract = sorted(
        (row["function"], row["expected"]["size"], len(row["relocations"]))
        for row in leaves
    )
    if sha256(json.dumps(config_contract, separators=(",", ":")).encode()) \
            != CONFIG_LEAF_CONTRACT_SHA256:
        raise AuditError("HCI command leaf configuration changed")

    sites = [
        row for row in config["patch_sites"]
        if row["name"].startswith("replace_cordio_hci_cmd_core_")
    ]
    if len(sites) != 50 or sum(row["expected_size"] for row in sites) != BODY_BYTES:
        raise AuditError("HCI command-core routes changed")
    if any(row["branch"] != "b_w" for row in sites):
        raise AuditError("HCI command-core route is not guarded")
    route_contract = sorted(
        (row["target_function"], row["expected_size"], row["branch"])
        for row in sites
    )
    if sha256(json.dumps(route_contract, separators=(",", ":")).encode()) \
            != ROUTE_CONTRACT_SHA256:
        raise AuditError("HCI command route contract changed")

    report = json.loads(BUILD_REPORT.read_text())
    built = {
        row["extraction"]["function"]: row
        for row in report["relocated_leaves"]
        if row.get("source", {}).get("path")
        == "components/shared/cordio/runtime_cordio_hci_cmd.c"
    }
    if len(built) != 50:
        raise AuditError("HCI command-core build inventory changed")
    build_contract = sorted(
        (function, row["extraction"]["size"],
         row["extraction"]["relocation_count"], row["placement"]["padding_before"])
        for function, row in built.items()
    )
    if sha256(json.dumps(build_contract, separators=(",", ":")).encode()) \
            != BUILD_LEAF_CONTRACT_SHA256:
        raise AuditError("HCI command production build changed")
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
        != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI command-core build aggregate changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (
        override["provider"].get("size"), override["provider"].get("sha256")
    ) != PRODUCTION_COMPONENT:
        raise AuditError("HCI command-core provider changed")
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_hci_cmd_core_")
    ]
    if len(regions) != 91:
        raise AuditError("HCI command-core manifest regions changed")
    verify_file(PACKAGE, PRODUCTION_PACKAGE, "HCI command-core package")
    verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN, "HCI command-core flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (7104, 0, 8, 6):
        raise AuditError("HCI command-core flash-plan counts changed")
    return {
        "status": "production-routed",
        "redirected_stock_functions": 50,
        "redirected_stock_bytes": BODY_BYTES,
        "source_owned_bytes_added": 4_052,
        "alignment_bytes_added": 68,
        "strict_relocations": 106,
        "source_only_functions_compiled": 22,
        "manifest_regions": len(regions),
        "flash_plan_counts": counts,
        "remaining_unrouted_linked_functions": 0,
        "remaining_source_only_functions": 0,
        "full_command_layer_complete": True,
        "proprietary_source_copied": False,
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned HCI-command input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row["function"] for row in rows if row["stock_status"] == "source_only"]
    if len(rows) != 72 or len(linked) != 50 or source_only != SOURCE_ONLY:
        raise AuditError("HCI-command source inventory changed")
    if [int(row["source_order"]) for row in rows] != list(range(1, 73)):
        raise AuditError("HCI-command source ordering changed")

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
        raise AuditError("HCI-command body concatenation changed")
    if sha256(image_slice(blob, MODULE_START, MODULE_END)) != MODULE_SHA256:
        raise AuditError("HCI-command physical interval changed")

    island = image_slice(blob, *LITERAL_ISLAND)
    if sha256(island) != LITERAL_ISLAND_SHA256 or island[:2] != b"\x00\x00":
        raise AuditError("HCI-command literal/alignment island changed")
    for cell, expected in LITERAL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"HCI-command literal changed at 0x{cell:08x}")

    decoder = load_decoder()
    ingress = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            ingress.append((address, target))
    if len(ingress) != DIRECT_CALL_COUNT or packed_pairs_digest(ingress) != DIRECT_CALL_DIGEST:
        raise AuditError("HCI-command direct-call ingress changed")

    body_calls = []
    for row in linked:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                body_calls.append((address, target))
    if len(body_calls) != BODY_CALL_COUNT or packed_pairs_digest(body_calls) != BODY_CALL_DIGEST:
        raise AuditError("HCI-command direct callee closure changed")

    stored_entries = []
    stored_interiors = []
    for address in range(BASE, BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if stored_entries or stored_interiors != ACCIDENTAL_INTERIOR_WORDS:
        raise AuditError("stored HCI-command entry/interior classification changed")

    exact_entry_windows = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if (value & ~1) in starts:
            exact_entry_windows.append((BASE + offset, value))
    if exact_entry_windows:
        raise AuditError("unaligned stored HCI-command entry pointer appeared")

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
            "source_only_functions": SOURCE_ONLY,
            "inline_and_tail_data_bytes": len(island),
            "direct_bl_ingress_sites": len(ingress),
            "direct_body_call_sites": len(body_calls),
            "stored_entry_pointers": 0,
            "accepted_strict_interior_pointers": 0,
            "excluded_data_words_resembling_interior_pointers": ACCIDENTAL_INTERIOR_WORDS,
        },
        "abi": {
            "hci_cmd_cb": 0x20073A90,
            "timer_offset": 0x00,
            "queue_offset": 0x10,
            "opcode_offset": 0x18,
            "command_credit_offset": 0x1A,
            "hci_cb": 0x20073870,
            "command_header_bytes": 3,
            "command_timeout_seconds": 10,
        },
        "behavior": {
            "send_queues_before_transport": True,
            "successful_transport_dequeues_and_frees": True,
            "completion_restores_one_command_credit": True,
            "timeout_reboots_radio_then_requests_dm_reset": True,
            "reset_drains_pending_queue": True,
        },
        "lineage": {
            "selected_oracle": "AmbiqSuite R4.4.1 later official import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "106e76123c0f03f05f7ce3e4238d02b1ac98fd8f",
            "selected_sha256": "3a2d4609d803524f4765dbdfc65ec043035f2aa75526b0aa39f04873e62d5468",
            "historical_generating_commit_resolved": False,
            "whole_file_source_exact": False,
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
            "Ambiq hci_cmd production-routed: 50 linked / 22 source-only APIs"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
