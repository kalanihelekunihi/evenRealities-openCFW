#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_terminal object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-terminal-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-terminal-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-terminal-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_terminal.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "05b6c64c568eff4ee5c25b9a0344cc948f8ed72a6ed524b9d858642bbbe959e4",
    CLOSURE: "efcb8e562d1aed8083d8ebbbfd91d8cfa1cfc58a87d4f642890ad3f154522830",
    PROVENANCE: "71e10f399312df13bbc70a383f5d69adcc6bf02bcf482129178b01ae1e4aa95b",
}
SOURCE_SIZE = 14861
SOURCE_SHA256 = "b6feacf5bb491f28e1a3718dbf29ee2c5f5038e94ee9eabfb1f584eb5a2cb123"
FUNCTIONS = (
    ("open_cfw_pb_service_terminal_buffer_write", 146, 200356, 0),
    ("open_cfw_pb_service_terminal_zero", 88, 200504, 0),
    ("open_cfw_pb_terminal_encode_and_send", 358, 200592, 7),
    ("APP_PbTerminalRxFrameDataProcess", 112, 200952, 3),
    ("APP_PbTerminalTxEncodeCommResp", 36, 201064, 1),
    ("APP_PbTerminalTxEncodeStatusReply", 48, 201100, 1),
    ("APP_PbTerminalTxEncodeVoiceInput", 48, 201148, 1),
    ("APP_PbTerminalTxEncodeQueryReply", 48, 201196, 1),
    ("APP_PbTerminalTxEncodeAgentInterrupt", 48, 201244, 1),
    ("APP_PbTerminalTxEncodeSessionSwitchRequest", 84, 201292, 1),
    ("APP_PbTerminalTxEncodeNewSessionRequest", 62, 201376, 1),
    ("APP_PbTerminalTxEncodeNewSessionCancel", 48, 201440, 1),
    ("APP_PbTerminalTxEncodeDisplayStateNotify", 104, 201488, 2),
    ("APP_PbTerminalTxEncodeListFocus", 62, 201592, 1),
    ("APP_PbTerminalTxEncodeOverlayFocus", 76, 201656, 2),
)
PATCH_SUFFIXES = (
    "encode", "rx", "comm_resp", "status_reply", "voice_input",
    "query_reply", "agent_interrupt", "session_switch", "new_session",
    "new_session_cancel", "display_state", "list_focus", "overlay_focus",
)
PHYSICAL = (0x005CE7C4, 0x005CF2B4)
PHYSICAL_SHA256 = "8163d6203ef880d6eb46be6f0f9bab099b8b830cddb248c7f1bc512aa0cb1c4e"
TAIL = (0x005CF1BE, 0x005CF2B4)
TAIL_SHA256 = "7d09b766d6efb89199b2c33d609f3a7a35adc963da8fd3d3914792242eb41d02"
BODY_SHA256 = "954b591a128ed3b02804f7f832bc9f59ba992c6450fa5f3badb03db4df4ae620"
ENTRY_SHA256 = "bf6a62b1ff5a842af15a247ef1cb3669772c6cf929b25aa271ae47bc5b444c55"
BODY_CALL_SHA256 = "e142154181b5431781bbf37b7ba7e65b2f5baadb54456df88dbd88cfc44381a0"
RAW_WINDOW_SHA256 = "407d3efbe23644a2db29198f8c29dacba8e7bb821359e2fa92357ba14440b8f3"
RETAINED_PATH_ADDRESS = 0x006DB484
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_terminal\pb_service_terminal.c"
)
TAIL_WORDS = (
    0x200F9694, 0x20374378, 0x0077C634, 0x00763870,
    0x0076FB38, 0x006DB484, 0x0078B7C8, 0x00741704,
    0x0078DF7C, 0x0076FB54, 0x0074C6FC, 0x00763890,
    0x00757F20, 0x00741730, 0x0076FB70, 0x0074C724,
    0x20074874, 0x20074FFF, 0x00736A34, 0x0070DBE4,
    0x0076FB8C, 0x007638B0, 0x0074C74C, 0x0074175C,
    0x007215C0, 0x007638D0, 0x00757F44, 0x00741788,
    0x007178FC, 0x006F51E4, 0x007638F0, 0x00757F68,
    0x007417B4, 0x0074C774, 0x0072BDC4, 0x00763910,
    0x00757F8C, 0x007417E0, 0x00717938, 0x006FBE34,
    0x00757FB0, 0x0074C79C, 0x00736A64, 0x0070DC24,
    0x0074180C, 0x006F5230, 0x00736A94, 0x0074C7C4,
    0x0070DC64, 0x0074C814, 0x0074C7EC, 0x0072BDF8,
    0x006FBE7C, 0x00741838, 0x006E4748, 0x00736AC4,
    0x00763930, 0x0070DCA4, 0x0070DCE4, 0x00757FD4,
    0x006F527C,
)
SYMBOLS = {
    0x0076FB38: "terminal_encode_and_send",
    0x00757F20: "APP_PbTerminalRxFrameDataProcess",
    0x007638B0: "APP_PbTerminalTxEncodeCommResp",
    0x00757F44: "APP_PbTerminalTxEncodeStatusReply",
    0x00757F68: "APP_PbTerminalTxEncodeVoiceInput",
    0x00757F8C: "APP_PbTerminalTxEncodeQueryReply",
    0x0074C79C: "APP_PbTerminalTxEncodeAgentInterrupt",
    0x0074180C: "APP_PbTerminalTxEncodeSessionSwitchRequest",
    0x0074C7C4: "APP_PbTerminalTxEncodeNewSessionRequest",
    0x0074C7EC: "APP_PbTerminalTxEncodeNewSessionCancel",
    0x00741838: "APP_PbTerminalTxEncodeDisplayStateNotify",
    0x00763930: "APP_PbTerminalTxEncodeListFocus",
    0x00757FD4: "APP_PbTerminalTxEncodeOverlayFocus",
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
    if len(rows) != 13 or sum(map(len, bodies)) != 2554:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    tail = image_slice(data, *TAIL)
    if len(tail) != 246 or sha256(tail) != TAIL_SHA256 or tail[:2] != b"\0\0":
        raise AuditError("alignment/literal tail changed")
    if struct.unpack("<61I", tail[2:]) != TAIL_WORDS:
        raise AuditError("literal pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("70b50400"):
        raise AuditError("next-function boundary changed")
    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    for address, expected in SYMBOLS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained symbol changed at 0x{address:08x}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != [0x005CF1D4]:
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
        (0x005CEB9A, 0x005CE7C4), (0x005CEC6A, 0x005CE7C4),
        (0x005CED30, 0x005CE7C4), (0x005CEE00, 0x005CE7C4),
        (0x005CEE84, 0x005CE7C4), (0x005CEF0C, 0x005CE7C4),
        (0x005CEF84, 0x005CE7C4), (0x005CEFF2, 0x005CE7C4),
        (0x005CF0B2, 0x005CE7C4), (0x005CF12C, 0x005CE7C4),
        (0x005CF1B6, 0x005CE7C4), (0x005E4320, 0x005CEBA2),
        (0x005E44A4, 0x005CE990), (0x005E44B4, 0x005CEAEC),
        (0x005E44C6, 0x005CEAEC), (0x005E44E8, 0x005CEAEC),
        (0x005E548A, 0x005CEFFA), (0x005E5492, 0x005CF0BA),
        (0x005E549C, 0x005CF134), (0x005E593C, 0x005CEC72),
        (0x005E59B2, 0x005CEC72), (0x005E5BFC, 0x005CEC72),
        (0x005E5CF0, 0x005CEC72), (0x005E5E20, 0x005CEC72),
        (0x005E6860, 0x005CEE8C), (0x005E6A12, 0x005CED38),
        (0x005E70BC, 0x005CEE08), (0x005E8078, 0x005CEC72),
        (0x005E8954, 0x005CEBA2), (0x005E8BFA, 0x005CEBA2),
        (0x005ED23A, 0x005CEF8C), (0x005ED5E8, 0x005CEE8C),
        (0x005ED67E, 0x005CEF14),
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
    if len(calls) != 130 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if len(stored) != 15 or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sha256(source) != SOURCE_SHA256:
        raise AuditError("production source changed")
    overlay = json.loads(OVERLAY.read_text())
    names = {item[0] for item in FUNCTIONS}
    leaves = {item.get("function"): item for item in overlay["relocated_leaves"]
              if item.get("function") in names}
    if set(leaves) != names:
        raise AuditError("production leaf inventory changed")
    for name, size, offset, relocation_count in FUNCTIONS:
        leaf = leaves[name]
        if (leaf["source"].get("path") !=
                "components/apollo_main/core_overlay/pb_service_terminal.c"
                or leaf["source"].get("size") != SOURCE_SIZE
                or leaf["source"].get("sha256") != SOURCE_SHA256
                or leaf.get("profiles") != ["apple-clang"]
                or leaf.get("strict_relocation_contract") is not True
                or (leaf["expected"].get("size"),
                    leaf["expected"].get("offset"),
                    leaf["expected"].get("alignment")) != (size, offset, 4)
                or len(leaf.get("relocations", [])) != relocation_count):
            raise AuditError(f"production leaf changed: {name}")
    patch_by_name = {item.get("name"): item for item in overlay["patch_sites"]}
    for suffix, row in zip(PATCH_SUFFIXES, rows):
        patch = patch_by_name.get(f"replace_pb_terminal_{suffix}")
        target = ("open_cfw_pb_terminal_encode_and_send" if suffix == "encode"
                  else row["function"])
        expected = (
            int(row["stock_start"], 0), int(row["stock_bytes"]),
            row["stock_sha256"], "b_w", target, ["apple-clang"],
        )
        if patch is None or (
            patch.get("runtime_address"), patch.get("expected_size"),
            patch.get("expected_sha256"), patch.get("branch"),
            patch.get("target_function"), patch.get("profiles"),
        ) != expected:
            raise AuditError(f"production patch changed: {row['function']}")
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
    region_by_name = {item["name"]: item for item in main["regions"]}
    for suffix, row in zip(PATCH_SUFFIXES, rows):
        region = region_by_name.get(f"pb_terminal_{suffix}_entry_replacement")
        if region is None or (
            region.get("target_address"), region.get("size"),
            region.get("address_status"),
        ) != (int(row["stock_start"], 0), int(row["stock_bytes"]),
              "generated_source_entry_replacement"):
            raise AuditError(f"production manifest replacement changed: {row['function']}")
    for name, size, offset, _ in FUNCTIONS:
        leaf = leaves[name]
        selector = next(
            flag for flag in leaf["toolchain"]["flags"]
            if flag.startswith("-DOPEN_CFW_PB_TERMINAL_")
        ).removeprefix("-DOPEN_CFW_PB_TERMINAL_").removesuffix("_ONLY=1").lower()
        region = region_by_name.get(f"pb_terminal_{selector}_source_text")
        if region is None or (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (3523396 + offset, size, 0x00794324 + offset,
              "source_compiled"):
            raise AuditError(f"production manifest source changed: {name}")
    retained = region_by_name.get("pb_terminal_retained_literal_tail")
    alignment = [item for item in main["regions"]
                 if item["name"].startswith("pb_terminal_")
                 and item["name"].endswith("_source_alignment")]
    if retained is None or retained.get("size") != 246 or (
            retained.get("address_status") != "official_blob") or (
            sum(item["size"] for item in alignment) != 8):
        raise AuditError("production manifest retained/alignment accounting changed")

    return {
        "surface": {
            "linked_functions": 13,
            "body_bytes": 2554,
            "owned_tail_bytes": 246,
            "physical_bytes": 2800,
            "direct_bl_entry_sites": 33,
            "direct_body_calls": 130,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 15,
        },
        "contracts": {
            "rx_status": {"success": 0, "decode_failure": 5,
                          "null": 6, "duplicate": 13},
            "duplicate_window_ms": 3000,
            "tx_status": {"success": 0, "encode_failure": 5,
                          "unsupported_tag": 8, "null": 6},
            "route": 1,
            "service": 0x30,
            "message": "0x200f9694",
            "message_bytes": 0x850,
            "encode_buffer": "0x20374378",
            "encode_capacity": 0x878,
            "last_magic": "0x20074fff",
            "last_magic_tick": "0x20074874",
            "command_tags": [
                {"name": "status_reply", "command": 0xA1, "tag": 9, "payload_bytes": 2},
                {"name": "voice_input", "command": 0xA2, "tag": 10, "payload_bytes": 1},
                {"name": "query_reply", "command": 0xA3, "tag": 11, "payload_bytes": 8},
                {"name": "agent_interrupt", "command": 0xA4, "tag": 12, "payload_bytes": 1},
                {"name": "session_switch", "command": 0xA5, "tag": 18, "payload_bytes": 8},
                {"name": "new_session", "command": 0xA6, "tag": 19, "payload_bytes": 4},
                {"name": "display_state", "command": 0xA7, "tag": 20, "payload_bytes": 12},
                {"name": "new_session_cancel", "command": 0xA8, "tag": 22, "payload_bytes": 1},
                {"name": "list_focus", "command": 0xA9, "tag": 24, "payload_bytes": 4},
                {"name": "overlay_focus", "command": 0xAA, "tag": 25, "payload_bytes": 8},
            ],
            "command_response": {"command": 0xF0, "tag": 13,
                                 "payload_bytes": 1, "send": "tx"},
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [row["function"] for row in rows],
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 2554,
            "source_inventory_available": True,
            "source_functions": 15,
            "compiled_text_bytes": 1368,
            "alignment_bytes": 8,
            "strict_relocations": 23,
            "stock_replaced_bytes": 2554,
            "retained_tail_bytes": 246,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized live G2 service 0x30 master/peer BLE and terminal "
                "UI evidence is available; the authorized right temple is "
                "nonresponsive and the left temple must remain stock."
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
    print("G2 pb_service_terminal audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
