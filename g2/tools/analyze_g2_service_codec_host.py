#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 GX8002 codec-host object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-service-codec-host-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-service-codec-host-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-service-codec-host-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/service_codec_host.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINS = {
    FUNCTION_MAP: "3f4fd075d5b51648f952231f1cf0b503ce14a57d8434a51c0728660f7f5ea896",
    CLOSURE: "a433a3c352f57dd1cec155539a506e42aeebcbba7e6e1d3e0a68fff777de6203",
    PROVENANCE: "e613cbb862ed07649833216743b431401952399e41c6ad1466191faa1c239b39",
}
SOURCE_SHA256 = "770aec4fc610a89bf47a28d820e97adbfbe8028304075553a456dc683f949b32"
FUNCTIONS = (
    "open_cfw_codec_host_init", "open_cfw_codec_host_cleanup",
    "open_cfw_codec_host_magic_matches", "open_cfw_codec_host_pack_message",
    "open_cfw_codec_host_unpack_message", "open_cfw_codec_host_send_message",
    "open_cfw_codec_host_uart_read_blocking",
    "open_cfw_codec_host_read_uart_data",
    "open_cfw_codec_host_send_and_wait_response",
    "open_cfw_codec_host_free_message", "open_cfw_codec_read_version",
    "open_cfw_codec_switch_bf_mode", "open_cfw_codec_switch_wakeup_mode",
    "open_cfw_codec_query_mic_state", "open_cfw_codec_set_mic_gain",
    "open_cfw_codec_dmic_control", "open_cfw_codec_i2s_output_control",
    "open_cfw_codec_mic_delay_1bit", "open_cfw_svc_switch_bf_mode",
    "open_cfw_svc_switch_wakeup_mode", "open_cfw_svc_set_mic_gain",
    "open_cfw_svc_codec_dmic_open", "open_cfw_svc_codec_dmic_close",
    "open_cfw_svc_codec_mic_delay_1bit",
    "open_cfw_svc_i2s_output_control", "open_cfw_codec_get_voice_event",
)
SOURCE_OFFSETS = (
    240692, 240720, 240724, 240780, 241020, 241536, 241592, 241788,
    241836, 241980, 242040, 242312, 242564, 242816, 243076, 243348,
    243624, 243900, 244412, 244452, 244492, 244532, 244576, 244616,
    244656, 244696,
)
SOURCE_SIZES = (
    26, 4, 42, 240, 514, 54, 194, 46, 144, 60, 270, 252, 252,
    260, 270, 276, 268, 512, 40, 40, 40, 42, 40, 40, 40, 296,
)
PHYSICAL = (0x0057BA88, 0x0057DC40)
PHYSICAL_SHA256 = "83a042c43132baea06c3377689d7bc90b789fabc4bea39f25a4a4fe66cac261a"
BODY_SHA256 = "88264b60441f49660eba62171af67a9303c92985e90ab5539fda6b8b864a0b4f"
GAP_SHA256 = "9ed4d2b885b71bea352cf06d2a972bb79708bbb2e3d9d48db80e7a54a618bd34"
ENTRY_SHA256 = "f4f9f14be8990a0ed823332c2c4bdd83e0bae39e57ecf9b760558ab50bad79da"
BODY_CALL_SHA256 = "a688287e438040cc3e97f7a0cfece0dd532fa9d6efab5b105cb64d1033f5be78"
RAW_WINDOW_SHA256 = "e9e2cae8fa1676671499e3039087288c7af4938e4e805247e7cb1d0c686d9b13"
RETAINED_PATH_ADDRESS = 0x006FCCD4
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_codec_host.c"
PATH_CELLS = (0x0057C618, 0x0057D00C, 0x0057DA28, 0x0057DC2C)
EXACT_SYMBOLS = (
    (0x00783000, "gx8002_host_init"),
    (0x00783014, "gx8002_pack_message"),
    (0x0077B5FC, "gx8002_unpack_message"),
    (0x0078303C, "gx8002_send_message"),
    (0x00771054, "gx8002_uart_read_blocking"),
    (0x0077B62C, "gx8002_read_uart_data"),
    (0x00764C50, "gx8002_send_and_wait_response"),
    (0x00783064, "GX8002_ReadVersion"),
    (0x00783078, "GX8002_SwitchBFMode"),
    (0x0077B674, "GX8002_SwitchWakeupMode"),
    (0x0077B68C, "GX8002_QueryMicState"),
    (0x0078308C, "GX8002_SetMicGain"),
    (0x00788890, "GX8002_DMICCtrl"),
    (0x0077B6A4, "GX8002_I2SOutputCtrl"),
    (0x007830A0, "GX8002_MicDelay1Bit"),
    (0x007830B4, "SVC_SwitchBFMode"),
    (0x0077B6D4, "SVC_SwitchWakeupMode"),
    (0x007888B0, "SVC_SetMicGain"),
    (0x007830C8, "SVC_CodecDMICOpen"),
    (0x007830F0, "SVC_CodecDMICClose"),
    (0x0077B6EC, "SVC_CodecMicDelay1Bit"),
    (0x00783118, "SVC_I2SOutputCtrl"),
    (0x0077B704, "GX8002_GetVoiceEvent"),
)
GAPS = (
    (0x0057C610, 0x0057C640, "5195c8c452f4bbbe2e35e1524aecd842fdb80ba2af3b8d0d3064cc9d22ccc50d"),
    (0x0057C7BC, 0x0057C830, "02b5c2a1c63cbe685ba7c3d814c15b94fa96ec70f4e0693d37a0297fa0b78e5b"),
    (0x0057C93E, 0x0057C9B8, "28cdc6071b84cec85371bdce613939625088a23f6bdc3fd6a7c7cfdf3b5cb879"),
    (0x0057CAC6, 0x0057CB60, "950dedf61edfe5298bc592b35dcb0bb1fe0659c609df8e9de2cb3fda1bd6752d"),
    (0x0057CC7A, 0x0057CCEC, "b9d9e2f55246be10af45abf8d44ae2a1177d9d8977aa553a9432dcd793148e99"),
    (0x0057CE54, 0x0057CE78, "f52cea3d27de1caf0322aa3ab83423ec042e2bed17a96088e76c2cbf4ee369f5"),
    (0x0057CFA6, 0x0057D024, "94d50453cfd6f5f10d72508c320e30c8a687706a0471d31c341ee983bd191f92"),
    (0x0057D146, 0x0057D1CC, "a7cf0b167f08b311122cccc73c9d8c6034be694264339fb92fcb2d8c508c23dc"),
    (0x0057D3B0, 0x0057D418, "b217d22e28f576b4b761b319e95c586b4d2ac72b003322a40d39f2d5f615196b"),
    (0x0057D4E0, 0x0057D4E4, "cfe009f7d078748f99f1ecfede8955ccfc95bfb3dfbe7940cb977a1cd4a1d4b4"),
    (0x0057D5AC, 0x0057D5C0, "7dee72ad74d843f9e82723cfc26cb61cfae11550137ab189a3ac2252770d585a"),
    (0x0057D6A2, 0x0057D6B4, "cab8b989f8eb2b97ee5b8ec85a3c13adb33bfda68fca6c87770c1d0d2948f6ff"),
    (0x0057D784, 0x0057D794, "ccddc76c3d97daa1c26d5d9d63f473e6597f1d16da6b25fff0536329b956021c"),
    (0x0057D860, 0x0057D870, "42d19236cef7343b12385eff23ba62a86f221265e186ac037515d553dc793a47"),
    (0x0057D92A, 0x0057D93C, "351783d05ba24de1fb38f52fbfc448d960448293bcd60a423170bc8b14d71923"),
    (0x0057DA1C, 0x0057DA40, "3e50af328a6b771b5ec8406a75752b9846adf42595abbc978dcddcbf5c9f8dc3"),
    (0x0057DB58, 0x0057DC40, "464b11a65be8a4d108967828cf967dfa9daa3ed5a9608f3ddd15af53b15b21e0"),
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    return data[start - BASE:end - BASE]


def pair_digest(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("ascii")


def thumb_bw_target(data: bytes, address: int) -> int | None:
    first, second = struct.unpack_from("<HH", data, address - BASE)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1, j2 = (second >> 13) & 1, (second >> 11) & 1
    i1, i2 = (~(j1 ^ sign)) & 1, (~(j2 ^ sign)) & 1
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
        start, end = int(row["entry"], 0), int(row["end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["size"]) or sha256(raw) != row["sha256"]:
            raise AuditError(f"body changed: {row['name']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 26 or sum(map(len, bodies)) != 7_318:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps: list[bytes] = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 1_314 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(image_slice(data, PHYSICAL[0] - 24, PHYSICAL[0])) != "cffbdc88c017628813447bde3b13807ec05a88c6aeda4c8ef3dae8acb37dda1f":
        raise AuditError("previous-object boundary changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 8) != bytes.fromhex("00b551ec100b53ec"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained codec symbol changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != list(PATH_CELLS):
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entries: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    bw_hits: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts or target in interiors:
            bw_hits.append((site, target))
    if len(entries) != 83 or pair_digest(entries) != ENTRY_SHA256 or interior:
        raise AuditError("direct BL entry/interior closure changed")
    if bw_hits:
        raise AuditError("B.W entry/interior ingress appeared")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 379 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    raw_windows: list[tuple[int, int]] = []
    aligned_entry_pointers: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        target = (value & ~1) if value & 1 else value
        if target in starts or target in interiors:
            raw_windows.append((BASE + offset, value))
            if offset % 4 == 0 and target in starts:
                aligned_entry_pointers.append((BASE + offset, value))
    if raw_windows != [(0x006309BC, 0x0057C001)]:
        raise AuditError("raw entry/interior byte-window closure changed")
    if pair_digest(raw_windows) != RAW_WINDOW_SHA256 or aligned_entry_pointers:
        raise AuditError("stored entry-pointer closure changed")

    if image_slice(data, 0x0078F3B8, 0x0078F3C0) != b"BUXXBUXX":
        raise AuditError("GX8002 magic changed")
    if image_slice(data, 0x007888A0, 0x007888AE) != bytes.fromhex("425558580e0101000000d4db2f68"):
        raise AuditError("manual delay message changed")
    literal_contract = {
        0x0057C634: 0x0078F3BC,
        0x0057C638: 0x20075013,
        0x0057CB30: 0x2007399C,
        0x0057CE6C: 0x2007397C,
        0x0057DB70: 0x007888A0,
        0x0057DB7C: 0x2007397C,
    }
    if any(struct.unpack_from("<I", data, site - BASE)[0] != value
           for site, value in literal_contract.items()):
        raise AuditError("GX8002 state/message literal changed")

    source = SOURCE.read_bytes()
    if len(source) != 29_300 or sha256(source) != SOURCE_SHA256:
        raise AuditError("codec-host production source changed")
    source_text = source.decode("utf-8")
    required_source_tokens = (
        "OPEN_CFW_CODEC_HEADER_BYTES = 14",
        "OPEN_CFW_CODEC_BODY_MAX = 16",
        "OPEN_CFW_CODEC_RETRIES = 3",
        "OPEN_CFW_CODEC_UART_SET_BAUD(115200u)",
        "open_cfw_codec_host_pack_message",
        "open_cfw_codec_host_unpack_message",
        "open_cfw_codec_get_voice_event",
        "body_length < 3u",
    )
    if any(token not in source_text for token in required_source_tokens):
        raise AuditError("codec-host source contract changed")

    overlay = json.loads(OVERLAY.read_text())
    leaves = [item for item in overlay["relocated_leaves"]
              if item.get("source", {}).get("path") ==
              "components/apollo_main/core_overlay/service_codec_host.c"]
    if tuple(item["function"] for item in leaves) != FUNCTIONS:
        raise AuditError("codec-host source leaf order changed")
    if tuple(item["expected"]["offset"] for item in leaves) != SOURCE_OFFSETS:
        raise AuditError("codec-host source placement changed")
    if tuple(item["expected"]["size"] for item in leaves) != SOURCE_SIZES:
        raise AuditError("codec-host compiled text sizes changed")
    if sum(len(item["relocations"]) for item in leaves) != 111:
        raise AuditError("codec-host relocation closure changed")
    if any(item.get("source", {}).get("sha256") != SOURCE_SHA256
           or item.get("strict_relocation_contract") is not True
           for item in leaves):
        raise AuditError("codec-host source/relocation authentication changed")
    patches = [item for item in overlay["patch_sites"]
               if item.get("name", "").startswith("replace_service_codec_host_")]
    for index, (patch, row, function) in enumerate(zip(patches, rows, FUNCTIONS), 1):
        if (
            patch.get("name") != f"replace_service_codec_host_{index:02d}"
            or patch.get("runtime_address") != int(row["entry"], 0)
            or patch.get("expected_size") != int(row["size"])
            or patch.get("expected_sha256") != row["sha256"]
            or patch.get("target_function") != function
            or patch.get("branch") != "b_w"
        ):
            raise AuditError(f"codec-host guarded redirect {index:02d} changed")
    expected = overlay["expected"]
    build = json.loads(BUILD_REPORT.read_text())
    if (build["overlay"]["size"], build["overlay"]["sha256"],
            build["component"]["size"], build["component"]["sha256"]) != (
            expected["overlay_size"], expected["overlay_sha256"],
            expected["component_size"], expected["component_sha256"]):
        raise AuditError("codec-host build/overlay accounting diverged")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    if (main["provider"]["size"], main["provider"]["sha256"]) != (
            build["component"]["size"], build["component"]["sha256"]):
        raise AuditError("codec-host manifest/component accounting diverged")
    regions = main["regions"]
    body_regions = [item for item in regions
                    if item["name"].startswith("service_codec_host_")
                    and item["name"].endswith("_source_replacement")]
    gap_regions = [item for item in regions
                   if item["name"].startswith("service_codec_host_official_gap_")]
    text_regions = [item for item in regions
                    if item["name"].startswith("service_codec_host_")
                    and item["name"].endswith("_source_text")]
    align_regions = [item for item in regions
                     if item["name"].startswith("service_codec_host_")
                     and item["name"].endswith("_overlay_alignment")]
    if (len(body_regions), sum(item["size"] for item in body_regions),
            len(gap_regions), sum(item["size"] for item in gap_regions),
            len(text_regions), sum(item["size"] for item in text_regions),
            len(align_regions), sum(item["size"] for item in align_regions)) != (
            26, 7_318, 17, 1_314, 26, 4_262, 10, 38):
        raise AuditError("codec-host manifest ownership changed")
    package = PACKAGE.read_bytes()
    if (len(package), sha256(package)) != (
            manifest["package"]["expected_size"],
            manifest["package"]["expected_sha256"]):
        raise AuditError("codec-host package artifact changed")
    flash_plan = json.loads(FLASH_PLAN.read_text())
    if (not flash_plan.get("flash_regions")
            or flash_plan.get("unresolved_flash_regions") != []
            or flash_plan.get("package_sha256") !=
            manifest["package"]["expected_sha256"]):
        raise AuditError("codec-host flash-plan closure changed")

    external_entries = [pair for pair in entries
                        if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    return {
        "surface": {
            "retained_path_anchors": 13,
            "restored_pathless_functions": 13,
            "linked_functions": 26,
            "body_bytes": 7_318,
            "owned_gap_pool_bytes": 1_314,
            "physical_bytes": 8_632,
            "direct_bl_entry_sites": 83,
            "external_direct_bl_entry_sites": len(external_entries),
            "direct_body_calls": 379,
            "b_w_entry_or_interior_targets": 0,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 1,
        },
        "contracts": {
            "magic": "BUXX",
            "uart_baud": 115_200,
            "wire_header_bytes": 14,
            "wire_header": [
                "magic_u32", "command_u16", "sequence_u8", "flags_u8",
                "body_length_u16", "header_crc32_u32",
            ],
            "header_crc_input_bytes": 10,
            "body_max_bytes": 16,
            "optional_body_crc_bytes": 4,
            "sequence_address": "0x20075013",
            "outbound_staging": "0x2007399c",
            "inbound_staging": "0x2007397c",
            "known_commands": {
                0x02: "read_version",
                0x07: "switch_beamforming_mode",
                0x08: "switch_wakeup_mode",
                0x0B: "set_microphone_gain",
                0x0C: "open_digital_microphone",
                0x0D: "close_digital_microphone",
                0x0E: "microphone_delay_1bit",
                0x0F: "i2s_output_control",
                0x70: "query_microphone_state",
            },
            "command_retry_limit": 3,
            "blocking_read_yield_ticks": 1,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": [name for _, name in EXACT_SYMBOLS],
            "source_inventory": "26-function clean-room production C",
            "historical_source_inventory": "unavailable",
            "license": "MIT",
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "source_inventory_available": True,
            "production_routed": True,
            "ownership_bytes": 7_318,
            "compiled_text_bytes": 4_262,
            "generated_alignment_bytes": 38,
            "strict_relocations": 111,
            "guarded_redirects": 26,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": (
                "hardware validation is blocked by unavailable physical evidence; future qualification requires "
                "an authorized G2 pair and either a component-specific codec/UART host fixture or an "
                "authenticated golden codec/UART host capture"
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 codec-host audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 codec-host audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
