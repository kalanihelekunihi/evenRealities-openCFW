#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio ATT client-features module."""

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
SOURCE = ROOT / "third_party/cordio/ble-host/sources/stack/att/atts_csf.c"
SOURCE_SHA256 = "1464bff0dbb063ce0e69c5781b73fd7b95656afcd8f710084449298189f2f747"
MATRIX_MANIFEST = (
    ROOT / "research/readiness/atts-csf/SHA256SUMS"
)
MATRIX_SHA256 = "9476cfb102d7d190d1f2c9b94a400322fdd0a367f6a3bc9102f5f4ffcd753b2c"

FUNCTIONS = [
    ("attsCsfSetHashUpdateStatus", 0x0052C6C0, 0x0052C914, "3e82cdcf8bf6da52ceffe46b07aa79953cdfa886b77e41ba9d438319f4601298", [0x004B76FE, 0x00534DBE, 0x005353DE]),
    ("attsCsfGetHashUpdateStatus", 0x0052C914, 0x0052C91C, "e5832fa04a4f4191d1bcdeac73ab1e4f2dde3554c5cbef9774abbbcc1a279e53", [0x004B7C20, 0x0056DED8]),
    ("attsCsfIsClientChangeAware", 0x0052C928, 0x0052CA9C, "b00ee5a3ddb20016ee5b8aed9bd359b34b9e159a6ffafc9787a78ffc81b00670", [0x00533CDA]),
    ("attsCsfActClientState", 0x0052CAA8, 0x0052D06E, "849c162055eda43262db91479bdb8fa0fc871067b878c845a936875d34509f59", [0x00534A1E]),
    ("AttsCsfSetClientsChangeAwarenessState", 0x0052D090, 0x0052D35A, "00d960d49cac61b86ac49c890005a97aca98f4fa0bcc8fcbe1fb606794a2e287", [0x00533E16, 0x0053471A]),
    ("AttsCsfConnOpen", 0x0052D370, 0x0052D4E0, "7e588c21c9d085103a9dd83eb3cd4d574d197a5d7e075bad359f5b4b1d05cb31", [0x004B3826, 0x004B39B8, 0x005345D6, 0x00534614]),
    ("AttsCsfRegister", 0x0052D4E0, 0x0052D4E8, "35fd5f87a5d1760d18de0d80da1d8305e8d922ef8d71e379085c77a016abe77b", [0x0053486A]),
    ("AttsCsfWriteFeatures", 0x0052D508, 0x0052D7B6, "94830e4b9c49ab72bc62f524a2ba7807d3dc7e96fea6303bd7479c55e0b03ca1", [0x004B5B18]),
    ("AttsCsfGetFeatures", 0x0052D7C4, 0x0052D8EE, "d8cfcde7d9789d6fec8d1b30906eedb59dc5a65ae8fd531ff0d9ae91b3a4d7ba", [0x004B5AEC, 0x00534692, 0x0056C70C]),
    ("AttsCsfGetChangeAwareState", 0x0052D8EE, 0x0052DA0C, "c4c1172ec2756d26686491c8e0f2a2683c347d212ea0bec4550ab0a9394ef6ea", [0x00533E08, 0x0053469A]),
]
ENCLOSING_SPAN = (0x0052C6C0, 0x0052DA0C)
ENCLOSING_SHA256 = "adc127436a4dc6d6c2170c6e8a09801d9a3928ae597f4bb5b57804f9be562f09"
CONCATENATED_BODY_SHA256 = "15ae8f65b2be9207298e92daca09ef40bcb3afc808f1240452afcd83ddca3ffa"
CONTROL_BLOCK = 0x20073E04
CONTROL_BLOCK_LITERAL_CELLS = [0x0052D07C, 0x0052DA1C]
SOURCE_PATH = 0x006DC934
SOURCE_PATH_POINTER_CELLS = [0x0052D088, 0x0052DA2C]
# This aligned word occurs inside executable instruction bytes and is not a
# loaded/stored function pointer.  The corpus/xref audit rejects it explicitly.
KNOWN_NONPOINTER_OCCURRENCES = {
    0x0048A894: 0x0052D200,  # aligned instruction bytes
    0x00644A07: 0x0052D800,  # unaligned sequence crossing table fields
}

