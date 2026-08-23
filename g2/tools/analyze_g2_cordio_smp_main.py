#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio SMP main module."""

from __future__ import annotations

import argparse
import csv
import hashlib
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
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_main.c"
PRODUCTION_SOURCE_SIZE = 29_363
PRODUCTION_SOURCE_SHA256 = "ea5f2e24d9eb9ab36365a41280464e825dd03049acf5e634b5b13385b4178c70"
PRODUCTION_ROUTES = {
    "open_cfw_cordio_smp_main_packet_length": (168140, 90, "39ecf1da6972aa1bb12cf6343842640c3ba4359bd107a747327af82618c29070", None),
    "open_cfw_cordio_smp_main_ccb_by_connection_id": (168232, 26, "784e4bcf71771c417a626cafcc0cb3fb8705efa6b1db3b1dd631a47dd5e3d166", 'smpCcbByConnId'),
    "open_cfw_cordio_smp_main_ccb_by_handle": (168260, 20, "9db79d880c29d9373fb7525126fcd3c99bc895ed786b5181df3774d0c4060dd2", 'smpCcbByHandle'),
    "open_cfw_cordio_smp_main_state_idle": (168280, 12, "077cdc8f10743c5c13d248d7ff569e5d4af73e8f8c0596082dc5b2eb6881f709", 'smpStateIdle'),
    "open_cfw_cordio_smp_main_send_packet": (168292, 50, "6b533535c6e791c15f6cb65c37efae2f3ef0877981fbbd02654f8cf2408e5115", 'smpSendPkt'),
    "open_cfw_cordio_smp_main_l2c_data_callback": (168344, 106, "0987c126c1b60aedb443b4da14571ac346384b5700ae92d239257e67ec81d173", 'smpL2cDataCback'),
    "open_cfw_cordio_smp_main_l2c_control_callback": (168452, 82, "882e55e83ce2c3923a6e12dc3fbd55dccac07ca8dee4c14523e7bee7ca650dc0", 'smpL2cCtrlCback'),
    "open_cfw_cordio_smp_main_resume_attempts": (168536, 90, "06f1f4cc084ff0d412739d803b1b174b52c20dc47f89bfe2883e63538a4bd2e0", 'smpResumeAttemptsState'),
    "open_cfw_cordio_smp_main_dm_connection_callback": (168628, 180, "15a76afacb91d77b935722804031bf46fad4028068a31626edfe7f72a3046765", 'smpDmConnCback'),
    "open_cfw_cordio_smp_main_calculate_c1_part1": (168808, 500, "ee337f5c849aa6423d6932dc4cd8330b109d2d33deda9d93544643ff8c6d4568", 'smpCalcC1Part1'),
    "open_cfw_cordio_smp_main_calculate_c1_part2": (169308, 384, "6afc58ffe207fc84a3b0ad50f76a3048a84d9f8e79f8cda157bc38ef9afbb61d", 'smpCalcC1Part2'),
    "open_cfw_cordio_smp_main_calculate_s1": (169692, 92, "236f6778cdb349465d2275c03acc0475f1d76dc6636251ef0dff00065ac399bd", 'smpCalcS1'),
    "open_cfw_cordio_smp_main_generate_ltk": (169784, 86, "675c471125149fe1caeb848192a447d1fd50c5a352591bd16b86c8fb56ebe0b7", 'smpGenerateLtk'),
    "open_cfw_cordio_smp_main_message_allocate": (169872, 6, "debc979802f9f4305a8f7dd5d7d840da5dac58bcc7f12e2b4d29137afe879c6d", 'smpMsgAlloc'),
    "open_cfw_cordio_smp_main_dm_message_send": (169880, 20, "8ebf2df6019c53f32cef42f8c5085972ca5c70007fb98533f07d013489b71a68", 'SmpDmMsgSend'),
    "open_cfw_cordio_smp_main_get_sc_security_level": (169900, 38, "f9a0d70b4042e436ffd7f843789152e41e2ac0ca4f3c61609a35b065bfcd4603", 'smpGetScSecLevel'),
    "open_cfw_cordio_smp_main_dm_lesc_enabled": (169940, 20, "b1308d12aad8927279efbaa2c284225e7e591835db1cbfe1ac3cfc3b5e5710e3", 'SmpDmLescEnabled'),
    "open_cfw_cordio_smp_main_dm_get_stk": (169960, 86, "69a5efe08ccbeb47345424a69fcc8ecafd17d6b67ae2ad92e61d0adc3832c366", 'SmpDmGetStk'),
    "open_cfw_cordio_smp_main_handler": (170048, 124, "f2a06e6b0cd6ffc0e3a7a5b4bb339fbb50def0079c955f70fa2a277fe0483e45", 'SmpHandler'),
    "open_cfw_cordio_smp_main_dm_encrypt_indication": (170172, 22, "49e24254964eeb9febea4313e315a8696868662a0f101aa71fd3a1589c2cd02c", 'SmpDmEncryptInd'),
    "open_cfw_cordio_smp_main_handler_init": (170196, 112, "196ea463b18ca3625423e18c95ceebe639bf42c61f94875382e93e8353f3ef43", 'SmpHandlerInit'),
}
FUNCTION_MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-main-function-map.tsv"
READINESS_MANIFEST = ROOT / "research/readiness/smp-main/SHA256SUMS"
READINESS_SHA256 = "0ee02d564ac137eaeacda02b280b308c7bbae99810a5bd92ab648ab6e8af142e"
PATCH = ROOT / "third_party/cordio/g2-patches/smp_main-ambiq-aes-queue-cleanup.patch"
PINNED_INPUTS = {
    FUNCTION_MAP: "018816f5d2d34f9a156daa143ec319f6be6bc5518fcf3825ade043400bf30c39",
    ROOT / "tools/manifests/packetcraft-cordio-smp-main-provenance.tsv": "da7e704805c9ffa9c7f1c8f78b8c1689bbd2e71913369d5d9374fbde2540ea72",
    PATCH: "0b86bf4ff50cdae14662a9c06824404737993d966523421fd3a347d1c3fbdf52",
    ROOT / "tools/manifests/readiness-cordio-smp-main-build-results.tsv": "7c9f4352f14765709294d204d64270ade6286134e26681134eafa65ab0ff963a",
    ROOT / "tools/manifests/readiness-cordio-smp-main-closure-results.tsv": "bf77568aff88ed19aa3db607c2522a56a7bc64668ffc8b6a49224a4a3204ddcf",
    ROOT / "tools/manifests/readiness-cordio-smp-main-include-closure.tsv": "61dc8470b22afd53361768730421354e1a25d616a86bdc4a50762eabaf0ae3e3",
    ROOT / "tools/manifests/readiness-cordio-smp-main-source-identities.tsv": "159834446375565e4a5f18c098f94d60f4dcbd6215a43843e21c39eeac7ab3a2",
    ROOT / "tools/manifests/readiness-cordio-smp-main-undefined-providers.tsv": "072522c62af3e925134692fe0cefaa6261a200c40dd6d8566f7d45d634490620",
}

