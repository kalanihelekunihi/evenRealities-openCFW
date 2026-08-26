#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio ATT CCC module."""

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
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
READINESS_MANIFEST = ROOT / "research/readiness/atts-ccc/SHA256SUMS"
READINESS_SHA256 = "c27d125cfe2e8bd14848d047b20d38a6355b71281c2c11a6cfa9fe1ba15e3978"
PINNED_INPUTS = {
    ROOT / "components/shared/cordio/runtime_cordio_atts_ccc.c": "e9d9ec6bfcce047911a43405657f2c6f3e811dcaefd9c5334689d9c1ac38fbee",
    ROOT / "components/shared/cordio/runtime_cordio_atts_ccc.h": "c603f5ce10c4edaaca5f9a7e9f2bc2500ad84c8bcdd7901aa0535f6605265dbb",
    ROOT / "tools/manifests/packetcraft-cordio-atts-ccc-provenance.tsv": "f1bb185dda75d22216077cb5cd60e03c76e0f7736c60bf7298be838ffa6cdd0d",
    ROOT / "tools/manifests/packetcraft-cordio-atts-ccc-function-map.tsv": "d04abd1a75cfd5a66f39622442ef4ab28f668facff92a7f224ccdd97e94fb801",
    ROOT / "tools/manifests/readiness-cordio-atts-ccc-build-results.tsv": "3286d144687750bc976c12fb5551f0af176e24981f3fd51cc4f8a9e97b78222e",
    ROOT / "tools/manifests/readiness-cordio-atts-ccc-closure-results.tsv": "2158633e5d4468d371afbbe0ffb661f17dad5a9b61dff9ada7ce4e0e1f169bf9",
    ROOT / "tools/manifests/readiness-cordio-atts-ccc-source-identities.tsv": "30bb840731c917b425ce8bffe20f80270586fdad0e3974f914eecc4e9231b21a",
    ROOT / "tools/manifests/readiness-cordio-atts-ccc-undefined-providers.tsv": "cd7dec8bb4e1a5e9caf6769c60389c8939de3a324bd8e992ad80ad51c0416471",
}

OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_atts_ccc.c"
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_atts_ccc_callback",
    "open_cfw_cordio_atts_ccc_allocate_table",
    "open_cfw_cordio_atts_ccc_get_table",
    "open_cfw_cordio_atts_ccc_free_table",
    "open_cfw_cordio_atts_ccc_read_value",
    "open_cfw_cordio_atts_ccc_write_value",
    "open_cfw_cordio_atts_ccc_main_callback",
    "open_cfw_cordio_atts_ccc_register",
    "open_cfw_cordio_atts_ccc_initialize_table",
    "open_cfw_cordio_atts_ccc_clear_table",
    "open_cfw_cordio_atts_ccc_get",
    "open_cfw_cordio_atts_ccc_set",
    "open_cfw_cordio_atts_ccc_enabled",
    "open_cfw_cordio_atts_ccc_table_length",
]
CANDIDATE_LEAF_METRICS = [
    (335892, 46, 0), (335940, 44, 1), (335984, 20, 0),
    (336004, 40, 1), (336044, 156, 1), (336200, 212, 2),
    (336412, 20, 2), (336432, 34, 0), (336468, 96, 2),
    (336564, 14, 1), (336580, 20, 1), (336600, 20, 1),
    (336620, 50, 2), (336672, 12, 0),
]

