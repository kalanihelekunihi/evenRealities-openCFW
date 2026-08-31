#!/usr/bin/env python3
"""Clean-room inclusion and ABI audit for Ambiq Cordio's stock HCI core port."""

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
FUNCTION_MAP = ROOT / "tools/manifests/ambiq-cordio-hci-core-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiq-cordio-hci-core-provenance.tsv"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_core.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_hci_core.h"
RUNTIME_TEST = ROOT / "tests/test_runtime_cordio_hci_core.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINNED_INPUTS = {
    FUNCTION_MAP: "3ebc11cf2dceb2971ea8caee389581fec6a196690ffb37185bb35adee9b8db67",
    PROVENANCE: "f06cdd2edcc2b87746b7799fde643958508b38be3a519ade0a0cda80bfd31247",
}
PRODUCTION_FILES = {
    SOURCE: (17_758, "e176b15dfbb91b7491dce6958250d44717c8a60e58d0ba73e965432c1b320544"),
    HEADER: (1_509, "27ed4d0537f084535c2ccf9c31caec48d02043d1b13d4ad48bb71ce391775fe8"),
    RUNTIME_TEST: (5_144, "fb1122cb2caa9bfc40a0766cc85acf236de25dbe6680fce0f5275c80f13bed06"),
}
PRODUCTION_OVERLAY = (362_272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae")
PRODUCTION_COMPONENT = (3_885_668, "898d5efb1430dc0c3e0b8b7e26823a653952114ffeab0d3ae6e89d8925301ef5")
PRODUCTION_PACKAGE = (4_678_740, "d569793138c6bc2ee456536daee59dcef0bb6051034ed966f7144083790a777a")
PRODUCTION_FLASH_PLAN = (4_595_610, "b217e924841c0fda423dfc7727d76d31499f8057aade7339e4bc3b338104c127")

MODULE_START = 0x0052A67C
MODULE_END = 0x0052AE38
MODULE_SHA256 = "89aa38ab7907c0b6a8b18d1949c7dbf9d85dc382b528e396ac3a6e8f35b505e3"
BODY_BYTES = 1_964
BODY_SHA256 = "5fdf336b7831dad9ec50157d35551af8ebdd9ee6e525d8ac5e99c487e42f7cd5"
LITERAL_POOL = (0x0052AE14, 0x0052AE24)
LITERAL_POOL_SHA256 = "e6dc2ab51885972f75da408b86a5a46c89dcf84b311345328c11506fd92b4260"

HCI_CORE_CB = 0x20071478
HCI_CB = 0x20073870
HCI_LE_SUP_FEAT_CFG = 0x20000028
HCI_CORE_CIS = 0x200714CC
TAIL_WORDS = {
    0x0052AE14: HCI_CORE_CB,
    0x0052AE18: HCI_CB,
    0x0052AE1C: HCI_LE_SUP_FEAT_CFG,
    0x0052AE20: HCI_CORE_CIS,
}

DIRECT_CALL_EDGES = [
    (0x004B2E22, 0x0052AC6A),
    (0x004B808E, 0x0052ACCE),
    (0x004C585E, 0x0052ACD6),
    (0x0052A6FC, 0x0052A79E),
    (0x0052A75C, 0x0052A67C),
    (0x0052A766, 0x0052A6B0),
    (0x0052A7DC, 0x0052A936),
    (0x0052A7F0, 0x0052A8B0),
    (0x0052A81E, 0x0052A704),
    (0x0052A830, 0x0052A850),
    (0x0052A886, 0x0052A76C),
    (0x0052A8AA, 0x0052A76C),
    (0x0052A8B8, 0x0052A72E),
    (0x0052A906, 0x0052A76C),
    (0x0052A926, 0x0052A936),
    (0x0052A98C, 0x0052A704),
    (0x0052ACB2, 0x0052A79E),
    (0x0052AD28, 0x0052A704),
    (0x0052AD56, 0x0052A79E),
    (0x0052AE28, 0x0052AD9C),
    (0x0052AE32, 0x0052ADC2),
    (0x00530BF8, 0x0052AD04),
    (0x00530C30, 0x0052A704),
    (0x00530C80, 0x0052A79E),
    (0x00530D08, 0x0052A962),
    (0x00536808, 0x0052AC02),
    (0x0056B4D0, 0x0052A758),
    (0x0056B508, 0x0052A758),
    (0x0056B688, 0x0052AE24),
    (0x0056B6D0, 0x0052ADEC),
    (0x0056B79A, 0x0052A762),
    (0x0056B7B4, 0x0052AE2E),
]
DIRECT_CALL_DIGEST = "fd71441ac394b10951ba9d0a10858b1b8d5ce4900321fbfde7f5b9600e0ec92d"


class AuditError(RuntimeError):
    """Raised when authenticated HCI core evidence changes."""


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
    spec = importlib.util.spec_from_file_location("hci_core_thumb", path)
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
        verify_file(path, expected, f"HCI core production input {path.name}")

    config = json.loads(CONFIG.read_text())
    expected = config["expected"]
    if (
        (expected["overlay_size"], expected["overlay_sha256"]) != PRODUCTION_OVERLAY
        or (expected["component_size"], expected["component_sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI core production aggregate pins changed")

    leaf_contract = {
        "hciCoreConnAlloc": (50, 0, 2),
        "hciCoreConnFree": (90, 3, 2),
        "hciCoreConnByHandle": (52, 0, 2),
        "hciCoreNextConnFragment": (68, 0, 0),
        "hciCoreConnOpen": (54, 0, 0),
        "hciCoreConnClose": (90, 3, 2),
        "hciCoreSendAclData": (64, 1, 2),
        "hciCoreTxReady": (356, 11, 0),
        "hciCoreTxAclStart": (170, 3, 0),
        "hciCoreTxAclContinue": (218, 4, 2),
        "hciCoreTxAclComplete": (48, 2, 2),
        "hciCoreAclReassembly": (1_296, 5, 0),
        "HciCoreInit": (98, 1, 0),
        "HciResetSequence": (240, 11, 2),
        "HciSetMaxRxAclLen": (18, 0, 0),
        "HciSetLeSupFeat": (38, 0, 2),
        "HciSendAclData": (274, 6, 2),
        "hciCoreCisAlloc": (108, 0, 2),
        "hciCoreCisFree": (78, 0, 0),
        "hciCoreCisByHandle": (94, 0, 2),
        "hciCoreCisOpen": (108, 0, 2),
        "hciCoreCisClose": (78, 0, 0),
    }
    leaves = [
        row for row in config["relocated_leaves"]
        if row.get("source", {}).get("path")
        == "components/shared/cordio/runtime_cordio_hci_core.c"
    ]
    if {row["function"] for row in leaves} != set(leaf_contract):
        raise AuditError("HCI core production leaf inventory changed")
    for row in leaves:
        size, relocations, _padding = leaf_contract[row["function"]]
        if (
            row["expected"]["size"] != size
            or len(row["relocations"]) != relocations
            or row.get("strict_relocation_contract") is not True
            or row.get("allow_discarded_alloc_sections") is not True
        ):
            raise AuditError(f"HCI core leaf contract changed: {row['function']}")

    site_names = {f"replace_cordio_hci_core_{index:02d}" for index in range(1, 23)}
    sites = [row for row in config["patch_sites"] if row["name"] in site_names]
    if len(sites) != 22 or sum(row["expected_size"] for row in sites) != BODY_BYTES:
        raise AuditError("HCI core production routes changed")
    if any(row["branch"] != "b_w" for row in sites):
        raise AuditError("HCI core route is not a guarded redirect")

    report = json.loads(BUILD_REPORT.read_text())
    built = {
        row["extraction"]["function"]: row
        for row in report["relocated_leaves"]
        if row.get("source", {}).get("path")
        == "components/shared/cordio/runtime_cordio_hci_core.c"
    }
    if set(built) != set(leaf_contract):
        raise AuditError("HCI core production build inventory changed")
    for function, (size, relocations, padding) in leaf_contract.items():
        row = built[function]
        if (
            row["extraction"]["size"] != size
            or row["extraction"]["relocation_count"] != relocations
            or row["placement"]["padding_before"] != padding
        ):
            raise AuditError(f"HCI core production build changed: {function}")
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
        != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI core production build aggregate changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (
        override["provider"].get("size"), override["provider"].get("sha256")
    ) != PRODUCTION_COMPONENT:
        raise AuditError("HCI core production provider changed")
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_hci_core_")
        and not row["name"].startswith("cordio_hci_core_ps_")
    ]
    if len(regions) != 57:
        raise AuditError("HCI core production manifest regions changed")

    verify_file(PACKAGE, PRODUCTION_PACKAGE, "HCI core package")
    verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN, "HCI core flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (6588, 0, 6, 6):
        raise AuditError("HCI core flash-plan counts changed")
    return {
        "status": "production-routed",
        "stock_bytes_replaced": BODY_BYTES,
        "source_owned_bytes_added": sum(row[0] for row in leaf_contract.values()),
        "alignment_bytes_added": sum(row[2] for row in leaf_contract.values()),
        "strict_relocations": sum(row[1] for row in leaf_contract.values()),
        "source_only_functions_compiled": 2,
        "manifest_regions": len(regions),
        "flash_plan_counts": counts,
        "proprietary_source_copied": False,
        "public_behavior_license": "Apache-2.0",
        "transport_rejection_preserves_fragment": True,
        "partial_l2cap_header_hardened": True,
        "overlong_continuation_hardened": True,
        "watermark_validation_hardened": True,
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned HCI core input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 24:
        raise AuditError("R4 hci_core.c source inventory changed")
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row for row in rows if row["stock_status"] == "source_only"]
    expected_source_only = ["hciCoreTxAclDataFragmented", "HciSetAclQueueWatermarks"]
    if len(linked) != 22 or [row["function"] for row in source_only] != expected_source_only:
        raise AuditError("HCI core function inclusion changed")

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
        raise AuditError("HCI core body concatenation changed")
    if sha256(image_slice(blob, MODULE_START, MODULE_END)) != MODULE_SHA256:
        raise AuditError("HCI core physical interval changed")

    literal_raw = image_slice(blob, *LITERAL_POOL)
    if sha256(literal_raw) != LITERAL_POOL_SHA256:
        raise AuditError("HCI core literal pool changed")
    for cell, expected in TAIL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"HCI core literal changed at 0x{cell:08x}")

    decoder = load_decoder()
    edges = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            edges.append((address, target))
    if edges != DIRECT_CALL_EDGES or packed_pairs_digest(edges) != DIRECT_CALL_DIGEST:
        raise AuditError("HCI core direct-call closure changed")

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
        raise AuditError("stored HCI core entry/interior pointer appeared")

    if occurrences(blob, HCI_CORE_CB) != [0x0052AE14, 0x00530D68, 0x00569D28]:
        raise AuditError("hciCoreCb reference closure changed")
    if occurrences(blob, HCI_CB) != [
        0x0052AE18, 0x0052B6B8, 0x00530D6C, 0x00536810,
        0x00569D48, 0x0056B140, 0x0056B7C8,
    ]:
        raise AuditError("hciCb reference closure changed")
    if occurrences(blob, HCI_CORE_CIS) != [0x0052AE20]:
        raise AuditError("HCI CIS-array literal closure changed")

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
            "inline_and_tail_data_bytes": len(literal_raw),
            "direct_bl_ingress_sites": len(edges),
            "stored_entry_pointers": 0,
            "strict_interior_pointers": 0,
        },
        "abi": {
            "hci_core_cb": HCI_CORE_CB,
            "hci_cb": HCI_CB,
            "hci_le_sup_feat_cfg": HCI_LE_SUP_FEAT_CFG,
            "hci_core_cis": HCI_CORE_CIS,
            "connection_records": 3,
            "connection_record_bytes": 0x1C,
            "cis_records": 6,
            "le_feature_bits": 64,
            "acl_queue_offset": 0x70,
            "flow_callback_offset_in_hci_cb": 0x14,
        },
        "lineage": {
            "public_behavior_source": "Packetcraft Cordio r20.05c common/hci_core.c",
            "public_behavior_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "public_behavior_license": "Apache-2.0",
            "selected_oracle": "AmbiqSuite R4.4.1 later official import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "1f81040608ca6f977d37a58aad5ab0b63229d607",
            "selected_sha256": "03ab8c9d340dd8cc9958779f6e336188cca2bbbc92ef39759dc165e84835e549",
            "r25_source_functions": 19,
            "r44_source_functions": 24,
            "historical_generating_commit_resolved": False,
            "whole_file_source_exact": False,
            "stock_excludes_r44_neuralspot_delay": True,
            "stock_excludes_nsx_priority_trace_path": True,
            "license": "Arm Cordio proprietary SLA",
        },
        "behavior": {
            "transport_send_returns_success": True,
            "acl_reassembly_handles_short_first_fragment": True,
            "reset_frees_three_connection_fragment_sets": True,
            "reset_initializes_six_cis_handles": True,
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
        print("Ambiq hci_core production-routed: 22 linked / 2 source-only; R4-era 64-bit/CIS ABI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
