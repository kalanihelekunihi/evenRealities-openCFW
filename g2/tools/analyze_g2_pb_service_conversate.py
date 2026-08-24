#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_conversate object."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-conversate-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-conversate-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-conversate-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_conversate.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "8aa74eee0465950b21ff578add627df49e6b96b227beb7ce97167569955c4d31",
    CLOSURE: "68bef70d987506d41098eae1932a35ec44d56501e4cf32b5be9a66fba0784883",
    PROVENANCE: "d6e10558860b88b9af4a792496c0feb3a46fdfa93a5f3a6887e3f10b0a771a65",
}
SOURCE_SIZE = 12137
SOURCE_SHA256 = "04ded321c0a5f25be9328fbe971512cf16f54657e9e91e6c56605e2d740d579c"
FUNCTIONS = (
    ("open_cfw_pb_service_conversate_buffer_write", 146, 195032, 0),
    ("open_cfw_pb_service_conversate_zero", 88, 195180, 0),
    ("APP_PbConversateRxFrameDataProcess", 112, 195268, 3),
    ("APP_PbConversateTxEncodeNotify", 148, 195380, 6),
    ("APP_PbConversateTxEncodePrepNoteListRequest", 132, 195528, 6),
    ("APP_PbConversateTxEncodePrepNoteSelect", 150, 195660, 6),
    ("APP_PbConversateTxEncodeCommResp", 134, 195812, 6),
    ("APP_PbConversateTxEncodeTagTrackingData", 188, 195948, 6),
)
PATCHES = (
    ("replace_pb_conversate_rx", 0x005B1B4C, 478,
     "9055629cf9abb554af3ba3c7e59c869c0286a5e9660530fcf27f2f54c2954e90",
     "APP_PbConversateRxFrameDataProcess"),
    ("replace_pb_conversate_notify", 0x005B1D2A, 296,
     "30dcade56040cb400d07ea0227e4e5fd06ef82248ec075fdb51b82d9af2611f8",
     "APP_PbConversateTxEncodeNotify"),
    ("replace_pb_conversate_prep_list", 0x005B1E52, 220,
     "8853d8e3ccc7a935284ca42f964e6d4438b59dde5962ed0e9331212f86d7a83e",
     "APP_PbConversateTxEncodePrepNoteListRequest"),
    ("replace_pb_conversate_prep_select", 0x005B1F2E, 224,
     "49f6118e9df734a2d83a2875eef01760473e6e49c61f5443a406a3e1c4d1498a",
     "APP_PbConversateTxEncodePrepNoteSelect"),
    ("replace_pb_conversate_comm_resp", 0x005B200E, 288,
     "b3a9bbda733270d509a7bc3c85c0a47af5b922fbc4502e338ffe1e656991bc5e",
     "APP_PbConversateTxEncodeCommResp"),
    ("replace_pb_conversate_tag_tracking", 0x005B212E, 270,
     "3bea211c087a0db1d6b9c791a9625e6c1ef27b6b2caea13f7e8d6459ca0fd257",
     "APP_PbConversateTxEncodeTagTrackingData"),
)
PHYSICAL = (0x005B1B4C, 0x005B22BC)
PHYSICAL_SHA256 = "8973bc2f23588773f4ce41491809689c35bbe7f1f835bf5b21c038a5c657e841"
POOL = (0x005B223C, 0x005B22BC)
POOL_SHA256 = "fc31e0445401528eb108e36d401ac1f290153a7f9ea1afc9599a348873dc9153"
BODY_SHA256 = "a5a3e25703df5244595d88d3c2653a814fcd43854f059ea5dce3b2a9af0c2fce"
ENTRY_SHA256 = "6fcc3dfebf5af553422cdf012699d59fc88355531fbf21bdc8ca91756aff6eb3"
BODY_CALL_SHA256 = "48540779e8e309d4057f409f72426e412efab45e628c373aa25820ba4bf65940"
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_conversate\pb_service_conversate.c"
)
POOL_WORDS = (
    0x0076F48C, 0x007576B0, 0x006D942C, 0x00787D00, 0x0074C134,
    0x007818E0, 0x00775B24, 0x0078DE84, 0x007818F4, 0x007576D4,
    0x20074FF8, 0x0071753C, 0x006F4F84, 0x2007485C, 0x006F4FD0,
    0x006E1150, 0x00787D10, 0x00762F50, 0x00762F70, 0x200F4808,
    0x2037C2A0, 0x00781908, 0x007576F8, 0x00741158, 0x0074C15C,
    0x00787D20, 0x0075771C, 0x00762F90, 0x0078191C, 0x0076F4A8,
    0x0074C184, 0x0074C1AC,
)
STRINGS = {
    0x0076F48C: "pData or message is NULL",
    0x007576B0: "APP_PbConversateRxFrameDataProcess",
    0x006D942C: RETAINED_PATH,
    0x00787D00: "pb.conversate",
    0x0074C134: "[pb.conversate]pData or message is NULL",
    0x007818E0: "Conversate_pb_rx",
    0x0078DE84: "(none)",
    0x007818F4: "Decoding failed: %s",
    0x007576D4: "[pb.conversate]Decoding failed: %s",
    0x0071753C: "command_id: %d, magic number = %d, last magic number = %d",
    0x006F4F84: "[pb.conversate]command_id: %d, magic number = %d, last magic number = %d",
    0x006F4FD0: "Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore",
    0x006E1150: "[pb.conversate]Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore",
    0x00787D10: "pNotify is NULL",
    0x00762F50: "APP_PbConversateTxEncodeNotify",
    0x00762F70: "[pb.conversate]pNotify is NULL",
    0x00781908: "Encoding failed: %s",
    0x007576F8: "[pb.conversate]Encoding failed: %s",
    0x00741158: "APP_PbConversateTxEncodePrepNoteListRequest",
    0x0074C15C: "APP_PbConversateTxEncodePrepNoteSelect",
    0x00787D20: "pResp is NULL",
    0x0075771C: "APP_PbConversateTxEncodeCommResp",
    0x00762F90: "[pb.conversate]pResp is NULL",
    0x0078191C: "Conversate_pb_resp",
    0x0076F4A8: "pTagTrackingData is NULL",
    0x0074C184: "APP_PbConversateTxEncodeTagTrackingData",
    0x0074C1AC: "[pb.conversate]pTagTrackingData is NULL",
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
    if len(rows) != 6 or sum(map(len, bodies)) != 1776:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")
    pool = image_slice(data, *POOL)
    if len(pool) != 128 or sha256(pool) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if struct.unpack("<32I", pool) != POOL_WORDS:
        raise AuditError("literal pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("70b50400"):
        raise AuditError("next-function boundary changed")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == 0x006D942C]
    if path_cells != [0x005B2244]:
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
        (0x005B049A, 0x005B1B4C), (0x005B04F0, 0x005B200E),
        (0x005B054C, 0x005B200E), (0x005B05AC, 0x005B200E),
        (0x005B05BA, 0x005B200E), (0x005B0840, 0x005B1D2A),
        (0x005B57D0, 0x005B1F2E), (0x005B5828, 0x005B1F2E),
        (0x005B59BA, 0x005B1E52), (0x005B66C6, 0x005B212E),
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
    if len(calls) != 96 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if stored:
        raise AuditError("unexpected stored entry/interior pointer")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sha256(source) != SOURCE_SHA256:
        raise AuditError("production source changed")
    overlay = json.loads(OVERLAY.read_text())
    names = {item[0] for item in FUNCTIONS}
    leaves = {item.get("function"): item for item in overlay["relocated_leaves"]
              if item.get("function") in names}
    if set(leaves) != names:
        raise AuditError("production leaf inventory changed")
    for name, size, offset, relocations in FUNCTIONS:
        leaf = leaves[name]
        if (leaf["source"].get("path") !=
                "components/apollo_main/core_overlay/pb_service_conversate.c"
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
    if (report["overlay"]["size"], report["overlay"]["sha256"],
            report["component"]["size"], report["component"]["sha256"]) != (
        240692, "2db11ff707bf253280eb07667c3d76954347cc9e31796c7589faf788fed629ae",
        3764088, "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
    ):
        raise AuditError("production build pins changed")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    if (main["provider"].get("size"), main["provider"].get("sha256"),
            manifest["package"].get("expected_size"),
            manifest["package"].get("expected_sha256")) != (
        3764088, "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
        4542582, "275a9e691c0bad851f7adbc80ed2abc1580e13d67f031912e198f984d18f7f85",
    ):
        raise AuditError("production manifest pins changed")
    region_names = {item["name"] for item in main["regions"]}
    required = {name.removeprefix("replace_") + "_source_replacement"
                for name, *_ in PATCHES}
    required |= {
        "pb_service_conversate_retained_literal_pool",
        "pb_conversate_buffer_write_source_alignment",
        "pb_conversate_buffer_write_source_text",
        "pb_conversate_zero_source_alignment",
        "pb_conversate_zero_source_text",
        "pb_conversate_rx_source_text",
        "pb_conversate_notify_source_text",
        "pb_conversate_prep_list_source_text",
        "pb_conversate_prep_select_source_text",
        "pb_conversate_comm_resp_source_alignment",
        "pb_conversate_comm_resp_source_text",
        "pb_conversate_tag_tracking_source_alignment",
        "pb_conversate_tag_tracking_source_text",
    }
    if not required <= region_names:
        raise AuditError("production manifest regions changed")

    return {
        "surface": {
            "linked_functions": 6,
            "body_bytes": 1776,
            "owned_pool_bytes": 128,
            "physical_bytes": 1904,
            "direct_bl_entry_sites": 10,
            "direct_body_calls": 96,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 0,
        },
        "contracts": {
            "rx_status": {"success": 0, "decode_failure": 5,
                          "null": 6, "duplicate": 13},
            "duplicate_window_ms": 3000,
            "rx_hexdump_limit": 0x20,
            "tx_status": {"success": 0, "encode_failure": 5, "null": 6},
            "route": 1,
            "service": "0x0b",
            "message": "0x200f4808",
            "message_bytes": 0xFAC,
            "encode_buffer": "0x2037c2a0",
            "encode_capacity": 0x100,
            "last_magic": "0x20074ff8",
            "last_magic_tick": "0x2007485c",
            "envelopes": {
                "notify": {"command": 0xA1, "tag": 9, "send": "notify"},
                "prep_note_list": {"command": 2, "tag": 4, "send": "notify"},
                "prep_note_select": {"command": 4, "tag": 6, "send": "notify"},
                "command_response": {"command": 0xA2, "tag": 10, "send": "tx"},
                "tag_tracking": {"command": 0xA3, "tag": 12, "send": "notify",
                                 "payload_bytes": 12},
            },
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [row["function"] for row in rows],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 1776,
            "source_inventory_available": True,
            "source_functions": 8,
            "compiled_text_bytes": 1098,
            "alignment_bytes": 8,
            "strict_relocations": 33,
            "stock_replaced_bytes": 1776,
            "retained_literal_pool_bytes": 128,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 0x0B master/peer BLE and "
                "conversate UI evidence is available; the authorized right "
                "temple is nonresponsive and the left temple must remain stock."
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
    print("G2 pb_service_conversate audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
