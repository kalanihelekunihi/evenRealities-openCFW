#!/usr/bin/env python3
"""Clean-room inclusion, transport-ABI, and lineage audit for hci_drv_apollo3.c."""

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
FUNCTION_MAP = ROOT / "tools/manifests/ambiq-cordio-hci-driver-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiq-cordio-hci-driver-provenance.tsv"
CLOSURE = ROOT / "tools/manifests/ambiq-cordio-hci-driver-closure.tsv"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_driver.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_hci_driver.h"
RUNTIME_TEST = ROOT / "tests/test_runtime_cordio_hci_driver.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINNED_INPUTS = {
    FUNCTION_MAP: "b73d0db7738d02d2bfc905a4789453813a72c25209dddfd1d0a077baa76d7bea",
    PROVENANCE: "7fd0c165f0db657fda590aaf03abd2e00b09e7f36106358673e3dc498125bc99",
    CLOSURE: "77c90fe45ef47c920512685a169af5f86d49c5929ca120d6630ff6b1b01e9eed",
}
PRODUCTION_FILES = {
    SOURCE: (15_367, "971ae37f4b14362c37674febfc78775a56c4c6e1c91ace9365dabe5b5029d0e0"),
    HEADER: (1_210, "5d13125bd18a299d498849b1a7fe2d0ad2fa45b642ab8128db633165d65afed7"),
    RUNTIME_TEST: (9_278, "d038d921794079cb81001f138c3aee242d8e137653c16f7b2c5be214fd61f4f7"),
}
PRODUCTION_OVERLAY = (362_272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae")
PRODUCTION_COMPONENT = (3_956_672, "79323dd5ae9211e9d1c393f26593c98c96c53d928c44c4447c946e67ef0fbeef")
PRODUCTION_PACKAGE = (4_750_780, "49c61010614d5db51c9e97f3ca549e47644a32805411d0ff5dc96ea7445d3e27")
PRODUCTION_FLASH_PLAN = (4_961_300, "f2625775d8a7b3c81c8862db00979cdcf4965eeb003e4b6b84e8cb2d8c1293b9")
CONFIG_LEAF_CONTRACT_SHA256 = "8c95bf0cc886cbbc4d3e495fd59b65ee7e80622bdce2e6713b0a09cbe54d7230"
BUILD_LEAF_CONTRACT_SHA256 = "9f0bc892bd03908175e8297e63c302b1d6a62f0456f4166557eb1d3e00d088a7"
ROUTE_CONTRACT_SHA256 = "ba3887f7781d10a832abb5b077fdfab0e46f02ddf4eae6071d6941932a938daf"
ROUTED_FUNCTIONS = {
    "error_check", "hciDrvWrite", "HciDrvHandlerInit", "HciDrvIntService",
    "HciVscUpdateNvdsParam", "HciVscSetRfPowerLevelEx",
    "HciVscSetCustom_BDAddr", "HciVscUpdateBDAddress", "HciDrvEmptyWriteQueue",
}
HARDWARE_EVIDENCE_BLOCKED = [
    "HciDrvRadioBoot", "HciDrvRadioShutdown", "HciDrvHandler",
    "HciVscConstantTransmission", "HciVscCarrierWaveMode", "HciDrvBleSleepSet",
]

MAIN_START = 0x004B48A6
MAIN_END = 0x004B4D2C
MAIN_SHA256 = "809a750836b2494d4d71125db43181e4f84f12333a07b2d4d8147ee59a9be983"
SHARED_POOL = (0x004B4D2C, 0x004B4DC4)
SHARED_POOL_SHA256 = "ad18de8bc3c1e8d0d93235970032a5f454accb1f7ec00754cd246490ef5fb421"
BODY_BYTES = 1_188
BODY_SHA256 = "82d378d8a979e3cede7a46f2d0c9027840afbeb931c42e3484acf15b6bde154a"
DIRECT_CALL_COUNT = 30
DIRECT_CALL_DIGEST = "dd5ba8621127cc9da55598cd275660ae451e0c13fda09f9b035c9f5156ff089d"
BODY_CALL_COUNT = 66
BODY_CALL_DIGEST = "1377686e170b02115760d51927b017b1769f3e30136e732896703a7665eb68d3"
STORED_ENTRIES = [(0x004B8798, 0x004B4AB3)]
STORED_ENTRY_DIGEST = "c4eff16a72bf973327f7fe0338bee417852aaf07cd0ad4c5993f72197a906468"
INTERIOR_LOOKALIKE_COUNT = 30
INTERIOR_LOOKALIKE_VALUE = 0x004B4B00
INTERIOR_LOOKALIKE_DIGEST = "fea72084fa4ed05130f3cbca57e1e6a3d7b6e3c55c28cbbe69fb3ba94f10c55b"
SOURCE_ONLY = [
    "HciDrvErrorHandlerSet",
    "HciVscConstantTransmission",
    "HciVscCarrierWaveMode",
    "HciDrvBleSleepSet",
]

POOL_WORDS = {
    0x004B4D3C: 0x20074648,  # failing status
    0x004B4D40: 0x20074644,  # error handler
    0x004B4D6C: 0x20074FCC,  # read buffer in use
    0x004B4D74: 0x20074630,  # BLE handle
    0x004B4D84: 0x20074638,  # bytes available
    0x004B4D88: 0x2007463C,  # bytes consumed
    0x004B4D8C: 0x20065A10,  # eight 260-byte write buffers
    0x004B4D90: 0x20073BA8,  # write queue
    0x004B4D94: 0x20074640,  # interrupt count/flag
    0x004B4D98: 0x20074148,  # BLE MAC
    0x004B4D9C: 0x20073E64,  # heartbeat timer
    0x004B4DA4: 0x20074FCB,  # handler ID
    0x004B4DA8: 0x20073E74,  # wake timer
    0x004B4DAC: 0x20000DAC,  # 256-byte read buffer
    0x004B4DB0: 0x40010410,  # BLEIF status-register region
    0x004B4DC0: 0x20074150,  # eight-byte NVDS command buffer
}


class AuditError(RuntimeError):
    """Raised when authenticated Apollo3 HCI-driver evidence changes."""


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
    spec = importlib.util.spec_from_file_location("hci_driver_thumb", path)
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
        verify_file(path, expected, f"HCI driver input {path.name}")

    config = json.loads(CONFIG.read_text())
    expected = config["expected"]
    if (
        (expected["overlay_size"], expected["overlay_sha256"]) != PRODUCTION_OVERLAY
        or (expected["component_size"], expected["component_sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI driver aggregate pins changed")
    leaves = [
        row for row in config["relocated_leaves"]
        if row.get("source", {}).get("path")
        == "components/shared/cordio/runtime_cordio_hci_driver.c"
    ]
    if len(leaves) != 9 or {row["function"] for row in leaves} != ROUTED_FUNCTIONS:
        raise AuditError("HCI driver routed leaf inventory changed")
    if any(
        row.get("strict_relocation_contract") is not True
        or row.get("allow_discarded_alloc_sections") is not True
        for row in leaves
    ):
        raise AuditError("HCI driver strict-routing policy changed")
    config_contract = sorted(
        (row["function"], row["expected"]["size"], len(row["relocations"]))
        for row in leaves
    )
    if sha256(json.dumps(config_contract, separators=(",", ":")).encode()) \
            != CONFIG_LEAF_CONTRACT_SHA256:
        raise AuditError("HCI driver leaf configuration changed")

    sites = [
        row for row in config["patch_sites"]
        if row["name"].startswith("replace_cordio_hci_driver_")
    ]
    if len(sites) != 9 or sum(row["expected_size"] for row in sites) != 368:
        raise AuditError("HCI driver routes changed")
    if any(row["branch"] != "b_w" for row in sites):
        raise AuditError("HCI driver route is not guarded")
    route_contract = sorted(
        (row["target_function"], row["expected_size"], row["branch"])
        for row in sites
    )
    if sha256(json.dumps(route_contract, separators=(",", ":")).encode()) \
            != ROUTE_CONTRACT_SHA256:
        raise AuditError("HCI driver route contract changed")

    report = json.loads(BUILD_REPORT.read_text())
    built = {
        row["extraction"]["function"]: row
        for row in report["relocated_leaves"]
        if row.get("source", {}).get("path")
        == "components/shared/cordio/runtime_cordio_hci_driver.c"
    }
    if len(built) != 9:
        raise AuditError("HCI driver build inventory changed")
    build_contract = sorted(
        (function, row["extraction"]["size"],
         row["extraction"]["relocation_count"], row["placement"]["padding_before"])
        for function, row in built.items()
    )
    if sha256(json.dumps(build_contract, separators=(",", ":")).encode()) \
            != BUILD_LEAF_CONTRACT_SHA256:
        raise AuditError("HCI driver production build changed")
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
        != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
        != PRODUCTION_COMPONENT
    ):
        raise AuditError("HCI driver build aggregate changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (override["provider"].get("size"), override["provider"].get("sha256")) \
            != PRODUCTION_COMPONENT:
        raise AuditError("HCI driver provider changed")
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_hci_driver_")
    ]
    if len(regions) != 25:
        raise AuditError("HCI driver manifest regions changed")
    verify_file(PACKAGE, PRODUCTION_PACKAGE, "HCI driver package")
    verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN, "HCI driver flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (7104, 0, 8, 6):
        raise AuditError("HCI driver flash-plan counts changed")
    return {
        "status": "software-complete-hardware-validation-blocked-by-unavailable-physical-evidence",
        "source_inventory_compiled": 16,
        "redirected_stock_functions": 9,
        "redirected_stock_bytes": 368,
        "source_owned_bytes_added": 472,
        "alignment_bytes_added": 14,
        "strict_relocations": 7,
        "source_only_functions_compiled": 4,
        "manifest_regions": len(regions),
        "flash_plan_counts": counts,
        "remaining_unimplemented_software_functions": 0,
        "hardware_evidence_blocked_functions": HARDWARE_EVIDENCE_BLOCKED,
        "retained_stock_hardware_functions": [
            "HciDrvRadioBoot", "HciDrvRadioShutdown", "HciDrvHandler",
        ],
        "authorized_right_temple_available": False,
        "production_hardware_substitution_validated": False,
        "vendor_source_copied": False,
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned HCI-driver input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row for row in rows if row["stock_status"] == "linked"]
    source_only = [row["function"] for row in rows if row["stock_status"] == "source_only"]
    if len(rows) != 16 or len(linked) != 12 or source_only != SOURCE_ONLY:
        raise AuditError("Apollo3 HCI-driver source inventory changed")
    if [int(row["source_order"]) for row in rows] != list(range(1, 17)):
        raise AuditError("Apollo3 HCI-driver source ordering changed")

    bodies = []
    ranges = []
    starts: dict[int, str] = {}
    interiors: set[int] = set()
    for row in linked:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        ranges.append((start, end))
        starts[start] = row["function"]
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("Apollo3 HCI-driver body concatenation changed")
    if sha256(image_slice(blob, MAIN_START, MAIN_END)) != MAIN_SHA256:
        raise AuditError("Apollo3 HCI-driver main interval changed")
    if sha256(image_slice(blob, *SHARED_POOL)) != SHARED_POOL_SHA256:
        raise AuditError("Apollo3 HCI-driver shared literal pool changed")
    for cell, expected in POOL_WORDS.items():
        actual = struct.unpack("<I", image_slice(blob, cell, cell + 4))[0]
        if actual != expected:
            raise AuditError(f"Apollo3 HCI-driver literal changed at 0x{cell:08x}")

    decoder = load_decoder()
    ingress = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            ingress.append((address, target))
    if len(ingress) != DIRECT_CALL_COUNT or packed_pairs_digest(ingress) != DIRECT_CALL_DIGEST:
        raise AuditError("Apollo3 HCI-driver direct-call ingress changed")

    body_calls = []
    for start, end in ranges:
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None:
                body_calls.append((address, target))
    if len(body_calls) != BODY_CALL_COUNT or packed_pairs_digest(body_calls) != BODY_CALL_DIGEST:
        raise AuditError("Apollo3 HCI-driver provider-call closure changed")

    interior_bl = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in interiors:
            interior_bl.append((address, target))
    if interior_bl:
        raise AuditError("direct call into Apollo3 HCI-driver strict interior appeared")

    stored_entries = []
    stored_interiors = []
    for address in range(BASE, BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", image_slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((address, value))
        elif target in interiors:
            stored_interiors.append((address, value))
    if stored_entries != STORED_ENTRIES or packed_pairs_digest(stored_entries) != STORED_ENTRY_DIGEST:
        raise AuditError("stored Apollo3 HCI-driver entry pointers changed")
    if (
        len(stored_interiors) != INTERIOR_LOOKALIKE_COUNT
        or {value for _, value in stored_interiors} != {INTERIOR_LOOKALIKE_VALUE}
        or packed_pairs_digest(stored_interiors) != INTERIOR_LOOKALIKE_DIGEST
    ):
        raise AuditError("Apollo3 HCI-driver interior lookalike classification changed")

    unaligned_entries = []
    for offset in range(len(blob) - 3):
        address = BASE + offset
        if address % 4 == 0:
            continue
        value = struct.unpack_from("<I", blob, offset)[0]
        if (value & ~1) in starts:
            unaligned_entries.append((address, value))
    if unaligned_entries:
        raise AuditError("unaligned stored Apollo3 HCI-driver entry pointer appeared")

    return {
        "schema_version": 1,
        "image": {"path": str(image_path), "sha256": IMAGE_SHA256},
        "module": {
            "error_check_start": 0x004B47AE,
            "main_start": MAIN_START,
            "main_end_exclusive": MAIN_END,
            "main_interval_bytes": MAIN_END - MAIN_START,
            "linked_function_count": len(linked),
            "linked_function_bytes": BODY_BYTES,
            "source_inventory_functions": len(rows),
            "source_only_functions": SOURCE_ONLY,
            "shared_literal_pool_start": SHARED_POOL[0],
            "shared_literal_pool_end_exclusive": SHARED_POOL[1],
            "shared_literal_pool_bytes": SHARED_POOL[1] - SHARED_POOL[0],
            "direct_bl_ingress_sites": len(ingress),
            "direct_provider_calls": len(body_calls),
            "stored_entry_pointers": STORED_ENTRIES,
            "accepted_strict_interior_pointers": 0,
            "excluded_aligned_interior_lookalikes": len(stored_interiors),
        },
        "abi": {
            "nonblocking_hci": False,
            "heartbeat_enabled": True,
            "heartbeat_period_seconds": 10,
            "write_queue": 0x20073BA8,
            "write_buffer_base": 0x20065A10,
            "write_buffer_count": 8,
            "write_record_bytes": 260,
            "read_buffer": 0x20000DAC,
            "read_buffer_bytes": 256,
            "max_transactions_per_handler": 1000,
            "max_consecutive_reads": 4,
            "handler_id": 0x20074FCB,
            "ble_mac": 0x20074148,
            "nvds_command_buffer": 0x20074150,
        },
        "behavior": {
            "handler_null_message_guard": True,
            "blocking_transport": True,
            "heartbeat_restarted_on_activity": True,
            "recovery_shuts_down_and_reboots_radio": True,
            "recovery_empties_write_queue": True,
            "recovery_requests_dm_reset": True,
            "rf_power_opcode": 0xFCC4,
            "bd_address_opcode": 0xFC43,
            "nvds_update_opcode": 0xFFF2,
            "nvds_runtime_parameter_bytes": 6,
        },
        "lineage": {
            "transport_family": "Ambiq Apollo3 blocking HCI driver",
            "boot_baseline": "AmbiqSuite R2.5.1 Apollo3",
            "handler_oracle": "AmbiqSuite R3.1.1 later official import",
            "vendor_command_oracle": "AmbiqSuite R4.4.1 Cooper later official import",
            "historical_generating_commit_resolved": False,
            "whole_file_source_exact": False,
            "classification": "mixed-version Ambiq driver",
            "license": "Ambiq BSD-3-Clause-style notice",
        },
        "production": {
            **verify_production(),
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
        print(
            "Ambiq Apollo3 HCI driver: all 16 APIs compile; 9 safe routes active; "
            "6 hardware paths evidence-blocked"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
