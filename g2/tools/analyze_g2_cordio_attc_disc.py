#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio ATT client discovery module."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
READINESS_MANIFEST = ROOT / "research/readiness/attc-disc/SHA256SUMS"
READINESS_BYTES = 1_386
READINESS_SHA256 = "1be8534914ad2679e16eb5cb68df6c244484e79442c4f4b628a1b42427f68504"
PINNED_INPUTS = {
    ROOT / "components/shared/cordio/runtime_cordio_attc_disc.c": "aa4da8bb83ab559f1f77a34a834983e3c4a93e4dfbe17987e66b062f34436294",
    ROOT / "components/shared/cordio/runtime_cordio_attc_disc.h": "854672577f0a8aa14e6bb3c8f7c115b2c72a2538cc398b426fcd94eb7b21cd24",
    ROOT / "tools/manifests/packetcraft-cordio-attc-disc-provenance.tsv": "f3f5617d81fa8ab5c2f20dd77d3426c8e3e357c6a1638910155bfbf1c2b3e632",
    ROOT / "tools/manifests/packetcraft-cordio-attc-disc-function-map.tsv": "00ab3c9f2fdb9c8d6a8303af34b217b593b2442850631a40e75744de4812d69f",
    ROOT / "tools/manifests/readiness-cordio-attc-disc-build-results.tsv": "f8f7751563606f4ecc2f499ab68b6e8dd3af8624ea89874c60f79d61fa19b101",
    ROOT / "tools/manifests/readiness-cordio-attc-disc-closure-results.tsv": "2fd45e129d93d99752dc15bf1d8d666385990260a46467f2c5720d239b2d5bba",
    ROOT / "tools/manifests/readiness-cordio-attc-disc-source-identities.tsv": "d508454464a0da1dc2d488c4784b54708d4cc195020bf9175fd4fba445f07c21",
    ROOT / "tools/manifests/readiness-cordio-attc-disc-undefined-providers.tsv": "a1291dd9af7c2afdbd06bf0ea2a2618db31c805c07b33f9d6959c5621554463c",
}
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_attc_disc.c"
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_attc_discovery_uuid_compare",
    "open_cfw_cordio_attc_discovery_verify",
    "open_cfw_cordio_attc_discovery_descriptors",
    "open_cfw_cordio_attc_discovery_process_descriptor_pair",
    "open_cfw_cordio_attc_discovery_process_descriptor",
    "open_cfw_cordio_attc_discovery_process_characteristic_declaration",
    "open_cfw_cordio_attc_discovery_process_characteristic",
    "open_cfw_cordio_attc_discovery_configuration_next",
    "open_cfw_cordio_attc_discover_service",
    "open_cfw_cordio_attc_complete_service_discovery",
    "open_cfw_cordio_attc_start_characteristic_discovery",
    "open_cfw_cordio_attc_complete_characteristic_discovery",
    "open_cfw_cordio_attc_start_configuration",
    "open_cfw_cordio_attc_complete_configuration",
    "open_cfw_cordio_attc_resume_configuration",
]
CANDIDATE_METRICS = [
    (351712,190,1),(351904,60,0),(351964,166,2),(352132,120,1),
    (352252,222,2),(352476,200,1),(352676,178,2),(352856,132,2),
    (352988,48,1),(353036,94,0),(353132,68,1),(353200,90,2),
    (353292,16,1),(353308,22,1),(353332,4,1),
]