PINNED_INPUTS = {
    ROOT / "components/shared/cordio/runtime_cordio_atts_csf.c": "f344ea292739c1ddc3e1c59e74d5ed8a8277eb8de424e9759779fd3368564cf0",
    ROOT / "components/shared/cordio/runtime_cordio_atts_csf.h": "ee2ab15775b546aab8d7ce60bd593f22e56e55ae4af1ddced6228f708d13b209",
    ROOT / "tools/manifests/packetcraft-cordio-atts-csf-provenance.tsv": "9fc0f455c04f870b8899b3f717a3dee934d84c52179dcbe776e3fb958f316e31",
    ROOT / "tools/manifests/packetcraft-cordio-atts-csf-function-map.tsv": "fefe258423bbc0b510b02d139c87f01f42abef6525cff24d478e1f72755c6e55",
    ROOT / "tools/manifests/readiness-cordio-atts-csf-build-results.tsv": "0d9817ca888a2826d09882dd60d75cbe40dfd74dededdf988979415daeca8ab5",
    ROOT / "tools/manifests/readiness-cordio-atts-csf-closure-results.tsv": "947002781dbc09d60390c1e48eab96606b81f65303c8d877a32c19f1effa6b25",
    ROOT / "tools/manifests/readiness-cordio-atts-csf-coverage-ranking.tsv": "408a815b339f7275b370eb3679d73ed3b61be40be2ca9514e8df8111c5e45a3c",
    ROOT / "tools/manifests/readiness-cordio-atts-csf-source-identities.tsv": "dffb758f19f36624395946ef7ebeba85be930ca86202c9eef8630fdea81c971c",
    ROOT / "tools/manifests/readiness-cordio-atts-csf-undefined-providers.tsv": "5223cfa9ccacaaff53b55d6e44dc1b654dfceb9cd5e4cf896ea5e1e6bd41e9e7",
    MATRIX_MANIFEST: MATRIX_SHA256,
}

OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_atts_csf.c"
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_atts_csf_set_hash_update_status",
    "open_cfw_cordio_atts_csf_get_hash_update_status",
    "open_cfw_cordio_atts_csf_is_client_change_aware",
    "open_cfw_cordio_atts_csf_act_client_state",
    "open_cfw_cordio_atts_csf_set_clients_change_awareness_state",
    "open_cfw_cordio_atts_csf_connection_open",
    "open_cfw_cordio_atts_csf_register",
    "open_cfw_cordio_atts_csf_write_features",
    "open_cfw_cordio_atts_csf_get_features",
    "open_cfw_cordio_atts_csf_get_change_aware_state",
]
CANDIDATE_LEAF_METRICS = [
    (335380, 58, 1), (335440, 12, 0), (335452, 40, 0),
    (335492, 158, 0), (335652, 62, 0), (335716, 34, 0),
    (335752, 12, 0), (335764, 82, 0), (335848, 24, 0),
    (335872, 20, 0),
]


