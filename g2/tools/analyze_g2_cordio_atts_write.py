#!/usr/bin/env python3
"""Fail-closed audit for Cordio's ATT server write processors."""

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
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-atts-write-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-atts-write-provenance.tsv"
PINS = {
    ROOT / "components/shared/cordio/runtime_cordio_atts_write.c": "7d1fb3be9f754d518c2ee88826c7f809671bf3ca71ce2af2ad568f78bb711e05",
    ROOT / "components/shared/cordio/runtime_cordio_atts_write.h": "897e103c5e77df84da51929b5f41dabcb7fe3a1d4ad0bc6102486828ee239fac",
    MAP: "d44b3f94dc3b716680efd82a7f5493596ba609d51729f1ead5a027a93faea4fe",
    PROVENANCE: "ddb213ef571c5fa891d707026d58f2bb1da03a889509249340b3ecd3f2c365fc",
}

FUNCTIONS = {
    "attsExecPrepWrite": (0x005A5D94, 0x005A5E3A, "f1cc4fe51476d5aa047e7927ef1a77c29370b195396682ec12fee51fd09d8244"),
    "attsProcWrite": (0x005A5E3A, 0x005A5FC2, "db8b9b061c1855b40870fc7296335a6fb55f8f0b21773de2549a2c7b35ee3971"),
    "attsProcPrepWriteReq": (0x005A5FC2, 0x005A6170, "110a713e8e79398bf5e9b11a4b51b5831563ad1339c6de5ddcdf4a8797510bed"),
    "attsProcExecWriteReq": (0x005A6170, 0x005A6258, "90375b68086d75df1d9a7b04155578b24b768b46619d2484447da891516c8c3c"),
}
SOURCE_ONLY = ["AttsContinueWriteReq"]
BODY_CONCAT_SHA = "77f20f9bedbee5c74d98b4282c874f0bff39d0713e4a11ab64e08c66d417a9f4"
PHYSICAL = (0x005A5D94, 0x005A6260)
PHYSICAL_SHA = "5ff375c13498c4194fda9790e70ee116e8257cfc659c6aa6cfd95f4fc3b34ebc"
TAIL = (0x005A6258, 0x005A6260, "5601ead32bc60f93d83681b03065f721f9bf77e9a816a242281b86a4d20edd3b")
TAIL_WORDS = [0x2006E5F0, 0x200004B4]

OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_atts_write.c"
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_atts_execute_prepared_write",
    "open_cfw_cordio_atts_process_write",
    "open_cfw_cordio_atts_process_prepare_write_request",
    "open_cfw_cordio_atts_process_execute_write_request",
]
CANDIDATE_LEAF_METRICS = [
    (336684, 206, 1),
    (336892, 358, 5),
    (337260, 880, 8),
    (338140, 200, 11),
]

CALLERS = {
    "attsExecPrepWrite": [0x005A61FC],
    "attsProcWrite": [], "attsProcPrepWriteReq": [], "attsProcExecWriteReq": [],
}
CALLER_DIGESTS = {
    "attsExecPrepWrite": "270e48df95fad1282366f48c11aefa19db3cdf4093b29b940a2d84ee9d176bc7",
    "attsProcWrite": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcPrepWriteReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcExecWriteReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}
DIRECT_CALLEE_SITE_COUNT = 28
DIRECT_CALLEE_DIGEST = "b84964819f0bec3a9c3ee917f3476623faaf0c7498eb3f51fb1bb493219988dc"
WIDE_INSTRUCTION_SECOND_HALVES = {0x005A5FE6}
WIDE_INSTRUCTION_SECOND_HALF_SHA = "493d8fe532505fbd3cc1dd834cb21af8aea2cad05974f742d9e7c19d0a4bfe9a"

