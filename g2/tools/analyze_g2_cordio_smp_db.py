#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio SMP pairing database."""

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
SOURCE = ROOT / "third_party/cordio/ble-host/sources/stack/smp/smp_db.c"
SOURCE_SHA256 = "d73d33be7c3d64476b8edb763bb0f32f4a49b54e07a65d44cbfbc4b2deb76645"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_db.c"
PRODUCTION_SOURCE_SIZE = 11_087
PRODUCTION_SOURCE_SHA256 = "e103f1e933f1d7bff5939c2e013162de68bace7298320d879bddd5f5859c5cb5"
PRODUCTION_ROUTES = {
    "open_cfw_cordio_smp_db_start_service_timer": (167428, 24, "08be799b93d245443105e7f6ff3bc8ec63b407a151bb5dad494e9bd91dccf907", "smpDbStartServiceTimer"),
    "open_cfw_cordio_smp_db_record_in_use": (167452, 22, "c7fae2a177d131316029dd50b843fdbb4f943af4a2bfc5017ce3beeef17131d4", "smpDbRecordInUse"),
    "open_cfw_cordio_smp_db_add_device": (167476, 164, "1283c3496a28beffc9edf6fbb0fc0b7d944add3bbdd6c993ec0e81f82ae26ba6", "smpDbAddDevice"),
    "open_cfw_cordio_smp_db_get_record": (167640, 154, "5807d82fbd2186deb39dfff0c9e88890d08c68c2d0bc1e2ee95a6ce002a9f7b8", "smpDbGetRecord"),
    "open_cfw_cordio_smp_db_init": (167796, 50, "e677955d7d28beab21c27affe4664ca54afd929641d3a254fe830cd1c9ccf6b4", "SmpDbInit"),
    "open_cfw_cordio_smp_db_get_pairing_disabled_time": (167848, 10, "1e1d3e59424b66960e5a6cd0ca209bd6d786f8122e243d5816ee0bc36b06da88", "SmpDbGetPairingDisabledTime"),
    "open_cfw_cordio_smp_db_set_failure_count": (167860, 32, "be5dc5191a5863551d1832c0c08fc1c4fdfa5ae9c2bd4256bc7c94d3f2d58686", "SmpDbSetFailureCount"),
    "open_cfw_cordio_smp_db_get_failure_count": (167892, 10, "2eee09488f14ec7e9da9e8a6eb30a6fca3a64dad74e64f911e4ef1883ac5303e", "SmpDbGetFailureCount"),
    "open_cfw_cordio_smp_db_max_attempt_reached": (167904, 68, "e9c8c77d2fb7b0985f2e97bbb8ff971c39ec73a9909ff8abfd6151d78d6baa1c", "SmpDbMaxAttemptReached"),
    "open_cfw_cordio_smp_db_pairing_failed": (167972, 22, "f64d381e31652844412d56423c349122e4d1236825313c99766b044399178397", "SmpDbPairingFailed"),
    "open_cfw_cordio_smp_db_service": (167996, 142, "f2f2ad97e900de41137e9223d3d04c687ccdfaaf22c9c577be38ea677f71a9ca", "SmpDbService"),
}
READINESS_MANIFEST = ROOT / "research/readiness/smp-db/SHA256SUMS"
READINESS_SHA256 = "cdb7e4f260e901cc1036a5d6be521e2b9c55b08ecf0510df55ca77c355a5d48e"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-smp-db-function-map.tsv": "7686a2a99385ed03b7c6f4c81d26e3b501f5e7b0ecfe0757e0245469a83b453a",
    ROOT / "tools/manifests/packetcraft-cordio-smp-db-provenance.tsv": "2e8dea8bd81498a0b4229a9f48a6cf71fbb60e3c59fcec74bbf0abfd760dfbf5",
    ROOT / "tools/manifests/readiness-cordio-smp-db-build-results.tsv": "ddc13459bbbc8d302792bcc2621f7fd12051ff0ef0edc97509300fe79b49bf86",
    ROOT / "tools/manifests/readiness-cordio-smp-db-closure-results.tsv": "d85bfc1430724ca8525273d2df901231b6a5cc4b9ed472ff9eb8e3e11234b8d7",
    ROOT / "tools/manifests/readiness-cordio-smp-db-source-identities.tsv": "9fbb27ea8527a2ea02ee5f1721cae98d4f50096bc5413ded3db3a0c7a2eefb5e",
    ROOT / "tools/manifests/readiness-cordio-smp-db-undefined-providers.tsv": "39c5db9f1448e86e9384f818e968e30c6fb8c72151a54301d9bcef2a4d28afa2",
}

