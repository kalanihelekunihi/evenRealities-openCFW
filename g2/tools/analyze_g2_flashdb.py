#!/usr/bin/env python3
"""Fail-closed, read-only audit of the G2 FlashDB 2.1.1 configuration.

The analyzer authenticates the official Apollo-main image and recovers the
KVDB compile-time configuration, object ABI, FAL partition table, and backing
flash-device ABI.  It has no device, debugger, serial, or flash-writing path.
Run addresses use ``run = file_offset + 0x00437FE0``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
MAIN_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x00437FE0


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant drifts."""


IDENTITY_STRINGS = {
    0x0078D60C: b"2.1.1",
    0x00754944: b"FlashDB V%s is initialize success.\n",
}

# ``01PE`` is the little-endian FAL magic 0x45503130 immediately before the
# first name.  It is an anchor, not itself a database/partition name.
NAME_STRINGS = {
    0x006D5358: b"01PEkvdb",
    0x006D539C: b"NVdb",
    0x0078E58C: b"kvdb",
    0x0078E594: b"sysenv",
    0x0078E60C: b"factory",
    0x0078E614: b"NVdb",
}

STOCK_INIT_MARKERS = {
    0x0073EE21: b"sec_size & (db->sec_size - 1)) == 0",
    0x0070BFEE: b"sector size (%u) MUST align with block size (%zu).\n",
    0x0076B9DA: b"sec_size(db) == 0",
}

SUBSYSTEMS_PRESENT = (b"[FlashDB][kv]", b"[FlashDB][utils]")
SUBSYSTEMS_ABSENT = (b"[FlashDB][tsdb]", b".tsl", b"tsdb")
AUTO_UPDATE_MARKERS_ABSENT = (b"__ver_num__", b"Update the KV from version")
DEBUG_MARKERS_ABSENT = (b"KVDB size is ", b"The oldest addr is")

FAL_READ_WRAPPER = 0x00597D34
FAL_PARTITION_OFFSET_OFFSET = 0x34
FAL_PARTITION_LENGTH_OFFSET = 0x38
FAL_DEVICE_CALLBACK_OFFSETS = {"read": 0x28, "write": 0x2C, "erase": 0x30}

FAL_PARTITION_TABLE = 0x006D5358
FAL_PARTITION_RECORD_SIZE = 64
FAL_PARTITION_MAGIC = 0x45503130
FAL_PARTITIONS = (
    {
        "name": "kvdb",
        "flash_name": "norflash",
        "offset": 0x01FC0000,
        "length": 0x00038000,
    },
    {
        "name": "NVdb",
        "flash_name": "norflash",
        "offset": 0x01FF8000,
        "length": 0x00008000,
    },
)

FAL_DEVICE = 0x00722B30
FAL_DEVICE_RECORD_SIZE = 56
FAL_DEVICE_EXPECTED = {
    "name": "norflash",
    "address": 0x01FC0000,
    "length": 0x02000000,
    "block_size": 0x1000,
    "init": 0x00540ED1,
    "read": 0x00540ED5,
    "write": 0x00540F2D,
    "erase": 0x00540F85,
    "write_granularity_bits": 1,
}

