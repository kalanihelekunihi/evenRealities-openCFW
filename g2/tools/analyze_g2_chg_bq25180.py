#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party BQ25180 charger object."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-chg-bq25180-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-chg-bq25180-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-chg-bq25180-provenance.tsv"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
CANDIDATE = ROOT / "components/apollo_main/core_overlay/chg_bq25180.c"
PINS = {
    FUNCTION_MAP: "5c71b831fbe1f1a254a742d0c3d07b89617b1397412b185625397dab6c60ef57",
    CLOSURE: "752542d39dcf921550abbb0323ceb07aef4046242851abe45d5f3730e711e7d2",
    PROVENANCE: "397ecc397ffd8251a65274d4dbbee40f9171de2d89e171f6fcf386fc8f81dbd4",
    CANDIDATE: "2edddc05bdf6a68b6347d3a44a118939992643cf8d5a73cdfa8b4681882f2cbd",
}
PHYSICAL = (0x0053A670, 0x0053AFC0)
PHYSICAL_SHA256 = "a2886fb69c9abc85bfa25a1d71db3c9c040a47d0609751f71c9f5c305c6c1f30"
POOL = (0x0053AF4C, 0x0053AFC0)
POOL_SHA256 = "1709443848efd8bb84f60e554b5d07002e4d74f32a13a5288ea6e1dd2b3da4cf"
BODY_SHA256 = "7ddab9a21b4394ca80bbedcac0fee1141f4e407c7c86038f4aa52b9f50fc8620"
ENTRY_COUNT = 56
ENTRY_SHA256 = "ac7ddc6f6d0b6367d958649975065e3b90206e94bbb93f843ef1941f8f9d8bc0"
EXTERIOR_ENTRY_CALLS = [(0x004C6886, 0x0053AE66), (0x00509438, 0x0053AE7E)]
EXTERIOR_ENTRY_SHA256 = "041227f3ea11d59807015a1b123667cbaff5555e08c299ccff7fa868d4c0c6ae"
BODY_CALLS = 93
BODY_CALL_SHA256 = "d0cf5ecd1fa1327b6b806638ed38471d8f1e73a46cf92458025c099ec8dbf5d5"
WORDS = {
    0x0053AF4C: 0x00000000,
    0x0053AF50: 0x2007456C,
    0x0053AF54: 0x00776AB4,
    0x0053AF58: 0x0078A8B0,
    0x0053AF5C: 0x007538AC,
    0x0053AF60: 0x0070AD24,
    0x0053AF64: 0x0078D45C,
    0x0053AF68: 0x00776ACC,
    0x0053AF6C: 0x20073B18,
    0x0053AF70: 0x00733224,
    0x0053AF74: 0x00776AE4,
    0x0053AF78: 0x0078D464,
    0x0053AF7C: 0x0071DFF0,
    0x0053AF80: 0x00733254,
    0x0053AF84: 0x0071E028,
    0x0053AF88: 0x00749344,
    0x0053AF8C: 0x007021D4,
    0x0053AF90: 0x0073E0B4,
    0x0053AF94: 0x006E7630,
    0x0053AF98: 0x0075F570,
    0x0053AF9C: 0x0070AD64,
    0x0053AFA0: 0x200744FC,
    0x0053AFA4: 0x0074936C,
    0x0053AFA8: 0x0077EEC4,
    0x0053AFAC: 0x00733284,
    0x0053AFB0: 0x0071E060,
    0x0053AFB4: 0x0070ADA4,
    0x0053AFB8: 0x007538D0,
    0x0053AFBC: 0x007332B4,
}
STRINGS = {
    0x00776AB4: "DRV_Bq25180ReadEvent",
    0x0078A8B0: "p != NULL",
    0x0070AD24: r"D:\01_workspace\s200_ap510b_iar_git\driver\chg\drv_bq25180.c",
    0x00776ACC: "DRV_Bq25180ReadStatet",
    0x00776AE4: "bq25180_read_device_id",
    0x00749344: "DRV_Bq25180SetBatteryRegulationVoltage",
    0x007021D4: "millivoltage >= MIN_BAT_REG_mV && millivoltage <= MAX_BAT_REG_mV",
    0x0073E0B4: "DRV_Bq25180SetBatteryUnderVoltage_lockout",
    0x006E7630: "millivoltage >= MIN_BAT_UNDERVOLTAGE_mV && millivoltage <= MAX_BAT_UNDERVOLTAGE_mV",
    0x0075F570: "DRV_Bq25180SetFastchargeCurrent",
    0x0070AD64: "milliampere >= MIN_IN_CURR_mA && milliampere <= MAX_IN_CURR_mA",
    0x0077EEC4: "DRV_Bq25180HwInit",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def pairs(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def load(name: str, path: Path):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def cstring(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    return blob[offset:end].decode("ascii")


def thumb_bw_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", blob, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != 3_523_396 or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    starts: set[int] = set()
    interiors: set[int] = set()
    bodies: list[bytes] = []
    intervals: list[tuple[int, int]] = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = sl(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 28 or sum(map(len, bodies)) != 2268:
        raise AuditError("function inventory changed")
    if intervals[0][0] != PHYSICAL[0] or intervals[-1][1] != POOL[0]:
        raise AuditError("object boundary changed")
    if any(left[1] != right[0] for left, right in zip(intervals, intervals[1:])):
        raise AuditError("unexpected function gap appeared")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("owned literal pool changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"pool word changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

    decoder = load(
        "chg_bq25180_thumb",
        ROOT / "tools/recover_apollo_embedded_source_paths.py",
    )
    entry: list[tuple[int, int]] = []
    interior_bl: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior_bl.append((site, target))
        target = thumb_bw_target(blob, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    if len(entry) != ENTRY_COUNT or pairs(entry) != ENTRY_SHA256 or interior_bl:
        raise AuditError("BL entry/interior closure changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < POOL[0])]
    if exterior != EXTERIOR_ENTRY_CALLS or pairs(exterior) != EXTERIOR_ENTRY_SHA256:
        raise AuditError("exterior entry closure changed")
    if entry_bw or interior_bw:
        raise AuditError("B.W entry/interior closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != BODY_CALLS or pairs(calls) != BODY_CALL_SHA256:
        raise AuditError("direct-call closure changed")

    encoded_entries = starts | {value | 1 for value in starts}
    encoded_interiors = interiors | {value | 1 for value in interiors}
    stored_entries = []
    stored_interiors = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries or stored_interiors:
        raise AuditError("stored entry/interior pointer appeared")

    overlay = json.loads(OVERLAY.read_text())
    candidate_rel = str(CANDIDATE.relative_to(ROOT))
    expected_patches = {
        "replace_bq25180_read_event": (
            0x0053A7CC, 224,
            "2ffb7ed8fed9bdf2468d2fcbf8a56f85746ac03315fb384e47f3f9663d57afd4",
            "open_cfw_bq25180_read_event",
        ),
        "replace_bq25180_read_state": (
            0x0053A8AC, 292,
            "f4764d0d8157d8c917472fd97d30e1ad95118d1a27e88dd5bff26281c4ddbffb",
            "open_cfw_bq25180_read_state",
        ),
        "replace_bq25180_read_device_id": (
            0x0053A9D0, 180,
            "e6404eaa81eade54be3c8b1f31b260f03a22a15e29c41d658df9891d388c9ee6",
            "open_cfw_bq25180_read_device_id",
        ),
        "replace_bq25180_set_charge_enabled": (
            0x0053AA84, 28,
            "b0d11f885f410c569ab178a0422764b92196fcb72b6b066af94e17c21aba9591",
            "open_cfw_bq25180_set_charge_enabled",
        ),
        "replace_bq25180_set_ts_enabled": (
            0x0053AAA0, 18,
            "5a24f3a763aad3d95d723cc646ec6cce43c593768e3c0cc3a035a110e2344c44",
            "open_cfw_bq25180_set_ts_enabled",
        ),
        "replace_bq25180_set_safety_timer": (
            0x0053AAB2, 18,
            "758b3da2ca9a1b9a795efe20ecbb0cd015cd10811c4c1c8916ff4984af53f0f1",
            "open_cfw_bq25180_set_safety_timer",
        ),
        "replace_bq25180_set_watchdog": (
            0x0053AAC4, 18,
            "8aff5fb5ea84e26fd3211112c7db04d8d8fc6b013427f1cdf9eb10a11ab7c5c4",
            "open_cfw_bq25180_set_watchdog",
        ),
        "replace_bq25180_set_battery_regulation_voltage": (
            0x0053AAD6, 122,
            "53abad6b880231bc264d979999d19d253ac65d38babde0a92d0cf05f5b128215",
            "open_cfw_bq25180_set_battery_regulation_voltage",
        ),
        "replace_bq25180_set_battery_overcurrent": (
            0x0053AB50, 18,
            "5894c213d476786d20c1b466fc43c6519412c8c1bf5ba1a955c1e813b19e76d3",
            "open_cfw_bq25180_set_battery_overcurrent",
        ),
        "replace_bq25180_set_battery_undervoltage_lockout": (
            0x0053AB62, 190,
            "5d9cb9dcc0f7748973032acd1337e81d0cddd93cb9c6b78e50f971f58a0923d1",
            "open_cfw_bq25180_set_battery_undervoltage_lockout",
        ),
        "replace_bq25180_set_precharge_threshold": (
            0x0053AC20, 30,
            "2d6338bb172e44e6a26b5bcf33b25d0ef78fecd73533e8c08dd6c924fbfa80f1",
            "open_cfw_bq25180_set_precharge_threshold",
        ),
        "replace_bq25180_set_precharge_ratio": (
            0x0053AC3E, 30,
            "ffa00028db6ae02a3432130d289115d7e1924f2ce8427949c332eda15bf8523d",
            "open_cfw_bq25180_set_precharge_ratio",
        ),
        "replace_bq25180_set_fastcharge_current": (
            0x0053AC5C, 134,
            "62b2fe5df0db4b120de9976de9a745a5ab2789caa545fd0982e9a2e1ad4a362c",
            "open_cfw_bq25180_set_fastcharge_current",
        ),
        "replace_bq25180_set_termination_percent": (
            0x0053ACE2, 50,
            "3db14f368be150d44668e5d1660f539200cc24bb2222851519b6a09e51f13ce5",
            "open_cfw_bq25180_set_termination_percent",
        ),
        "replace_bq25180_set_vindpm": (
            0x0053AD14, 18,
            "3f3b6a84b13c2b59cbf070cbf89e8a0f4ec4c85a9bd5c79e7181824c2529186f",
            "open_cfw_bq25180_set_vindpm",
        ),
        "replace_bq25180_set_vdppm_enabled": (
            0x0053AD26, 28,
            "eac81a0dfb48627e9e9493672a6681907269df3b59586a2fe9b7054eadc009be",
            "open_cfw_bq25180_set_vdppm_enabled",
        ),
        "replace_bq25180_set_input_current_limit": (
            0x0053AD42, 110,
            "22116f6f42af9adc92d92eebd0cb143277941e80d210339ef4974c698afa571a",
            "open_cfw_bq25180_set_input_current_limit",
        ),
        "replace_bq25180_set_system_mode": (
            0x0053ADB0, 18,
            "edd6bce30be66516883a5341d4a75eb9eede51b299a5f2d494382384f33e102f",
            "open_cfw_bq25180_set_system_mode",
        ),
        "replace_bq25180_set_system_voltage": (
            0x0053ADC2, 18,
            "0dac0f3a3f626c21120fe6e3a824ccf3314973962371b5a9d6a8f168cb89ba67",
            "open_cfw_bq25180_set_system_voltage",
        ),
        "replace_bq25180_set_ts_auto_enabled": (
            0x0053ADD4, 18,
            "a8347071eaaebef0f48ed0107cf1e0ab1676c6ca124eb530af1fcb4a32a25309",
            "open_cfw_bq25180_set_ts_auto_enabled",
        ),
        "replace_bq25180_refresh_status": (
            0x0053AE66, 24,
            "58aae337d1c0264f8be3da7069d60eb569f27b08aca5ebe1c46ef97ab5ebd0ef",
            "open_cfw_bq25180_refresh_status",
        ),
        "replace_bq25180_hardware_init": (
            0x0053AE7E, 206,
            "df88ce0ebdd1477c5fc1069c878ed5da0d85ff9b6aae1ac9d9afde3feb882ec2",
            "open_cfw_bq25180_hardware_init",
        ),
    }
    patches = {
        row["name"]: row
        for row in overlay["patch_sites"]
        if row.get("name") in expected_patches
    }
    leaves = {
        row["function"]: row
        for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == candidate_rel
    }
    if (
        set(patches) != set(expected_patches)
        or any(
            patches[name]["runtime_address"] != address
            or patches[name]["expected_size"] != size
            or patches[name]["expected_sha256"] != digest
            or patches[name]["branch"] != "b_w"
            or patches[name]["target_function"] != target
            or patches[name].get("profiles") != ["apple-clang"]
            for name, (address, size, digest, target) in expected_patches.items()
        )
        or set(leaves) != {target for *_, target in expected_patches.values()}
        or any(
            leaf["source"]["sha256"] != PINS[CANDIDATE]
            or leaf.get("profiles") != ["apple-clang"]
            or leaf.get("allow_bound_static_data") is not None
            for name, leaf in leaves.items()
        )
    ):
        raise AuditError("production BQ25180 routing changed")

    return {
        "surface": {
            "linked_functions": 28,
            "body_bytes": 2268,
            "owned_pool_bytes": 116,
            "physical_bytes": 2384,
            "direct_bl_entry_sites": 56,
            "exterior_bl_entry_sites": 2,
            "direct_body_calls": 93,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        },
        "abi": {
            "i2c_bus": 7,
            "i2c_address": "0x6a",
            "runtime_pointer": "0x200744fc",
            "runtime_event_offset": "0x14",
            "runtime_state_offset": "0x16",
            "cached_charge_state": "0x20073b18",
        },
        "defaults": {
            "call_count": 19,
            "register_image_hex": "0000005a24241f4406002100f0",
            "battery_regulation_mv": 4400,
            "fastcharge_ma": 91,
            "input_limit_ma": 1000,
            "battery_uvlo_mv": 2800,
            "charger_enabled_at_exit": True,
        },
        "behavior": {
            "device_id_register": "0x0c",
            "accepted_device_id": 0,
            "event_register": "0x02",
            "state_registers": ["0x00", "0x01"],
            "field_helper_masks_input_value": False,
        },
        "production": {
            "candidate": candidate_rel,
            "candidate_sha256": PINS[CANDIDATE],
            "production_routed": True,
            "ownership_bytes": 1792,
            "retained_stock_noncode_bytes": 116,
            "retained_stock_dead_body_bytes": 476,
            "bound_providers": {
                "open_cfw_bq25180_bus_read": "0x0050436e",
                "open_cfw_bq25180_bus_write": "0x005044b4",
                "memset": "0x0043c0e4",
            },
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