class AuditError(RuntimeError):
    """Raised when authenticated ATT CSF evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("atts_csf_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _callers(blob: bytes, decoder: Any, target: int) -> list[int]:
    return [
        address
        for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2)
        if decoder._thumb_bl_target(blob, address) == target
    ]


def _all_u32_occurrences(blob: bytes, value: int) -> list[int]:
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
    enclosing_start, enclosing_end = ENCLOSING_SPAN
    for offset in range(len(blob) - 3):
        address = LOAD_BASE + offset
        if enclosing_start <= address < enclosing_end:
            continue
        value = struct.unpack_from("<I", blob, offset)[0]
        if KNOWN_NONPOINTER_OCCURRENCES.get(address) == value:
            continue
        if value in targets:
            raise AuditError(f"unexpected stored ATT CSF pointer at 0x{address:08x}")


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if _sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise AuditError("authenticated Packetcraft atts_csf.c changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned ATT CSF input changed: {path.name}")

    decoder = _load_decoder()
    body_parts: list[bytes] = []
    function_reports = []
    for name, start, end, expected, callers in FUNCTIONS:
        body = _slice(blob, start, end)
        if _sha256(body) != expected:
            raise AuditError(f"ATT CSF stock span changed at 0x{start:08x}")
        actual_callers = _callers(blob, decoder, start)
        if actual_callers != callers:
            raise AuditError(f"ATT CSF direct caller closure changed for {name}")
        body_parts.append(body)
        function_reports.append({
            "name": name,
            "start": start,
            "end_exclusive": end,
            "size": end - start,
            "sha256": expected,
            "direct_bl_callers": actual_callers,
        })
    if _sha256(b"".join(body_parts)) != CONCATENATED_BODY_SHA256:
        raise AuditError("ATT CSF concatenated body identity changed")
    if _sha256(_slice(blob, *ENCLOSING_SPAN)) != ENCLOSING_SHA256:
        raise AuditError("ATT CSF enclosing span identity changed")
    if _all_u32_occurrences(blob, CONTROL_BLOCK) != CONTROL_BLOCK_LITERAL_CELLS:
        raise AuditError("ATT CSF control-block literal closure changed")
    if _all_u32_occurrences(blob, SOURCE_PATH) != SOURCE_PATH_POINTER_CELLS:
        raise AuditError("ATT CSF source-path pointer closure changed")
    _verify_no_stored_function_pointers(blob)

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise AuditError("ATT CSF production leaf inventory changed")
    candidate_hash = PINNED_INPUTS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_LEAF_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != candidate_hash:
            raise AuditError(f"ATT CSF production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, ((_, start, end, expected, _), function) in enumerate(
        zip(FUNCTIONS, CANDIDATE_FUNCTIONS), 1
    ):
        site = sites.get(f"replace_cordio_atts_csf_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise AuditError(f"ATT CSF production route {index} changed")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = 2
    alignment += sum(
        right["expected"]["offset"]
        - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (502, 12, 1):
        raise AuditError("ATT CSF production metrics changed")

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
            if row["name"].startswith("cordio_atts_csf_")
        ]) != 26
    ):
        raise AuditError("ATT CSF component/manifest ownership changed")
    if (
        PACKAGE.stat().st_size != 4706686
        or _sha256(PACKAGE.read_bytes())
        != "30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf"
    ):
        raise AuditError("ATT CSF package changed")
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
        raise AuditError("ATT CSF flash plan changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": ENCLOSING_SPAN[0],
            "end_exclusive": ENCLOSING_SPAN[1],
            "enclosing_bytes": ENCLOSING_SPAN[1] - ENCLOSING_SPAN[0],
            "enclosing_sha256": ENCLOSING_SHA256,
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for _, start, end, _, _ in FUNCTIONS),
            "concatenated_body_sha256": CONCATENATED_BODY_SHA256,
            "literal_or_data_gap_bytes": (ENCLOSING_SPAN[1] - ENCLOSING_SPAN[0]) - sum(end - start for _, start, end, _, _ in FUNCTIONS),
            "functions": function_reports,
            "source_only_dead_stripped": ["AttsCsfInit"],
            "stored_external_entry_or_interior_pointers": 0,
        },
        "abi": {
            "control_block": CONTROL_BLOCK,
            "record_count": 3,
            "record_size": 2,
            "record_csf_offset": 0,
            "record_state_offset": 1,
            "write_callback_offset": 8,
            "hash_update_offset": 12,
            "minimum_control_block_size": 13,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "historical_ambiq_oracle": "AmbiqSuite 2.4.2/2.5.1 equals Packetcraft r19.02",
            "r20_discriminator": "WriteFeatures masks 0x07, rejects only old-nonzero to new-zero, and ORs new bits",
            "stock_qualification": "r20 public behavior with Ambiq-era exported names and vendor validation/diagnostic augmentation",
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(MATRIX_MANIFEST),
            "archive_sha256": MATRIX_SHA256,
            "compiler_profiles": 2,
            "external_provider_seams": ["WsfTrace", "attsCheckPendDbHashReadRsp", "memcpy", "memset"],
            "linked_unresolved_symbols": 0,
            "normalized_comparison": "deferred until vendor instrumentation seam is modeled",
        },
        "production": {
            "status": "routed",
            "functions": 10,
            "stock_bytes": 4814,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 10,
            "business_provider": "0x00534DD8 attsCheckPendDbHashReadRsp",
            "vendor_diagnostics": "not copied; public Packetcraft business behavior retained",
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
        print("Cordio ATTS CSF audit: 10 linked functions / 4,814 bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