# read_kv's 0x18-byte header is the v2.1.1 layout unique to 1-bit write
# granularity.  fdb_kvdb_init has two 64-iteration loops: 24-byte sector-cache
# nodes at +0x2A8 and 8-byte KV-cache nodes at +0xA8.  The complete Even
# initializer and generic FAL wrapper bodies are pinned too, so call-window,
# literal-pool, and FAL-record claims cannot outlive the code that uses them.
PINNED_BODIES = {
    "sysenv_default_descriptor": (
        0x004D9590,
        0x004D959C,
        "b4e6cd8aa6a079f67c4372949852e97a8a89f88ffe0e83535947cd3f0ec87e87",
    ),
    "sysenv_default_validator": (
        0x004D959C,
        0x004D96D8,
        "8b22c9ea24a21a18e49b93bc909d6d204c09207c19d7935c9ccc1c4acf84c22d",
    ),
    "sysenv_init_wrapper": (
        0x004D96D8,
        0x004D9A84,
        "9fa5ed5c2df612cdd46667b4f9f4a536f884c44484c65c629ba20becb238190a",
    ),
    "factory_init_wrapper": (
        0x0051079C,
        0x00510992,
        "34674ed6155198d4ae3db6e87ecf98fa5039a7709970867f74a4c9b5b0424957",
    ),
    "factory_default_descriptor": (
        0x00510614,
        0x00510620,
        "6d3efa7d37ce3bea5769eea71335a37f37c7052c7e59cfa8aeb6f7afc4a5c6c4",
    ),
    "factory_default_validator": (
        0x00510620,
        0x0051079C,
        "e3284c7b9b970dc3d7f36fffbaa52cbf4da0d072bac8af08043b7e5988b1ab40",
    ),
    "read_kv": (
        0x00544000,
        0x0054418E,
        "1afc3c8acc4d095995d504e4c6b7ae68c0face093fe5c0c23b0a6299a8863c28",
    ),
    "fdb_kvdb_init": (
        0x005453FE,
        0x0054552C,
        "c40571f5f8710c17ca10a713ec7dd6fa7a32da2fac0e2c1571806ff33cd03aad",
    ),
    "db_object_accessor": (
        0x00541232,
        0x00541240,
        "a6ce82abb413ebb05e36f957ec398e3503a2d9fa7eea371b40fe09e2d052d40d",
    ),
    "fal_partition_read_wrapper": (
        0x00597D34,
        0x00597D72,
        "bd8aef1675f28c9b51abfd974f1bc7d3ed9cf3d64a0dba974f6d2ad9876d6c50",
    ),
    "fal_partition_write_wrapper": (
        0x00597D72,
        0x00597DB0,
        "2f1b6688f627b068ba062edf1b985c268ba805a803b1b51b003c6a3d693510dd",
    ),
    "fal_partition_erase_wrapper": (
        0x00597DB0,
        0x00597DEA,
        "9f34d5139292961ffe7f117181feddf1fe51c686c43f3feea855ca21abde6047",
    ),
    "norflash_init": (
        0x00540ED0,
        0x00540ED4,
        "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
    ),
    "norflash_read": (
        0x00540ED4,
        0x00540F2C,
        "c28c6e9a762ec7f6d30eece41aaba076d4cd1ab4c4ed8896e2f96d61411f18ce",
    ),
    "norflash_write": (
        0x00540F2C,
        0x00540F84,
        "99b560ec6bd2a08e55fc2aea1c175469000c34d192b27ea637b8c8c45d7dcecd",
    ),
    "norflash_erase": (
        0x00540F84,
        0x00541088,
        "40e5ef897aa952e713cd4a1e5e22770169812c154c8a7a57d668bfaa423beadc",
    ),
    "flashdb_mutex_init": (
        0x00541088,
        0x005410DA,
        "8a302e6a6a4bc1a341cb2927e1c3d2016138a44024bcae425513bedf39a5cc52",
    ),
    "flashdb_mutex_lock": (
        0x005410DA,
        0x00541126,
        "937c96b8ce5aebc4ae9e32e77ecca2aa1888810249198a9fd84a4c119f22d844",
    ),
    "flashdb_mutex_unlock": (
        0x00541126,
        0x0054116E,
        "866a665a4e069f7d88714cd00664a5dcb1102c1bd25f6489b34519a0554e5dd4",
    ),
    "flashdb_low_level_read": (
        0x00585A12,
        0x00585A32,
        "f1884d1237841c070c072523606e977d6e9f91ffe3d76cb13783907442ef761d",
    ),
    "flashdb_low_level_erase": (
        0x00585A32,
        0x00585A52,
        "49ac3926ed086029df22bc5a5ddc0e22b692cffe4e2696ac04eab7b2bed1a603",
    ),
    "flashdb_low_level_write": (
        0x00585A52,
        0x00585A72,
        "5385e4cb1f6df57608c8245cfecfc81352837682f3fba0a3fcb003610b687146",
    ),
}
KVDB_INIT_CACHE_LOOP_RUN = 0x005454AC
KVDB_INIT_CACHE_LOOP = bytes.fromhex(
    "1821002201fb00f32b4483f8a8225ff0ff3201fb00f32b44c3f8bc22"
    "01fb00f12944c1f8ac22401c4028e9d3002006e05ff0ff3105ebc002"
    "c2f8ac10401c4028f6d3"
)
KV_HEADER_SIZE = 0x18
KV_CACHE_TABLE_SIZE = 64
SECTOR_CACHE_TABLE_SIZE = 64
DB_OBJECT_BASE = 0x2005DFFC
DB_OBJECT_STRIDE = 0x8AC
DB_OBJECT_COUNT = 2

# The only statically recovered fdb_kvdb_control callers set lock/unlock.
# Sector size is not overridden, so _fdb_init_ex takes fal_flash_dev.blk_size.
KVDB_CONTROL_ENTRY = 0x00545320
KVDB_CONTROL_CALLS = {
    0x004D9744: 2,
    0x004D9752: 3,
    0x005107C2: 2,
    0x005107D0: 3,
}

