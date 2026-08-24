#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 eAT buzzer command module."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-at-buzzer-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-at-buzzer-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-at-buzzer-provenance.tsv"
PINS = {
    FUNCTION_MAP: "4464ea24a5d714eeb07f294f021f0eea2afbf089b962a566fcc573c8202c25e5",
    CLOSURE: "0bff9f1708946204e9b5f23b33b249b949be9664f7d9d684d5658881b1fd0e4b",
    PROVENANCE: "9f91b75770fdbbbb75526ffdee8a96e2a35e905cabb286149f161ed2ba6daadf",
}
BODY = (0x005A4FD0, 0x005A53C6)
BODY_SHA256 = "b2a6c3ec39cd168200cc68667e3939d0bf4067ea862115c5108b653b07d38d28"
POOL = (0x005A53C6, 0x005A5488)
POOL_SHA256 = "75323c9f7c225d63ae1dfb650d70f62e6791e42120c075a6e5280ca97236e8d6"
PHYSICAL = (BODY[0], POOL[1])
PHYSICAL_SHA256 = "8ed84915f03b701c32e522528da58df5c52d7a60dd81f91504a78fef7a248aca"
BODY_CALL_SHA256 = "9a6653b91dc534c56a0171ef70e16bbf0a6b58aba3c02187721b7eab3a9318d3"
STORED_POINTER_SHA256 = "179072865c23dc4d3cdb1c8e8fda251591f84eee71a446bfa3610f83f0697364"
COMMAND_RECORD = (0x006C9280, 0x006C9290)
COMMAND_RECORD_SHA256 = "dc6356d5f0069fbbe59b1e3e38d1bf65a76be62db80090eac5f1da2e0e8ec195"
COMMAND_RECORD_WORDS = (2, 0x0078A334, 0x005A4FD1, 0)
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\at_buzzer.c"
DRIVER_CALLS = {
    0x005A51E0: 0x00502BF8,
    0x005A527E: 0x00502BF0,
    0x005A5350: 0x00502C88,
    0x005A53A8: 0x00502D4C,
}
STRINGS = {
    0x006F87EC: RETAINED_PATH,
    0x0078A334: "AT^BUZZER",
    0x007850F0: "_atBuzzerTest",
    0x0077E190: "AT^BUZZER: para1=%s",
    0x0075E150: "AT^BUZZER: Missing parameters\r\n",
    0x0078A310: "Usage:\r\n",
    0x00747B5C: "  AT^BUZZER=note,<note>,<tone>,<beat>\r\n",
    0x00769B14: "  AT^BUZZER=play,<type>\r\n",
    0x007522E0: "  AT^BUZZER=start,<freq>,<duty>\r\n",
    0x0077E1A4: "  AT^BUZZER=stop\r\n",
    0x00775554: "subcmd=%s, params=%s",
    0x0078CB94: "note",
    0x00747B84: "AT^BUZZER=note: Missing parameters\r\n",
    0x00731B14: "Usage: AT^BUZZER=note,<note>,<tone>,<beat>\r\n",
    0x0078A31C: "%d,%d,%d",
    0x00727164: "AT^BUZZER=note: Invalid parameters (parsed %d)\r\n",
    0x00747BAC: "Buzzer note: note=%d, tone=%d, beat=%d",
    0x00747BD4: "Buzzer note: %d, tone: %d, beat: %d\r\n",
    0x00785100: "AT^BUZZER+OK\r\n",
    0x0073C4B0: "AT^BUZZER=note: Parameters out of range\r\n",
    0x00752304: "note: 0-7, tone: 0-3, beat: 1-100\r\n",
    0x0078CB9C: "play",
    0x00752328: "AT^BUZZER=play: Missing parameter\r\n",
    0x0075E190: "Usage: AT^BUZZER=play,<type>\r\n",
    0x0073C4DC: "AT^BUZZER=play: Type out of range (0-10)\r\n",
    0x0077556C: "Buzzer play type: %d",
    0x00775584: "Buzzer play type: %d\r\n",
    0x0078CBA4: "start",
    0x00747BFC: "AT^BUZZER=start: Missing parameters\r\n",
    0x00747C24: "Usage: AT^BUZZER=start,<freq>,<duty>\r\n",
    0x0078CBAC: "%d,%d",
    0x007271CC: "AT^BUZZER=start: Invalid parameters (parsed %d)\r\n",
    0x0073C508: "AT^BUZZER=start: Parameters out of range\r\n",
    0x0075E1D0: "freq: 1-20000, duty: 0-100\r\n",
    0x0075E1F0: "Buzzer start: freq=%d, duty=%d",
    0x0075234C: "Buzzer start: freq=%d, duty=%d\r\n",
    0x0078CBB4: "stop",
    0x0078A328: "Buzzer stop",
    0x00785110: "Buzzer stop\r\n",
    0x00747C4C: "AT^BUZZER: Unknown subcommand '%s'\r\n",
    0x0075E210: "Use: note, play, start, stop\r\n",
}
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/at_buzzer.c"
OVERLAY_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PRODUCTION_PIN = (
    11707,
    "9e0b37c03975f2f588300922507789599f63b162a77533aa6c40c7703601da7a",
)
PRODUCTION_LEAF_PIN = (
    2740,
    "a3eeb877b669e96b2f0122ebdd399a5795a6f0a7bd7d3fd938f03375c5cd0305",
    186072,
    "ad410f96ed64029c338fc5e522f952226d10676935ca991583c498ee9810efdf",
)


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
    if (start, end) != BODY:
        raise AuditError("function boundary changed")
    body = image_slice(data, start, end)
    if len(body) != int(row["stock_bytes"]) or sha256(body) != row["stock_sha256"]:
        raise AuditError("handler body changed")
    if sha256(body) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *POOL)) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    command_record = image_slice(data, *COMMAND_RECORD)
    if sha256(command_record) != COMMAND_RECORD_SHA256:
        raise AuditError("AT command record changed")
    if struct.unpack("<IIII", command_record) != COMMAND_RECORD_WORDS:
        raise AuditError("AT command record layout changed")
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
    if len(calls) != 76 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")
    call_map = dict(calls)
    if any(call_map.get(site) != target for site, target in DRIVER_CALLS.items()):
        raise AuditError("buzzer-driver dispatch changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    expected_pointer = [(0x006C9288, 0x005A4FD1)]
    if raw_addresses != expected_pointer or pair_digest(raw_addresses) != STORED_POINTER_SHA256:
        raise AuditError("stored handler-pointer closure changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    source = PRODUCTION_SOURCE.read_bytes()
    if (len(source), sha256(source)) != PRODUCTION_PIN:
        raise AuditError("production AT^BUZZER source changed")
    leaves = [
        item for item in overlay.get("relocated_leaves", [])
        if item.get("function") == "open_cfw_at_buzzer_test"
    ]
    if len(leaves) != 1 or "open_cfw_at_buzzer_test" not in overlay["functions"]:
        raise AuditError("production AT^BUZZER leaf inventory changed")
    leaf = leaves[0]
    source_record = leaf.get("source", {})
    expected = leaf.get("expected", {})
    relocation_offsets = (
        0x38, 0x44, 0x52, 0x5E, 0x6A, 0x30A, 0x30E, 0x320,
        0x32E, 0x35A, 0x36A, 0x386, 0x4B2, 0x59E, 0x5A4, 0x5B0,
        0x626, 0x93A, 0x942, 0x956, 0xA74, 0xAA4, 0xAAE,
    )
    target_by_symbol = {
        "open_cfw_retained_at_buzzer_output": 0x00541430,
        "open_cfw_retained_buzzer_play": 0x00502BF0,
        "open_cfw_retained_buzzer_play_note": 0x00502BF8,
        "open_cfw_retained_buzzer_start": 0x00502C88,
        "open_cfw_retained_buzzer_stop": 0x00502D4C,
    }
    relocations = leaf.get("relocations", [])
    if (
        source_record.get("path")
        != "components/apollo_main/core_overlay/at_buzzer.c"
        or (source_record.get("size"), source_record.get("sha256"))
        != PRODUCTION_PIN
        or leaf.get("profiles") != ["apple-clang"]
        or not leaf.get("strict_relocation_contract")
        or (
            expected.get("size"), expected.get("sha256"),
            expected.get("alignment"), expected.get("offset"),
            expected.get("unrelocated_sha256"),
        ) != (
            PRODUCTION_LEAF_PIN[0], PRODUCTION_LEAF_PIN[1], 4,
            PRODUCTION_LEAF_PIN[2], PRODUCTION_LEAF_PIN[3],
        )
        or tuple(item.get("offset") for item in relocations)
        != relocation_offsets
        or any(
            item.get("type") != "R_ARM_THM_CALL"
            or item.get("symbol_type") != "STT_NOTYPE"
            or target_by_symbol.get(item.get("symbol"))
            != item.get("target_address")
            for item in relocations
        )
    ):
        raise AuditError("production AT^BUZZER leaf changed")
    patches = [
        item for item in overlay.get("patch_sites", [])
        if item.get("name") == "replace_at_buzzer_test"
    ]
    if len(patches) != 1:
        raise AuditError("production AT^BUZZER patch inventory changed")
    patch = patches[0]
    if (
        patch.get("runtime_address"), patch.get("expected_size"),
        patch.get("expected_sha256"), patch.get("target_function"),
        patch.get("branch"), patch.get("profiles"),
    ) != (
        PHYSICAL[0], 1208, PHYSICAL_SHA256, "open_cfw_at_buzzer_test",
        "b_w", ["apple-clang"],
    ):
        raise AuditError("production AT^BUZZER patch changed")

    build = json.loads(OVERLAY_REPORT.read_text())
    if (
        build["overlay"]["size"], build["overlay"]["sha256"],
        build["component"]["size"], build["component"]["sha256"],
    ) != (
        240692,
        "2db11ff707bf253280eb07667c3d76954347cc9e31796c7589faf788fed629ae",
        3764088,
        "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
    ):
        raise AuditError("production AT^BUZZER build pins changed")
    built = [
        item for item in build.get("relocated_leaves", [])
        if item.get("extraction", {}).get("function")
        == "open_cfw_at_buzzer_test"
    ]
    if (
        len(built) != 1
        or built[0]["placement"].get("size") != 2740
        or built[0]["placement"].get("padding_before") != 0
        or built[0]["extraction"].get("relocation_count") != 23
    ):
        raise AuditError("production AT^BUZZER compiled closure changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    regions = {item.get("name"): item for item in main["regions"]}
    generated = regions.get("at_buzzer_test_source_replacement")
    appended = regions.get("at_buzzer_test_source_text")
    if (
        generated is None or appended is None
        or (
            generated.get("file_offset"), generated.get("size"),
            generated.get("target_address"), generated.get("address_status"),
        ) != (1495024, 1208, PHYSICAL[0], "generated_source_entry_replacement")
        or (
            appended.get("file_offset"), appended.get("size"),
            appended.get("target_address"), appended.get("address_status"),
        ) != (3709468, 2740, 0x007C19FC, "source_compiled")
        or (
            main["provider"]["size"], main["provider"]["sha256"],
            manifest["package"]["expected_size"],
            manifest["package"]["expected_sha256"],
        ) != (
            3764088,
            "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
            4542582,
            "275a9e691c0bad851f7adbc80ed2abc1580e13d67f031912e198f984d18f7f85",
        )
    ):
        raise AuditError("production AT^BUZZER manifest closure changed")

    return {
        "surface": {
            "linked_functions": 1,
            "body_bytes": 1014,
            "owned_noncode_bytes": 194,
            "physical_bytes": 1208,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 76,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
        },
        "command": {
            "name": "AT^BUZZER",
            "handler": "_atBuzzerTest",
            "record_type": 2,
            "subcommands": ["note", "play", "start", "stop"],
            "note_ranges": {"note": [0, 7], "tone": [0, 3], "beat": [1, 100]},
            "play_type_range": [0, 10],
            "start_ranges": {"frequency_hz": [1, 20000], "duty_percent": [0, 100]},
            "driver_targets": {
                "note": "0x00502bf8",
                "play": "0x00502bf0",
                "start": "0x00502c88",
                "stop": "0x00502d4c",
            },
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "exact_symbol": "_atBuzzerTest",
            "command_record": "[0x006c9280,0x006c9290)",
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/at_buzzer.c",
            "production_routed": True,
            "ownership_bytes": 3948,
            "source_inventory_available": True,
            "source_functions": 1,
            "compiled_text_bytes": 2740,
            "alignment_bytes": 0,
            "stock_replaced_bytes": 1208,
            "strict_relocations": 23,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized physical G2 buzzer/piezo device or captured "
                "acoustic/frequency/duty/timing evidence is available."
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 eAT buzzer audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