ATTS_PROC_FCN_TBL = 0x2000045C
PROCESSOR_METHODS = {9: "attsProcWrite", 10: "attsProcWrite", 11: "attsProcPrepWriteReq", 12: "attsProcExecWriteReq"}
PROCESSOR_WORDS = {9: 0x005A5E3B, 10: 0x005A5E3B, 11: 0x005A5FC3, 12: 0x005A6171}
INITIALIZER_ENTRY_WINDOWS = [(0x00791AC6, 0x005A5FC3)]
ACCIDENTAL_INTERIOR_WINDOWS = [(0x00597287, 0x005A6041), (0x00597359, 0x005A6041), (0x0064A9C3, 0x005A6200)]


class AuditError(RuntimeError):
    """Raised when authenticated ATT write-processor evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def load_tool(name: str, filename: str):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / filename)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_inventory() -> tuple[list[str], list[str]]:
    with MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    linked = [row["function"] for row in rows if row["stock_status"] == "linked"]
    source_only = [row["function"] for row in rows if row["stock_status"] == "source_only"]
    if len(linked) + len(source_only) != len(rows):
        raise AuditError("unexpected atts_write source-map status")
    return linked, source_only


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")
    linked, source_only = source_inventory()
    if linked != list(FUNCTIONS) or source_only != SOURCE_ONLY:
        raise AuditError("atts_write source inventory changed")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError(f"stock atts_write body changed: {name}")
        bodies.append(data)
    if sha(b"".join(bodies)) != BODY_CONCAT_SHA or sha(image_slice(blob, *PHYSICAL)) != PHYSICAL_SHA:
        raise AuditError("atts_write physical/body concatenation changed")
    tail = image_slice(blob, TAIL[0], TAIL[1])
    if sha(tail) != TAIL[2] or list(struct.unpack("<2I", tail)) != TAIL_WORDS:
        raise AuditError("atts_write literal tail changed")

    flashdb = load_tool("atts_write_flashdb", "analyze_g2_flashdb.py")
    initialized = flashdb._decode_initialized_sram(blob)
    table = flashdb._sram_slice(initialized, ATTS_PROC_FCN_TBL, 72)
    table_words = list(struct.unpack("<18I", table))
    for method, expected in PROCESSOR_WORDS.items():
        if table_words[method] != expected:
            raise AuditError(f"live atts_write method {method} changed")

    decoder = load_tool("atts_write_thumb", "recover_apollo_embedded_source_paths.py")
    direct_by_target: dict[int, list[int]] = {}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target is not None:
            direct_by_target.setdefault(target, []).append(address)
    for name, (start, _, _) in FUNCTIONS.items():
        sites = direct_by_target.get(start, [])
        if sites != CALLERS[name]:
            raise AuditError(f"direct caller closure changed: {name}")
        if sha(b"".join(struct.pack("<I", site) for site in sites)) != CALLER_DIGESTS[name]:
            raise AuditError(f"direct caller digest changed: {name}")
    false_bl_bytes = b"".join(image_slice(blob, address, address + 4) for address in sorted(WIDE_INSTRUCTION_SECOND_HALVES))
    if sha(false_bl_bytes) != WIDE_INSTRUCTION_SECOND_HALF_SHA:
        raise AuditError("atts_write wide-instruction overlap changed")
    callee_edges = []
    for _, (start, end, _) in FUNCTIONS.items():
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None and address not in WIDE_INSTRUCTION_SECOND_HALVES:
                callee_edges.append((address, target))
    if len(callee_edges) != DIRECT_CALLEE_SITE_COUNT or sha(b"".join(struct.pack("<II", *edge) for edge in callee_edges)) != DIRECT_CALLEE_DIGEST:
        raise AuditError("atts_write direct-callee closure changed")

    entries = {start for start, _, _ in FUNCTIONS.values()}
    interiors = {address for start, end, _ in FUNCTIONS.values() for address in range(start + 1, end)}
    stored_entries, stored_interiors = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in entries:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != INITIALIZER_ENTRY_WINDOWS or stored_interiors != ACCIDENTAL_INTERIOR_WINDOWS:
        raise AuditError("atts_write stored-entry/interior window closure changed")
    if any(address % 2 == 0 for address, _ in stored_interiors):
        raise AuditError("an accidental interior byte window became aligned")
    for target, sites in direct_by_target.items():
        if target in interiors and sites:
            raise AuditError("unexpected direct BL into atts_write interior")

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise AuditError("ATTS write production leaf inventory changed")
    source_hash = PINS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_LEAF_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise AuditError(f"ATTS write production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, (function, (name, (start, end, expected))) in enumerate(
        zip(CANDIDATE_FUNCTIONS, FUNCTIONS.items()), 1
    ):
        site = sites.get(f"replace_cordio_atts_write_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise AuditError(f"ATTS write production route changed: {name}")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = sum(
        right["expected"]["offset"]
        - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (1644, 12, 25):
        raise AuditError("ATTS write production metrics changed")

    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    validate_apollo_main_artifacts(ROOT, AuditError, "ATT server write")
    if len([
        row for row in override["regions"]
        if row["name"].startswith("cordio_atts_write_")
    ]) != 10:
        raise AuditError("ATTS write component/manifest ownership changed")

    return {
        "schema_version": 1,
        "module": {
            "classification": "linked_eatt_server_write_processors",
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "owned_noncode_bytes": TAIL[1] - TAIL[0],
            "source_inventory_functions": len(FUNCTIONS) + len(SOURCE_ONLY),
            "source_only_functions": SOURCE_ONLY,
            "direct_bl_ingress_sites": sum(len(sites) for sites in CALLERS.values()),
            "direct_callee_sites": len(callee_edges),
            "raw_bl_like_wide_instruction_overlaps": len(WIDE_INSTRUCTION_SECOND_HALVES),
            "live_processor_table_entries": len(PROCESSOR_METHODS),
            "initializer_stream_entry_windows": len(INITIALIZER_ENTRY_WINDOWS),
            "accidental_interior_byte_windows": len(ACCIDENTAL_INTERIOR_WINDOWS),
            "strict_interior_pointers": 0,
        },
        "dispatch": {
            "processor_table_live_sram": ATTS_PROC_FCN_TBL,
            "methods": {str(method): {"name": PROCESSOR_METHODS[method], "entry": PROCESSOR_WORDS[method]} for method in PROCESSOR_METHODS},
            "initializer_stream_is_not_runtime_table": True,
        },
        "architecture": {
            "write_request_and_command_share_processor": True,
            "per_connection_prepare_write_queues": True,
            "prepare_queue_count_configured": True,
            "execute_cancel_and_commit": True,
            "response_pending_state_supported": True,
            "continue_pending_response_api_linked": False,
        },
        "abi": {
            "atts_cb": 0x2006E5F0, "p_att_cfg": 0x200004B4,
            "prep_write_queues_offset": 0x238, "prep_write_queue_stride": 8,
            "server_ccb_main_offset": 0x10, "server_ccb_conn_id_offset": 0x24,
            "server_ccb_slot_offset": 0x25,
        },
        "lineage": {
            "selected_source": "Packetcraft r20.05c / byte-identical AmbiqSuite R4.4.1 import",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "1b41582c58124a49014317b987f304dd216ce100",
            "selected_sha256": "8c205dcd4162d5b3e30322bb13dbd552568a5aa62ecddabf7f0a69edad17d7b1",
            "historical_generating_commit_resolved": False, "license": "Apache-2.0",
        },
        "production": {
            "status": "routed",
            "functions": 4,
            "stock_bytes_replaced": 1220,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 4,
            "source_only_api": "AttsContinueWriteReq implemented and ARM-compiled; not linked by stock",
            "hardware_validation": "deferred by project direction",
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
        print("Cordio atts_write closed: 4 linked functions / 4 initialized method cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
