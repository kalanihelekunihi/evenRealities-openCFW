#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 eAT touch-panel command module."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-at-tp-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-at-tp-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-at-tp-provenance.tsv"
PINS = {
    FUNCTION_MAP: "415f3c4347339e4b7d29258f8a5837fb201cf10a0c3344953941cabe3136075a",
    CLOSURE: "c2eb28ee6c01b02e4ab37ba2a0655c7b9f982731ff0a498687fb1905ca522714",
    PROVENANCE: "872e3bbfa76f707ec48397a2fb78fbc238c9ebf1945e621ef73ceb4a129f2fb5",
}
PHYSICAL = (0x005A5984, 0x005A5D94)
PHYSICAL_SHA256 = "d6b869880ca7b842b74efd388baeee07790680c4bc40a20ea0a08bc8cdf7659d"
PAD = (0x005A5996, 0x005A5998)
POOL = (0x005A5D08, 0x005A5D94)
NONCODE_SHA256 = "9a346273272f4bc2feadfb900fead304af2b893fd18a5ca908d408894e18025f"
BODY_SHA256 = "23d47d710882ff10a69e14e9e27b450fbe04ad838295a3c07965934c8f6509e0"
ENTRY_SHA256 = "d45c3711b074c96a3eba2b7bf96bd201065e4f474fbf9b1d8a4a8faffc72ff72"
BODY_CALL_SHA256 = "49e9f0c065e07398a650e37cbc9b3454f0246295529862be78becefb9a7c0082"
STORED_POINTER_SHA256 = "7121a5a81800fa3872e00154a9047a8dc703dbc3d4fcc518bb0802a309e66d60"
COMMAND_RECORD = (0x006C93A0, 0x006C93B0)
COMMAND_RECORD_SHA256 = "360a914f44bdf3fb36b973af5800eb5de14c14735528b41f8f409983d2112be9"
COMMAND_RECORD_WORDS = (0, 0x0078CC44, 0x005A5999, 0)
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\at_tp.c"
WORDS = {
    0x005A5D08: 0x00000031,
    0x005A5D0C: 0x00000030,
    0x005A5D10: 0x00007525,
    0x005A5D14: 0x0073C560,
    0x005A5D18: 0x0078A424,
    0x005A5D1C: 0x0078A418,
    0x005A5D20: 0x00700898,
    0x005A5D24: 0x0078CC2C,
    0x005A5D28: 0x0077E1E0,
    0x005A5D2C: 0x0078A430,
    0x005A5D30: 0x0077E1F4,
    0x005A5D34: 0x00769C48,
    0x005A5D38: 0x0075E250,
    0x005A5D3C: 0x00769C64,
    0x005A5D40: 0x0078CC34,
    0x005A5D44: 0x20075017,
    0x005A5D48: 0x0078CC3C,
    0x005A5D4C: 0x0078A43C,
    0x005A5D50: 0x0077562C,
    0x005A5D54: 0x0075E270,
    0x005A5D58: 0x00769C80,
    0x005A5D5C: 0x0078A448,
    0x005A5D60: 0x00747CC4,
    0x005A5D64: 0x0073C58C,
    0x005A5D68: 0x0071C348,
    0x005A5D6C: 0x0077E208,
    0x005A5D70: 0x00769C9C,
    0x005A5D74: 0x007851C0,
    0x005A5D78: 0x00731BA4,
    0x005A5D7C: 0x007008DC,
    0x005A5D80: 0x00769CB8,
    0x005A5D84: 0x00727234,
    0x005A5D88: 0x006F1B90,
    0x005A5D8C: 0x00727268,
    0x005A5D90: 0x0078A454,
}
STRINGS = {
    0x0078CC44: "AT^TP",
    0x0073C560: "Gesture cfg: long_press_threshold_ms=%u\r\n",
    0x0078A424: "para1: %s",
    0x0078A418: "_atTpTest",
    0x00700898: RETAINED_PATH,
    0x0078CC2C: "at.tp",
    0x0077E1E0: "[at.tp]para1: %s",
    0x0078A430: "para2: %s",
    0x0077E1F4: "[at.tp]para2: %s",
    0x00769C48: "diff: %u, %u, %u, %u, %u",
    0x0075E250: "[at.tp]diff: %u, %u, %u, %u, %u",
    0x00769C64: "diff: %u, %u, %u, %u, %u\r\n",
    0x0078CC34: "debug1",
    0x0078CC3C: "debug0",
    0x0078A43C: "bsln_read",
    0x0077562C: "Proximity baseline: %u",
    0x0075E270: "[at.tp]Proximity baseline: %u",
    0x00769C80: "Proximity baseline: %u\r\n",
    0x0078A448: "bsln_set",
    0x00747CC4: "Proximity baseline save command sent",
    0x0073C58C: "[at.tp]Proximity baseline save command sent",
    0x0071C348: "Proximity baseline save command sent successfully.\r\n",
    0x0077E208: "gesture_cfg_read",
    0x00769C9C: "Gesture cfg read failed.\r\n",
    0x007851C0: "gesture_cfg_set",
    0x00731BA4: "Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n",
    0x007008DC: "Invalid gesture cfg. Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n",
    0x00769CB8: "Gesture cfg write failed.\r\n",
    0x00727234: "Gesture cfg write success, but readback failed.\r\n",
    0x006F1B90: "Gesture cfg write mismatch: wrote threshold=%u, read back threshold=%u\r\n",
    0x00727268: "Gesture cfg updated and verified successfully.\r\n",
    0x0078A454: "AT^TP+OK\r\n",
}
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/at_tp.c"
OVERLAY_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PRODUCTION_PIN = (
    9164,
    "b1865b7ae51a77ccb0ccce05a7b9832a89b6e167171bded7c4915d6afe08fa03",
)
PRODUCTION_LEAVES = (
    (
        "open_cfw_at_tp_print_gesture_cfg",
        "OPEN_CFW_AT_TP_PRINT_ONLY",
        20,
        "50230ca357e1b9360db9c3f3f0d7d56da99ce9465d69cade7ce271a2616a82cb",
        184524,
        1,
    ),
    (
        "open_cfw_at_tp_test",
        "OPEN_CFW_AT_TP_TEST_ONLY",
        1528,
        "6f351a53aa7b2b95bd7242000caf2e5d54871c65e7599f7daf0c3f067dba89c0",
        184544,
        17,
    ),
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
    if len(rows) != 2 or sum(map(len, bodies)) != 898:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    noncode = image_slice(data, *PAD) + image_slice(data, *POOL)
    if len(noncode) != 142 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned noncode changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    record = image_slice(data, *COMMAND_RECORD)
    if sha256(record) != COMMAND_RECORD_SHA256:
        raise AuditError("AT command record changed")
    if struct.unpack("<IIII", record) != COMMAND_RECORD_WORDS:
        raise AuditError("AT command-record layout changed")
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
    expected_entry = [(0x005A5C30, 0x005A5984), (0x005A5CF8, 0x005A5984)]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    if interior or entry_bw or interior_bw:
        raise AuditError("strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 70 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    expected_pointer = [(0x006C93A8, 0x005A5999)]
    if raw_addresses != expected_pointer or pair_digest(raw_addresses) != STORED_POINTER_SHA256:
        raise AuditError("stored handler-pointer closure changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    source = PRODUCTION_SOURCE.read_bytes()
    if (len(source), sha256(source)) != PRODUCTION_PIN:
        raise AuditError("production AT^TP source changed")
    leaf_names = {item[0] for item in PRODUCTION_LEAVES}
    leaves = {
        item.get("function"): item
        for item in overlay.get("relocated_leaves", [])
        if item.get("function") in leaf_names
    }
    if set(leaves) != leaf_names or not leaf_names.issubset(
        set(overlay.get("functions", []))
    ):
        raise AuditError("production AT^TP leaf inventory changed")
    for name, selector, size, digest, offset, relocations in PRODUCTION_LEAVES:
        leaf = leaves[name]
        source_record = leaf.get("source", {})
        toolchain = leaf.get("toolchain", {})
        expected = leaf.get("expected", {})
        if (
            source_record.get("path")
            != "components/apollo_main/core_overlay/at_tp.c"
            or (source_record.get("size"), source_record.get("sha256"))
            != PRODUCTION_PIN
            or f"-D{selector}=1" not in toolchain.get("flags", [])
            or leaf.get("profiles") != ["apple-clang"]
            or not leaf.get("strict_relocation_contract")
            or (
                expected.get("size"), expected.get("sha256"),
                expected.get("alignment"), expected.get("offset"),
            ) != (size, digest, 4, offset)
            or len(leaf.get("relocations", [])) != relocations
        ):
            raise AuditError(f"production AT^TP leaf changed: {name}")
    expected_patches = {
        "replace_at_tp_print_gesture_cfg": (
            0x005A5984, 20,
            "f1c47ad01b8bc1568fa02671aadb3bec56ff4f6d967c99ad33f7fbaf8941767a",
            "open_cfw_at_tp_print_gesture_cfg",
        ),
        "replace_at_tp_test": (
            0x005A5998, 1020,
            "26aff044e7f3fa8314f06b54256c16d35576d7c19ce1b33b23f5294fb8de4a06",
            "open_cfw_at_tp_test",
        ),
    }
    patches = {
        item.get("name"): item for item in overlay.get("patch_sites", [])
        if item.get("name") in expected_patches
    }
    if set(patches) != set(expected_patches):
        raise AuditError("production AT^TP patch inventory changed")
    for name, (address, size, digest, target) in expected_patches.items():
        patch = patches[name]
        if (
            patch.get("runtime_address"), patch.get("expected_size"),
            patch.get("expected_sha256"), patch.get("target_function"),
            patch.get("branch"), patch.get("profiles"),
        ) != (address, size, digest, target, "b_w", ["apple-clang"]):
            raise AuditError(f"production AT^TP patch changed: {name}")
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
        raise AuditError("production AT^TP build pins changed")
    built = {
        item.get("extraction", {}).get("function"): item
        for item in build.get("relocated_leaves", [])
        if item.get("extraction", {}).get("function") in leaf_names
    }
    if (
        set(built) != leaf_names
        or sum(item[2] for item in PRODUCTION_LEAVES) != 1548
        or sum(item["placement"].get("padding_before", 0)
               for item in built.values()) != 2
    ):
        raise AuditError("production AT^TP compiled closure changed")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    regions = main["regions"]
    generated = [
        item for item in regions
        if item.get("name") in {
            "at_tp_print_gesture_cfg_source_replacement",
            "at_tp_test_source_replacement",
        }
    ]
    appended = [
        item for item in regions
        if item.get("name") in {
            "at_tp_print_gesture_cfg_source_text", "at_tp_test_source_text"
        }
    ]
    alignment = [
        item for item in regions
        if item.get("name") == "at_tp_print_gesture_cfg_source_alignment"
    ]
    if (
        len(generated), sum(item["size"] for item in generated),
        len(appended), sum(item["size"] for item in appended),
        len(alignment), sum(item["size"] for item in alignment),
    ) != (2, 1040, 2, 1548, 1, 2):
        raise AuditError("production AT^TP manifest closure changed")
    if (
        main["provider"]["size"], main["provider"]["sha256"],
        manifest["package"]["expected_size"],
        manifest["package"]["expected_sha256"],
    ) != (
        3764088,
        "b3ee7d2fb560f134bd5c4a27eb8203abdc0dd9482816319be0b03320fc2067ed",
        4542582,
        "275a9e691c0bad851f7adbc80ed2abc1580e13d67f031912e198f984d18f7f85",
    ):
        raise AuditError("production AT^TP package pins changed")

    return {
        "surface": {
            "linked_functions": 2,
            "body_bytes": 898,
            "owned_noncode_bytes": 142,
            "physical_bytes": 1040,
            "direct_bl_entry_sites": 2,
            "exterior_bl_entry_sites": 0,
            "direct_body_calls": 70,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
        },
        "command": {
            "name": "AT^TP",
            "handler": "_atTpTest",
            "record_type": 0,
            "subcommands": [
                "1", "0", "debug1", "debug0", "bsln_read", "bsln_set",
                "gesture_cfg_read", "gesture_cfg_set",
            ],
            "debug_flag": "0x20075017",
            "gesture_threshold_ms": [1, 65535],
            "gesture_write_provider": "0x0055b840",
            "gesture_read_provider": "0x0055b92a",
            "gesture_readback_delay_ms": 100,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "exact_symbol": "_atTpTest",
            "command_record": "[0x006c93a0,0x006c93b0)",
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/at_tp.c",
            "production_routed": True,
            "ownership_bytes": 2590,
            "source_inventory_available": True,
            "source_functions": 2,
            "compiled_text_bytes": 1548,
            "alignment_bytes": 2,
            "stock_replaced_bytes": 1040,
            "strict_relocations": 18,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized physical G2 touch panel and Cypress "
                "controller evidence is available in this workspace."
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
    print("G2 eAT touch-panel audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
