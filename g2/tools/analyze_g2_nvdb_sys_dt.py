#!/usr/bin/env python3
"""Fail-closed audit of the G2 172-byte system-data NVDB object.

The audit authenticates all 13 Thumb bodies, split literal pools, direct and
stored ingress, the decoded IAR factory record, and the legacy/OTP PSN ABI.
It is read-only and has no device or flash-writing path.
"""

from __future__ import annotations

import argparse
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
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

FUNCTION_MAP = ROOT / "tools/manifests/g2-nvdb-sys-dt-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-nvdb-sys-dt-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-nvdb-sys-dt-provenance.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "b69524ca1817807f9f5da9f949c047c232bedbc4ad1a722738339e10b91a68eb",
    CLOSURE: "cf079fedfaa0f0451b1f0a1c72fa3063e62f3c70b15088e4c61e0051b5e8fa58",
    PROVENANCE: "1a6c2653ab23d30c67e2d18d1b4212d166c972dc95b552fa58fa03f434156939",
}

PHYSICAL_SPAN = (0x004AEE28, 0x004B03E0)
PHYSICAL_SHA256 = "b26a244bac13d02e90a91a82a4f4332b7c7331258f1b1c3a5d6cb7f856ffbc67"
BODY_BYTES = 5_084
BODY_SHA256 = "5ab990b798f06a9bbe3e56b66c86f5b1ddd33bb0dc7f29dfad1ad91b4c31f1a1"
NONCODE_BYTES = 476
NONCODE_SHA256 = "225b6fb544b8f763b1cccbe25602afa22c8f07ea19bbd0528ce63170a3053a03"
NONCODE_SPANS = [
    (0x004AF87E, 0x004AF8D0, "f25d72f7bbfa5be8840cf89efd35fe4fd410a10cdfcb3a6306adb86fb7719cf2"),
    (0x004AFBB6, 0x004AFBBC, "79d51e66bbd2ecbc3568cdd1dce5aac2c9ed1285879014f935f79c1f1b1973f1"),
    (0x004AFC0C, 0x004AFC10, "143089c847b850e5e1b62ad9adf3acb13adb3ceeede1733fcb56863f9793fb0a"),
    (0x004AFC64, 0x004AFC68, "30756624e5bfd973e9fadb82c81c23a3ac85abf204c02d118d7a038167c01c00"),
    (0x004AFCA2, 0x004AFCDC, "bbd4d12dd767dd4be7406cca9705469e6aeafdcc1c822191aa93feeadd32169c"),
    (0x004AFF54, 0x004AFFC0, "f5c9eac5eb5194133a13cc26288451dd27bcda9043a81ea1fce91b0340e28356"),
    (0x004B030A, 0x004B03E0, "1ac8b04f7f1f70a0e474a7527f786d834d17e01b55d5f29ddda98e42aaf6ddbe"),
]

