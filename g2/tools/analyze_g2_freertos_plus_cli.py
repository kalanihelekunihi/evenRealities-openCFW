#!/usr/bin/env python3
"""Fail-closed FreeRTOS-Plus-CLI source/configuration audit for G2.

The default mode authenticates and reads only the official 2.2.6.10 Apollo
image.  ``--upstream-checkout`` additionally authenticates the selected
official FreeRTOS Git objects without modifying that checkout.  There is no
device, debugger, serial, signing, or flash-writing path.

Run addresses use ``run = file_offset + 0x00437FE0``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
MAIN_SIZE = 3_523_396
MAIN_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x00437FE0


class AuditError(RuntimeError):
    """Raised when an authenticated binary or upstream invariant drifts."""


# The IAR initialized-data record is independently authenticated by the
# littlefs/FlashDB audits.  The CLI command descriptors live in that SRAM
# image, so this audit keeps a standalone decoder and its own pins.
IAR_SCATTER_RECORD = 0x0075D3F0
IAR_SCATTER_HANDLER = 0x0043A11F
IAR_SCATTER_STREAM = 0x0079189E
IAR_SCATTER_ENCODED_FIELD = 0x54E0
IAR_SCATTER_DESTINATION = 0x20000000
IAR_SCATTER_OUTPUT_SIZE = 17_752
IAR_SCATTER_OUTPUT_SHA256 = (
    "df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743"
)


PINNED_BODIES = {
    "FreeRTOS_CLIRegisterCommand": (
        0x005847AC,
        0x005847FE,
        "f38c77e0e672a21d1bb24fd6a26e604b1a782b5d633839aad036a96a69f7390b",
    ),
    "FreeRTOS_CLIProcessCommand": (
        0x005847FE,
        0x005848FC,
        "a276b358abd3ec722f4da8e17928590941d16f06ae92ad1375a1baf963e2893d",
    ),
    "FreeRTOS_CLIGetParameter": (
        0x005848FC,
        0x00584960,
        "35c6a4ce194bbea2a6044c3ab8f1108bb6c88806bafbf196fdb88c49a983a6f4",
    ),
    "prvHelpCommand": (
        0x00584960,
        0x0058498E,
        "7603491ef1e11c9a1163028ac35a5800f53402536eb99633a45fee477948a32c",
    ),
    "prvGetNumberOfParameters": (
        0x005849A8,
        0x005849D4,
        "e490fbface011c7219cd628b01e189998e661015dc22991ef18ed63f7faea508",
    ),
}

BLANK_INPUT_PATCH = (
    0x005848CA,
    0x005848F4,
    "4ed35ac83ff6802181aee553929f5eadff5e6b6c797601145d1c688c88eae7c1",
)

CONSOLE_WINDOWS = {
    "process_and_clear": (
        0x00541664,
        0x00541692,
        "e16fc653bfe0755f6951c4831e5d0f6b9d81d7ca93704658e2fc2e2d80bf9ac3",
    ),
    "input_limit": (
        0x00541704,
        0x0054171C,
        "93ed4e2a27efe979fcfe6ec2158443550f9bc1176be6fc7a814e693b78b97284",
    ),
    "maximum_parameter_request_loop": (
        0x00580AF4,
        0x00580B1C,
        "8a19c2866a484db48995aedef803a5d404ec12a03cdae35ac7f466b30a19318f",
    ),
    "registration_module_fanout": (
        0x00541604,
        0x0054165C,
        "2bf7b1cbed6deaa6d71877d00816f5aca3cb3f4d2c665e2b7e46951393236628",
    ),
}

STRING_PINS = {
    0x006E3568: b'Incorrect command parameter(s).  Enter "help" to view a list of available commands.\r\n\r\n',
    0x006ED568: b"Command not recognised.  Enter 'help' to view a list of available commands.\r\n\r\n",
    0x0078D62C: b"help",
    0x00734334: b"\r\nhelp:\r\n Lists all the registered commands\r\n\r\n",
    0x006DE434: b"D:\\01_workspace\\s200_ap510b_iar_git\\kernel\\FreeRTOS-Plus-CLI\\prvCommand\\prvCommand_filesystem.c",
}

REGISTER_ENTRY = 0x005847AC
PROCESS_ENTRY = 0x005847FE
GET_PARAMETER_ENTRY = 0x005848FC
MALLOC_ENTRY = 0x00456110
ASSERT_ENTRY = 0x005FA0A4
ENTER_CRITICAL_ENTRY = 0x004420D0
EXIT_CRITICAL_ENTRY = 0x004420E8

REGISTER_CALL_COUNT = 76
REGISTER_CALLS_SHA256 = "a62ca0d02bd54b7bb02c6fd1ac9c5483d7964fb9851d9455939e5ed02251cde1"
PROCESS_CALLS_SHA256 = "f70c431346e9fa060d8e0f0326bf4912eb9d8fd0413f6fa3f16735697dc5c300"
GET_PARAMETER_CALL_COUNT = 115
GET_PARAMETER_CALLS_SHA256 = "e43d8a1d82be6ce7313378790a1c74156806f3c0d1d6f1f9db1251d6a8ffee69"
VENDOR_DESCRIPTOR_AGGREGATE_SHA256 = (
    "268128313cc6da003e82e72b4341f5208a480196b3da1a1c0085b49a79d51788"
)

VENDOR_COMMAND_NAMES = (
    "reset", "clear", "enterProductMode", "exitProductMode", "SetGPIO",
    "ResetGPIO", "ProductControlCodec", "ChargerControl", "ReadDieId",
    "ReadChipId", "info", "AT^thread", "AT^dump", "ls", "cat", "rm",
    "cd", "mkdir", "touch", "pwd", "mv", "md5", "df", "free",
    "rename", "xip", "file2xip", "xip2file", "syncTest", "input",
    "dispStop", "dispExit", "dispBlockEn", "dispBlockCancel", "dispStart",
    "udata", "pdata", "dispReflash", "singleStart", "singleStop",
    "singleReflash", "sinput", "logcat", "logf", "AT^LOGTYPE", "imu",
    "codec", "audm", "AT^psn", "pdm", "AT^BleGetMac", "AT^BLECleanBond",
    "AT^BLES", "AT^BLEM", "AT^BLEMC", "AT^BLERingSend", "AT^EM9305",
    "AT^BLEADV", "AT^BLE_KEEPCONNECT", "xmodem", "alert",
    "dashboard_layout", "tp", "weardetect", "teleprompt", "translate",
    "conversate", "legalregulatory", "terminal", "set", "buzzer", "gpio",
    "box_force_out", "SetLanguage", "onboarding", "get",
)

HELP_DESCRIPTOR = 0x00785F90
REGISTERED_COMMANDS_NODE = 0x20000BE8
LAST_COMMAND_POINTER = 0x20000BF0
PROCESS_CURSOR = 0x200745E4
HELP_CURSOR = 0x200745E8

CONSOLE_OUTPUT_BUFFER = 0x20071B48
CONSOLE_INPUT_BUFFER = 0x20071BC8
CONSOLE_BUFFER_SIZE = 128
SAFE_NUL_TERMINATED_INPUT_MAX = 127
MAX_WANTED_PARAMETER = 11


UPSTREAM = {
    "repository": "https://github.com/FreeRTOS/FreeRTOS.git",
    "selected_component_version": "FreeRTOS+CLI V1.0.4",
    "historical_component_version": (
        "not unique: retained ABI/logic is compatible with the V1.0.1--V1.0.4 "
        "lineage after the canonical single-quote error-string change"
    ),
    "license": "MIT",
    "historical_semantic_floor": {
        "commit": "747a0e15faf033e9b80cfec0c31b68a29b304f92",
        "tree": "2b070fbc59c70147d091bde27631e924b7607244",
        "date": "2013-08-16T13:34:28Z",
        "advertised_version": "1.0.1",
        "discriminator": "introduces the retained single-quoted 'help' unknown-command text",
        "license_at_floor": "GPLv2 or commercial; not the selected reusable source",
    },
    # This exact official file pair is the selected source base.  It is the
    # 202112-era pair naturally accompanying a V10.5.1 kernel import.
    "selected": {
        "commit": "43defa566cc440251dbd6b48d1fcca27f88cfcdd",
        "tree": "1244875832c8ef8a39ee5b97a9dad657f7ea13ec",
        "date": "2021-12-23T10:16:27-08:00",
    },
    # The C/H Git blobs remain identical through this commit.  This interval
    # identifies the exact reusable source pair, not the unknowable vendor
    # checkout date.  The following commit restructures registration to add a
    # static-allocation API.
    "identical_file_pair_ceiling": {
        "commit": "1309654d6f5d1342b4a9d3d7ae0824e8fcaefaf2",
        "tree": "6d95fe580646a9f12b9cc2f37bd1e9c4d72fbad7",
        "date": "2023-04-11T11:52:56-07:00",
    },
    "next_source_topology_change": {
        "commit": "4727d6b3cc369310306ff24f61cafc1017853f82",
        "date": "2023-04-13T10:32:41-04:00",
        "change": "adds FreeRTOS_CLIRegisterCommandStatic and a shared registration helper",
    },
    "files": {
        "FreeRTOS-Plus/Source/FreeRTOS-Plus-CLI/FreeRTOS_CLI.c": {
            "git_blob": "52dbe0d4a616b094ba92a7285bb4f31124b90e51",
            "sha256": "1719b355951afaf3349a371ff633d9dd4867a3e3442b91552fd3550082ef93f4",
        },
        "FreeRTOS-Plus/Source/FreeRTOS-Plus-CLI/FreeRTOS_CLI.h": {
            "git_blob": "0f670ca8303f4732559d4a40a615f186a2d07985",
            "sha256": "c60d23b875d04429ba745b340d934b6c5eae89ce3be2b3a4aa92a034e6176890",
        },
        "FreeRTOS-Plus/Source/FreeRTOS-Plus-CLI/History.txt": {
            "git_blob": "8c62cf90bb1d1995ece6ba95f12862505ab27303",
            "sha256": "5a561aba760ef014190a64fcf7235af99e005bc63a6732fffc2cc00d8ef5a960",
        },
        "FreeRTOS-Plus/Source/FreeRTOS-Plus-CLI/LICENSE_INFORMATION.txt": {
            "git_blob": "6812e2716eee9232d8a247daa300584675a1a83a",
            "sha256": "6aa2663d0ffab6e9c830273b00d6f7b233955773057881c808bc368ca0079928",
        },
    },
    # No official revision through this first upstream behavioral change has
    # G2's blank-input suppression.  The cited commit instead adds explicit
    # output termination and is not a G2 match.
    "first_later_process_behavior_change": {
        "commit": "0e199e6d061ca0bfd065eda131f7d24d717d3c04",
        "date": "2026-07-15T22:05:29+05:30",
        "change": "NUL-terminates bounded CLI output copies",
    },
    "historical_semantic_ceiling": {
        "commit": "c73a397a418b1d5935dcc4233e651cf1773a57ca",
        "tree": "e45f9deab34f911f9013442776936cc783e0648a",
        "date": "2026-07-09T15:08:00-07:00",
        "qualification": (
            "official dynamic interpreter behavior still lacks both G2's blank-input "
            "patch and the following commit's explicit output terminators"
        ),
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or first >= last or last > len(data):
        raise AuditError(f"run span [0x{start:08x},0x{end:08x}) is outside image")
    return data[first:last]


def u32(data: bytes, address: int) -> int:
    return struct.unpack("<I", image_slice(data, address, address + 4))[0]


def flash_cstr(data: bytes, address: int, limit: int = 4096) -> bytes:
    raw = image_slice(data, address, min(address + limit, LOAD_BASE + len(data)))
    end = raw.find(b"\x00")
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return raw[:end]


def decode_thumb_bl(address: int, encoded: bytes) -> int | None:
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
        (sign << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def thumb_bl_calls_to(data: bytes, target: int) -> list[int]:
    return [
        LOAD_BASE + offset
        for offset in range(0, len(data) - 3, 2)
        if decode_thumb_bl(
            LOAD_BASE + offset, data[offset : offset + 4]
        ) == target
    ]


def decode_initialized_sram(data: bytes) -> bytes:
    record = image_slice(data, IAR_SCATTER_RECORD, IAR_SCATTER_RECORD + 16)
    handler_delta, stream_delta, encoded_field, destination = struct.unpack(
        "<iiII", record
    )
    recovered = (
        (IAR_SCATTER_RECORD + handler_delta) & 0xFFFF_FFFF,
        (IAR_SCATTER_RECORD + 4 + stream_delta) & 0xFFFF_FFFF,
        encoded_field,
        destination,
    )
    expected = (
        IAR_SCATTER_HANDLER,
        IAR_SCATTER_STREAM,
        IAR_SCATTER_ENCODED_FIELD,
        IAR_SCATTER_DESTINATION,
    )
    if recovered != expected:
        raise AuditError(f"IAR initialized-data record drift: {recovered!r}")

    source = image_slice(data, IAR_SCATTER_STREAM, IAR_SCATTER_STREAM + (encoded_field >> 1))
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
    if sha256(decoded) != IAR_SCATTER_OUTPUT_SHA256:
        raise AuditError("IAR initialized-data SHA-256 drift")
    return decoded


def sram_slice(sram: bytes, address: int, size: int) -> bytes:
    offset = address - IAR_SCATTER_DESTINATION
    if offset < 0 or offset + size > len(sram):
        raise AuditError(f"initialized SRAM span 0x{address:08x}+0x{size:x} unavailable")
    return sram[offset : offset + size]


def descriptor_literal_before_call(data: bytes, call: int) -> int:
    """Decode the exact 16-bit ``ldr r0,[pc,#imm]`` immediately before BL."""

    instruction_address = call - 2
    instruction = struct.unpack(
        "<H", image_slice(data, instruction_address, call)
    )[0]
    if instruction & 0xFF00 != 0x4800:
        raise AuditError(f"registration call at 0x{call:08x} lost its r0 literal load")
    pc = (instruction_address + 4) & ~3
    literal_address = pc + ((instruction & 0xFF) << 2)
    return u32(data, literal_address)


def audit_image(data: bytes) -> dict[str, Any]:
    if len(data) != MAIN_SIZE:
        raise AuditError(f"official image size mismatch: {len(data)} != {MAIN_SIZE}")
    digest = sha256(data)
    if digest != MAIN_SHA256:
        raise AuditError(f"official image SHA-256 mismatch: {digest}")

    for address, expected in STRING_PINS.items():
        got = flash_cstr(data, address, max(256, len(expected) + 1))
        if got != expected:
            raise AuditError(f"string at 0x{address:08x} drift: {got!r}")
    for name, (start, end, expected_hash) in PINNED_BODIES.items():
        got = sha256(image_slice(data, start, end))
        if got != expected_hash:
            raise AuditError(f"{name} body SHA-256 drift: {got}")
    for name, (start, end, expected_hash) in CONSOLE_WINDOWS.items():
        got = sha256(image_slice(data, start, end))
        if got != expected_hash:
            raise AuditError(f"{name} window SHA-256 drift: {got}")
    start, end, expected_hash = BLANK_INPUT_PATCH
    if sha256(image_slice(data, start, end)) != expected_hash:
        raise AuditError("blank-input patch drift")

    # Exact call targets in the dynamic registration implementation.
    register_calls = {
        0x005847B6: ASSERT_ENTRY,
        0x005847C6: MALLOC_ENTRY,
        0x005847D0: ASSERT_ENTRY,
        0x005847E2: ENTER_CRITICAL_ENTRY,
        0x005847F4: EXIT_CRITICAL_ENTRY,
    }
    for call, target in register_calls.items():
        got = decode_thumb_bl(call, image_slice(data, call, call + 4))
        if got != target:
            raise AuditError(f"registration call 0x{call:08x} -> {got!r}, expected 0x{target:08x}")

    if u32(data, 0x00584990) != LAST_COMMAND_POINTER:
        raise AuditError("last-command pointer literal drift")
    if u32(data, 0x00584994) != PROCESS_CURSOR:
        raise AuditError("process cursor literal drift")
    if u32(data, 0x00584998) != REGISTERED_COMMANDS_NODE:
        raise AuditError("registered-command head literal drift")
    if u32(data, 0x005849A4) != HELP_CURSOR:
        raise AuditError("help cursor literal drift")

    sram = decode_initialized_sram(data)
    help_raw = image_slice(data, HELP_DESCRIPTOR, HELP_DESCRIPTOR + 16)
    help_command, help_string, help_callback = struct.unpack_from("<III", help_raw)
    help_expected = struct.unpack_from("<b", help_raw, 12)[0]
    if (
        help_command,
        help_string,
        help_callback,
        help_expected,
    ) != (0x0078D62C, 0x00734334, 0x00584961, 0):
        raise AuditError("built-in help descriptor drift")
    if struct.unpack("<II", sram_slice(sram, REGISTERED_COMMANDS_NODE, 8)) != (
        HELP_DESCRIPTOR,
        0,
    ):
        raise AuditError("built-in registered-command node drift")
    if struct.unpack("<I", sram_slice(sram, LAST_COMMAND_POINTER, 4))[0] != REGISTERED_COMMANDS_NODE:
        raise AuditError("initialized last-command pointer drift")

    calls = thumb_bl_calls_to(data, REGISTER_ENTRY)
    call_hash = sha256(b"".join(struct.pack("<I", call) for call in calls))
    if len(calls) != REGISTER_CALL_COUNT or call_hash != REGISTER_CALLS_SHA256:
        raise AuditError("registration caller set drift")

    descriptors: list[dict[str, Any]] = []
    aggregate = bytearray()
    for call in calls:
        descriptor = descriptor_literal_before_call(data, call)
        raw = sram_slice(sram, descriptor, 16)
        command_ptr, help_ptr, callback = struct.unpack_from("<III", raw)
        expected_count = struct.unpack_from("<b", raw, 12)[0]
        command_bytes = flash_cstr(data, command_ptr)
        help_bytes = flash_cstr(data, help_ptr)
        if callback & 1 == 0:
            raise AuditError(f"descriptor at 0x{descriptor:08x} callback is not Thumb")
        aggregate.extend(struct.pack("<II", call, descriptor))
        aggregate.extend(raw)
        aggregate.extend(
            bytes.fromhex(sha256(command_bytes + b"\0" + help_bytes + b"\0"))
        )
        descriptors.append(
            {
                "registration_call": call,
                "address": descriptor,
                "command": command_bytes.decode("ascii"),
                "help_address": help_ptr,
                "callback": callback,
                "expected_parameters": expected_count,
            }
        )
    if sha256(bytes(aggregate)) != VENDOR_DESCRIPTOR_AGGREGATE_SHA256:
        raise AuditError("vendor descriptor aggregate drift")
    names = tuple(item["command"] for item in descriptors)
    if names != VENDOR_COMMAND_NAMES:
        raise AuditError("vendor command ordering/name census drift")

    process_calls = thumb_bl_calls_to(data, PROCESS_ENTRY)
    process_call_hash = sha256(b"".join(struct.pack("<I", call) for call in process_calls))
    if process_calls != [0x0054166E] or process_call_hash != PROCESS_CALLS_SHA256:
        raise AuditError("CLI process caller set drift")
    parameter_calls = thumb_bl_calls_to(data, GET_PARAMETER_ENTRY)
    parameter_call_hash = sha256(
        b"".join(struct.pack("<I", call) for call in parameter_calls)
    )
    if (
        len(parameter_calls) != GET_PARAMETER_CALL_COUNT
        or parameter_call_hash != GET_PARAMETER_CALLS_SHA256
    ):
        raise AuditError("CLI parameter-accessor caller set drift")

    # Literal table used by the only command-console task.
    if (
        u32(data, 0x00541774),
        u32(data, 0x00541778),
    ) != (CONSOLE_OUTPUT_BUFFER, CONSOLE_INPUT_BUFFER):
        raise AuditError("console buffer address literals drift")

    expected_distribution = {-1: 15, 0: 19, 1: 27, 2: 12, 3: 3}
    distribution = dict(sorted(Counter(item["expected_parameters"] for item in descriptors).items()))
    if distribution != expected_distribution:
        raise AuditError(f"descriptor parameter distribution drift: {distribution}")

    return {
        "status": "official MIT V1.0.4-compatible source base plus one proven Even patch",
        "exact_historical_upstream_commit": None,
        "exact_historical_component_version": None,
        "qualification": (
            "The retained core is not an unmodified upstream import: G2 suppresses "
            "the unknown-command response for CR-only and empty input. Use the pinned "
            "MIT source pair plus that explicit patch; do not decompile the stock core."
        ),
        "image": {"path": str(MAIN), "size": len(data), "sha256": digest},
        "upstream": UPSTREAM,
        "code": {
            name: {"range": [start, end], "size": end - start, "sha256": expected_hash}
            for name, (start, end, expected_hash) in PINNED_BODIES.items()
        },
        "local_patch": {
            "range": [BLANK_INPUT_PATCH[0], BLANK_INPUT_PATCH[1]],
            "sha256": BLANK_INPUT_PATCH[2],
            "behavior": "do not emit unknown-command text for exactly CR or empty input",
            "present_in_official_history": False,
        },
        "abi": {
            "pointer_bytes": 4,
            "BaseType_t_bytes": 4,
            "UBaseType_t_bytes": 4,
            "size_t_bytes": 4,
            "descriptor_size": 16,
            "descriptor_fields": {
                "pcCommand": 0,
                "pcHelpString": 4,
                "pxCommandInterpreter": 8,
                "cExpectedNumberOfParameters": 12,
            },
            "expected_parameter_type": "signed int8_t",
            "variable_parameter_sentinel": -1,
            "negative_expected_counts_bypass_validation": True,
            "callback_arguments": ["char *output", "uint32_t output_len", "const char *input"],
            "list_node_size": 8,
            "list_node_fields": {"descriptor": 0, "next": 4},
        },
        "buffers": {
            "effective_output": {"address": CONSOLE_OUTPUT_BUFFER, "bytes": CONSOLE_BUFFER_SIZE},
            "input": {
                "address": CONSOLE_INPUT_BUFFER,
                "bytes": CONSOLE_BUFFER_SIZE,
                "safe_nul_terminated_payload_max": SAFE_NUL_TERMINATED_INPUT_MAX,
                "stock_full_buffer_hazard": (
                    "the console accepts byte 128 without appending a terminator; "
                    "a 128-byte line can make the upstream strlen parser read past the array"
                ),
            },
            "configCOMMAND_INT_MAX_OUTPUT_SIZE": (
                "not recoverable: FreeRTOS_CLIGetOutputBuffer and its optional upstream "
                "array are not retained; the sole G2 caller independently passes 128"
            ),
            "configAPPLICATION_PROVIDES_cOutputBuffer": "not statically proven",
        },
        "parameters": {
            "descriptor_representable_fixed_range": [0, 127],
            "vendor_descriptor_range": [-1, 3],
            "vendor_distribution": {str(key): value for key, value in distribution.items()},
            "FreeRTOS_CLIGetParameter_internal_limit": None,
            "highest_parameter_index_requested_by_retained_handlers": MAX_WANTED_PARAMETER,
            "accessor_call_count": len(parameter_calls),
        },
        "allocation": {
            "observed_registration_api": "dynamic",
            "bytes_per_registered_command": 8,
            "vendor_dynamic_nodes": len(descriptors),
            "minimum_payload_bytes_allocated": 8 * len(descriptors),
            "allocator": MALLOC_ENTRY,
            "null_descriptor_and_allocation_assert": ASSERT_ENTRY,
            "critical_section": [ENTER_CRITICAL_ENTRY, EXIT_CRITICAL_ENTRY],
            "free_path": False,
            "static_registration_observed": False,
            "static_registration_body_identity": "not established",
            "configSUPPORT_STATIC_ALLOCATION": "not statically proven; dead stripping can erase an enabled unused API",
        },
        "state": {
            "registered_commands_node": REGISTERED_COMMANDS_NODE,
            "last_command_pointer": LAST_COMMAND_POINTER,
            "process_cursor": PROCESS_CURSOR,
            "help_cursor": HELP_CURSOR,
            "non_reentrant": True,
        },
        "vendor_glue": {
            "source_path_marker": STRING_PINS[0x006DE434].decode("ascii"),
            "registered_descriptor_count": len(descriptors),
            "descriptor_aggregate_sha256": VENDOR_DESCRIPTOR_AGGREGATE_SHA256,
            "commands": descriptors,
            "separation": "descriptors and handlers are G2 vendor glue; interpreter/list/parser are the upstream-derived core",
        },
    }


def _git(checkout: Path, *arguments: str) -> bytes:
    try:
        return subprocess.run(
            ["git", "-C", str(checkout), *arguments],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AuditError(f"upstream Git verification failed: {exc}") from exc


def verify_upstream_checkout(checkout: Path) -> dict[str, Any]:
    selected = UPSTREAM["selected"]
    ceiling = UPSTREAM["identical_file_pair_ceiling"]
    for label, revision in (
        ("historical semantic floor", UPSTREAM["historical_semantic_floor"]),
        ("selected", selected),
        ("identical-file ceiling", ceiling),
        ("historical semantic ceiling", UPSTREAM["historical_semantic_ceiling"]),
    ):
        commit = _git(checkout, "rev-parse", revision["commit"]).decode().strip()
        tree = _git(checkout, "rev-parse", f"{revision['commit']}^{{tree}}").decode().strip()
        if commit != revision["commit"] or tree != revision["tree"]:
            raise AuditError(f"upstream {label} commit/tree identity drift")
    verified: dict[str, dict[str, str]] = {}
    for path, expected in UPSTREAM["files"].items():
        spec = f"{selected['commit']}:{path}"
        blob = _git(checkout, "rev-parse", spec).decode().strip()
        content = _git(checkout, "show", spec)
        ceiling_blob = _git(checkout, "rev-parse", f"{ceiling['commit']}:{path}").decode().strip()
        if blob != expected["git_blob"] or ceiling_blob != blob:
            raise AuditError(f"upstream blob identity drift for {path}")
        digest = sha256(content)
        if digest != expected["sha256"]:
            raise AuditError(f"upstream SHA-256 drift for {path}: {digest}")
        verified[path] = {"git_blob": blob, "sha256": digest}

    cli_path = "FreeRTOS-Plus/Source/FreeRTOS-Plus-CLI/FreeRTOS_CLI.c"
    revisions = _git(checkout, "rev-list", "--all", "--", cli_path).decode().split()
    unique_cli_blobs: set[str] = set()
    blank_patch_markers = (
        b"strlen( pcCommandInput )",
        b"strlen(pcCommandInput)",
        b"pcCommandInput[ 0 ] == '\\r'",
        b"pcCommandInput[0] == '\\r'",
    )
    for revision in revisions:
        spec = f"{revision}:{cli_path}"
        try:
            blob = _git(checkout, "rev-parse", spec).decode().strip()
        except AuditError:
            # One historical repository snapshot removed the path.  It carries
            # no candidate source and therefore contributes no source blob.
            continue
        if blob in unique_cli_blobs:
            continue
        unique_cli_blobs.add(blob)
        content = _git(checkout, "show", spec)
        if any(marker in content for marker in blank_patch_markers):
            raise AuditError(
                f"official history gained a possible G2 blank-input patch in {blob}"
            )
    return {
        "repository": UPSTREAM["repository"],
        "selected_commit": selected["commit"],
        "ceiling_commit": ceiling["commit"],
        "files": verified,
        "history": {
            "revisions_examined": len(revisions),
            "unique_cli_blobs_examined": len(unique_cli_blobs),
            "g2_blank_input_patch_found": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--upstream-checkout",
        type=Path,
        help="existing official FreeRTOS Git checkout to authenticate read-only",
    )
    args = parser.parse_args()
    report = audit_image(MAIN.read_bytes())
    if args.upstream_checkout is not None:
        report["upstream_checkout_verification"] = verify_upstream_checkout(
            args.upstream_checkout.resolve()
        )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