ENCLOSING_SPAN = (0x00537278, 0x00537EEC)
ENCLOSING_SHA256 = "bba2ea8b7c5ed581d8202b2b7c2978f0ae8f874eccea15cca7de17ff645732fb"
CONCATENATED_BODY_SHA256 = "c70987596989d69f3828cc2d1d5515e7badce57caae5e611f052a75cc55fc88e"
GAPS = [
    (0x005375EE, 0x005375FC, "eb7df66f732c9435836b9ea3c04507f9d7908eeb866db5345abb2a1f39a8251c"),
    (0x00537CF8, 0x00537D0C, "6de58e692a9b935f6e04b28807e635545ac2ab47bd3f1bf4cdaf54cfb5ac3e1b"),
    (0x00537E9E, 0x00537EEC, "441c52381656e608ad9d70c451b97d21439938bc93d21a89b7400fd354ca8e89"),
]
SOURCE_PATH = 0x006DE854
SOURCE_PATH_BYTES = 93
SOURCE_PATH_SHA256 = "966a611194a5bef07b5f981ab9d01670cb980f9b903525afc8ea9a1200389787"
SOURCE_PATH_CELL = 0x00537EAC
SMP_CB = 0x20070AEC
SEC_CB = 0x20072CD8
EXPECTED_FUNCTION_POINTERS = {
    0x004B878C: 0x00537D0D,
    0x00537ED4: 0x00537445,
    0x00537ED8: 0x00537279,
    0x00537EDC: 0x00537503,
}