EXPECTED_ENTRY_CALLS = [
    (0x0046C252, 0x004AF73A), (0x004AEE92, 0x004AF8D0),
    (0x004AEEA4, 0x004AFC68), (0x004AEEB0, 0x004AFCDC),
    (0x004AF106, 0x004AF11C), (0x004AF110, 0x004AF11C),
    (0x004AF7CA, 0x004AFC68), (0x004AF7D4, 0x004AFCDC),
    (0x004AF876, 0x004AF73A), (0x004AF96A, 0x004AFBBC),
    (0x004AF974, 0x004AFBCE), (0x004AF97E, 0x004AFBE4),
    (0x004AFC5C, 0x004AF11C), (0x004B00CE, 0x004AFCDC),
    (0x004C6AD0, 0x004AF11C), (0x004C6BDC, 0x004AF11C),
    (0x0051071E, 0x004AFC68), (0x00510728, 0x004AFCDC),
    (0x00570384, 0x004AF11C), (0x0057038C, 0x004AF11C),
    (0x005727D2, 0x004AF11C), (0x005727D8, 0x004AF7B8),
    (0x005728C0, 0x004AF73A), (0x0057343C, 0x004AFFC0),
    (0x00573444, 0x004AF11C), (0x0057344A, 0x004AF7B8),
    (0x00573598, 0x004AF73A), (0x00573AE2, 0x004AF11C),
    (0x00573DF0, 0x004AFC10), (0x00573E34, 0x004AF11C),
    (0x00573F0A, 0x004AF11C), (0x0057689E, 0x004AF11C),
    (0x0057E7B6, 0x004AF7B8), (0x005810C6, 0x004AF11C),
    (0x005A5762, 0x004AF7B8), (0x005A580A, 0x004AF11C),
    (0x005BC6DA, 0x004AF73A),
]
ENTRY_CALL_SHA256 = "32acb99397ff26774ab598dcc9e92caa2f0c8e79e56c4b4ec5aa01a57f120875"
BODY_CALL_COUNT = 299
BODY_CALL_SHA256 = "130fd0310a7153978bc5da5d349785a990d63e400d05ceb231a1882ae71c77b5"
STORED_ENTRIES = [(0x006D1EAC, 0x004AEE29), (0x0078F52C, 0x004AEE3F)]
STORED_ENTRY_SHA256 = "38f53a0555681253608e5c0ea5451f1b1b0adcfb8f1236136c25fc5b917695b1"
FALSE_INTERIOR_BLS = [(0x004AB932, 0x004AF9EC)]
RAW_INTERIOR_COUNT = 48
RAW_INTERIOR_SHA256 = "bc614c76a1b921c56de5b7c0cd5d5993f2f52b66990c867f9eda53c1fbea9e33"
ALIGNED_INTERIOR_WINDOWS = [
    (0x0047970C, 0x004AF10D), (0x00526708, 0x004AF9B0),
    (0x00526A78, 0x004AF9B4), (0x005DC0F0, 0x004AF9B7),
    (0x0064D578, 0x004B0037), (0x006C1CF4, 0x004B004A),
    (0x006D1FA4, 0x004B0014), (0x006D713C, 0x004B004A),
]
ALIGNED_INTERIOR_SHA256 = "07ce3222c0692490e90a3c1170defbdf68183193d6c3b66100c73c055e7ce86a"

EXPECTED_STRINGS = {
    0x006E4FE0: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_sys_dt.c",
    0x00783488: "_nvdbUpdataSysDt",
    0x0077BB6C: "SVC_NvdbWriteSysData",
    0x00783500: "SVC_NvdbReadSysData",
    0x00783514: "SVC_NvdbparsePsn",
    0x0078358C: "SVC_ReadPSNFromOTP",
    0x007835A0: "SVC_WritePSNToOTP",
    0x0078C02C: "nv.sysDt",
    0x0078E63C: "nvSysDt",
}
FACTORY_ADDRESS = 0x20003994
FACTORY_RECORD = bytes.fromhex(
    "02533230304c4442453231303030310053323030455642544c4e323530363330"
    "3131313131000000693401000c0a0f0000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000"
)
FACTORY_SHA256 = "f2b3d283ef574404c0d9c402a52a43cba58c0d415f23d7d6d8f38005aca7f05d"
LEGACY_TABLE = 0x006D3358
LEGACY_TABLE_SHA256 = "ced8332c75782b5c1b3d18e99500f923aad63ad01807e8c2f31bc357eda9a0e1"
LEGACY_PSNS = [
    "S200LABI270028", "S200LABI270036", "S200LABI270050",
    "S200LDBE210004", "S200LABI260010", "S200LABI270068",
    "S200LABI270066", "S200LABI270004", "S200LABI270072",
    "S200LABI260003", "S200LABI250030", "S200LABI260024",
    "S200LABI260026", "S200LABI260021", "S200LABI270029",
    "S200LABI270058", "S200LABI270022", "S200LABI270073",
    "S200LABI250002", "S200LABI270071", "S200LABI270001",
    "S200LABI270012", "S200LABI260014", "S200LABI270027",
    "S200LABI270069", "S200LABI260009", "S200LABI270008",
    "S200LABI270060", "S200LABI270053", "S200LABI250023",
    "S200LABI270043", "S200LABG190017", "S200LCBI190019",
    "S200LCBI200013", "S200LABI270031", "S200LCBI200010",
    "S200LCBI200008", "S200LCBI190022", "S200LCBI200001",
    "S200LCBI190025",
]