FUNCTIONS = [
    ("smpDbStartServiceTimer", 0x00541E34, 0x00541E50, "cfda2c7f20e17faf4edec629bc74e4006fc417227acc9f51bba221a972660f6e", [0x00542822, 0x005429B2]),
    ("smpDbRecordInUse", 0x00541E50, 0x00541E72, "59c1b23356e3a794b34b59d680fa15bf83a5f8b21a71ed6de528dc889cebe6fb", [0x00541F92, 0x00542140, 0x005429AA, 0x005429C4]),
    ("smpDbAddDevice", 0x00541E72, 0x00541FB8, "9b0fb1de560cbdf00cdd0743dfc9c49ef0098913149edc9bedad75e011bac94a", [0x00542168]),
    ("smpDbGetRecord", 0x00541FB8, 0x00542284, "c30bfc998d2d154018f99bf4abdd603e631d8c87c1056a184532cb4a3fcb166f", [0x005422CE, 0x00542422, 0x00542586, 0x005426C8, 0x00542840]),
    ("SmpDbInit", 0x00542288, 0x005422C0, "0c5fae6586c0694d46e588a99da1d80ecb0c61fc49815b0d5fdc5bc391c225f4", [0x004D2546, 0x00537CBC]),
    ("SmpDbGetPairingDisabledTime", 0x005422C4, 0x00542418, "78150cb326603fd44f1abc62b94d872836d47be33cb7ed861dd3d2305fd635ae", [0x005374AE]),
    ("SmpDbSetFailureCount", 0x00542418, 0x00542570, "9bf8baf9e6f7f22579d9573254cfb3b002272b3cb40e2251e2f45e595c6cde69", [0x00537590]),
    ("SmpDbGetFailureCount", 0x0054257C, 0x005426C0, "103da856edd34946a156321579273b3edba3b1baa4761978bc6a64e824bd9de8", [0x00537556]),
    ("SmpDbMaxAttemptReached", 0x005426C0, 0x0054282A, "8044e0eb9c12b829b3971389513601525c606146d4174ec22449c8206e565b19", [0x0056EDBC]),
    ("SmpDbPairingFailed", 0x00542838, 0x0054294C, "5fbbc65f4efd1c3410a19038221f6eae68a0dbe281573c6bfc52f1c275df19b7", [0x0056D2D8, 0x005E32C0, 0x005E3876, 0x005E3B86, 0x005E41DC]),
    ("SmpDbService", 0x00542960, 0x005429F2, "a44bd312af6978a1232f7a5a26a46578c0c60844a24505a87291dd8cff62ac5d", [0x00537D1E]),
]
ENCLOSING_SPAN = (0x00541E34, 0x005429F2)
ENCLOSING_SHA256 = "c95c938f90cd5eb037d82d6346e2ebe63ae7d99b9962fbaa50f193e4c1f4e88c"
CONCATENATED_BODY_SHA256 = "a4713a22d25b1b8730a81fab7fb18e1c9db4d92f1e5db5ed7b0aa785bab7b23a"
CONTROL_BLOCK = 0x200708EC
CONTROL_BLOCK_LITERAL_CELLS = [0x005429F4]
FIRST_SPECIFIC_RECORD = 0x20070904
FIRST_SPECIFIC_RECORD_LITERAL_CELLS = [0x0054294C]
SOURCE_PATH = 0x006E19F0
SOURCE_PATH_POINTER_CELLS = [0x00542958]
BOOT_CONFIG = (0x007759A4, 24, "63afedc66e52e80b44aa4454ae9c03415c9082fef1f250ddbc4b0bf2460c2c18")
RUNTIME_CONFIG = (0x00774D44, 24, "7db420b72422b1d33d7bc86233f0a483fc1b506589168714a8d3e5503c793a3b")


