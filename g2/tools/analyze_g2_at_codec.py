#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 eAT audio-control module."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-at-codec-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-at-codec-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-at-codec-provenance.tsv"
PINS = {
    FUNCTION_MAP: "e48d4af2f24e7ef84ffc48209bb8b4db05d272ab04a3a841cc108ece4550119b",
    CLOSURE: "8f394e22c5762bb6bad0ddb13d980ddbda369e403ea2da20ad37c5d44aaaf480",
    PROVENANCE: "3f88a730cada8f282c27b68a1f3f46fd9d754068a01af52f1b699832a9e4a570",
}
BODY = (0x005A5488, 0x005A54FE)
BODY_SHA256 = "628aa45af330f4c03626207810d875e9810f93929d14de2f83df360a26ec701a"
POOL = (0x005A54FE, 0x005A5520)
POOL_SHA256 = "4f10eb7e21c7a624181dd3495b5622e5fb7ca67624108870925107e20a7e84f3"
PHYSICAL = (BODY[0], POOL[1])
PHYSICAL_SHA256 = "73f108e6a639ee2be60360f24c80f3547aa9980e836c289da0464a6322c08b1b"
BODY_CALL_SHA256 = "c4b2c910a1658b5e25789eb0837ac34875a63c66d2f605ac13f49148149109cc"
STORED_POINTER_SHA256 = "56582a994b92d57ed46a37b83a97ea1e90d69a390f80985554b20ccdeb87bd79"
COMMAND_RECORD = (0x006C9290, 0x006C92A0)
COMMAND_RECORD_SHA256 = "cb9368ca3c22c87b64b3a0c7df3ff9e01f1cd5d94c18bd1f331db65757776713"
COMMAND_RECORD_WORDS = (0, 0x0078A34C, 0x005A5489, 0)
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\at_codec.c"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/at_codec.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
AUDIO_CALLS = {
    0x005A54D8: 0x0054F380,
    0x005A54EE: 0x0054F50E,
}
WORDS = {
    0x005A5500: 0x00000031,
    0x005A5504: 0x00000030,
    0x005A5508: 0x00785130,
    0x005A550C: 0x00785120,
    0x005A5510: 0x00700810,
    0x005A5514: 0x0078A340,
    0x005A5518: 0x007755B4,
    0x005A551C: 0x00785140,
}
STRINGS = {
    0x0078A34C: "AT^AUDIO",
    0x00785130: "set audio %s",
    0x00785120: "_atAudioCtrl",
    0x00700810: RETAINED_PATH,
    0x0078A340: "at.codec",
    0x007755B4: "[at.codec]set audio %s",
    0x00785140: "AUD_AUDIO+OK\r\n",
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
    if len(rows) != 1:
        raise AuditError("function inventory changed")
    row = rows[0]
    start = int(row["stock_start"], 0)
    end = int(row["stock_end_exclusive"], 0)
    body = image_slice(data, start, end)
    if (start, end) != BODY or len(body) != int(row["stock_bytes"]):
        raise AuditError("function boundary changed")
    if sha256(body) != row["stock_sha256"] or sha256(body) != BODY_SHA256:
        raise AuditError("handler body changed")
    if sha256(image_slice(data, *POOL)) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    command_record = image_slice(data, *COMMAND_RECORD)
    if sha256(command_record) != COMMAND_RECORD_SHA256:
        raise AuditError("AT command record changed")
    if struct.unpack("<IIII", command_record) != COMMAND_RECORD_WORDS:
        raise AuditError("AT command record layout changed")
    for address, expected in WORDS.items():
        actual = struct.unpack("<I", image_slice(data, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    starts = {BODY[0]}
    interiors = set(range(BODY[0] + 2, BODY[1], 2))
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
    if entry or interior or entry_bw or interior_bw:
        raise AuditError("unexpected direct entry/interior ingress")

    calls: list[tuple[int, int]] = []
    for site in range(BODY[0], BODY[1] - 3, 2):
        target = decoder._thumb_bl_target(data, site)
        if target is not None:
            calls.append((site, target))
    if len(calls) != 10 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")
    call_map = dict(calls)
    if any(call_map.get(site) != target for site, target in AUDIO_CALLS.items()):
        raise AuditError("audio-provider dispatch changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    expected_pointer = [(0x006C9298, 0x005A5489)]
    if raw_addresses != expected_pointer or pair_digest(raw_addresses) != STORED_POINTER_SHA256:
        raise AuditError("stored handler-pointer closure changed")

    source = PRODUCTION_SOURCE.read_bytes()
    if (len(source), sha256(source)) != (
        1186, "b276eedcad875fecd41e64f9bc60005c17aea09c234dd706b1c32ce7bf108431"
    ):
        raise AuditError("production AT^AUDIO source changed")
    text = source.decode("utf-8")
    for token in ("parameter[0] == '1'", "parameter[0] == '0'",
                  "OPEN_CFW_AT_CODEC_ACQUIRE(7u)",
                  "OPEN_CFW_AT_CODEC_RELEASE(7u)",
                  "OPEN_CFW_AT_CODEC_OUTPUT(OPEN_CFW_AT_CODEC_OK)"):
        if token not in text:
            raise AuditError("production AT^AUDIO source policy changed")
    overlay = json.loads(OVERLAY.read_text())
    leaf = next(item for item in overlay["relocated_leaves"]
                if item.get("source", {}).get("path") ==
                "components/apollo_main/core_overlay/at_codec.c")
    if (
        leaf.get("function") != "open_cfw_at_codec_audio_control"
        or leaf.get("expected") != {
            "alignment": 4, "offset": 299880,
            "sha256": "45b3f6cbfbf226e46c6fda376d2eed84da7a2f7a0ee6fc3dfe70e8f0b2319125",
            "size": 44,
            "unrelocated_sha256": "3397c32638e65c1d14f3bf8aaf813436eefedfb74ebce6710f284871bedb8ec8",
        }
        or [(item["offset"], item["symbol"], item["target_address"])
            for item in leaf.get("relocations", [])] != [
                (16, "open_cfw_audio_app_acquire", 0x0054F380),
                (24, "open_cfw_audio_app_release", 0x0054F50E),
                (36, "open_cfw_at_codec_output", 0x005415F0),
            ]
    ):
        raise AuditError("production AT^AUDIO leaf changed")
    patch = next(item for item in overlay["patch_sites"]
                 if item.get("target_function") ==
                 "open_cfw_at_codec_audio_control")
    if (
        patch.get("runtime_address"), patch.get("expected_size"),
        patch.get("expected_sha256"), patch.get("target_function"),
        patch.get("branch"), patch.get("profiles"),
    ) != (
        BODY[0], 118, BODY_SHA256, "open_cfw_at_codec_audio_control",
        "b_w", ["apple-clang"],
    ):
        raise AuditError("production AT^AUDIO redirect changed")
    build = json.loads(BUILD_REPORT.read_text())
    if (
        build["overlay"]["size"], build["overlay"]["sha256"],
        build["component"]["size"], build["component"]["sha256"],
    ) != (
        332148, "588a29c8d680068b6f27dd2cff831dcfd5aa71a91e4f9f97537d9bcb4a0d145d",
        3855544, "df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc",
    ):
        raise AuditError("production AT^AUDIO build pins changed")
    built = next(item for item in build["relocated_leaves"]
                 if item.get("source", {}).get("path") ==
                 "components/apollo_main/core_overlay/at_codec.c")
    if (
        built["extraction"]["function"], built["extraction"]["size"],
        built["extraction"]["relocation_count"],
        built["placement"]["padding_before"],
    ) != ("open_cfw_at_codec_audio_control", 44, 3, 0):
        raise AuditError("production AT^AUDIO compiled closure changed")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    if (
        main["provider"]["size"], main["provider"]["sha256"],
        manifest["package"]["expected_size"],
        manifest["package"]["expected_sha256"],
    ) != (
        3855544, "df6d3b4d5aeffa8e7341937d0d72e3425a6dacfc8fa964cf2b2cda9995079bdc",
        4634038, "3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731",
    ):
        raise AuditError("production AT^AUDIO manifest/package pins changed")
    regions = [item for item in main["regions"]
               if item["name"].startswith("at_codec_")]
    if ([item["size"] for item in regions],
        [item["address_status"] for item in regions]) != (
            [118, 34, 44],
            ["generated_source_entry_replacement", "official_blob", "source_compiled"],
        ):
        raise AuditError("production AT^AUDIO manifest closure changed")
    package = PACKAGE.read_bytes()
    if (len(package), sha256(package)) != (
        4634038, manifest["package"]["expected_sha256"]
    ):
        raise AuditError("production AT^AUDIO package artifact changed")
    plan_bytes = FLASH_PLAN.read_bytes()
    plan = json.loads(plan_bytes)
    if (
        len(plan_bytes), sha256(plan_bytes), plan.get("package_sha256"),
        tuple(len(plan[key]) for key in (
            "flash_regions", "unresolved_flash_regions",
            "container_only_regions", "protected_regions",
        )),
    ) != (
        3108201, "e91992690cb5766623f0b95b0928d3113ea9c0deac6d12275d55db6f12741297",
        "3953d7a537b11d75c7f589522ae7958bd7c4f59a15d35b98d92d5bec79b90731",
        (4482, 2, 5, 6),
    ):
        raise AuditError("production AT^AUDIO flash plan changed")

    return {
        "surface": {
            "linked_functions": 1,
            "body_bytes": 118,
            "owned_noncode_bytes": 34,
            "physical_bytes": 152,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 10,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
        },
        "command": {
            "name": "AT^AUDIO",
            "handler": "_atAudioCtrl",
            "record_type": 0,
            "enable": {"leading_character": "1", "provider": "0x0054f380", "selector": 7},
            "disable": {"leading_character": "0", "provider": "0x0054f50e", "selector": 7},
            "response": "AUD_AUDIO+OK\r\n",
            "return_value": 1,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "exact_symbol": "_atAudioCtrl",
            "command_record": "[0x006c9290,0x006c92a0)",
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/at_codec.c",
            "production_routed": True,
            "ownership_bytes": 162,
            "source_inventory_available": True,
            "source_functions": 1,
            "compiled_text_bytes": 44,
            "alignment_bytes": 0,
            "stock_replaced_bytes": 118,
            "retained_official_pool_bytes": 34,
            "strict_relocations": 3,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": "No authorized responsive G2 and live audio/codec evidence is available.",
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 eAT codec audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
