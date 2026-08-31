#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio ATT client PDU processor."""

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
BASE = 0x437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-attc-proc-function-map.tsv"
PINS = {
    ROOT / "components/shared/cordio/runtime_cordio_attc_proc.c": (
        "18f5997b9a022ab719cd3b5d13458fa2ae2c6c6187b8a4aee2d3e27e965ab901"
    ),
    ROOT / "components/shared/cordio/runtime_cordio_attc_proc.h": (
        "773a26e2d75b0465f3ad29c1d6e3ab76b36ff02fab9efacefd47c7ed4b129966"
    ),
    MAP: "7a0381b4525d16a2da37333d95765fad62bf59430366cfc261998a3215493165",
    ROOT / "tools/manifests/packetcraft-cordio-attc-proc-provenance.tsv": (
        "095ecbb46df57a4d58b7c3ac7ad0326c73fd1bb3c7b3b107254c13bdf42ac615"
    ),
}
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_attc_proc.c"
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_attc_process_error_response",
    "open_cfw_cordio_attc_process_mtu_response",
    "open_cfw_cordio_attc_process_find_or_read_response",
    "open_cfw_cordio_attc_process_read_response",
    "open_cfw_cordio_attc_process_write_response",
    "open_cfw_cordio_attc_process_read_multiple_variable_response",
    "open_cfw_cordio_attc_process_multiple_variable_notification",
    "open_cfw_cordio_attc_process_response",
    "open_cfw_cordio_attc_process_indication_notification",
    "open_cfw_cordio_attc_send_message",
    "open_cfw_cordio_attc_find_information_request",
    "open_cfw_cordio_attc_read_request",
    "open_cfw_cordio_attc_write_request",
    "open_cfw_cordio_attc_mtu_request",
    "open_cfw_cordio_attc_indication_confirm",
]
CANDIDATE_METRICS = [
    (279244,48,0),(279292,66,2),(279360,238,0),(279600,2,0),
    (279604,6,0),(279612,2,0),(279616,84,0),(279700,570,14),
    (280272,160,2),(280432,182,9),(280616,50,2),(280668,50,2),
    (280720,114,2),(280836,50,2),(280888,72,3),
]

CALLS = {
    "attcProcErrRsp": [],
    "attcProcMtuRsp": [],
    "attcProcFindOrReadRsp": [],
    "attcProcReadRsp": [],
    "attcProcWriteRsp": [],
    "attcProcReadMultVarRsp": [],
    "attcProcMultiVarNtf": [0x5311FE],
    "attcProcRsp": [0x5311CE],
    "attcProcInd": [0x5311EA],
    "attcSendMsg": [
        0x4B5754,
        0x4B5796,
        0x4B57F2,
        0x4B5832,
        0x539E40,
        0x56C4E6,
        0x56C546,
    ],
    "AttcFindInfoReq": [0x56B8F2],
    "AttcReadReq": [0x56BF06],
    "AttcWriteReq": [0x4BEB7A, 0x4BEBBE, 0x4BEC18, 0x4C47FC, 0x56BEF6],
    "AttcMtuReq": [0x46DF78, 0x53139C],
    "AttcIndConfirm": [0x531348],
}

