#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party BQ27427 fuel-gauge object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-chg-bq27427-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-chg-bq27427-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-chg-bq27427-provenance.tsv"
CANDIDATE = ROOT / "components/apollo_main/core_overlay/chg_bq27427.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
PINS = {
    FUNCTION_MAP: "1450c00f03999356aeaca638922f4262a753ab5dad678df5bd76a0afc5e1097b",
    CLOSURE: "f30798d74045a62776e35e790161c0aab61d8fa655677f8b06d384b8386af586",
    PROVENANCE: "b2e1ec42b629da0da760df6652be1b0c3894b8f965599dd6abc9cabc8a3a5aca",
    CANDIDATE: "2e8389a849a07af5a1d59467da0a3fa0a30dcb29c63be736a4f1db6a78412dc9",
}
PHYSICAL = (0x0053AFC0, 0x0053C2A4)
PHYSICAL_SHA256 = "ed5d39ec1667c7b623eba6dfd0deddb9d732ab53dc0e8c6b18392c77a6a929a5"
BODY_SHA256 = "0cdbcb99880d06d844f54b183fbcd484ec45b4c299bf230e2c251c32d28d4529"
NONCODE = [
    (0x0053BB6A, 0x0053BB8C),
    (0x0053BCDA, 0x0053BD0C),
    (0x0053BE8A, 0x0053BEB4),
    (0x0053C016, 0x0053C024),
    (0x0053C0D4, 0x0053C0F4),
    (0x0053C1C4, 0x0053C2A4),
]
NONCODE_SHA256 = "2945fc1a3fc2e2b8c8db96a3577605d213c1962e4a1ef2d7a2c95c1af960ae83"
ENTRY_COUNT = 88
ENTRY_SHA256 = "31c5e418944241c3dcebe62042ad1cf8d7c4227a91a5c397df3e6d57d0f9db00"
EXTERIOR_ENTRY = [(0x004C688A, 0x0053C0F4), (0x0050943C, 0x0053C0FE)]
EXTERIOR_ENTRY_SHA256 = "6352135e959405e766fcacfb4541fde22830f5cb86d0b37b909ad1a5a895664c"
BODY_CALL_COUNT = 287
BODY_CALL_SHA256 = "9633a7b8a873d6b33a91492c47448a07b5cf684140483ef373cfdc9f49049c34"
RAW_INTERIOR_FALSE_POSITIVE = [(0x0063062A, 0x0053B4BE)]
PATH_ADDRESS = 0x0070ADE4
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\chg\drv_bq27427.c"
UNSEAL_KEY_ADDRESS = 0x200006E8
UNSEAL_KEY = bytes.fromhex("00800080")
UNSEAL_KEY_SHA256 = "da60b92bc70e999c07a6ded180a16c1e801e89a5722b565ea242d6aff2f507d8"
DM_TABLE_ADDRESS = 0x200006EC
DM_TABLE = bytes.fromhex(
    "520602000000401f520802000000ff7f520a0200b80b3011400401000000ff00"
    "520201000000ff00510002000000d007690501000000ff7f0604000000000000"
)
DM_TABLE_SHA256 = "4c4a1ae9505326f73b3a74b1e5b3845b7d984ff065d454684fbd9dc1b037a08a"
DEFAULTS_ADDRESS = 0x0078A8BC
DEFAULTS = bytes.fromhex("f0000000500000001c0c0000")
DEFAULTS_SHA256 = "49083b7573db70b2264c79114484fec2ea30facc04431f8cacefde2a1c141f62"


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
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
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
    if len(rows) != 37 or sum(map(len, bodies)) != 4440:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    noncode = b"".join(image_slice(data, *span) for span in NONCODE)
    if len(noncode) != 396 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned non-code changed")
    if cstring(data, PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained source path changed")
    if image_slice(data, DEFAULTS_ADDRESS, DEFAULTS_ADDRESS + 12) != DEFAULTS:
        raise AuditError("product defaults changed")
    if sha256(DEFAULTS) != DEFAULTS_SHA256:
        raise AuditError("product-default pin changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import analyze_g2_flashdb as flashdb
    import recover_apollo_embedded_source_paths as decoder
    initialized = flashdb._decode_initialized_sram(data)
    key_offset = UNSEAL_KEY_ADDRESS - flashdb.IAR_SCATTER_DESTINATION
    table_offset = DM_TABLE_ADDRESS - flashdb.IAR_SCATTER_DESTINATION
    if initialized[key_offset : key_offset + 4] != UNSEAL_KEY:
        raise AuditError("initialized unseal key changed")
    if initialized[table_offset : table_offset + 64] != DM_TABLE:
        raise AuditError("initialized DM descriptor table changed")
    if sha256(UNSEAL_KEY) != UNSEAL_KEY_SHA256 or sha256(DM_TABLE) != DM_TABLE_SHA256:
        raise AuditError("initialized-data pin changed")

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
    if len(entry) != ENTRY_COUNT or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("BL entry closure changed")
    if interior != RAW_INTERIOR_FALSE_POSITIVE:
        raise AuditError("raw BL interior-window classification changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if exterior != EXTERIOR_ENTRY or pair_digest(exterior) != EXTERIOR_ENTRY_SHA256:
        raise AuditError("exterior BL closure changed")
    if entry_bw or interior_bw:
        raise AuditError("B.W entry/interior closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != BODY_CALL_COUNT or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded_entries = starts | {value | 1 for value in starts}
    encoded_interiors = interiors | {value | 1 for value in interiors}
    stored_entries = []
    stored_interiors = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries or stored_interiors:
        raise AuditError("stored entry/interior pointer appeared")

    overlay = json.loads(OVERLAY.read_text())
    candidate_rel = str(CANDIDATE.relative_to(ROOT))
    expected_patches = {
        "replace_bq27427_read_flags": (
            0x0053B10A, 86,
            "0728d87d1621321e8927cacf9e6da4cc5a5c4e04a19b36c4bd53d3eadf14aa40",
            "open_cfw_bq27427_read_flags",
        ),
        "replace_bq27427_read_soc": (
            0x0053B160, 86,
            "703990a20d8045c5d5475252bbdd477eded40dcd465f36c1616f522fee6d97f0",
            "open_cfw_bq27427_read_soc",
        ),
        "replace_bq27427_read_temperature": (
            0x0053B1B6, 90,
            "d40b1a7b66e8181def9807f206dee5235473a66d8d9cd703b1fecff84c162a85",
            "open_cfw_bq27427_read_temperature",
        ),
        "replace_bq27427_read_battery_voltage": (
            0x0053B210, 88,
            "50807c5b3839945b1e2ebd772d3b68fa274d5533fe57e8fb5cd1ae261bb5522a",
            "open_cfw_bq27427_read_battery_voltage",
        ),
        "replace_bq27427_read_charge": (
            0x0053B268, 112,
            "454a9d1000b56b2d25ec4d1bf35752c4477e017cd547caec212882d569397295",
            "open_cfw_bq27427_read_charge",
        ),
        "replace_bq27427_read_nom_capacity": (
            0x0053B2D8, 10,
            "a920002bb323c5704fc877f596d06b110d4adf2465f22a2739c32291d4fc7f29",
            "open_cfw_bq27427_read_nom_capacity",
        ),
        "replace_bq27427_read_avail_capacity": (
            0x0053B2E2, 10,
            "5a7129d00d2662d4890dc359df521c6ffa5a6f000b06b92245005c9aa81a6b0d",
            "open_cfw_bq27427_read_avail_capacity",
        ),
        "replace_bq27427_read_rem_capacity": (
            0x0053B2EC, 10,
            "dc259a213b7bda99116020e14562094ce50e808beeab4b17ce7e9dd5960bf3f6",
            "open_cfw_bq27427_read_rem_capacity",
        ),
        "replace_bq27427_read_full_capacity": (
            0x0053B2F6, 10,
            "82d5ddc33a0bd1af86a48cb33842b12807c493fe42cc0f2ecdda165481dbe697",
            "open_cfw_bq27427_read_full_capacity",
        ),
        "replace_bq27427_read_ai": (
            0x0053B300, 92,
            "c67de10a4ba2ee3637973a152982ffa822a0413f451cb6ef7cc6de1cf3ce6225",
            "open_cfw_bq27427_read_ai",
        ),
        "replace_bq27427_read_ap": (
            0x0053B35C, 92,
            "93dddcc0de8656bc4cf6ff89738237ddce731a048cd44002bb9d19c594f4434c",
            "open_cfw_bq27427_read_ap",
        ),
        "replace_bq27427_read_int_temp": (
            0x0053B3B8, 10,
            "629fecbd605223a984567dabaf128107e5367ef62735df6523ac9f61240f6842",
            "open_cfw_bq27427_read_int_temp",
        ),
        "replace_bq27427_read_rem_cap_unfl": (
            0x0053B3C2, 10,
            "57432df7e5590a57ace30e2fec171f274d39b7bf991d4d46af6a596a54e3d946",
            "open_cfw_bq27427_read_rem_cap_unfl",
        ),
        "replace_bq27427_read_rem_cap_fil": (
            0x0053B3CC, 10,
            "bb0ce0177c5ab578866e33dc5b887dfe7ec3fde9ce2fad8367bd4e6902ede1c4",
            "open_cfw_bq27427_read_rem_cap_fil",
        ),
        "replace_bq27427_read_full_cap_unfl": (
            0x0053B3D6, 10,
            "41af9ea9608e012a71987a84af047c2254868defb9df7cdaa86685007083dd9d",
            "open_cfw_bq27427_read_full_cap_unfl",
        ),
        "replace_bq27427_read_full_cap_fil": (
            0x0053B3E0, 10,
            "7416d145e60fc09b76beda01124fc776059299ccb768060396605704dd08f3e0",
            "open_cfw_bq27427_read_full_cap_fil",
        ),
        "replace_bq27427_read_soc_unfl": (
            0x0053B3EA, 10,
            "d8ab9018090d2eb7a6a2373ada9d1d4ef2a037a24491efdcd1c714e5fdfe1df2",
            "open_cfw_bq27427_read_soc_unfl",
        ),
        "replace_bq27427_seal": (
            0x0053B3F4, 100,
            "e0e5090fa8e176220fa6f086f1305b3e22ab8b981d2e167326728bbac339ef37",
            "open_cfw_bq27427_seal",
        ),
        "replace_bq27427_unseal": (
            0x0053B458, 202,
            "a9b9c3cebcb739bcf8e937df1ed8e9494481a15094bc9520b8ba349bb7879ef9",
            "open_cfw_bq27427_unseal",
        ),
        "replace_bq27427_checksum_dm_block": (
            0x0053B522, 126,
            "0f5c6c2a0a77e5c674c0bd9d7abb69071a7af4332b2c89601c1d2a71c975f3b1",
            "open_cfw_bq27427_checksum_dm_block",
        ),
        "replace_bq27427_read_dm_block": (
            0x0053B5A0, 336,
            "48711b766d41e248ee1c4dd806f4fcfbf353d13c85003cb323a4ff13e99c0956",
            "open_cfw_bq27427_read_dm_block",
        ),
        "replace_bq27427_update_dm_block": (
            0x0053B6F0, 458,
            "ffa13effca5ff6bfbc0f8400917e362a63f02ed8334ba11e1d711ca4c2a688f7",
            "open_cfw_bq27427_update_dm_block",
        ),
        "replace_bq27427_set_cfgupdate": (
            0x0053B966, 88,
            "ee7adb8e6a690b61b708ec12bde9711e058b96e3be577c2a1d46776b4f7120de",
            "open_cfw_bq27427_set_cfgupdate",
        ),
        "replace_bq27427_soft_reset": (
            0x0053B9BE, 88,
            "b11c6412f91f0a2525eda2f62d90eb620ab88457ffa3220fcb2d9889a144b866",
            "open_cfw_bq27427_soft_reset",
        ),
        "replace_bq27427_execute_control_word": (
            0x0053BA16, 28,
            "a5aaa1061b44e653ab579b69799dad115e555f91a6b8470d4b3f62b3df6909f6",
            "open_cfw_bq27427_execute_control_word",
        ),
        "replace_bq27427_write_dm_block": (
            0x0053BA32, 312,
            "44134f7391a61a7dc4374c84d60c102a5259f696555e17dfa8005a4b2a460371",
            "open_cfw_bq27427_write_dm_block",
        ),
        "replace_bq27427_configure_from_params": (
            0x0053BB8C, 334,
            "aa1a85372d9952b3cba9ec540200536d9e832d0a5c072819e84f246344c0ddb4",
            "open_cfw_bq27427_configure_from_params",
        ),
        "replace_bq27427_change_chemistry_profile": (
            0x0053BD0C, 382,
            "867ced92a59a1a3a84363de29c1744651450bfd019a8680afb5882ff3aebb28f",
            "open_cfw_bq27427_change_chemistry_profile",
        ),
        "replace_bq27427_settings": (
            0x0053BEB4, 354,
            "68dc4670db668825805a2d76074decab7e38e41c7e7e1ff9de34f7580d2d8e9f",
            "open_cfw_bq27427_settings_apply_defaults",
        ),
        "replace_bq27427_status_update": (
            0x0053C024, 176,
            "58488b32df2e40c5bc46172e9911f4f3390979054f3917fba9e5961ea36bca3d",
            "open_cfw_bq27427_status_update",
        ),
        "replace_bq27427_init_wrapper": (
            0x0053C0F4, 10,
            "a87205d11d6220d3d04f0a31d2ce97a25e622884c004dc8f20bdc8dc6b569f44",
            "open_cfw_bq27427_init_wrapper",
        ),
        "replace_bq27427_hardware_init": (
            0x0053C0FE, 198,
            "11b61edcd86c46bdbb22cd1a88a13463518a92f46f7548fc3141171745f495c0",
            "open_cfw_bq27427_hardware_init",
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
    provider_leaf = "open_cfw_bq27427_cfgupdate_priv"
    local_target_leaves = {
        "open_cfw_bq27427_set_cfgupdate",
        "open_cfw_bq27427_soft_reset",
        "open_cfw_bq27427_write_dm_block",
        "open_cfw_bq27427_change_chemistry_profile",
    }
    closure_leaves = {
        "open_cfw_bq27427_update_dm_block": (
            ".rodata.open_cfw_bq27427_dm_map", 56,
        ),
        "open_cfw_bq27427_settings_apply_defaults": (
            ".rodata.open_cfw_bq27427_defaults", 12,
        ),
        "open_cfw_bq27427_hardware_init": (
            ".rodata.open_cfw_bq27427_defaults", 12,
        ),
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
        or set(leaves)
        != {target for *_, target in expected_patches.values()} | {provider_leaf}
        or any(
            leaf["source"]["sha256"] != PINS[CANDIDATE]
            or leaf.get("profiles") != ["apple-clang"]
            or leaf.get("allow_local_function") is not (
                True if name == provider_leaf else None
            )
            or leaf.get("allow_local_relocation_targets") is not (
                True if name in local_target_leaves else None
            )
            or leaf.get("allow_bound_static_data") is not None
            or (
                name in closure_leaves
                and (
                    leaf.get("closure", {}).get("rodata", {}).get("section")
                    != closure_leaves[name][0]
                    or leaf.get("closure", {}).get("rodata", {}).get("size")
                    != closure_leaves[name][1]
                )
            )
            or (name not in closure_leaves and "closure" in leaf)
            for name, leaf in leaves.items()
        )
    ):
        raise AuditError("production BQ27427 routing changed")

    descriptors = [
        {
            "subclass": DM_TABLE[index],
            "offset": DM_TABLE[index + 1],
            "width": DM_TABLE[index + 2],
            "minimum": struct.unpack_from("<H", DM_TABLE, index + 4)[0],
            "maximum": struct.unpack_from("<H", DM_TABLE, index + 6)[0],
        }
        for index in range(0, 56, 8)
    ]
    return {
        "surface": {
            "linked_functions": 37,
            "body_bytes": 4440,
            "owned_noncode_bytes": 396,
            "physical_bytes": 4836,
            "direct_bl_entry_sites": 88,
            "exterior_bl_entry_sites": 2,
            "direct_body_calls": 287,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        },
        "abi": {
            "i2c_bus": 7,
            "i2c_address": "0x55",
            "runtime_global": "0x20073b18",
            "runtime_offsets": {"soc": 4, "voltage": 8, "current": 12, "temperature": 16},
            "unseal_key": "0x80008000",
            "dm_block_size": 36,
        },
        "configuration": {
            "defaults": [240, 80, 3100],
            "descriptors": descriptors,
            "dm_table_sha256": DM_TABLE_SHA256,
        },
        "production": {
            "candidate": candidate_rel,
            "candidate_sha256": PINS[CANDIDATE],
            "production_routed": True,
            "ownership_bytes": 3938,
            "retained_stock_noncode_bytes": 396,
            "retained_stock_dead_body_bytes": 502,
            "bound_providers": {
                "open_cfw_bq27427_transfer_read": "0x0050436e",
                "open_cfw_bq27427_transfer_write": "0x005044b4",
                "open_cfw_bq27427_delay_ms": "0x004910f4",
                "memcpy": "0x00439be4",
                "memset": "0x0043c0e4",
            },
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 BQ27427 fuel-gauge audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
