#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_glasses_case object."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-glasses-case-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-glasses-case-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-glasses-case-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_glasses_case.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "9a4b8121f28d1b0692a6ce7416b8f33946246b39b64ae66cf8acd03d5013d5fe",
    CLOSURE: "f2622f912f0581658b67830678f839fd03d5872f32f0dc9cfd4beca236540d70",
    PROVENANCE: "1b21a58be7a2b305c720a7cef16cba829cadd893f28a7bf5075ed001de375713",
}
SOURCE_SIZE = 9310
SOURCE_SHA256 = "ea16057545663e50239f29b573cf5f09f25d4441d8ac92626d1919826b5dcb90"
FUNCTIONS = (
    ("open_cfw_pb_service_glasses_case_buffer_write", 146, 254324, 0),
    ("PB_RxGlassesCaseInfo", 10, 254472, 0),
    ("APP_PbTxEncodeGlassesCaseInfo", 146, 254484, 8),
    ("APP_PbNotifyEncodeGlassesCaseInfo", 142, 254632, 4),
    ("APP_PbRxGlassesCaseFrameDataProcess", 102, 254776, 4),
)
PATCHES = (
    ("replace_pb_case_rx_frame", 0x00510A0C, 498,
     "51066606d4eddeff00303140367954f03d501a5f413fedcac973c0b1f5bbe5b7",
     "APP_PbRxGlassesCaseFrameDataProcess"),
    ("replace_pb_case_rx_info", 0x00510BFE, 114,
     "e881ef96ab4ee313b75c0d407bb549e8aa96ab9de1f7be03156f3fc8291ab44d",
     "PB_RxGlassesCaseInfo"),
    ("replace_pb_case_tx_info", 0x00510C70, 380,
     "45f08df708bb8714a8097839808bdb3233101624c63ecddc25f80dec4abc7487",
     "APP_PbTxEncodeGlassesCaseInfo"),
    ("replace_pb_case_notify_info", 0x00510DEC, 368,
     "265fcf4acbf63011c595cacf8184c475b85bddc2f742fcdeb7390b886b15007d",
     "APP_PbNotifyEncodeGlassesCaseInfo"),
)
PHYSICAL = (0x00510A0C, 0x00510FD8)
PHYSICAL_SHA256 = "ac1926863f4700afd938a0f9d234c3a6c0be103f327f591c7cc066d13be61bf2"
POOL = (0x00510F5C, 0x00510FD8)
POOL_SHA256 = "e6e942104a74517b41485867b0b592911951af365363935b324d92110a362de1"
BODY_SHA256 = "39f291afe8bb87e933c35c4d28ed0a66f7f925dcdb0ca765b2bf3562f25e2472"
ENTRY_SHA256 = "8b88414a2a4ea904a86c373f4489b4925766a5ba0942d815639a37690086ea2b"
BODY_CALL_SHA256 = "ac3635c1e3013186a5d1f9cada25caac3e1089d399281468c5e3e6da88d8ef25"
RAW_WINDOW_SHA256 = "8dc7a9779381da6b39105f4564beb7fe749aa1f578dc0bfb91eccb70dfe543a4"
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_glasses_case\pb_service_glasses_case.c"
)
POOL_WORDS = (
    0x0078DEBC, 0x007579C8, 0x006D7B1C, 0x00787DA0, 0x0077A2AC,
    0x00787DB0, 0x007633F0, 0x200F5A90, 0x0077793C, 0x0078DEC4,
    0x00781DF4, 0x0074C33C, 0x0076F684, 0x00736704, 0x0077A2C4,
    0x0074C364, 0x00781E08, 0x00787DC0, 0x0077A2DC, 0x00763410,
    0x00781E1C, 0x00763430, 0x2037C5A0, 0x200F5A9C, 0x0078B714,
    0x0076F6A0, 0x0077A2F4, 0x0074C38C, 0x00781E30, 0x007579EC,
    0x20074FFA,
)
STRINGS = {
    0x0078DEBC: "len=%d",
    0x007579C8: "APP_PbRxGlassesCaseFrameDataProcess",
    0x006D7B1C: RETAINED_PATH,
    0x00787DA0: "pb.glasses_case",
    0x0077A2AC: "[pb.glasses_case]len=%d",
    0x00787DB0: "pData is NULL",
    0x007633F0: "[pb.glasses_case]pData is NULL",
    0x0078DEC4: "(none)",
    0x00781DF4: "Decoding failed: %s",
    0x0074C33C: "[pb.glasses_case]Decoding failed: %s",
    0x0076F684: "glasses_case command_id: %d",
    0x00736704: "[pb.glasses_case]glasses_case command_id: %d",
    0x0077A2C4: "Unknown command_id: %d",
    0x0074C364: "[pb.glasses_case]Unknown command_id: %d",
    0x00787DC0: "POINTER NULL",
    0x0077A2DC: "PB_RxGlassesCaseInfo",
    0x00763410: "[pb.glasses_case]POINTER NULL",
    0x00763430: "APP_PbTxEncodeGlassesCaseInfo",
    0x0078B714: "txLen = %d",
    0x0076F6A0: "[pb.glasses_case]txLen = %d",
    0x0077A2F4: "Encoding failed: %s\n",
    0x0074C38C: "[pb.glasses_case]Encoding failed: %s\n",
    0x007579EC: "APP_PbNotifyEncodeGlassesCaseInfo",
}
ASSERT_RECORDS = {
    0x00781E08: "00000000000000001c7b6d00dca2770056000000",
    0x00781E1C: "00000000000000001c7b6d003034760064000000",
    0x00781E30: "00000000000000001c7b6d00ec7975008a000000",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    return data[start - BASE : end - BASE]


def pair_digest(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("ascii")


def thumb_bw_target(data: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", data, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def analyze(image_path: Path = IMAGE) -> dict:
    data = image_path.read_bytes()
    if len(data) != 3_523_396 or sha256(data) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 4 or sum(map(len, bodies)) != 1360:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")
    pool = image_slice(data, *POOL)
    if len(pool) != 124 or sha256(pool) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if struct.unpack("<31I", pool) != POOL_WORDS:
        raise AuditError("literal pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("80b50020"):
        raise AuditError("next-function boundary changed")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    for address, expected_hex in ASSERT_RECORDS.items():
        if image_slice(data, address, address + 20).hex() != expected_hex:
            raise AuditError(f"assert record changed at 0x{address:08x}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == 0x006D7B1C]
    if path_cells != [0x00510F64, 0x00781E10, 0x00781E24, 0x00781E38]:
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    expected_entry = [
        (0x004ABF7E, 0x00510DEC), (0x004ACB52, 0x00510A0C),
        (0x00510B9C, 0x00510BFE), (0x00510BA8, 0x00510C70),
    ]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    if interior or entry_bw or interior_bw:
        raise AuditError("direct strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 86 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_windows: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_windows.append((BASE + offset, value))
    if len(raw_windows) != 6 or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw pointer-window closure changed")
    if any((value & ~1) in starts for _, value in raw_windows):
        raise AuditError("unexpected stored exact-entry pointer")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sha256(source) != SOURCE_SHA256:
        raise AuditError("production source changed")
    overlay = json.loads(OVERLAY.read_text())
    names = {row[0] for row in FUNCTIONS}
    leaves = {item.get("function"): item for item in overlay["relocated_leaves"]
              if item.get("function") in names}
    if set(leaves) != names:
        raise AuditError("production leaf inventory changed")
    for name, size, offset, relocations in FUNCTIONS:
        leaf = leaves[name]
        if (leaf["source"].get("path") !=
                "components/apollo_main/core_overlay/pb_service_glasses_case.c"
                or leaf["source"].get("size") != SOURCE_SIZE
                or leaf["source"].get("sha256") != SOURCE_SHA256
                or leaf.get("profiles") != ["apple-clang"]
                or leaf.get("strict_relocation_contract") is not True
                or (leaf["expected"].get("size"), leaf["expected"].get("offset"),
                    leaf["expected"].get("alignment")) != (size, offset, 4)
                or len(leaf.get("relocations", [])) != relocations):
            raise AuditError(f"production leaf changed: {name}")
    patch_by_name = {item.get("name"): item for item in overlay["patch_sites"]}
    for name, address, size, digest, function in PATCHES:
        patch = patch_by_name.get(name)
        if patch is None or (
            patch.get("runtime_address"), patch.get("expected_size"),
            patch.get("expected_sha256"), patch.get("branch"),
            patch.get("target_function"), patch.get("profiles"),
        ) != (address, size, digest, "b_w", function, ["apple-clang"]):
            raise AuditError(f"production patch changed: {name}")
    report = json.loads(REPORT.read_text())
    validate_apollo_main_artifacts(ROOT, AuditError, "protobuf glasses-case service")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    region_names = {item["name"] for item in main["regions"]}
    required = {name.removeprefix("replace_") + "_source_replacement"
                for name, *_ in PATCHES}
    required |= {
        "pb_service_glasses_case_retained_literal_pool",
        "pb_case_buffer_write_source_alignment", "pb_case_buffer_write_source_text",
        "pb_case_rx_info_source_alignment", "pb_case_rx_info_source_text",
        "pb_case_tx_info_source_alignment", "pb_case_tx_info_source_text",
        "pb_case_notify_info_source_alignment", "pb_case_notify_info_source_text",
        "pb_case_rx_frame_source_alignment", "pb_case_rx_frame_source_text",
    }
    if not required <= region_names:
        raise AuditError("production manifest regions changed")

    return {
        "surface": {
            "linked_functions": 4,
            "body_bytes": 1360,
            "owned_pool_bytes": 124,
            "physical_bytes": 1484,
            "direct_bl_entry_sites": 4,
            "direct_body_calls": 86,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 6,
        },
        "contracts": {
            "rx_status": {"success": 0, "unsupported_or_invalid": 1,
                          "null": 2, "decode_failure": 0x2B},
            "tx_status": {"success": 0, "null": 2, "encode_failure": 0x2B},
            "command_id": 1,
            "nested_payload_tag": 3,
            "route": 1,
            "service": "0x81",
            "decoded_message": "0x200f5a90",
            "encoded_message": "0x200f5a9c",
            "message_bytes": 10,
            "encode_buffer": "0x2037c5a0",
            "encode_capacity": 0x100,
            "notify_sequence": "0x20074ffa",
            "case_info_bytes": ["battery", "charging", "lid", "glasses_present", "error"],
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [row["function"] for row in rows],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 1360,
            "source_inventory_available": True,
            "source_functions": 5,
            "compiled_text_bytes": 546,
            "alignment_bytes": 10,
            "strict_relocations": 16,
            "stock_replaced_bytes": 1360,
            "retained_literal_pool_bytes": 124,
            "software_functional_gap": False,
            "hardware_validation": "deferred by project direction",
            "hardware_blocker": (
                "No authorized live glasses-case/temple BLE service 0x81 exchange "
                "or physical case-state evidence is required for future qualification; the authorized right "
                "temple is not under test because qualification is deferred by project direction and the left temple must remain stock."
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_glasses_case audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