RESPONSE_TABLE = [
    0x4B5231,
    0x4B527B,
    0x4B52C3,
    0x56C3B1,
    0x4B52C3,
    0x4B53DB,
    0x56C455,
    0x4B53DB,
    0x4B52C3,
    0x4B53DD,
    0,
    0x539DCD,
    0x4B53DD,
    0,
    0,
    0,
    0x4B53E3,
]
MIN_PDU_LENGTHS = bytes([5, 3, 2, 1, 2, 1, 1, 1, 2, 1, 3, 5, 1])


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("attc_proc_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows():
    linked, source_only = [], []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] == "linked":
                linked.append(
                    (
                        row["function"],
                        int(row["stock_start"], 0),
                        int(row["stock_end_exclusive"], 0),
                        row["stock_sha256"],
                    )
                )
            else:
                source_only.append(row["function"])
    return linked, source_only


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, expected in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != expected:
            raise RuntimeError(f"pinned input changed: {path}")

    linked, source_only = load_rows()
    if len(linked) != 15 or source_only != ["AttcCancelReq"]:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, expected in linked:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != expected:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "aa8095e5a8fc97cf677e25c77b66bbcafec262642d54154672ec547266deec57":
        raise RuntimeError("body concatenation changed")
    if sha(image_slice(blob, 0x4B5230, 0x4B59C0)) != "7e521c5695399e2c58d626a65ba261349de066bb0ac79a430105a0a5b4beb73a":
        raise RuntimeError("physical object changed")
    if sha(image_slice(blob, 0x4B598C, 0x4B59C0)) != "70186ccab44e47b4176c0cbf732923acc0f53a65aa9084b963cd47928af5f60b":
        raise RuntimeError("literal tail changed")

    path_data = image_slice(blob, 0x6DC874, 0x6DC8D4)
    if sha(path_data) != "9a3bb99503029f0e4973d75def2fa43eebfe9a7a35b19b1300bc2d307e38a336":
        raise RuntimeError("retained path changed")
    literals = {
        0x4B5998: 0x200004B4,
        0x4B599C: 0x200610AC,
        0x4B59A0: 0x700964,
        0x4B59A4: 0x785270,
        0x4B59A8: 0x2006F904,
        0x4B59B8: 0x6DC874,
    }
    for address, expected in literals.items():
        if struct.unpack_from("<I", blob, address - BASE)[0] != expected:
            raise RuntimeError(f"literal changed at {address:#x}")

    table = image_slice(blob, 0x700964, 0x7009A8)
    if sha(table) != "40b2b1622ca8902324d31e7d4f91d4d506865a9ab3b2e3a8ccffec32e98220a4":
        raise RuntimeError("response table changed")
    if list(struct.unpack("<17I", table)) != RESPONSE_TABLE:
        raise RuntimeError("response dispatch changed")
    minimums = image_slice(blob, 0x785270, 0x78527D)
    if sha(minimums) != "f71e0b9bb1d2fa415c1c022f858bbc959a113bd08f1c9db1bd2b9d93b42ecb83":
        raise RuntimeError("minimum-PDU table changed")
    if minimums != MIN_PDU_LENGTHS:
        raise RuntimeError("minimum-PDU values changed")
    if image_slice(blob, 0x78527D, 0x785280) != b"\0\0\0":
        raise RuntimeError("minimum-PDU alignment changed")
    if image_slice(blob, 0x785280, 0x785281) != b"a":
        raise RuntimeError("method-16 adjacent byte changed")
    if image_slice(blob, 0x7009A8, 0x7009AC) != b"Inva":
        raise RuntimeError("method-17 adjacent word changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in linked}
    calls = {name: [] for name, _, _, _ in linked}
    interiors = set()
    for _, start, end, _ in linked:
        interiors.update(range(start + 2, end, 2))
    interior_branches = []
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
        elif target in interiors:
            interior_branches.append((address, target))
    if calls != CALLS:
        raise RuntimeError("direct ingress changed")
    if interior_branches:
        raise RuntimeError("direct branch to strict interior found")

    stored, inside = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if not value & 1:
            continue
        target = value & ~1
        if target in starts:
            stored.append((BASE + offset, value))
        elif target in interiors:
            inside.append((BASE + offset, value))
    expected_stored = [
        (0x700964, 0x4B5231),
        (0x700968, 0x4B527B),
        (0x70096C, 0x4B52C3),
        (0x700974, 0x4B52C3),
        (0x700978, 0x4B53DB),
        (0x700980, 0x4B53DB),
        (0x700984, 0x4B52C3),
        (0x700988, 0x4B53DD),
        (0x700994, 0x4B53DD),
        (0x7009A4, 0x4B53E3),
    ]
    if stored != expected_stored:
        raise RuntimeError("stored entry-pointer closure changed")
    false_windows = [
        (0x78A0ED, 0x4B5249),
        (0x78A0FA, 0x4B5253),
        (0x78A12A, 0x4B5249),
        (0x78A135, 0x4B5253),
        (0x78A143, 0x4B5253),
        (0x78CA68, 0x4B5249),
    ]
    if inside != false_windows:
        raise RuntimeError("strict-interior byte-window closure changed")
    if image_slice(blob, 0x78CA68, 0x78CA6C) != b"IRK\0":
        raise RuntimeError("aligned ASCII pointer collision changed")

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise RuntimeError("attc_proc production leaf inventory changed")
    source_hash = PINS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_METRICS):
        leaf = leaves_by_function[function]
        actual = (leaf["expected"]["offset"], leaf["expected"]["size"], len(leaf["relocations"]))
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise RuntimeError(f"attc_proc production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    copy_indexes = {4, 6}
    for index, (function, (name, start, end, expected)) in enumerate(
        zip(CANDIDATE_FUNCTIONS, linked), 1
    ):
        site = sites.get(f"replace_cordio_attc_proc_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or site.get("branch") != ("copy" if index in copy_indexes else "b_w")
            or function not in overlay["functions"]
        ):
            raise RuntimeError(f"attc_proc production route changed: {name}")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = leaves[0]["expected"]["offset"] - 279244
    alignment += sum(
        right["expected"]["offset"] - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (1694, 22, 38):
        raise RuntimeError("attc_proc production metrics changed")
    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    validate_apollo_main_artifacts(ROOT, RuntimeError, "ATT client processor")
    if len([row for row in override["regions"] if row["name"].startswith("cordio_attc_proc_")]) != 41:
        raise RuntimeError("attc_proc component/manifest ownership changed")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x4B5230,
            "end_exclusive": 0x4B59C0,
            "physical_bytes": 1936,
            "linked_function_count": 15,
            "linked_function_bytes": 1884,
            "source_inventory_functions": 16,
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": sum(len(sites) for sites in CALLS.values()),
            "registered_function_pointers": len(expected_stored),
            "strict_interior_pointers": 0,
            "strict_interior_branches": 0,
            "unaligned_false_pointer_windows": 5,
            "aligned_ascii_pointer_collisions": 1,
        },
        "architecture": {
            "retained_source_path": 0x6DC874,
            "att_control_block": 0x200610AC,
            "attc_control_block": 0x2006F904,
            "response_table": 0x700964,
            "response_table_entries": 17,
            "response_table_nonnull_entries": 13,
            "minimum_pdu_table": 0x785270,
            "minimum_pdu_table_entries": 13,
            "r4_event_and_length_guards": True,
            "read_multiple_variable_method": True,
            "bearer_aware_processing": True,
            "inherited_method_16_17_bounds_defect": True,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "edb846b41398a2580162a35063e3dc0955822804",
            "selected_sha256": "eff902813acebd98bf0ea4ef0540400a8f094d31dde81d2f5e4ae788ee876d10",
            "later_r4_blob": "f189110a32de691dfd18a332d4aed6b7e74d8b30",
            "later_r4_sha256": "9a6cbac237c70d9595b5f167cbc28cbbe535f131641779adfed4266a4738eb5f",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "historical_generating_commit_resolved": False,
            "discriminator": "r20 variable-read/EATT architecture plus exact R4 event/length guards and line-794 layout",
        },
        "production": {
            "status": "routed", "linked_functions": 15, "source_functions": 16,
            "stock_bytes_replaced": 1884, "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled, "alignment_bytes": alignment,
            "strict_relocations": relocations, "guarded_redirects": 13,
            "exact_in_place_copies": 2, "source_only_public_helpers": source_only,
            "method_table_bounds_defect_remediated": True,
            "hardware_validation": "blocked by unavailable physical evidence",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Cordio attc_proc closed: 15 linked / 1 source-only; 20 BL + 10 stored ingress")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