DB_BINDING_LITERAL_POINTERS = (
    {
        "index": 0,
        "database_literal_pool": 0x004D9AD4,
        "database_string": 0x0078E594,
        "database_name": "sysenv",
        "partition_literal_pool": 0x004D9AB8,
        "partition_string": 0x0078E58C,
        "partition_name": "kvdb",
    },
    {
        "index": 1,
        "database_literal_pool": 0x005109D0,
        "database_string": 0x0078E60C,
        "database_name": "factory",
        "partition_literal_pool": 0x005109D4,
        "partition_string": 0x0078E614,
        "partition_name": "NVdb",
    },
)
DB0_CALL_WINDOW = (
    0x004D9756,
    bytes.fromhex(
        "dff87c53dff85c63340006a8fff715ff002067f063fd0021009106ab22002900"
        "6bf042fe0500"
    ),
)
DB1_CALL_WINDOW = (
    0x005107D4,
    bytes.fromhex(
        "7e4e7f4c250005a8fff71aff012030f026fd0021009105ab2a00310034f005fe"
        "05002800"
    ),
)

# IAR initialized-data record already authenticated independently by the G2
# MSPI audit.  Its decoded range contains both default-KV node arrays and all
# but one of their value buffers.  Keeping the decoder here makes this audit
# fail closed and standalone.
IAR_SCATTER_RECORD = 0x0075D3F0
IAR_SCATTER_HANDLER = 0x0043A11F
IAR_SCATTER_STREAM = 0x0079189E
IAR_SCATTER_ENCODED_FIELD = 0x54E0
IAR_SCATTER_DESTINATION = 0x20000000
IAR_SCATTER_OUTPUT_SIZE = 17752
IAR_SCATTER_OUTPUT_SHA256 = "df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743"
STARTUP_ZERO_GATE = (0x005E4228, 0x005E4232)
STARTUP_ZERO_RECORD = (0x0075D3C8, 0x0075D3E0)
STARTUP_ZERO_HANDLER = (0x005FA01E, 0x005FA056)
STARTUP_ZERO_RANGE = (0x20004558, 0x20075048)
BOOT_COUNT_ADDRESS = 0x20074988
KV_MIGRATION_TABLE = (0x00746D20, 0x00746D4C)
KV_MIGRATION_TARGETS = (
    0x004AECB8, 0x00492508, 0x00492422, 0x004922F8, 0x005D9B82,
    0x004AEB34, 0x0049B028, 0x004B03F4, 0x0058562C, 0x0049AEA4,
    0x0049AD20,
)

DEFAULT_KV_TABLES = (
    {
        "database": "sysenv",
        "address": 0x2000372C,
        "count": 12,
        "nodes": (
            ("kvString", 0x2000371C, 9, "6b76537472696e6700"),
            ("kvMagic", 0x20003728, 4, "2000005a"),
            ("kvbooCount", 0x20074988, 4, None),
            ("kvTime", 0x2000380C, 12, "010000002b2d376820000000"),
            ("kvTimeFormat", 0x20003818, 12, "010000000000000000000000"),
            ("kvTemperatureUnit", 0x200037FC, 12, "010000000000000000000000"),
            ("kvUniversalSetting", 0x20003824, 20, "030000000100000000000000ffffffffffff0000"),
            ("kvSetting", 0x200037E0, 28, "0164010000000000060101001e000000000000000000000000000000"),
            ("kvOnboardingConfig", 0x20000040, 1, "00"),
            ("kvRing", 0x200037C8, 24, "01ffffffffffff4556454e2052315f464646464646000000"),
            ("kvTerminalMode", 0x20003808, 4, "01000000"),
            ("kvAlsScale", 0x200037BC, 12, "010000000004000000000000"),
        ),
    },
    {
        "database": "factory",
        "address": 0x20003868,
        "count": 9,
        "nodes": (
            ("nvString", 0x20003858, 9, "6e76537472696e6700"),
            ("nvMagic", 0x20003864, 4, "22005555"),
            ("nvProdMode", 0x200038F0, 4, "01000000"),
            ("nvSysDt", 0x20003994, 172, "sha256:f2b3d283ef574404c0d9c402a52a43cba58c0d415f23d7d6d8f38005aca7f05d"),
            ("nvAdvMagic", 0x200038D4, 4, "01200000"),
            ("nvMAC", 0x200038E4, 10, "01000000000000000000"),
            ("nvSCald", 0x200038F4, 92, "010000000000a03f0000a03f0000a03f0000a03f0000a03f0000a03f0000a03f0000a03f0000a03f0000a03f7929edff87d6120087d612007929edff0000a03fffffffffffffffffffffffffffffffffffffffffffffffff00000000"),
            ("nvSCaldAG", 0x20003950, 68, "010000000000000000000000000000000000000000000000000000004bab51bf99d5bbbefd12d93ecb48e53eff0c8a3d02805f3f4ad1b2be88d66e3f849eed3d00000000"),
            ("nvBuzzer", 0x200038D8, 12, "02000000a00f00001e000000"),
        ),
    },
)