FUNCTIONS = [
    ("attcUuidCmp", 0x0056B7EC, 0x0056B834, "bec11106e5ed133dab73ea6ca8bbdf98df933efefde4df10090245ee95b644c3", [0x0056B954, 0x0056BBA0]),
    ("attcDiscVerify", 0x0056B834, 0x0056B86A, "1181ed4863eeead6e79f1a3e0366f956e0c809e59dc9f6f32e675eb8cd25e6cf", [0x0056B8C8]),
    ("attcDiscDescriptors", 0x0056B86A, 0x0056B8FA, "1ef2497bedb9599704a8fa08505ec609a17ca6846cf627c01c8a6c6d100a7049", [0x0056BB0E, 0x0056BEAA]),
    ("attcDiscProcDescPair", 0x0056B8FA, 0x0056BA82, "7f5a567b6dd92422da6244454a51a7eba517913e2ac846e979d4b199294e596a", [0x0056BACC]),
    ("attcDiscProcDesc", 0x0056BA82, 0x0056BB1A, "ebe9eec494463a7d5fcbe10ffd8e6869d4f0a5b0ff2a7e9dcc4d73ed92244ca8", [0x0056C322]),
    ("attcDiscProcCharDecl", 0x0056BB1C, 0x0056BE24, "e3705359bb0471bb6a65b0aad1603d1444f1c372e16b4da6e9a47f4d6fd4220f", [0x0056BE76]),
    ("attcDiscProcChar", 0x0056BE30, 0x0056BEB6, "08ea8fcc3cd98c18f26d086c48774df95d21feed53ef245ef3cdb239de155a63", [0x0056C316]),
    ("attcDiscConfigNext", 0x0056BEB6, 0x0056BF12, "f24649b5f51299239aa05551d62ae1043c3de3b2044ac7a928ee1a736abb9568", [0x0056C390, 0x0056C3A0, 0x0056C3AA]),
    ("AttcDiscService", 0x0056BF12, 0x0056BF32, "da6f168fcf95843b2b554f17e74f1e21b75f3935124ea055dc16cbcba572fcfe", [0x0053344A]),
    ("AttcDiscServiceCmpl", 0x0056BF32, 0x0056C1B8, "bac157d91cbef1d50445d41f9676ef39764f188557879a3aca36b309cf0abe71", [0x00532B64]),
    ("AttcDiscCharStart", 0x0056C1B8, 0x0056C1DA, "ca16f52d7e4aeeb21ce007a2329aa960174dca6910994c15c3b8bd862f6351c0", [0x00532C1C]),
    ("AttcDiscCharCmpl", 0x0056C1F8, 0x0056C34C, "946f7d88980d09cf325bb274e0f6ad3c2726cd3d10d8df522abeada506aa3a59", [0x00532C58]),
    ("AttcDiscConfigStart", 0x0056C388, 0x0056C396, "f296c2affca1390787dcb9f9cfbd8de771ef36615d389ce81a2acb68c157d9d2", [0x00533608]),
    ("AttcDiscConfigCmpl", 0x0056C396, 0x0056C3A6, "dda11f9ebe5309d848911f78bf90f66648a90a86549541b334a51f5c13484270", [0x00532D72]),
    ("AttcDiscConfigResume", 0x0056C3A6, 0x0056C3B0, "16efcb22f7c5c6d81333b8b5497c1df57945dbeff7f5406a33ffccc635cf0aa9", [0x00532216, 0x00532284]),
]
FULL_TU_SPAN = (0x0056B7EC, 0x0056C3B0)
FULL_TU_SHA256 = "d759dc33b12a98e42127bd1551dcd61038d6dfc6551c79b363c970d7f1f3281c"
CONCATENATED_BODY_SHA256 = "5327e9fb7478cbf5e9c175d33cf7dfe9b26292344e75a10f45ac767a85853452"
DATA_GAPS = [
    (0x0056BB1A, 0x0056BB1C),
    (0x0056BE24, 0x0056BE30),
    (0x0056C1DA, 0x0056C1F8),
    (0x0056C34C, 0x0056C388),
]
CONCATENATED_DATA_SHA256 = "1648ee5e1bda4e564fea853f1f338d703458544f68216a236893a30f686c8aeb"
SOURCE_PATH = 0x006DC7B4
SOURCE_PATH_POINTER_CELLS = [0x0056C1F4, 0x0056C384]
SOURCE_PATH_BYTES = (
    b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\"
    b"ble-host\\sources\\stack\\att\\attc_disc.c\x00"
)
ATT_CH_UUID = (0x0078F53E, b"\x03\x28")
DEAD_STRIPPED = [
    "attcDiscProcIncSvc",
    "AttcDiscIncSvcStart",
    "AttcDiscIncSvcCmpl",
]
R20_ONLY_ABSENT_LITERAL = b"service include found handle"