FUNCTIONS = [
    ("attsCccCback", 0x0052BB64, 0x0052BB8A, "2122c745eb8360485c188d36af3757d6c1a0841df9720e7ccd32159410bbfe80", [0x0052C092, 0x0052C3A8]),
    ("attsCccAllocTbl", 0x0052BB8A, 0x0052BCEA, "4d22cf525363670d976aed495f6846bddc3a6414cf02d5812e41b40b17b8d7ac", [0x0052C376]),
    ("attsCccGetTbl", 0x0052BCEA, 0x0052BE26, "201ae319937c47f9ab38e5e5486858526777d28356dd01f53a533df0f5b7bfcf", [0x0052BFC4, 0x0052C05E, 0x0052C5F8, 0x0052C616]),
    ("attsCccFreeTbl", 0x0052BE34, 0x0052BF8E, "0de48626cb11cdbc01d5fe39b0821921643ae40dc4165ceeef69f387905a6566", [0x0052C5EC]),
    ("attsCccReadValue", 0x0052BF8E, 0x0052BFF0, "72848de45bd95e0bad12323e0a642978744ce9917ad06e41d2fcd3fcaade2b2d", [0x0052C20C]),
    ("attsCccWriteValue", 0x0052BFF0, 0x0052C09E, "b2ebdb9a3e3d6f6c2c194748b735ed3e4b5416a2b927fb2ea36c7ea62f329c1b", [0x0052C21C]),
    ("attsCccMainCback", 0x0052C0AC, 0x0052C224, "a0bf990585b00836d78cffff98880af67f555b359444b5cba5fb6340f92effb7", []),
    ("AttsCccRegister", 0x0052C224, 0x0052C23C, "b64330257a598d7e834a85a445c87d19df5aaa219ca468b66ea90e40b924c648", [0x004B7EF0]),
    ("AttsCccInitTable", 0x0052C244, 0x0052C3C4, "6af397d3949ce94d4e02c767bbeec082d52a0eba1f7cfe89d75f7be4b3075ba9", [0x004B3810, 0x004B39A2, 0x005345E6, 0x00534608]),
    ("AttsCccClearTable", 0x0052C3D0, 0x0052C5F2, "c3b4201fd806ad6402c2a3aa1ec147b1ee52dc73a721230c174e13003d824487", [0x005346C0]),
    ("AttsCccGet", 0x0052C5F2, 0x0052C60E, "25b8a15faf74d8306bbc60e1ca72c649b26cfe001dbd2410332ff91e8d15972d", [0x0052C65A, 0x00534660]),
    ("AttsCccSet", 0x0052C60E, 0x0052C628, "182404c06676e78506af6872f910fb731c17b1820c041b0613187a3412c502cf", [0x004B3B36]),
    ("AttsCccEnabled", 0x0052C628, 0x0052C660, "a36891a33659e9262866981c3c17baeceb5e10fd4942aa7b1224e5dea7070947", [0x004B5A82, 0x004B5AA2]),
    ("AttsGetCccTableLen", 0x0052C664, 0x0052C66A, "91ed55f143f7fe7bcc91a152aa9c4b1eeffb8202ee6e1c4c750d5523b18f466a", [0x004B3B3E, 0x0053464E]),
]
BODY_ENCLOSING_SPAN = (0x0052BB64, 0x0052C66A)
BODY_ENCLOSING_SHA256 = "5d7c6d28991e77004f7c5793c2f37cea2cfe1cab243e4675d11cc4687602db4e"
FULL_TU_SPAN = (0x0052BB64, 0x0052C6C0)
FULL_TU_SHA256 = "965f8260bed0ed9852331f2fe950aecaae33a0f1f9fc1b8af514af193be39ce1"
CONCATENATED_BODY_SHA256 = "9f221e670e7ba1314147cf258de57d1ea51955e9d728e7b0002f97a6e60e1b96"
TRAILING_DATA_SPAN = (0x0052C66A, 0x0052C6C0)
TRAILING_DATA_SHA256 = "b0368a504de3ce360d3cdb184d9b891421d773038e282a85b07b1d1ae9cb32e6"
CONTROL_BLOCK = 0x20073B00
CONTROL_BLOCK_LITERAL_CELLS = [0x0052C674]
SOURCE_PATH = 0x006DC8D4
SOURCE_PATH_POINTER_CELLS = [0x0052C684]
MAIN_CALLBACK_THUMB = 0x0052C0AD
MAIN_CALLBACK_POINTER_CELLS = [0x0052C6A4]
INDIRECT_MAIN_CALLBACK_SITES = [
    0x0056CB3E, 0x0056CCBC, 0x0056DB62, 0x0056DEBA,
    0x0056E002, 0x0056E1E2, 0x005A5E08, 0x005A5F14,
]
INDIRECT_APP_CALLBACK_SITE = 0x0052BB86
SETTINGS_TABLE = (0x007518C0, 36, "6ea4cf0a89f78d69bd90943924a583fc5faffa80caf21ece63aa114a35e2cbce")
EXPECTED_SETTINGS = [
    (0x0013, 2, 0),
    (0x0825, 1, 0),
    (0x0845, 1, 0),
    (0x0865, 1, 0),
    (0x0885, 1, 0),
    (0x08A5, 1, 0),
]