class AuditError(RuntimeError):
    """Raised when authenticated SMP DB evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smp_db_thumb", path)
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
        if value in targets:
            raise AuditError(f"unexpected stored SMP DB pointer at 0x{address:08x}")


def _production_report() -> dict[str, Any]:
    source = PRODUCTION_SOURCE.read_bytes()
    if len(source) != PRODUCTION_SOURCE_SIZE or _sha256(source) != PRODUCTION_SOURCE_SHA256:
        raise AuditError("Cordio SMP DB production source identity changed")
    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    leaves = {
        row["function"]: row for row in overlay.get("relocated_leaves", [])
        if row.get("function") in PRODUCTION_ROUTES
    }
    patches = {
        row["target_function"]: row for row in overlay.get("patch_sites", [])
        if row.get("target_function") in PRODUCTION_ROUTES
    }
    if set(leaves) != set(PRODUCTION_ROUTES) or set(patches) != set(PRODUCTION_ROUTES):
        raise AuditError("Cordio SMP DB production routing is incomplete")
    stock = {name: (start, end - start, digest) for name, start, end, digest, _ in FUNCTIONS}
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    for function, (offset, size, digest, stock_name) in PRODUCTION_ROUTES.items():
        leaf = leaves[function]
        patch = patches[function]
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
            or leaf.get("strict_relocation_contract") is not True
        ):
            raise AuditError(f"Cordio SMP DB production leaf changed: {function}")
        stock_start, stock_size, stock_digest = stock[stock_name]
        if (
            patch.get("profiles") != ["apple-clang"]
            or patch.get("runtime_address") != stock_start
            or patch.get("expected_size") != stock_size
            or patch.get("expected_sha256") != stock_digest
            or patch.get("branch") != "b_w"
        ):
            raise AuditError(f"Cordio SMP DB stock patch changed: {function}")
    return {
        "status": "production-routed authenticated Packetcraft definitions with G2 ten-record/r20 ABI",
        "candidate": source_path,
        "production_routed": True,
        "live_functions": len(PRODUCTION_ROUTES),
        "compiled_leaf_bytes": sum(item[1] for item in PRODUCTION_ROUTES.values()),
        "source_owned_bytes_added": 712,
        "stock_bytes_replaced": sum(item[1] for item in stock.values()),
        "hardware_validation": "blocked by unavailable physical evidence",
    }


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if _sha256(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise AuditError("authenticated Packetcraft smp_db.c changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei SMP DB readiness artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned SMP DB input changed: {path.name}")

    decoder = _load_decoder()
    all_callers = _all_callers(blob, decoder)
    body_parts: list[bytes] = []
    function_reports = []
    for name, start, end, expected, callers in FUNCTIONS:
        body = _slice(blob, start, end)
        if _sha256(body) != expected:
            raise AuditError(f"SMP DB stock span changed at 0x{start:08x}")
        if all_callers[start] != callers:
            raise AuditError(f"SMP DB direct caller closure changed for {name}")
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
        raise AuditError("SMP DB concatenated body identity changed")
    if _sha256(_slice(blob, *ENCLOSING_SPAN)) != ENCLOSING_SHA256:
        raise AuditError("SMP DB enclosing span identity changed")
    if _all_u32_occurrences(blob, CONTROL_BLOCK) != CONTROL_BLOCK_LITERAL_CELLS:
        raise AuditError("SMP DB control-block literal closure changed")
    if _all_u32_occurrences(blob, FIRST_SPECIFIC_RECORD) != FIRST_SPECIFIC_RECORD_LITERAL_CELLS:
        raise AuditError("SMP DB specific-record literal closure changed")
    if _all_u32_occurrences(blob, SOURCE_PATH) != SOURCE_PATH_POINTER_CELLS:
        raise AuditError("SMP DB source-path pointer closure changed")
    for address, size, expected in (BOOT_CONFIG, RUNTIME_CONFIG):
        if _sha256(_slice(blob, address, address + size)) != expected:
            raise AuditError(f"SMP configuration changed at 0x{address:08x}")
    _verify_no_stored_function_pointers(blob)

    linked_bytes = sum(end - start for _, start, end, _, _ in FUNCTIONS)
    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": ENCLOSING_SPAN[0],
            "end_exclusive": ENCLOSING_SPAN[1],
            "enclosing_bytes": ENCLOSING_SPAN[1] - ENCLOSING_SPAN[0],
            "enclosing_sha256": ENCLOSING_SHA256,
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": linked_bytes,
            "concatenated_body_sha256": CONCATENATED_BODY_SHA256,
            "literal_or_data_gap_bytes": ENCLOSING_SPAN[1] - ENCLOSING_SPAN[0] - linked_bytes,
            "functions": function_reports,
            "source_only_dead_stripped": ["SmpDbRemoveAllDevices", "SmpDbRemoveDevice"],
            "stored_external_entry_or_interior_pointers": 0,
        },
        "abi": {
            "control_block": CONTROL_BLOCK,
            "control_block_size": 0x100,
            "record_count": 10,
            "record_size": 24,
            "records_bytes": 240,
            "service_timer_offset": 0xF0,
            "service_timer_size": 16,
            "service_timer_event_offset": 0xFA,
            "service_timer_handler_id_offset": 0xFC,
            "service_timer_started_offset": 0xFD,
            "service_event": 0x20,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "definitions": "byte-identical across AmbiqSuite 2.4.2/2.5.1, Packetcraft r19.02, and r20.05c",
            "r20_discriminator": "SMP_DB_SERVICE_IND is stock value 0x20 after SMP_MSG_INT_CLEANUP",
            "product_override": "SMP_DB_MAX_DEVICES=10; examined upstream defaults are 3",
            "stock_qualification": "exact Apache definitions plus r20 event ABI, product record-count override, and expanded diagnostics",
            "license": "Apache-2.0",
        },
        "configuration": {
            "pointer_global": 0x200004B8,
            "boot_data_initializer": {
                "address": BOOT_CONFIG[0],
                "sha256": BOOT_CONFIG[2],
                "attempt_timeout_ms": 500,
                "max_attempts": 1,
                "auth": 0,
                "max_attempt_timeout_ms": 64_000,
                "attempt_decrement_timeout_ms": 64_000,
                "attempt_exponent": 2,
            },
            "normal_product_runtime_override": {
                "address": RUNTIME_CONFIG[0],
                "sha256": RUNTIME_CONFIG[2],
                "assignment_call_site": 0x004B80AA,
                "attempt_timeout_ms": 3_000,
                "max_attempts": 3,
                "auth": 1,
                "max_attempt_timeout_ms": 64_000,
                "attempt_decrement_timeout_ms": 64_000,
                "attempt_exponent": 2,
            },
            "shared_fields": {
                "io_capability": 3,
                "minimum_key_length": 7,
                "maximum_key_length": 16,
            },
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "anchored_functions_in_probe": 7,
            "anchored_bytes_in_probe": 2_688,
            "compiler_profiles": 2,
            "external_provider_seams": 11,
            "linked_unresolved_symbols": 0,
        },
        "production": _production_report(),
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
        print("Cordio SMP DB audit: 11 linked functions / 2,952 bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