FLASHDB_MUTEX_OBJECT = 0x20074944
FLASHDB_MUTEX_CALLBACKS = {"lock": 0x005410DB, "unlock": 0x00541127}
NORFLASH_DRIVER_CALLS = {0x00540EDA: 0x004709C8, 0x00540F32: 0x004708A8, 0x0054103C: 0x0047075C}
FLASHDB_MUTEX_CALLS = {0x00541094: 0x0044971C, 0x005410E4: 0x004497B6, 0x0054112C: 0x0044981C}
SET_DEFAULT_ENTRY = 0x005450A4
SET_DEFAULT_CALLERS = [0x004D990E, 0x0051093C, 0x005452CC]


def _load() -> bytes:
    data = MAIN.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != MAIN_SHA256:
        raise AuditError(f"main image SHA-256 drift: {got}")
    return data


def _slice(data: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or first >= last or last > len(data):
        raise AuditError(f"run span [0x{start:08x},0x{end:08x}) is outside the image")
    return data[first:last]


def _cstr(data: bytes, run: int, limit: int = 64) -> bytes:
    return _slice(data, run, run + limit).split(b"\x00", 1)[0]


def _u32(data: bytes, run: int) -> int:
    return struct.unpack("<I", _slice(data, run, run + 4))[0]


def _fixed_name(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("ascii")


def _decode_initialized_sram(data: bytes) -> bytes:
    record = _slice(data, IAR_SCATTER_RECORD, IAR_SCATTER_RECORD + 16)
    handler_delta, stream_delta, encoded_field, destination = struct.unpack(
        "<iiII", record
    )
    handler = (IAR_SCATTER_RECORD + handler_delta) & 0xFFFF_FFFF
    stream = (IAR_SCATTER_RECORD + 4 + stream_delta) & 0xFFFF_FFFF
    recovered = (handler, stream, encoded_field, destination)
    expected = (
        IAR_SCATTER_HANDLER,
        IAR_SCATTER_STREAM,
        IAR_SCATTER_ENCODED_FIELD,
        IAR_SCATTER_DESTINATION,
    )
    if recovered != expected:
        raise AuditError(f"IAR initialized-data record drift: {recovered!r}")

    source = _slice(data, stream, stream + (encoded_field >> 1))
    cursor = 0
    output = bytearray()
    while cursor < len(source):
        token = source[cursor]
        cursor += 1
        low = token & 3
        if low:
            literal_count = low - 1
        else:
            if cursor >= len(source):
                raise AuditError("truncated IAR literal count")
            literal_count = source[cursor] + 2
            cursor += 1
        match_count = token >> 4
        if match_count == 15:
            if cursor >= len(source):
                raise AuditError("truncated IAR match count")
            match_count = source[cursor] + 15
            cursor += 1
        literal_end = cursor + literal_count
        if literal_end > len(source):
            raise AuditError("truncated IAR literal run")
        output.extend(source[cursor:literal_end])
        cursor = literal_end
        if match_count:
            if cursor >= len(source):
                raise AuditError("truncated IAR match offset")
            offset = source[cursor]
            cursor += 1
            high = (token >> 2) & 3
            if high == 3:
                if cursor >= len(source):
                    raise AuditError("truncated IAR wide match offset")
                high = source[cursor]
                cursor += 1
            offset |= high << 8
            if offset == 0 or offset > len(output):
                raise AuditError(f"invalid IAR back-reference offset: {offset}")
            for _ in range(match_count + 2):
                output.append(output[-offset])
    decoded = bytes(output)
    if len(decoded) != IAR_SCATTER_OUTPUT_SIZE:
        raise AuditError(f"IAR initialized-data size drift: {len(decoded)}")
    if hashlib.sha256(decoded).hexdigest() != IAR_SCATTER_OUTPUT_SHA256:
        raise AuditError("IAR initialized-data SHA-256 drift")
    return decoded


def _sram_slice(sram: bytes, address: int, size: int) -> bytes:
    offset = address - IAR_SCATTER_DESTINATION
    if offset < 0 or offset + size > len(sram):
        raise AuditError(f"initialized SRAM span 0x{address:08x}+0x{size:x} unavailable")
    return sram[offset : offset + size]


def _decode_thumb_bl(address: int, encoded: bytes) -> int | None:
    if len(encoded) != 4:
        return None
    first, second = struct.unpack("<HH", encoded)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def _thumb_bl_calls_to(data: bytes, target: int) -> list[int]:
    calls: list[int] = []
    for offset in range(0, len(data) - 3, 2):
        run = LOAD_BASE + offset
        if _decode_thumb_bl(run, data[offset : offset + 4]) == target:
            calls.append(run)
    return calls


def audit(data: bytes) -> dict[str, Any]:
    findings: dict[str, Any] = {}

    for run, expected in {**IDENTITY_STRINGS, **NAME_STRINGS, **STOCK_INIT_MARKERS}.items():
        got = _cstr(data, run, max(len(expected) + 1, 16))
        if got != expected:
            raise AuditError(f"string at 0x{run:08x}: expected {expected!r}, got {got!r}")
    findings["version"] = "2.1.1"

    for tag in SUBSYSTEMS_PRESENT:
        if data.find(tag) < 0:
            raise AuditError(f"expected subsystem tag missing: {tag!r}")
    for tag in (*SUBSYSTEMS_ABSENT, *AUTO_UPDATE_MARKERS_ABSENT, *DEBUG_MARKERS_ABSENT):
        if data.find(tag) >= 0:
            raise AuditError(f"unexpected compiled feature marker present: {tag!r}")
    # Marker absence proves the linked/retained image has no live TSDB
    # subsystem.  It does not prove the original preprocessor macro was
    # undefined: a compiled TSDB translation unit could have been discarded.
    findings["retained_kvdb_only"] = True
    findings["feature_evidence"] = {
        "retained_tsdb_subsystem": False,
        "tsdb_macro_state": "not statically proven",
        "minimal_recovered_config_uses_tsdb": False,
    }

    for name, (start, end, expected_sha) in PINNED_BODIES.items():
        got = hashlib.sha256(_slice(data, start, end)).hexdigest()
        if got != expected_sha:
            raise AuditError(f"{name} body SHA-256 drift: {got}")
    if _slice(
        data,
        KVDB_INIT_CACHE_LOOP_RUN,
        KVDB_INIT_CACHE_LOOP_RUN + len(KVDB_INIT_CACHE_LOOP),
    ) != KVDB_INIT_CACHE_LOOP:
        raise AuditError("fdb_kvdb_init cache-loop encoding drift")
    if _u32(data, 0x005412C8) != DB_OBJECT_BASE:
        raise AuditError("FlashDB object-array base drift")

    for call, command in KVDB_CONTROL_CALLS.items():
        if _decode_thumb_bl(call, _slice(data, call, call + 4)) != KVDB_CONTROL_ENTRY:
            raise AuditError(f"fdb_kvdb_control call at 0x{call:08x} drift")
        if _slice(data, call - 2, call) != struct.pack("<H", 0x2100 | command):
            raise AuditError(f"control command at 0x{call - 2:08x} drift")
    if _thumb_bl_calls_to(data, KVDB_CONTROL_ENTRY) != list(KVDB_CONTROL_CALLS):
        raise AuditError("fdb_kvdb_control BL caller set drift")
    for run, expected in (DB0_CALL_WINDOW, DB1_CALL_WINDOW):
        if _slice(data, run, run + len(expected)) != expected:
            raise AuditError(f"database-init call window at 0x{run:08x} drift")

    sram = _decode_initialized_sram(data)
    gate = _slice(data, *STARTUP_ZERO_GATE)
    if (
        gate.hex() != "06480749086001207047"
        or hashlib.sha256(gate).hexdigest()
        != "bee8bcf07546d7e7b549b10cfe4fc3c6519a6a49dc357d32179df469f5a8e36c"
        or _decode_thumb_bl(0x005E4294, _slice(data, 0x005E4294, 0x005E4298))
        != STARTUP_ZERO_GATE[0]
        or _decode_thumb_bl(0x005E429C, _slice(data, 0x005E429C, 0x005E42A0))
        != 0x005E42B4
    ):
        raise AuditError("reset startup-zero gate drift")
    zero_record = _slice(data, *STARTUP_ZERO_RECORD)
    if hashlib.sha256(zero_record).hexdigest() != "2a52162870b1f1b036f1769e75dabcf475f17eb6c37c85ffcabcb9dcfd064e15":
        raise AuditError("startup zero record drift")
    handler_delta, zero_bytes, zero_start = struct.unpack_from("<iII", zero_record)
    zero_handler = (STARTUP_ZERO_RECORD[0] + handler_delta) & ~1
    if (
        (zero_handler, zero_start, zero_start + zero_bytes)
        != (STARTUP_ZERO_HANDLER[0], *STARTUP_ZERO_RANGE)
        or hashlib.sha256(_slice(data, *STARTUP_ZERO_HANDLER)).hexdigest()
        != "8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67"
        or not zero_start <= BOOT_COUNT_ADDRESS < BOOT_COUNT_ADDRESS + 4 <= zero_start + zero_bytes
    ):
        raise AuditError("startup zero handler/range drift")
    migration_table = _slice(data, *KV_MIGRATION_TABLE)
    migration_targets = tuple(value & ~1 for value in struct.unpack("<11I", migration_table))
    if (
        hashlib.sha256(migration_table).hexdigest()
        != "bd1d3336c4e37373945074a222e8bc34f71269373b0cf16ffe7fbd7bc779b112"
        or migration_targets != KV_MIGRATION_TARGETS
    ):
        raise AuditError("first-party KV migration table drift")
    default_tables: list[dict[str, Any]] = []
    for table in DEFAULT_KV_TABLES:
        nodes: list[dict[str, Any]] = []
        raw_table = _sram_slice(sram, table["address"], table["count"] * 12)
        for index, expected in enumerate(table["nodes"]):
            expected_key, expected_value, expected_len, expected_hex = expected
            key, value, value_len = struct.unpack_from("<III", raw_table, index * 12)
            got_key = _cstr(data, key, len(expected_key) + 1).decode("ascii")
            if (got_key, value, value_len) != (
                expected_key,
                expected_value,
                expected_len,
            ):
                raise AuditError(
                    f"{table['database']} default node {index} descriptor drift"
                )
            default_bytes = None
            value_provenance = "runtime RAM; initial/default bytes unresolved"
            if expected_hex is not None:
                got_bytes = _sram_slice(sram, value, value_len)
                if expected_hex.startswith("sha256:"):
                    matches = hashlib.sha256(got_bytes).hexdigest() == expected_hex[7:]
                else:
                    matches = got_bytes == bytes.fromhex(expected_hex)
                if not matches:
                    raise AuditError(
                        f"{table['database']} default node {index} value drift"
                    )
                default_bytes = got_bytes.hex()
                value_provenance = "authenticated IAR initialized SRAM"
            elif expected_key == "kvbooCount" and value == BOOT_COUNT_ADDRESS and value_len == 4:
                default_bytes = "00000000"
                value_provenance = (
                    "authenticated reset-called IAR zero scatter over "
                    "[0x20004558,0x20075048)"
                )
            nodes.append(
                {
                    "index": index,
                    "key": got_key,
                    "storage_kind": "explicit-length blob",
                    "value_address": value,
                    "value_len": value_len,
                    "default_hex": default_bytes,
                    "value_provenance": value_provenance,
                }
            )
        default_tables.append(
            {
                "database": table["database"],
                "address": table["address"],
                "node_size": 12,
                "count": table["count"],
                "nodes": nodes,
            }
        )

    for call, target in {**NORFLASH_DRIVER_CALLS, **FLASHDB_MUTEX_CALLS}.items():
        if _decode_thumb_bl(call, _slice(data, call, call + 4)) != target:
            raise AuditError(f"port BL target at 0x{call:08x} drift")
    if _u32(data, 0x0054129C) != FLASHDB_MUTEX_OBJECT:
        raise AuditError("FlashDB mutex object pointer drift")
    if _u32(data, 0x005412D8) != FLASHDB_MUTEX_CALLBACKS["lock"]:
        raise AuditError("FlashDB lock callback pointer drift")
    if _u32(data, 0x005412DC) != FLASHDB_MUTEX_CALLBACKS["unlock"]:
        raise AuditError("FlashDB unlock callback pointer drift")
    if _slice(data, 0x005410DC, 0x005410E0) != bytes.fromhex("5ff0ff31"):
        raise AuditError("FlashDB lock no-timeout argument drift")
    if _thumb_bl_calls_to(data, SET_DEFAULT_ENTRY) != SET_DEFAULT_CALLERS:
        raise AuditError("fdb_kv_set_default caller set drift")
    if _u32(data, 0x004D9AF4) != 0x5A000020 or _u32(data, 0x005109F0) != 0x55550022:
        raise AuditError("first-party database magic drift")

    database_bindings: list[dict[str, Any]] = []
    binding_literal_pointers: list[dict[str, Any]] = []
    for item in DB_BINDING_LITERAL_POINTERS:
        for role in ("database", "partition"):
            pool = item[f"{role}_literal_pool"]
            target = item[f"{role}_string"]
            expected_name = item[f"{role}_name"].encode("ascii")
            got_target = _u32(data, pool)
            if got_target != target:
                raise AuditError(
                    f"{role} literal pointer at 0x{pool:08x}: "
                    f"expected 0x{target:08x}, got 0x{got_target:08x}"
                )
            got_name = _cstr(data, got_target, len(expected_name) + 1)
            if got_name != expected_name:
                raise AuditError(
                    f"{role} literal target at 0x{target:08x}: "
                    f"expected {expected_name!r}, got {got_name!r}"
                )
            binding_literal_pointers.append(
                {
                    "index": item["index"],
                    "role": role,
                    "pool": pool,
                    "target": target,
                    "value": item[f"{role}_name"],
                }
            )
        database_bindings.append(
            {
                "index": item["index"],
                "database_name": item["database_name"],
                "partition_name": item["partition_name"],
            }
        )

    partitions: list[dict[str, Any]] = []
    for index, expected in enumerate(FAL_PARTITIONS):
        run = FAL_PARTITION_TABLE + index * FAL_PARTITION_RECORD_SIZE
        record = _slice(data, run, run + FAL_PARTITION_RECORD_SIZE)
        magic, raw_name, raw_flash, offset, length, reserved = struct.unpack(
            "<I24s24sIII", record
        )
        decoded = {
            "name": _fixed_name(raw_name),
            "flash_name": _fixed_name(raw_flash),
            "offset": offset,
            "length": length,
        }
        if magic != FAL_PARTITION_MAGIC or reserved != 0 or decoded != expected:
            raise AuditError(f"FAL partition record {index} drift: {decoded!r}")
        partitions.append(decoded)

    (
        raw_name,
        address,
        length,
        block_size,
        init,
        read,
        write,
        erase,
        write_granularity,
    ) = struct.unpack(
        "<24sIIIIIIII",
        _slice(data, FAL_DEVICE, FAL_DEVICE + FAL_DEVICE_RECORD_SIZE),
    )
    device = {
        "name": _fixed_name(raw_name),
        "address": address,
        "length": length,
        "block_size": block_size,
        "init": init,
        "read": read,
        "write": write,
        "erase": erase,
        "write_granularity_bits": write_granularity,
    }
    if device != FAL_DEVICE_EXPECTED:
        raise AuditError(f"FAL norflash device record drift: {device!r}")

    # Pin the read-wrapper bounds check against fal_partition.len at +0x38.
    window = _slice(data, FAL_READ_WRAPPER, FAL_READ_WRAPPER + 0x22)
    ldr_length = struct.pack(
        "<H", 0x6800 | (FAL_PARTITION_LENGTH_OFFSET // 4) << 6 | (4 << 3)
    )
    if ldr_length not in window:
        raise AuditError("FAL read wrapper missing partition[+0x38] length load")

    findings["fal_read_wrapper"] = f"0x{FAL_READ_WRAPPER:08x}"
    findings["fal_partition_offset_offset"] = FAL_PARTITION_OFFSET_OFFSET
    findings["fal_partition_length_offset"] = FAL_PARTITION_LENGTH_OFFSET
    findings["fal_device_callback_offsets"] = FAL_DEVICE_CALLBACK_OFFSETS
    findings["databases"] = [item["database_name"] for item in database_bindings]
    findings["database_bindings"] = database_bindings
    findings["binding_literal_pointers"] = binding_literal_pointers
    findings["partitions"] = partitions
    findings["fal_device"] = device
    findings["partition_table_anchor"] = "01PEkvdb"
    findings["stock_init_path"] = True
    findings["configuration"] = {
        "FDB_USING_KVDB": True,
        "FDB_USING_FAL_MODE": True,
        "FDB_USING_FILE_MODE": False,
        "FDB_WRITE_GRAN": 1,
        "sec_size": block_size,
        "FDB_KV_CACHE_TABLE_SIZE": KV_CACHE_TABLE_SIZE,
        "FDB_SECTOR_CACHE_TABLE_SIZE": SECTOR_CACHE_TABLE_SIZE,
        "FDB_KV_AUTO_UPDATE": False,
        "FDB_DEBUG_ENABLE": False,
        "compiler_short_enums": True,
    }
    findings["kv_header_size"] = KV_HEADER_SIZE
    findings["default_kv_tables"] = default_tables
    findings["database_callbacks"] = {
        "mutex_object": FLASHDB_MUTEX_OBJECT,
        "lock": FLASHDB_MUTEX_CALLBACKS["lock"],
        "unlock": FLASHDB_MUTEX_CALLBACKS["unlock"],
        "lock_wait": "forever",
        "per_node_callbacks": "none in FlashDB fdb_default_kv_node ABI",
    }
    findings["norflash_port"] = {
        "init": {"entry": 0x00540ED1, "return": 0},
        "read": {
            "entry": 0x00540ED5,
            "driver": 0x004709C8,
            "success": "requested byte count when driver returns 0",
            "failure": "0 when driver returns nonzero",
        },
        "write": {
            "entry": 0x00540F2D,
            "driver": 0x004708A8,
            "success": "requested byte count when driver returns 0",
            "failure": "0 when driver returns nonzero",
        },
        "erase": {
            "entry": 0x00540F85,
            "driver": 0x0047075C,
            "alignment": 0x1000,
            "size_policy": "round up to 4 KiB and erase one sector per call",
            "success": "4096 after all requested sectors",
            "failure": "0 for invalid alignment/size or driver failure",
        },
        "flashdb_error_mapping": (
            "unsafe stock seam: FlashDB 2.1.1 checks only negative FAL returns; "
            "the Even callbacks return 0 on device failure, so failures are not "
            "mapped to FDB_READ_ERR/FDB_WRITE_ERR/FDB_ERASE_ERR"
        ),
    }
    findings["first_party_policy"] = {
        "sysenv_magic": {"key": "kvMagic", "value": 0x5A000020},
        "factory_magic": {"key": "nvMagic", "value": 0x55550022},
        "missing_or_mismatched_magic": "call fdb_kv_set_default for that database",
        "migration": (
            "11 first-party per-record callbacks run after boot-count update; "
            "magic mismatch first performs wholesale default reset"
        ),
        "migration_targets": list(migration_targets),
        "boot_count_lifecycle": {
            "key": "kvbooCount",
            "value_address": BOOT_COUNT_ADDRESS,
            "startup_default": 0,
            "startup_zero_range": list(STARTUP_ZERO_RANGE),
            "runtime": "read persisted word, increment, write persisted word",
        },
        "set_default_callers": SET_DEFAULT_CALLERS,
        "stock_corruption_fallback": 0x005452CC,
    }
    findings["db_object_abi"] = {
        "base": DB_OBJECT_BASE,
        "count": DB_OBJECT_COUNT,
        "stride": DB_OBJECT_STRIDE,
        "fdb_db_offsets": {
            "name": 0x00,
            "type": 0x04,
            "storage_partition": 0x08,
            "sec_size": 0x0C,
            "max_size": 0x10,
            "oldest_addr": 0x14,
            "init_ok": 0x18,
            "file_mode": 0x19,
            "not_formatable": 0x1A,
            "lock": 0x1C,
            "unlock": 0x20,
            "user_data": 0x24,
        },
        "kv_cache_table": 0xA8,
        "sector_cache_table": 0x2A8,
        "user_data": 0x8A8,
    }
    findings["open_config"] = []
    findings["promotion_blockers"] = [
        "replace the Even zero-on-failure FAL callbacks with source-owned negative error mapping",
        "keep destructive magic/corruption reset policy unreachable in read-only builds",
        "validate the recovered on-disk format against a read-only golden capture",
    ]
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable findings")
    args = parser.parse_args(argv)
    findings = audit(_load())
    if args.json:
        print(json.dumps(findings, indent=2, sort_keys=True))
        return 0
    print("FlashDB 2.1.1 identity/configuration audit: OK")
    print(
        "version: 2.1.1 (retained KVDB/FAL path; no retained TSDB subsystem; "
        "TSDB macro state not statically proven)"
    )
    bindings = ", ".join(
        f"{item['database_name']}@{item['partition_name']}"
        for item in findings["database_bindings"]
    )
    print(f"database bindings: {bindings}")
    cfg = findings["configuration"]
    print(
        "configuration: "
        f"write-gran={cfg['FDB_WRITE_GRAN']} bit; sec-size=0x{cfg['sec_size']:x}; "
        f"KV/sector caches={cfg['FDB_KV_CACHE_TABLE_SIZE']}/"
        f"{cfg['FDB_SECTOR_CACHE_TABLE_SIZE']}"
    )
    print(
        f"FAL read wrapper {findings['fal_read_wrapper']}: partition "
        "offset/length +0x34/+0x38; device read/write/erase +0x28/+0x2c/+0x30"
    )
    print("requested compile-time configuration gaps: closed by static recovery")
    print("analysis mode: read-only; no device or flash operation performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