class AuditError(RuntimeError):
    """Raised when authenticated ATT discovery evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("attc_disc_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _all_callers(blob: bytes, decoder: Any) -> dict[int, list[int]]:
    callers = {start: [] for _, start, _, _, _ in FUNCTIONS}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in callers:
            callers[target].append(address)
    return callers


def _all_occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [
        LOAD_BASE + offset
        for offset in range(len(blob) - 3)
        if blob[offset:offset + 4] == packed
    ]


def _verify_no_stored_function_pointers(blob: bytes) -> None:
    targets = {
        address | thumb
        for _, start, end, _, _ in FUNCTIONS
        for address in range(start, end, 2)
        for thumb in (0, 1)
    }
    for offset in range(len(blob) - 3):
        if struct.unpack_from("<I", blob, offset)[0] in targets:
            raise AuditError(
                f"unexpected stored ATT discovery pointer at 0x{LOAD_BASE + offset:08x}"
            )


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES:
        raise AuditError("Lorelei ATT discovery artifact size changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei ATT discovery artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned ATT discovery input changed: {path}")

    decoder = _load_decoder()
    all_callers = _all_callers(blob, decoder)
    bodies: list[bytes] = []
    reports = []
    for name, start, end, expected, callers in FUNCTIONS:
        body = _slice(blob, start, end)
        if _sha256(body) != expected:
            raise AuditError(f"ATT discovery stock span changed at 0x{start:08x}")
        if all_callers[start] != callers:
            raise AuditError(f"ATT discovery caller closure changed for {name}")
        bodies.append(body)
        reports.append({
            "name": name,
            "start": start,
            "end_exclusive": end,
            "size": end - start,
            "sha256": expected,
            "direct_bl_callers": callers,
        })
    if _sha256(b"".join(bodies)) != CONCATENATED_BODY_SHA256:
        raise AuditError("ATT discovery concatenated body identity changed")
    if _sha256(_slice(blob, *FULL_TU_SPAN)) != FULL_TU_SHA256:
        raise AuditError("ATT discovery translation-unit span changed")
    gaps = [_slice(blob, start, end) for start, end in DATA_GAPS]
    if _sha256(b"".join(gaps)) != CONCATENATED_DATA_SHA256:
        raise AuditError("ATT discovery literal/data gaps changed")
    if _all_occurrences(blob, SOURCE_PATH) != SOURCE_PATH_POINTER_CELLS:
        raise AuditError("ATT discovery source-path pointer closure changed")
    if _slice(blob, SOURCE_PATH, SOURCE_PATH + len(SOURCE_PATH_BYTES)) != SOURCE_PATH_BYTES:
        raise AuditError("ATT discovery retained source path changed")
    if _slice(blob, ATT_CH_UUID[0], ATT_CH_UUID[0] + 2) != ATT_CH_UUID[1]:
        raise AuditError("ATT characteristic UUID constant changed")
    if R20_ONLY_ABSENT_LITERAL in blob:
        raise AuditError("dead-stripped included-service trace unexpectedly linked")
    _verify_no_stored_function_pointers(blob)

    linked_bytes = sum(end - start for _, start, end, _, _ in FUNCTIONS)
    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise AuditError("ATT discovery production leaf inventory changed")
    source_hash = PINNED_INPUTS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise AuditError(f"ATT discovery production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, (function, stock) in enumerate(
        zip(CANDIDATE_FUNCTIONS, FUNCTIONS), 1
    ):
        name, start, end, expected, _callers = stock
        site = sites.get(f"replace_cordio_attc_disc_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or site.get("branch") != "b_w"
            or function not in overlay["functions"]
        ):
            raise AuditError(f"ATT discovery production route changed: {name}")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = leaves[0]["expected"]["offset"] - 351710
    alignment += sum(
        right["expected"]["offset"] - left["expected"]["offset"]
        - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (1610, 16, 18):
        raise AuditError("ATT discovery production metrics changed")
    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    validate_apollo_main_artifacts(ROOT, AuditError, "ATT discovery")
    if len([row for row in override["regions"]
            if row["name"].startswith("cordio_attc_disc_")]) != 38:
        raise AuditError("ATT discovery component/manifest ownership changed")
    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": FULL_TU_SPAN[0],
            "end_exclusive": FULL_TU_SPAN[1],
            "translation_unit_bytes": FULL_TU_SPAN[1] - FULL_TU_SPAN[0],
            "translation_unit_sha256": FULL_TU_SHA256,
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": linked_bytes,
            "concatenated_body_sha256": CONCATENATED_BODY_SHA256,
            "literal_and_alignment_bytes": sum(end - start for start, end in DATA_GAPS),
            "concatenated_literal_data_sha256": CONCATENATED_DATA_SHA256,
            "functions": reports,
            "source_only_dead_stripped": DEAD_STRIPPED,
            "direct_bl_ingress_sites": sum(len(item[-1]) for item in FUNCTIONS),
            "indirect_ingress_sites": 0,
            "stored_entry_or_interior_pointers": 0,
        },
        "abi": {
            "attcDiscChar_size": 8,
            "attcDiscChar_offsets": {"pUuid": 0, "settings": 4},
            "attcDiscCfg_size": 8,
            "attcDiscCfg_offsets": {"pValue": 0, "valueLen": 4, "hdlIdx": 5},
            "attcDiscCb_size": 20,
            "attcDiscCb_offsets": {
                "pCharList": 0,
                "pHdlList": 4,
                "pCfgList": 8,
                "charListLen": 12,
                "cfgListLen": 13,
                "svcStartHdl": 14,
                "svcEndHdl": 16,
                "charListIdx": 18,
                "endHdlIdx": 19,
            },
            "settings_bits": {"uuid128": 1, "required": 2, "descriptor": 4},
            "status": {
                "not_found": 0x0A,
                "invalid_response": 0x73,
                "undefined": 0x75,
                "required_not_found": 0x76,
                "continuing": 0x79,
            },
            "owned_mutable_globals": 0,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "ebb7e5658db198940c6eaaef85ec9a7fbe4f0936",
            "r20_discriminator": "post-match break plus stock source lines 238,389,398,610,629,678",
            "r20_only_included_service_functions": "dead-stripped",
            "license": "Apache-2.0",
            "stock_qualification": "exact r20 behavior/API route plus vendor diagnostics",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "anchored_functions_in_probe": 4,
            "anchored_bytes_in_probe": 2_154,
            "source_inventory_functions": 18,
            "compiler_profiles": 2,
            "provider_seams": 11,
            "linked_unresolved_symbols": 0,
        },
        "production": {
            "status": "routed",
            "linked_functions": 15,
            "source_functions": 18,
            "stock_bytes_replaced": linked_bytes,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 15,
            "source_only_dead_stripped": DEAD_STRIPPED,
            "response_shape_bounds_hardened": True,
            "index_and_handle_bounds_hardened": True,
            "configuration_handle_index_hardened": True,
            "hardware_validation": (
                "deferred by project direction; future qualification requires authorized responsive G2/ATT peer evidence"
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
        print("Cordio ATT discovery audit: 15 linked functions / 2,908 bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