class AuditError(RuntimeError):
    """Raised when authenticated ATT CCC evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("atts_ccc_thumb", path)
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


def _all_u32_occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [
        LOAD_BASE + offset
        for offset in range(len(blob) - 3)
        if blob[offset:offset + 4] == packed
    ]


def _verify_no_other_stored_function_pointers(blob: bytes) -> None:
    targets = {
        address | thumb
        for _, start, end, _, _ in FUNCTIONS
        for address in range(start, end, 2)
        for thumb in (0, 1)
    }
    full_start, full_end = FULL_TU_SPAN
    # The stock image's pointer tables are word aligned.  Scanning every byte
    # admits accidental four-byte instruction/data windows that cannot be
    # loaded as table entries; keep the fail-closed census aligned to the
    # mechanically proved storage ABI.
    for offset in range(0, len(blob) - 3, 4):
        address = LOAD_BASE + offset
        if full_start <= address < full_end:
            continue
        if struct.unpack_from("<I", blob, offset)[0] in targets:
            raise AuditError(f"unexpected stored ATT CCC pointer at 0x{address:08x}")


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei ATT CCC readiness artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned ATT CCC input changed: {path}")

    decoder = _load_decoder()
    all_callers = _all_callers(blob, decoder)
    body_parts: list[bytes] = []
    function_reports = []
    for name, start, end, expected, callers in FUNCTIONS:
        body = _slice(blob, start, end)
        if _sha256(body) != expected:
            raise AuditError(f"ATT CCC stock span changed at 0x{start:08x}")
        if all_callers[start] != callers:
            raise AuditError(f"ATT CCC direct caller closure changed for {name}")
        body_parts.append(body)
        function_reports.append({
            "name": name,
            "start": start,
            "end_exclusive": end,
            "size": end - start,
            "sha256": expected,
            "direct_bl_callers": callers,
        })
    if _sha256(b"".join(body_parts)) != CONCATENATED_BODY_SHA256:
        raise AuditError("ATT CCC concatenated body identity changed")
    if _sha256(_slice(blob, *BODY_ENCLOSING_SPAN)) != BODY_ENCLOSING_SHA256:
        raise AuditError("ATT CCC body-enclosing span changed")
    if _sha256(_slice(blob, *FULL_TU_SPAN)) != FULL_TU_SHA256:
        raise AuditError("ATT CCC full translation-unit span changed")
    if _sha256(_slice(blob, *TRAILING_DATA_SPAN)) != TRAILING_DATA_SHA256:
        raise AuditError("ATT CCC trailing literal table changed")
    if _all_u32_occurrences(blob, CONTROL_BLOCK) != CONTROL_BLOCK_LITERAL_CELLS:
        raise AuditError("ATT CCC control-block literal closure changed")
    if _all_u32_occurrences(blob, SOURCE_PATH) != SOURCE_PATH_POINTER_CELLS:
        raise AuditError("ATT CCC source-path pointer closure changed")
    if _all_u32_occurrences(blob, MAIN_CALLBACK_THUMB) != MAIN_CALLBACK_POINTER_CELLS:
        raise AuditError("ATT CCC registered callback pointer closure changed")
    for address in INDIRECT_MAIN_CALLBACK_SITES:
        if _slice(blob, address, address + 2) not in (bytes.fromhex("e047"), bytes.fromhex("a047")):
            raise AuditError(f"ATT CCC indirect consumer changed at 0x{address:08x}")
    if _slice(blob, INDIRECT_APP_CALLBACK_SITE, INDIRECT_APP_CALLBACK_SITE + 2) != bytes.fromhex("8847"):
        raise AuditError("ATT CCC application callback call changed")
    table = _slice(blob, SETTINGS_TABLE[0], SETTINGS_TABLE[0] + SETTINGS_TABLE[1])
    if _sha256(table) != SETTINGS_TABLE[2]:
        raise AuditError("ATT CCC settings table changed")
    settings = [struct.unpack_from("<HHB", table, index * 6) for index in range(6)]
    if settings != EXPECTED_SETTINGS:
        raise AuditError("ATT CCC decoded settings changed")
    _verify_no_other_stored_function_pointers(blob)

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise AuditError("ATT CCC production leaf inventory changed")
    source_hash = PINNED_INPUTS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_LEAF_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise AuditError(f"ATT CCC production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, ((_, start, end, expected, _), function) in enumerate(
        zip(FUNCTIONS, CANDIDATE_FUNCTIONS), 1
    ):
        site = sites.get(f"replace_cordio_atts_ccc_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise AuditError(f"ATT CCC production route {index} changed")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = sum(
        right["expected"]["offset"]
        - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (784, 8, 14):
        raise AuditError("ATT CCC production metrics changed")

    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (
        build["overlay"]["size"] != 404796
        or build["overlay"]["sha256"]
        != "a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d"
        or build["component"]["size"] != 3928192
        or build["component"]["sha256"]
        != "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
        or override["provider"].get("size") != 3928192
        or override["provider"].get("sha256")
        != "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
        or len([
            row for row in override["regions"]
            if row["name"].startswith("cordio_atts_ccc_")
        ]) != 32
    ):
        raise AuditError("ATT CCC component/manifest ownership changed")
    if (
        PACKAGE.stat().st_size != 4706686
        or _sha256(PACKAGE.read_bytes())
        != "30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf"
    ):
        raise AuditError("ATT CCC package changed")
    flash = json.loads(FLASH_PLAN.read_text())
    if (
        FLASH_PLAN.stat().st_size != 4071097
        or _sha256(FLASH_PLAN.read_bytes())
        != "cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d"
        or (
            len(flash["flash_regions"]), len(flash["unresolved_flash_regions"]),
            len(flash["container_only_regions"]), len(flash["protected_regions"]),
        ) != (5863, 2, 5, 6)
    ):
        raise AuditError("ATT CCC flash plan changed")

    linked_bytes = sum(end - start for _, start, end, _, _ in FUNCTIONS)
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
            "inline_and_trailing_data_bytes": FULL_TU_SPAN[1] - FULL_TU_SPAN[0] - linked_bytes,
            "trailing_data_bytes": TRAILING_DATA_SPAN[1] - TRAILING_DATA_SPAN[0],
            "functions": function_reports,
            "source_only_dead_stripped": [],
            "direct_bl_ingress_sites": sum(len(item[-1]) for item in FUNCTIONS),
            "registered_indirect_consumer_sites": INDIRECT_MAIN_CALLBACK_SITES,
            "stored_entry_or_interior_pointers": 1,
            "stored_pointer_qualification": "intentional attsCccMainCback Thumb pointer in TU literal table",
        },
        "abi": {
            "control_block": CONTROL_BLOCK,
            "control_block_size": 24,
            "connection_count": 3,
            "table_pointer_offsets": [0, 4, 8],
            "settings_pointer_offset": 12,
            "application_callback_offset": 16,
            "set_length_offset": 20,
            "set_length": 6,
            "setting_record_size": 6,
            "settings_table": SETTINGS_TABLE[0],
            "settings_table_sha256": SETTINGS_TABLE[2],
            "settings": [
                {"handle": handle, "value_range": value_range, "security_level": security}
                for handle, value_range, security in settings
            ],
            "atts_control_block": 0x2006E5F0,
            "atts_ccc_callback_offset": 0x26C,
            "atts_ccc_callback_address": 0x2006E85C,
            "registered_main_callback": MAIN_CALLBACK_THUMB,
            "application_callback": 0x004B7533,
            "ccc_state_event": 0x14,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "definitions": "byte-identical across AmbiqSuite 2.4.2/2.5.1, Packetcraft r19.02, and r20.05c",
            "r20_discriminator": "ATTS_CCC_STATE_IND is stock value 0x14 rather than r19 value 0x10",
            "stock_qualification": "exact Apache definitions plus r20 event ABI and product validation/diagnostics",
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "anchored_functions_in_probe": 5,
            "anchored_bytes_in_probe": 1_944,
            "compiler_profiles": 2,
            "external_provider_seams": 7,
            "linked_unresolved_symbols": 0,
        },
        "production": {
            "status": "routed",
            "functions": 14,
            "stock_bytes": linked_bytes,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 14,
            "fixed_registered_callback": "0x0052C0AD guarded stock entry",
            "vendor_diagnostics": "not copied; public behavior and G2 validation retained",
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
        print("Cordio ATT CCC audit: 14 linked functions / 2,770 bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