class AuditError(RuntimeError):
    """Raised when authenticated system-data evidence changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or first >= last or last > len(blob):
        raise AuditError(f"invalid image span [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def cstring(blob: bytes, address: int) -> str:
    first = address - BASE
    last = blob.find(b"\0", first)
    if first < 0 or last < first:
        raise AuditError(f"invalid C string at 0x{address:08x}")
    return blob[first:last].decode("ascii")


def pair_digest(pairs: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def crc16_ccitt_false(data: bytes) -> int:
    crc = 0xFFFF
    for value in data:
        crc ^= value << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def load_module(name: str, path: Path):
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


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned sys-data input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 13 or [int(row["recovery_order"]) for row in rows] != list(range(1, 14)):
        raise AuditError("sys-data function inventory changed")
    bodies: list[bytes] = []
    starts: set[int] = set()
    interiors: set[int] = set()
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"stock body changed: {row['function']}")
        bodies.append(raw)
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
    if sum(map(len, bodies)) != BODY_BYTES or sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("sys-data body concatenation changed")
    if sha256(image_slice(blob, *PHYSICAL_SPAN)) != PHYSICAL_SHA256:
        raise AuditError("sys-data physical interval changed")
    noncode = []
    for start, end, expected in NONCODE_SPANS:
        raw = image_slice(blob, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"sys-data non-code span changed at 0x{start:08x}")
        noncode.append(raw)
    if sum(map(len, noncode)) != NONCODE_BYTES or sha256(b"".join(noncode)) != NONCODE_SHA256:
        raise AuditError("sys-data non-code concatenation changed")
    for address, expected in EXPECTED_STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"sys-data string changed at 0x{address:08x}")

    decoder = load_module("nvdb_sys_dt_thumb", ROOT / "tools/recover_apollo_embedded_source_paths.py")
    entry_calls = []
    interior_calls = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entry_calls.append((site, target))
        elif target in interiors:
            interior_calls.append((site, target))
    if entry_calls != EXPECTED_ENTRY_CALLS or pair_digest(entry_calls) != ENTRY_CALL_SHA256:
        raise AuditError("sys-data direct ingress changed")
    if interior_calls != FALSE_INTERIOR_BLS:
        raise AuditError("sys-data strict-interior BL classification changed")

    body_calls = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None:
                body_calls.append((site, target))
    if len(body_calls) != BODY_CALL_COUNT or pair_digest(body_calls) != BODY_CALL_SHA256:
        raise AuditError("sys-data provider-call closure changed")

    stored = []
    for start in starts:
        needle = struct.pack("<I", start | 1)
        position = blob.find(needle)
        while position >= 0:
            stored.append((BASE + position, start | 1))
            position = blob.find(needle, position + 1)
    stored.sort()
    if stored != STORED_ENTRIES or pair_digest(stored) != STORED_ENTRY_SHA256:
        raise AuditError("sys-data stored roots changed")

    encoded_interiors = interiors | {value | 1 for value in interiors}
    raw_windows = [
        (BASE + offset, value)
        for offset in range(0, len(blob) - 3)
        if (value := struct.unpack_from("<I", blob, offset)[0]) in encoded_interiors
    ]
    if len(raw_windows) != RAW_INTERIOR_COUNT or pair_digest(raw_windows) != RAW_INTERIOR_SHA256:
        raise AuditError("sys-data raw interior windows changed")
    aligned = [pair for pair in raw_windows if pair[0] % 4 == 0]
    if aligned != ALIGNED_INTERIOR_WINDOWS or pair_digest(aligned) != ALIGNED_INTERIOR_SHA256:
        raise AuditError("sys-data aligned interior-window classification changed")

    flashdb = load_module("nvdb_sys_dt_flashdb", ROOT / "tools/analyze_g2_flashdb.py")
    sram = flashdb._decode_initialized_sram(blob)
    record_offset = FACTORY_ADDRESS - flashdb.IAR_SCATTER_DESTINATION
    factory = sram[record_offset : record_offset + 172]
    if factory != FACTORY_RECORD or sha256(factory) != FACTORY_SHA256:
        raise AuditError("sys-data IAR factory record changed")
    if len(factory) != 172 or crc16_ccitt_false(factory[:38]) != 0x1DC7:
        raise AuditError("sys-data record ABI/CRC changed")

    table = image_slice(blob, LEGACY_TABLE, LEGACY_TABLE + 160)
    if sha256(table) != LEGACY_TABLE_SHA256:
        raise AuditError("legacy PSN pointer table changed")
    pointers = struct.unpack("<40I", table)
    legacy = [cstring(blob, pointer) for pointer in pointers]
    if legacy != LEGACY_PSNS:
        raise AuditError("legacy PSN strings changed")

    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    candidate = "components/apollo_main/core_overlay/nvdb_sys_dt.c"
    candidate_sha256 = "c6cf42cb277417fd0cf7bdf62d50167a194c983295a73599a6617477cbf2f8b0"
    expected_patches = {
        "replace_nvdb_sys_dt_default_initialize": (
            0x004AEE28, 22,
            "9f503b287f1267eb5f0875d35921851b74aebcd1cb50e64a5a54c03e1f81fa78",
            "open_cfw_nvdb_sys_dt_default_initialize",
        ),
        "replace_nvdb_sys_dt_load_and_migrate": (
            0x004AEE3E, 734,
            "861f74ec6afe45428e5d1dfe89c0baa258b1d6f5051d6b12da0fbd67442cdab7",
            "open_cfw_nvdb_sys_dt_load_and_migrate",
        ),
        "replace_nvdb_sys_dt_write": (
            0x004AF11C, 1566,
            "f3c7717a96bd19716d32fde553b9eb4fa738e18a8b14c721a73ccf3efd1358a8",
            "open_cfw_nvdb_sys_dt_write",
        ),
        "replace_nvdb_sys_dt_get": (
            0x004AF73A, 126,
            "7fd3682543fbbd09fa7c3eeb72f4e7bc8648c4e84ff725002a8b0ef1df1788c0",
            "open_cfw_nvdb_sys_dt_get",
        ),
        "replace_nvdb_sys_dt_read": (
            0x004AF7B8, 198,
            "2f2a9b3bcf0666493361da8b08830e52e0b20196328487c3043517d280442b83",
            "open_cfw_nvdb_sys_dt_read",
        ),
        "replace_nvdb_sys_dt_parse_psn": (
            0x004AF8D0, 742,
            "70907dd79604aa40eb32ceb8262146db672e668f3a128c1c42c2cda2bc1f0e74",
            "open_cfw_nvdb_sys_dt_parse_psn",
        ),
        "replace_nvdb_sys_dt_manufacturer_name": (
            0x004AFBBC, 18,
            "1cc4521522a4f20746e4f96e893ec669ad1c1e532be6a9a1179dda7b74bb7cd0",
            "open_cfw_nvdb_sys_dt_manufacturer_name",
        ),
        "replace_nvdb_sys_dt_year": (
            0x004AFBCE, 22,
            "2857535c47bc4d93ead4e206f9b260b5d3980f7ccf02d7b31938e5793ff58268",
            "open_cfw_nvdb_sys_dt_year",
        ),
        "replace_nvdb_sys_dt_month": (
            0x004AFBE4, 40,
            "2248967f80abeb67b495e44f590774be088cf983a30d8a130a34b9d74d9ef847",
            "open_cfw_nvdb_sys_dt_month",
        ),
        "replace_nvdb_sys_dt_reset_aging": (
            0x004AFC10, 84,
            "e371ac29fd36ef0f2df1906e478f89c360ea64b1456bde0a07fc07ae1904fddf",
            "open_cfw_nvdb_sys_dt_reset_aging",
        ),
        "replace_nvdb_sys_dt_mark_legacy_psn": (
            0x004AFC68, 58,
            "00a304e237b6c213864883d83bc7dec26e25db76f4868135b23ae61066170255",
            "open_cfw_nvdb_sys_dt_mark_legacy_psn",
        ),
        "replace_nvdb_sys_dt_read_psn_from_otp": (
            0x004AFCDC, 632,
            "52ea0eac7a2bcb82b0cea1b9665fc57b845b086e03de4d5a57e3f172e6266042",
            "open_cfw_nvdb_sys_dt_read_psn_from_otp",
        ),
        "replace_nvdb_sys_dt_write_psn_to_otp": (
            0x004AFFC0, 842,
            "86e34d465070b4776e029da8c43bf696fa6e246b8b6e80174dccc948531ffd96",
            "open_cfw_nvdb_sys_dt_write_psn_to_otp",
        ),
    }
    patches = {
        r["name"]: r
        for r in overlay["patch_sites"]
        if r.get("name") in expected_patches
    }
    leaves = {
        r["function"]: r
        for r in overlay["relocated_leaves"]
        if r.get("source", {}).get("path") == candidate
    }
    otp_begin_binding = (
        "-DOPEN_CFW_NVDB_SYS_DT_OTP_BEGIN()="
        "do { int open_cfw_pwrctrl_periph_enable(unsigned char); "
        "int open_cfw_cmsis_delay(unsigned int); "
        "(void)open_cfw_pwrctrl_periph_enable(0x1Du); "
        "(void)open_cfw_pwrctrl_periph_enable(0x17u); "
        "(void)open_cfw_cmsis_delay(1u); } while (0)"
    )
    otp_end_binding = (
        "-DOPEN_CFW_NVDB_SYS_DT_OTP_END()="
        "do { int open_cfw_pwrctrl_periph_disable(unsigned char); "
        "(void)open_cfw_pwrctrl_periph_disable(0x17u); "
        "(void)open_cfw_pwrctrl_periph_disable(0x1Du); } while (0)"
    )
    parsed_binding = (
        "-DOPEN_CFW_NVDB_SYS_DT_PARSED(project_code, manufacturer_code, "
        "manufacturer, color, year_code, year, month_code, month, day, "
        "serial_number)=do { (void)(project_code); (void)(manufacturer_code); "
        "(void)(manufacturer); (void)(color); (void)(year_code); (void)(year); "
        "(void)(month_code); (void)(month); (void)(day); "
        "(void)(serial_number); } while (0)"
    )
    legacy_table_binding = (
        "-DOPEN_CFW_NVDB_SYS_DT_LEGACY_PSNS="
        "((const char *const *)(uintptr_t)0x006D3358u)"
    )
    if (
        set(patches) != set(expected_patches)
        or any(
            patches[n]["runtime_address"] != a
            or patches[n]["expected_size"] != z
            or patches[n]["expected_sha256"] != d
            or patches[n]["branch"] != "b_w"
            or patches[n]["target_function"] != t
            or patches[n].get("profiles") != ["apple-clang"]
            for n, (a, z, d, t) in expected_patches.items()
        )
        or set(leaves) != {t for *_, t in expected_patches.values()}
        or any(
            l["source"]["sha256"] != candidate_sha256
            or l.get("profiles") != ["apple-clang"]
            or otp_begin_binding not in l["toolchain"]["flags"]
            or otp_end_binding not in l["toolchain"]["flags"]
            or parsed_binding not in l["toolchain"]["flags"]
            or legacy_table_binding not in l["toolchain"]["flags"]
            for l in leaves.values()
        )
    ):
        raise AuditError("production system-data routing changed")

    return {
        "image_sha256": IMAGE_SHA256,
        "surface": {
            "physical_span": [f"0x{value:08X}" for value in PHYSICAL_SPAN],
            "physical_bytes": PHYSICAL_SPAN[1] - PHYSICAL_SPAN[0],
            "physical_sha256": PHYSICAL_SHA256,
            "linked_functions": len(rows),
            "body_bytes": BODY_BYTES,
            "body_sha256": BODY_SHA256,
            "owned_noncode_bytes": NONCODE_BYTES,
            "direct_bl_ingress_sites": len(entry_calls),
            "direct_provider_calls": len(body_calls),
            "stored_entry_pointers": len(stored),
            "false_overlap_bls": len(interior_calls),
            "strict_interior_ingress": 0,
            "raw_interior_windows": len(raw_windows),
            "aligned_interior_windows": len(aligned),
        },
        "record": {
            "address": f"0x{FACTORY_ADDRESS:08X}",
            "bytes": len(factory),
            "factory_sha256": FACTORY_SHA256,
            "version_offset": 0,
            "product_serial_offset": 1,
            "board_serial_offset": 16,
            "crc_offset": 38,
            "initialized_crc16": "0x1DC7",
            "lux_base_offset": 40,
            "aging_offsets": [48, 88, 128],
        },
        "psn": {
            "legacy_table_address": f"0x{LEGACY_TABLE:08X}",
            "legacy_entries": len(legacy),
            "legacy_table_sha256": LEGACY_TABLE_SHA256,
            "otp_offset": "0x340",
            "otp_slots": 8,
            "otp_slot_bytes": 16,
            "otp_serial_bytes": 14,
        },
        "behavior": {
            "migration_imports_flashdb_record": False,
            "migration_marks_legacy_psn": True,
            "migration_resets_aging": False,
            "migration_prefers_latest_valid_otp_psn": True,
            "missing_record_rewrites_current": True,
            "pre_v2_crc_mismatch_rewrites_current": True,
            "read_imports_record_then_overrides_psn_from_otp": True,
        },
        "production": {
            "candidate": candidate,
            "candidate_sha256": candidate_sha256,
            "production_routed": True,
            "ownership_bytes": BODY_BYTES,
            "retained_stock_noncode_bytes": NONCODE_BYTES,
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze(args.image)
    except (AuditError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        surface = report["surface"]
        print(
            "sys-data NVDB closure OK: "
            f"{surface['linked_functions']} functions / {surface['body_bytes']} body bytes / "
            f"{surface['direct_bl_ingress_sites']} BL ingress / "
            f"{surface['stored_entry_pointers']} stored roots"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
