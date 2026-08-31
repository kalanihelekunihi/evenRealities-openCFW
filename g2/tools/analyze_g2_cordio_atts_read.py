#!/usr/bin/env python3
"""Fail-closed audit for Cordio's optional ATT server read processors."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-atts-read-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-atts-read-provenance.tsv"
PINS = {
    ROOT / "components/shared/cordio/runtime_cordio_atts_read.c": "87370930986311973aedc969c9522f49915a72d59a7784adaa9df2c86a10d6bd",
    ROOT / "components/shared/cordio/runtime_cordio_atts_read.h": "88a704f3aa23d77272c44c39f8617ff9a60f0c283cd2f063fc45cec247eb6ec9",
    MAP: "1d6257ab332d8046920a6f71e4de7b3d46418fe6643933111efaeda13a8eb26d",
    PROVENANCE: "f24e30cca8b89be7001ef097aca853845084c0b80c7373ce370c251d90702af6",
}

OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_atts_read.c"
CANDIDATE_PREVIOUS_OVERLAY_SIZE = 273210
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_atts_find_uuid_in_range",
    "open_cfw_cordio_atts_find_service_group_end",
    "open_cfw_cordio_atts_process_read_blob_request",
    "open_cfw_cordio_atts_process_find_type_request",
    "open_cfw_cordio_atts_process_read_type_request",
    "open_cfw_cordio_atts_process_read_multiple_request",
    "open_cfw_cordio_atts_process_read_group_type_request",
]
CANDIDATE_LEAF_METRICS = [
    (273212, 142, 1), (273356, 154, 2), (273512, 326, 5),
    (273840, 452, 9), (274292, 740, 9), (275032, 376, 6),
    (275408, 596, 12),
]

FUNCTIONS = {
    "attsFindUuidInRange": (0x0056D93C, 0x0056D9EC, "a87c995a5a4319ff7adabffc2946f875f04a11bdbad8a12d6181df8fd7febb0c"),
    "attsFindServiceGroupEnd": (0x0056D9EC, 0x0056DA9E, "4eaf37769775fc2f86f2ad896e4e0ee3f77fd96d3e09446bc498252d915006fb"),
    "attsProcReadBlobReq": (0x0056DA9E, 0x0056DC04, "71188999274558ec622215c646346306971d3dd0e4c3ee2a72f4f605c7335ef8"),
    "attsProcFindTypeReq": (0x0056DC04, 0x0056DD9C, "9739daf6539837f081f6820579b9daeaf56f68c94025cd57c28d8efcad8a581f"),
    "attsProcReadTypeReq": (0x0056DD9C, 0x0056E0DE, "04c0ee12ecf5930ba73d39395ffb66ea0aa4295b621e4ba7c7a19ad27fdbb1d1"),
    "attsProcReadMultReq": (0x0056E0DE, 0x0056E26C, "643ba549ddc48f243a57fcadc5e9cd19c6633b540aeaf7f54c148140f4d08e87"),
    "attsProcReadGroupTypeReq": (0x0056E26C, 0x0056E4E4, "d0a197e6da2deefb0c337d3f284bf9f5a0ad0dbcde3a109c76cfe33eaed223e1"),
}
BODY_CONCAT_SHA = "8c449cbb036fcc8a2aac443a6263142d3dd7ae6b5bf3175fdf0311ef2b3bf760"
PHYSICAL = (0x0056D93C, 0x0056E4F8)
PHYSICAL_SHA = "d54722d4facdc1e58a4636d61041c020ffe6ffd9e68a887fe1b87e7d7abbd89c"
TAIL = (0x0056E4E4, 0x0056E4F8, "200a058db672a94a438d40641e2191b8171f663ac8bcb330e4b2c3cb78e53d30")
TAIL_WORDS = [0x2006E5F0, 0x0078F550, 0x0078F552, 0x0078F54E, 0x0078F554]

CALLERS = {
    "attsFindUuidInRange": [0x00534DA6, 0x0056DCD4, 0x0056DE36, 0x0056DFA2, 0x0056E31A, 0x0056E3FC],
    "attsFindServiceGroupEnd": [0x0056DD24, 0x0056E3A6, 0x0056E45A],
    "attsProcReadBlobReq": [], "attsProcFindTypeReq": [], "attsProcReadTypeReq": [],
    "attsProcReadMultReq": [], "attsProcReadGroupTypeReq": [],
}
CALLER_DIGESTS = {
    "attsFindUuidInRange": "189276a77029782ab8cf60bae5dccaa6bef145be2a826a25673f1cf8b58fcd9c",
    "attsFindServiceGroupEnd": "74508f0e47159cafd89aecddb40b4868c1e3929161b1e2f4f73e2282ce47bbe4",
    "attsProcReadBlobReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcFindTypeReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcReadTypeReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcReadMultReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsProcReadGroupTypeReq": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}
DIRECT_CALLEE_SITE_COUNT = 50
DIRECT_CALLEE_DIGEST = "cddb97078ff624680dbd9cc5c986f4e11c39576d51b0c0d0fa0389e83b32b5ec"
WIDE_INSTRUCTION_SECOND_HALVES = {0x0056DDD8, 0x0056E150, 0x0056E2AA}
WIDE_INSTRUCTION_SECOND_HALF_SHA = "f22ffb789b5fd1855e0333579f20ada3ff647d6632063dd8a88210d71e186742"

ATTS_PROC_FCN_TBL = 0x2000045C
PROCESSOR_METHODS = {
    3: "attsProcFindTypeReq", 4: "attsProcReadTypeReq", 6: "attsProcReadBlobReq",
    7: "attsProcReadMultReq", 8: "attsProcReadGroupTypeReq",
}
PROCESSOR_WORDS = {3: 0x0056DC05, 4: 0x0056DD9D, 6: 0x0056DA9F, 7: 0x0056E0DF, 8: 0x0056E26D}
INITIALIZER_ENTRY_WINDOWS = [
    (0x00791AA8, 0x0056DC05), (0x00791AAC, 0x0056DD9D), (0x00791AB4, 0x0056DA9F),
    (0x00791AB8, 0x0056E0DF), (0x00791ABC, 0x0056E26D),
]
ACCIDENTAL_INTERIOR_WINDOWS = [(0x00643387, 0x0056E1FF)]
GUARD_WINDOWS = [
    (0x0056DD2C, 0x0056DD38, "0df15f3460cb127250c3d94c97e9f1a141d382cb3e9c58e4abc57ef469baabf7"),
    (0x0056E034, 0x0056E048, "e5844f6c47a556a48f2099e1d88ad9f4e98d00b97cae57cf2ff3bb74970ae303"),
    (0x0056E42E, 0x0056E442, "5b41cd5d40195749d8dc12c37c8ba0ab75ec0077601b87c215518bd445f68855"),
]


class AuditError(RuntimeError):
    """Raised when authenticated ATT read-processor evidence changes."""


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


def source_inventory() -> list[str]:
    with MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(row["stock_status"] != "linked" for row in rows):
        raise AuditError("unexpected atts_read source-map status")
    return [row["function"] for row in rows]


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")
    if source_inventory() != list(FUNCTIONS):
        raise AuditError("atts_read source inventory changed")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError(f"stock atts_read body changed: {name}")
        bodies.append(data)
    if sha(b"".join(bodies)) != BODY_CONCAT_SHA or sha(image_slice(blob, *PHYSICAL)) != PHYSICAL_SHA:
        raise AuditError("atts_read physical/body concatenation changed")
    tail = image_slice(blob, TAIL[0], TAIL[1])
    if sha(tail) != TAIL[2] or list(struct.unpack("<5I", tail)) != TAIL_WORDS:
        raise AuditError("atts_read literal tail changed")
    for start, end, expected in GUARD_WINDOWS:
        if sha(image_slice(blob, start, end)) != expected:
            raise AuditError("atts_read fit-check topology changed")

    flashdb = load_tool("atts_read_flashdb", "analyze_g2_flashdb.py")
    initialized = flashdb._decode_initialized_sram(blob)
    table = flashdb._sram_slice(initialized, ATTS_PROC_FCN_TBL, 72)
    table_words = list(struct.unpack("<18I", table))
    for method, expected in PROCESSOR_WORDS.items():
        if table_words[method] != expected:
            raise AuditError(f"live atts_read method {method} changed")

    decoder = load_tool("atts_read_thumb", "recover_apollo_embedded_source_paths.py")
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
        raise AuditError("atts_read wide-instruction overlap changed")
    callee_edges = []
    for _, (start, end, _) in FUNCTIONS.items():
        for address in range(start, end, 2):
            target = decoder._thumb_bl_target(blob, address)
            if target is not None and address not in WIDE_INSTRUCTION_SECOND_HALVES:
                callee_edges.append((address, target))
    if len(callee_edges) != DIRECT_CALLEE_SITE_COUNT or sha(b"".join(struct.pack("<II", *edge) for edge in callee_edges)) != DIRECT_CALLEE_DIGEST:
        raise AuditError("atts_read direct-callee closure changed")

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
        raise AuditError("atts_read stored-entry/interior window closure changed")
    if any(address % 2 == 0 for address, _ in stored_interiors):
        raise AuditError("an accidental interior byte window became aligned")
    for target, sites in direct_by_target.items():
        if target in interiors and sites:
            raise AuditError("unexpected direct BL into atts_read interior")

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise AuditError("ATTS read production leaf inventory changed")
    source_hash = PINS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_LEAF_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise AuditError(f"ATTS read production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, (function, (name, (start, end, expected))) in enumerate(
        zip(CANDIDATE_FUNCTIONS, FUNCTIONS.items()), 1
    ):
        site = sites.get(f"replace_cordio_atts_read_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise AuditError(f"ATTS read production route changed: {name}")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = leaves[0]["expected"]["offset"] - CANDIDATE_PREVIOUS_OVERLAY_SIZE
    alignment += sum(
        right["expected"]["offset"]
        - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (2786, 8, 44):
        raise AuditError("ATTS read production metrics changed")

    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    validate_apollo_main_artifacts(ROOT, AuditError, "ATT server read")
    if len([
        row for row in override["regions"]
        if row["name"].startswith("cordio_atts_read_")
    ]) != 18:
        raise AuditError("ATTS read component/manifest ownership changed")

    return {
        "schema_version": 1,
        "module": {
            "classification": "linked_optional_server_read_processors",
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "owned_noncode_bytes": TAIL[1] - TAIL[0],
            "source_inventory_functions": len(FUNCTIONS), "source_only_functions": [],
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
            "read_blob": True, "find_by_type_value": True, "read_by_type": True,
            "read_multiple": True, "read_by_group_type": True,
            "csf_database_hash_deferral": True,
            "iar_subtraction_safe_fit_checks": True,
            "fit_check_windows": len(GUARD_WINDOWS),
        },
        "abi": {
            "atts_cb": 0x2006E5F0, "server_ccb_main_offset": 0x10, "server_ccb_slot_offset": 0x25,
            "primary_service_uuid": 0x0078F550, "secondary_service_uuid": 0x0078F552,
            "database_hash_uuid": 0x0078F54E,
        },
        "lineage": {
            "public_lower_bound": "Packetcraft r20.05c",
            "selected_source": "AmbiqSuite R4.4.1 official later import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "52a7f290710c12ecba0850175c9bc1fe21f8e0aa",
            "selected_sha256": "b07b3b63a4c6f6bc0c7f1efa11c30f17cef39360c0619db7830f86647a74a425",
            "historical_generating_commit_resolved": False, "license": "Apache-2.0",
        },
        "production": {
            "status": "routed", "functions": 7,
            "stock_bytes_replaced": 2984,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 7,
            "subtraction_safe_fit_checks": 3,
            "hardware_validation": (
                "blocked by unavailable physical evidence; future qualification requires authorized responsive G2/ATT peer evidence"
            ),
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
        print("Cordio atts_read closed: 7 linked functions / 5 initialized processor entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
