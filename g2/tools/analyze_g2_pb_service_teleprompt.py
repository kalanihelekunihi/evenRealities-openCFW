#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_teleprompt object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-teleprompt-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-teleprompt-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-teleprompt-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_teleprompt.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "ada7f62b647ff85189ceecb5eb95b74e907f0f5af16e68432c0b292e6d651aaf",
    CLOSURE: "1f0b285bd9e488b17e7db011d83da521b269576bf351ac6adb7ecf145686af29",
    PROVENANCE: "ff746fdfc66df09c28cdd7e7d3ec44e6d137aa9e9f07e09c33fc37b9a9cae216",
}
SOURCE_SIZE = 13441
SOURCE_SHA256 = "d1f308195a7076fe41043f0cea8b70a6b1d9250dabb962f6b05285120c616c68"
FUNCTIONS = (
    ("open_cfw_pb_service_teleprompt_buffer_write", 146, 196136, 0),
    ("open_cfw_pb_service_teleprompt_zero", 88, 196284, 0),
    ("APP_PbRxTelepromptFrameDataProcess", 112, 196372, 3),
    ("APP_PbTelepromptTxEncodeCommResp", 126, 196484, 6),
    ("APP_PbTxEncodeStatusNotify", 136, 196612, 6),
    ("APP_PbTxEncodeFileListRequest", 136, 196748, 6),
    ("APP_PbTxEncodeFileSelect", 288, 196884, 6),
    ("APP_PbTxEncodePageDataRequest", 136, 197172, 6),
    ("APP_PbTxEncodeScrollSync", 180, 197308, 6),
)
PATCHES = (
    ("replace_pb_teleprompt_rx", 0x005885B4, 478,
     "0bf17663f645748d6d8d72170e9433bd53ffbefa8debc14a6329532849214801",
     "APP_PbRxTelepromptFrameDataProcess"),
    ("replace_pb_teleprompt_comm_resp", 0x00588792, 232,
     "bbe153af47c679b54331569dc7241569aaf432ef5e41da3f8fe2c1140853290b",
     "APP_PbTelepromptTxEncodeCommResp"),
    ("replace_pb_teleprompt_status", 0x0058887A, 238,
     "c654cb551c1337c0784660677301d03cec0a51c94aa2e082f2698d67bccd2d7b",
     "APP_PbTxEncodeStatusNotify"),
    ("replace_pb_teleprompt_file_list", 0x00588968, 238,
     "d70b9ef19d1b2311aaa0bdb3fd29e9ae2cf1d0448a6aefbdf309b81061f4b064",
     "APP_PbTxEncodeFileListRequest"),
    ("replace_pb_teleprompt_file_select", 0x00588A56, 234,
     "049487d10120cf04c650a6f4598b2f114ae6faf349927e3704268e0edbeb5f30",
     "APP_PbTxEncodeFileSelect"),
    ("replace_pb_teleprompt_page_data", 0x00588B40, 214,
     "b9783435cd0012319f79a28481a57eea9805ccd906f3a197273a0dac98934955",
     "APP_PbTxEncodePageDataRequest"),
    ("replace_pb_teleprompt_scroll_sync", 0x00588C16, 220,
     "2a3ca6d3744d38f048935f6442f6c298a28e4020fee6a8ecba984e1f671cbbcd",
     "APP_PbTxEncodeScrollSync"),
)
PHYSICAL = (0x005885B4, 0x00588D74)
PHYSICAL_SHA256 = "06e85d974b48111ab51fbfdff1cc23c56e1274f4971f1ca5407989440b75d0cc"
TAIL = (0x00588CF2, 0x00588D74)
TAIL_SHA256 = "9bd568fdf74affc604e3f493fa2fa3665bc5a08a87e1b828be1a8271364ef0c8"
BODY_SHA256 = "24f933ac204a24fdd8946526538df3b7e301314c079c8ea60a7b0c59813f8b3b"
ENTRY_SHA256 = "5e4c0ef3ef52542ca56e9096513b22e90ccae468c7581d55ac1fcd6f4f5a6ff4"
BODY_CALL_SHA256 = "282e521c4d6235324b225e5c55e988324055d5074328f2303b73b5667fa58a91"
FALSE_INTERIOR_SHA256 = "daf1c8e90e6bd4a796331e1a3db3e5cdb6bfa023aeb1368e33cb22e427eb784b"
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_teleprompt\pb_service_teleprompt.c"
)
TAIL_WORDS = (
    0x0076FA90, 0x00757E90, 0x006D9634, 0x00787F10,
    0x0074C6D4, 0x007824AC, 0x0077C304, 0x0078DF74,
    0x007824C0, 0x00757EB4, 0x20074FFE, 0x007178C0,
    0x006F514C, 0x20074870, 0x006F5198, 0x006E12C0,
    0x200F873C, 0x2037C9A0, 0x007824D4, 0x00757ED8,
    0x00757EFC, 0x007824E8, 0x0076FAAC, 0x0077A6CC,
    0x007637F0, 0x00763810, 0x0076FAC8, 0x0076FAE4,
    0x00763830, 0x00763850, 0x0076FB00, 0x0076FB1C,
)
STRINGS = {
    0x0076FA90: "pData or message is NULL",
    0x00757E90: "APP_PbRxTelepromptFrameDataProcess",
    0x006D9634: RETAINED_PATH,
    0x00787F10: "pb.teleprompt",
    0x0074C6D4: "[pb.teleprompt]pData or message is NULL",
    0x007824AC: "Teleprompt_pb_rx",
    0x0078DF74: "(none)",
    0x007824C0: "Decoding failed: %s",
    0x00757EB4: "[pb.teleprompt]Decoding failed: %s",
    0x007178C0: "command_id: %d, magic number = %d, last magic number = %d",
    0x006F514C: "[pb.teleprompt]command_id: %d, magic number = %d, last magic number = %d",
    0x006F5198: "Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore",
    0x006E12C0: "[pb.teleprompt]Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore",
    0x007824D4: "Encoding failed: %s",
    0x00757ED8: "APP_PbTelepromptTxEncodeCommResp",
    0x00757EFC: "[pb.teleprompt]Encoding failed: %s",
    0x007824E8: "Teleprompt_pb_resp",
    0x0076FAAC: "APP_PbTxEncodeStatusNotify",
    0x0077A6CC: "Teleprompt_pb_notify",
    0x007637F0: "APP_PbTxEncodeFileListRequest",
    0x00763810: "Teleprompt_pb_file_list_request",
    0x0076FAC8: "APP_PbTxEncodeFileSelect",
    0x0076FAE4: "Teleprompt_pb_file_select",
    0x00763830: "APP_PbTxEncodePageDataRequest",
    0x00763850: "Teleprompt_pb_page_data_request",
    0x0076FB00: "APP_PbTxEncodeScrollSync",
    0x0076FB1C: "Teleprompt_pb_scroll_sync",
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
    if len(rows) != 7 or sum(map(len, bodies)) != 1854:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")
    tail = image_slice(data, *TAIL)
    if len(tail) != 130 or sha256(tail) != TAIL_SHA256 or tail[:2] != b"\0\0":
        raise AuditError("alignment/literal tail changed")
    if struct.unpack("<32I", tail[2:]) != TAIL_WORDS:
        raise AuditError("literal pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("1fb5dff8"):
        raise AuditError("next-function boundary changed")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == 0x006D9634]
    if path_cells != [0x00588CFC]:
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    raw_interior: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            raw_interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    expected_entry = [
        (0x0055416A, 0x0058887A), (0x00555450, 0x00588C16),
        (0x00555870, 0x00588968), (0x005560B8, 0x00588A56),
        (0x0058A00A, 0x005885B4), (0x0058A05E, 0x00588792),
        (0x0058A0B4, 0x00588792), (0x0058A10C, 0x00588792),
        (0x0058A11A, 0x00588792), (0x0058A2A8, 0x0058887A),
        (0x0058ACC6, 0x00588B40),
    ]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    expected_false = [(0x0057FE74, 0x005885D8)]
    if raw_interior != expected_false or pair_digest(raw_interior) != FALSE_INTERIOR_SHA256:
        raise AuditError("raw interior candidate closure changed")
    if image_slice(data, 0x0057FE72, 0x0057FE76) != bytes.fromhex("00fb08f0"):
        raise AuditError("MUL overlap proof changed")
    if entry_bw or interior_bw:
        raise AuditError("direct B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 98 or pair_digest(calls) != BODY_CALL_SHA256:
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
                "components/apollo_main/core_overlay/pb_service_teleprompt.c"
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
        "pb_service_teleprompt_retained_literal_pool",
        "pb_teleprompt_buffer_write_source_text",
        "pb_teleprompt_zero_source_alignment",
        "pb_teleprompt_zero_source_text",
        "pb_teleprompt_rx_source_text",
        "pb_teleprompt_comm_resp_source_text",
        "pb_teleprompt_status_source_alignment",
        "pb_teleprompt_status_source_text",
        "pb_teleprompt_file_list_source_text",
        "pb_teleprompt_file_select_source_text",
        "pb_teleprompt_page_data_source_text",
        "pb_teleprompt_scroll_sync_source_text",
    }
    if not required <= region_names:
        raise AuditError("production manifest regions changed")

    return {
        "surface": {
            "linked_functions": 7,
            "body_bytes": 1854,
            "owned_tail_bytes": 130,
            "physical_bytes": 1984,
            "direct_bl_entry_sites": 11,
            "direct_body_calls": 98,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "false_halfword_bl_candidates": 1,
        },
        "contracts": {
            "rx_status": {"success": 0, "decode_failure": 5,
                          "null": 6, "duplicate": 13},
            "duplicate_window_ms": 3000,
            "rx_hexdump_limit": 0x20,
            "tx_status": {"success": 0, "encode_failure": 0x2B},
            "tx_pointer_null_guards": False,
            "route": 1,
            "service": 6,
            "message": "0x200f873c",
            "message_bytes": 0xF58,
            "encode_buffer": "0x2037c9a0",
            "encode_capacity": 0x100,
            "last_magic": "0x20074ffe",
            "last_magic_tick": "0x20074870",
            "envelopes": {
                "command_response": {"command": 0xA6, "tag": 12, "send": "tx",
                                     "payload_bytes": 1, "caller_magic": True},
                "status": {"command": 0xA1, "tag": 7, "send": "notify",
                           "payload_bytes": 2},
                "file_list": {"command": 0xA2, "tag": 8, "send": "notify",
                              "payload_bytes": 1},
                "file_select": {"command": 0xA3, "tag": 9, "send": "notify",
                                "payload_bytes": 0x42},
                "page_data": {"command": 0xA4, "tag": 10, "send": "notify",
                              "payload_bytes": 4},
                "scroll_sync": {"command": 0xA5, "tag": 11, "send": "notify",
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
            "ownership_bytes": 1854,
            "source_inventory_available": True,
            "source_functions": 9,
            "compiled_text_bytes": 1348,
            "alignment_bytes": 4,
            "strict_relocations": 39,
            "stock_replaced_bytes": 1854,
            "retained_literal_pool_bytes": 130,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 6 master/peer BLE and "
                "teleprompt UI evidence is available; the authorized right "
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
    print("G2 pb_service_teleprompt audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