class AuditError(RuntimeError):
    """Raised when authenticated SMP-main evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smp_main_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_functions() -> tuple[list[dict[str, Any]], list[str]]:
    functions: list[dict[str, Any]] = []
    source_only: list[str] = []
    with FUNCTION_MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if not row["stock_start"]:
                source_only.append(row["stock_name"])
                continue
            functions.append({
                "name": row["stock_name"],
                "start": int(row["stock_start"], 0),
                "end_exclusive": int(row["stock_end_exclusive"], 0),
                "size": int(row["stock_bytes"]),
                "sha256": row["stock_sha256"],
                "source_start_line": int(row["source_start_line"]),
                "source_end_line": int(row["source_end_line"]),
                "source_span_sha256": row["source_span_sha256"],
                "direct_bl_callers": [
                    int(item, 0) for item in row["direct_bl_callers"].split(",") if item
                ],
                "indirect_ingress": row["indirect_ingress"],
                "classification": row["classification"],
            })
    return functions, source_only


def _all_callers(blob: bytes, decoder: Any, functions: list[dict[str, Any]]) -> dict[int, list[int]]:
    callers = {item["start"]: [] for item in functions}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in callers:
            callers[target].append(address)
    return callers


def _aligned_function_pointers(blob: bytes, functions: list[dict[str, Any]]) -> dict[int, int]:
    targets = {
        address | thumb
        for item in functions
        for address in range(item["start"], item["end_exclusive"], 2)
        for thumb in (0, 1)
    }
    return {
        LOAD_BASE + offset: struct.unpack_from("<I", blob, offset)[0]
        for offset in range(0, len(blob) - 3, 4)
        if struct.unpack_from("<I", blob, offset)[0] in targets
    }


def _production_report(functions: list[dict[str, Any]]) -> dict[str, Any]:
    source = PRODUCTION_SOURCE.read_bytes()
    if (
        len(source) != PRODUCTION_SOURCE_SIZE
        or _sha256(source) != PRODUCTION_SOURCE_SHA256
    ):
        raise AuditError("Cordio SMP-main production source identity changed")
    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    leaves = {
        row["function"]: row
        for row in overlay.get("relocated_leaves", [])
        if row.get("function") in PRODUCTION_ROUTES
    }
    patch_routes = {
        function for function, route in PRODUCTION_ROUTES.items()
        if route[3] is not None
    }
    patches = {
        row["target_function"]: row
        for row in overlay.get("patch_sites", [])
        if row.get("target_function") in patch_routes
    }
    if set(leaves) != set(PRODUCTION_ROUTES) or set(patches) != patch_routes:
        raise AuditError("Cordio SMP-main production routing is incomplete")
    stock = {
        item["name"]: (item["start"], item["size"], item["sha256"])
        for item in functions
    }
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    for function, (offset, size, digest, stock_name) in PRODUCTION_ROUTES.items():
        leaf = leaves[function]
        source_record = leaf.get("source", {})
        if (
            leaf.get("profiles") != ["apple-clang"]
            or source_record.get("path") != source_path
            or source_record.get("size") != PRODUCTION_SOURCE_SIZE
            or source_record.get("sha256") != PRODUCTION_SOURCE_SHA256
            or source_record.get("license") != "Apache-2.0"
            or source_record.get("upstream_commit")
            != "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
            or leaf.get("expected", {}).get("offset") != offset
            or leaf.get("expected", {}).get("size") != size
            or leaf.get("expected", {}).get("sha256") != digest
            or leaf.get("strict_relocation_contract")
            != (function != "open_cfw_cordio_smp_main_handler_init")
        ):
            raise AuditError(f"Cordio SMP-main production leaf changed: {function}")
        if stock_name is None:
            continue
        patch = patches[function]
        stock_start, stock_size, stock_digest = stock[stock_name]
        if (
            patch.get("profiles") != ["apple-clang"]
            or patch.get("runtime_address") != stock_start
            or patch.get("expected_size") != stock_size
            or patch.get("expected_sha256") != stock_digest
            or patch.get("branch") != "b_w"
        ):
            raise AuditError(f"Cordio SMP-main stock patch changed: {function}")
    return {
        "status": (
            "production-routed authenticated Packetcraft r20.05c definitions "
            "with the Ambiq stale-AES queue fix and G2 SRAM ABI"
        ),
        "candidate": source_path,
        "production_routed": True,
        "live_functions": len(PRODUCTION_ROUTES),
        "compiled_leaf_bytes": sum(item[1] for item in PRODUCTION_ROUTES.values()),
        "source_owned_bytes_added": 2170,
        "stock_bytes_replaced": sum(item["size"] for item in functions),
        "hardware_validation": (
            "blocked by unavailable authorized G2/EM9305 pairing, reconnect, "
            "LESC, and stale-AES-queue physical evidence"
        ),
    }


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned SMP-main input changed: {path.name}")
    if not READINESS_MANIFEST.is_file() or _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei SMP-main readiness artifact changed")

    functions, source_only = _load_functions()
    decoder = _load_decoder()
    all_callers = _all_callers(blob, decoder, functions)
    body_parts: list[bytes] = []
    for item in functions:
        body = _slice(blob, item["start"], item["end_exclusive"])
        if len(body) != item["size"] or _sha256(body) != item["sha256"]:
            raise AuditError(f"SMP-main stock span changed for {item['name']}")
        if all_callers[item["start"]] != item["direct_bl_callers"]:
            raise AuditError(f"SMP-main direct caller closure changed for {item['name']}")
        body_parts.append(body)
    if _sha256(b"".join(body_parts)) != CONCATENATED_BODY_SHA256:
        raise AuditError("SMP-main concatenated body identity changed")
    if _sha256(_slice(blob, *ENCLOSING_SPAN)) != ENCLOSING_SHA256:
        raise AuditError("SMP-main enclosing interval changed")
    for start, end, expected in GAPS:
        if _sha256(_slice(blob, start, end)) != expected:
            raise AuditError(f"SMP-main data gap changed at 0x{start:08x}")
    if _sha256(_slice(blob, SOURCE_PATH, SOURCE_PATH + SOURCE_PATH_BYTES)) != SOURCE_PATH_SHA256:
        raise AuditError("SMP-main retained source path changed")
    if struct.unpack_from("<I", blob, SOURCE_PATH_CELL - LOAD_BASE)[0] != SOURCE_PATH:
        raise AuditError("SMP-main source-path pointer cell changed")
    if _aligned_function_pointers(blob, functions) != EXPECTED_FUNCTION_POINTERS:
        raise AuditError("SMP-main function-pointer closure changed")
    if struct.unpack_from("<I", blob, 0x00537EBC - LOAD_BASE)[0] != SMP_CB:
        raise AuditError("SMP-main control-block literal changed")
    if struct.unpack_from("<I", blob, 0x00537EE8 - LOAD_BASE)[0] != SEC_CB:
        raise AuditError("SMP-main security-queue literal changed")

    linked_bytes = sum(item["size"] for item in functions)
    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": ENCLOSING_SPAN[0],
            "end_exclusive": ENCLOSING_SPAN[1],
            "enclosing_bytes": ENCLOSING_SPAN[1] - ENCLOSING_SPAN[0],
            "enclosing_sha256": ENCLOSING_SHA256,
            "linked_function_count": len(functions),
            "linked_function_bytes": linked_bytes,
            "concatenated_body_sha256": CONCATENATED_BODY_SHA256,
            "literal_or_data_gap_bytes": sum(end - start for start, end, _ in GAPS),
            "functions": functions,
            "source_only_dead_stripped": source_only,
            "direct_bl_callers": sum(len(item["direct_bl_callers"]) for item in functions),
            "intentional_function_pointers": EXPECTED_FUNCTION_POINTERS,
            "unexpected_stored_entry_or_interior_pointers": 0,
        },
        "abi": {
            "control_block": SMP_CB,
            "control_block_size": 0xFC,
            "connection_count": 3,
            "ccb_size": 0x4C,
            "ccb_offsets": {
                "response_timer": 0x00,
                "wait_timer": 0x10,
                "pair_request": 0x20,
                "pair_response": 0x27,
                "scratch_pointer": 0x30,
                "queued_message_pointer": 0x34,
                "handle": 0x38,
                "connection_id": 0x3D,
                "state": 0x3E,
                "token": 0x41,
                "attempts": 0x42,
                "key_ready": 0x44,
                "secure_connections_pointer": 0x48,
            },
            "security_control_block": SEC_CB,
            "database_service_event": 0x20,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "vendor_patch_oracle": "AmbiqSuite R2.5.1 stale-AES-queue cleanup",
            "reconstruction": "r20.05c public source plus tracked cleanup patch",
            "reconstructed_source_sha256": "dd813e9b3bdf5d4ea6c879a78b7c7e542518a573ea70d18d9e144eb8909b6d74",
            "qualification": "semantic source candidate; retained line constants prove further local textual skew",
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "public_compiler_profiles": 2,
            "hybrid_compiler_profiles": 2,
            "external_provider_seams": 32,
            "base_closure_status": "invalid: linker retained zero text/data/BSS",
            "valid_hybrid_closure_profiles": 2,
            "linked_unresolved_symbols": 0,
        },
        "production": _production_report(functions),
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
        print("Cordio SMP main audit: 20 linked functions / 3,076 bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
