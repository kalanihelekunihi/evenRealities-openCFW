#!/usr/bin/env python3
"""Version-pinned static analysis of the R1 application-to-MBR boot bridge.

The script does not generate a modified image. It checks the standard S140
7.2.0 MBR and one or more R1 bootloader binaries for the exact instruction
shapes that make MBR commands reachable independently of Secure DFU policy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


FLASH_SIZE = 0x100000
APP_BASE = 0x27000
BOOTLOADER_BASE = 0xF8000
MBR_PARAM_PAGE = 0xFE000

NORMAL_APPLICATION_HANDOFF_HASHES = {
    "566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b",
    "e049131a92c203e1c1f0abb067653e046c6955157e522914556004402f29ac60",
}

MBR_SVC_HANDLER = bytes.fromhex(
    "1ef0040f0cbfeff30881eff30981886902380078182803d1"
)
MBR_DISPATCH_PREFIX = bytes.fromhex(
    "70b504460068c34d072876d2dfe800f033041929631e2500"
)
MBR_COPY_SD_CASE = bytes.fromhex(
    "d4e9026564682946304600f062f92a462146304600f031f9"
    "aa002146304600f057fb002800d0032070bd"
)
MBR_COPY_BL_CASE = bytes.fromhex(
    "fff7a2ff0028fad1d4e901034ff0805100eb830208694d6968438242"
)
MBR_VECTOR_CASE = bytes.fromhex(
    "fff772ff0028f7d1201d00f0f7f80028f2d160680028f0d1"
)
MBR_ADDRESS_CHECK = bytes.fromhex(
    "4ff080510a69496900684a43824201d81020704700207047"
)
MBR_IRQ_FORWARD_CASE = bytes.fromhex("60682860002070bd")
MBR_RESET_FORWARD_STORE = bytes.fromhex(
    "064a1060016881f3088840680047"
)

BOOTLOADER_MBR_COPY_WRAPPER = bytes.fromhex(
    "1fb58908002201ab009283e80700684618df04b010bd"
)
BOOTLOADER_ACTIVATION_SWITCH = bytes.fromhex(
    "012807d0a52808d0aa2809d0ac280ad0"
)
BOOTLOADER_ACL_HELPER = bytes.fromhex(
    "30b50a0502d1b0f57f2f01d9072030bd"
)
BOOTLOADER_APP_HANDOFF_ACL = bytes.fromhex(
    "10b504461448c0f57f2100f03df8"
)
BOOTLOADER_PROTOBUF_INIT_CALLBACK = bytes.fromhex(
    "0b4ac968914212d10a4ad0e90110d2e90134234301d00020"
    "08e011f8013ba0f101001b06f9d4c2e901100120907010bd"
)
BOOTLOADER_FW_HASH_FUNCTION_PREFIX = bytes.fromhex(
    "2de9f041aab005462020884629901e4617460124"
)
# movs r2,#32; mov r1,r5; ldr r0,<literal>; bl memcmp; cbz r0; movs r4,#0.
# The literal index and BL displacement differ between the normal and
# always-DFU links, so those bytes are intentionally masked.
BOOTLOADER_FW_HASH_COMPARE_PATTERN = bytes.fromhex(
    "2022294600480000000000b10024"
)
BOOTLOADER_FW_HASH_COMPARE_MASK = bytes.fromhex(
    "ffffffff00ff00000000ffffffff"
)
BOOTLOADER_POSTVALIDATE_HASH_GATE_PATTERN = bytes.fromhex(
    "2de9f04f81462f4817460e46c4680a4693b0012549462046"
    "00000000dff8a880aa4670b194f8550068b100f00101c0f34002"
    "4b462046cde9006700f049f808b3"
)
BOOTLOADER_POSTVALIDATE_HASH_GATE_MASK = bytes.fromhex(
    "ffffffffffffffffffffffffffffffffffffffffffffffff"
    "00000000ffffffffffffffffffffffffffffffffffffffff"
    "ffffffffffffffffffffffffffffffff"
)


def load_ihex(path: Path) -> bytes:
    memory: dict[int, int] = {}
    upper = 0
    for number, raw_line in enumerate(path.read_text().splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        if not line.startswith(":"):
            raise ValueError(f"line {number}: not Intel HEX")
        record = bytes.fromhex(line[1:])
        if len(record) < 5 or sum(record) & 0xFF:
            raise ValueError(f"line {number}: invalid Intel HEX checksum")
        count = record[0]
        address = int.from_bytes(record[1:3], "big")
        kind = record[3]
        data = record[4:-1]
        if count != len(data):
            raise ValueError(f"line {number}: invalid byte count")
        if kind == 0:
            absolute = upper + address
            memory.update((absolute + index, value) for index, value in enumerate(data))
        elif kind == 1:
            break
        elif kind == 4:
            if len(data) != 2:
                raise ValueError(f"line {number}: invalid extended address")
            upper = int.from_bytes(data, "big") << 16
    if not memory:
        raise ValueError("Intel HEX contains no data")
    image = bytearray(b"\xff" * (max(memory) + 1))
    for address, value in memory.items():
        image[address] = value
    return bytes(image)


def locate(image: bytes, pattern: bytes, base: int = 0) -> dict[str, Any]:
    offsets: list[int] = []
    start = 0
    while True:
        offset = image.find(pattern, start)
        if offset < 0:
            break
        offsets.append(base + offset)
        start = offset + 1
    return {
        "present": len(offsets) == 1,
        "matches": [hex(address) for address in offsets],
    }


def locate_masked(
    image: bytes, pattern: bytes, mask: bytes, base: int = 0
) -> dict[str, Any]:
    if len(pattern) != len(mask):
        raise ValueError("masked pattern and mask lengths differ")
    offsets = []
    for offset in range(0, len(image) - len(pattern) + 1):
        candidate = image[offset : offset + len(pattern)]
        if all((actual & keep) == (expected & keep)
               for actual, expected, keep in zip(candidate, pattern, mask)):
            offsets.append(base + offset)
    return {
        "present": len(offsets) == 1,
        "matches": [hex(address) for address in offsets],
    }


def bootloader_runtime_regions(image: bytes) -> dict[str, Any]:
    """Recover the two Arm C runtime copy/zero table entries.

    The first entry copies initialized data into SRAM. The second zeroes BSS,
    and its end is the reset vector's initial MSP. Requiring all of those
    relationships makes the table self-validating without debug symbols.
    """
    initial_msp = struct.unpack_from("<I", image, 0)[0]
    matches: list[dict[str, Any]] = []
    for offset in range(0, len(image) - 32, 4):
        data = struct.unpack_from("<IIII", image, offset)
        bss = struct.unpack_from("<IIII", image, offset + 16)
        if not (
            BOOTLOADER_BASE <= data[0] < BOOTLOADER_BASE + len(image)
            and 0x20000000 <= data[1] < initial_msp
            and data[2] > 0
            and data[2] % 4 == 0
            and BOOTLOADER_BASE <= data[3] < BOOTLOADER_BASE + len(image)
            and bss[1] == data[1] + data[2]
            and bss[2] > 0
            and bss[2] % 4 == 0
            and bss[1] + bss[2] == initial_msp
            and BOOTLOADER_BASE <= bss[3] < BOOTLOADER_BASE + len(image)
        ):
            continue
        matches.append(
            {
                "table_address": hex(BOOTLOADER_BASE + offset),
                "data_source": hex(data[0]),
                "data_start": hex(data[1]),
                "data_bytes": data[2],
                "data_copy_function": hex(data[3]),
                "bss_start": hex(bss[1]),
                "bss_bytes": bss[2],
                "bss_zero_function": hex(bss[3]),
                "initial_msp": hex(initial_msp),
                "upper_sram_not_initialized_by_c_runtime": [
                    hex(initial_msp),
                    hex(0x20040000),
                ],
            }
        )
    return {
        "present": len(matches) == 1,
        "matches": matches,
    }


def analyze_mbr(path: Path) -> dict[str, Any]:
    image = load_ihex(path)
    mbr = image[:0x1000]
    checks = {
        "svc_0x18_intercept": locate(mbr, MBR_SVC_HANDLER),
        "seven_command_dispatch": locate(mbr, MBR_DISPATCH_PREFIX),
        "copy_sd_case": locate(mbr, MBR_COPY_SD_CASE),
        "copy_bl_case": locate(mbr, MBR_COPY_BL_CASE),
        "vector_table_base_set_case": locate(mbr, MBR_VECTOR_CASE),
        "vector_address_flash_range_check": locate(mbr, MBR_ADDRESS_CHECK),
        "irq_forward_address_set_case": locate(mbr, MBR_IRQ_FORWARD_CASE),
        "reset_overwrites_live_irq_forward_base": locate(
            mbr, MBR_RESET_FORWARD_STORE
        ),
    }
    return {
        "source": str(path),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mbr_bytes": len(mbr),
        "mbr_sha256": hashlib.sha256(mbr).hexdigest(),
        "checks": checks,
        "all_checks_pass": all(check["present"] for check in checks.values()),
        "decompiled_policy": {
            "svc": "SVC 0x18 is handled by the MBR; other SVCs are forwarded",
            "copy_sd": "synchronous erase/copy/verify primitive with no source/destination range or signature check; protected-flash writes still encounter active hardware ACL",
            "copy_bl": "validates parameter page, source end, boot destination end; then persists command and resets; no caller/signature check",
            "vector_table_base_set": "validates parameter page and address < flash_size; nonzero address is persisted and reset; no caller/signature check",
            "irq_forward_address_set": "writes the supplied base to volatile RAM word 0x20000000 and returns; it is not retained across reset",
            "reset_forwarding": "reset stores the selected flash vector base to 0x20000000 immediately before loading MSP and branching",
            "invalid_vector_result": "address >= flash_size returns NRF_ERROR_INVALID_ADDR (0x10) before command persistence",
        },
    }


def analyze_bootloader(path: Path) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    checks = {
        "mbr_copy_bl_svc_wrapper": locate(
            image, BOOTLOADER_MBR_COPY_WRAPPER, BOOTLOADER_BASE
        ),
        "activation_bank_switch": locate(
            image, BOOTLOADER_ACTIVATION_SWITCH, BOOTLOADER_BASE
        ),
        "acl_region_helper": locate(image, BOOTLOADER_ACL_HELPER, BOOTLOADER_BASE),
        "protobuf_init_callback_unbounded_varint_scan": locate(
            image, BOOTLOADER_PROTOBUF_INIT_CALLBACK, BOOTLOADER_BASE
        ),
        "firmware_sha256_hash_function": locate(
            image, BOOTLOADER_FW_HASH_FUNCTION_PREFIX, BOOTLOADER_BASE
        ),
        "firmware_sha256_full_32_byte_compare": locate_masked(
            image,
            BOOTLOADER_FW_HASH_COMPARE_PATTERN,
            BOOTLOADER_FW_HASH_COMPARE_MASK,
            BOOTLOADER_BASE,
        ),
        "postvalidation_hash_gate_before_bank_dispatch": locate_masked(
            image,
            BOOTLOADER_POSTVALIDATE_HASH_GATE_PATTERN,
            BOOTLOADER_POSTVALIDATE_HASH_GATE_MASK,
            BOOTLOADER_BASE,
        ),
    }
    runtime = bootloader_runtime_regions(image)
    checks["c_runtime_data_copy_and_bss_zero"] = runtime
    app_handoff_acl = locate(
        image, BOOTLOADER_APP_HANDOFF_ACL, BOOTLOADER_BASE
    )
    if digest in NORMAL_APPLICATION_HANDOFF_HASHES:
        checks["application_handoff_acl"] = app_handoff_acl
    return {
        "source": str(path),
        "bytes": len(image),
        "sha256": digest,
        "checks": checks,
        "all_checks_pass": all(check["present"] for check in checks.values()),
        "application_handoff_reachable": digest in NORMAL_APPLICATION_HANDOFF_HASHES,
        "runtime_initialization": runtime,
        "application_acl_covers_mbr_parameter_page": (
            digest in NORMAL_APPLICATION_HANDOFF_HASHES
            and BOOTLOADER_BASE <= MBR_PARAM_PAGE < 0xFF000
            and checks["acl_region_helper"]["present"]
        ),
        "decompiled_policy": {
            "normal_dfu_activation": "bank codes 0x01/0xA5/0xAA/0xAC select app/SD/BL/SD+BL activation after signed DFU validation",
            "bootloader_update": "bl_activate passes staged source and image length to a wrapper that issues SVC 0x18 command 0",
            "application_handoff_acl": "ACL helper installs 4 KiB-aligned read/execute regions with permission 2; the retail handoff protects bootloader and installed MBR/SD/app",
            "retained_sram": "the C runtime recopies .data and zeroes all bootloader .bss before main; SRAM above the initial MSP may retain bytes but contains no bootloader globals or callbacks",
            "protobuf_callback": "the init-field decoding callback scans a protobuf varint until a byte clears bit 7 without checking bytes_left; this is an OOB read, not a write",
            "firmware_hash_gate": "postvalidation computes SHA-256 across the complete staged image and compares all 32 bytes before firmware-type dispatch or valid-bank state mutation",
        },
    }


def analyze_application(path: Path) -> dict[str, Any]:
    image = path.read_bytes()
    end = APP_BASE + len(image)
    protected_end = (end + 0xFFF) & ~0xFFF
    gap = BOOTLOADER_BASE - protected_end
    return {
        "source": str(path),
        "bytes": len(image),
        "sha256": hashlib.sha256(image).hexdigest(),
        "mapped_start": hex(APP_BASE),
        "mapped_end": hex(end),
        "acl_aligned_end": hex(protected_end),
        "writable_gap_start": hex(protected_end),
        "writable_gap_end": hex(BOOTLOADER_BASE),
        "writable_gap_bytes": gap,
        "fits_recovered_bootloader": gap >= 0x6000,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--softdevice-hex", required=True, type=Path)
    parser.add_argument("--bootloader", action="append", type=Path, default=[])
    parser.add_argument("--application", type=Path)
    args = parser.parse_args()

    report: dict[str, Any] = {
        "memory_map": {
            "flash_size": hex(FLASH_SIZE),
            "application_base": hex(APP_BASE),
            "bootloader_base": hex(BOOTLOADER_BASE),
            "mbr_parameter_page": hex(MBR_PARAM_PAGE),
        },
        "mbr": analyze_mbr(args.softdevice_hex),
        "bootloaders": [analyze_bootloader(path) for path in args.bootloader],
    }
    if args.application:
        report["application"] = analyze_application(args.application)

    mbr_pass = report["mbr"]["all_checks_pass"]
    boot_pass = bool(report["bootloaders"]) and all(
        item["all_checks_pass"] for item in report["bootloaders"]
    )
    gap_pass = report.get("application", {}).get("fits_recovered_bootloader", False)
    normal_profiles = [
        item for item in report["bootloaders"] if item["application_handoff_reachable"]
    ]
    acl_blocks_command_persistence = bool(normal_profiles) and all(
        item["application_acl_covers_mbr_parameter_page"] for item in normal_profiles
    )
    report["conclusion"] = {
        "application_ace_can_issue_mbr_svc": mbr_pass and boot_pass,
        "staged_bootloader_fits_in_gap": gap_pass,
        "mbr_command_persistence_page_is_acl_write_protected": acl_blocks_command_persistence,
        "copy_bl_bypasses_secure_dfu_admission": False,
        "vector_redirect_bypasses_bootloader_execution": False,
        "synchronous_copy_or_irq_forward_bypasses_acl_or_reset": False,
        "retained_irq_forward_base_survives_reset": False,
        "bootloader_globals_survive_reset": False,
        "qualification": (
            "COPY_BL and VECTOR_TABLE_BASE_SET are unauthenticated MBR commands, "
            "but both persist state through 0xFE000 before reset; the normal R1 "
            "bootloader write-protects 0xF8000...0xFEFFF before application ACE "
            "can run. They become viable only with pre-ACL/bootloader-context "
            "execution or an independent ACL bypass. COPY_SD has unchecked "
            "addresses but remains subject to ACL for protected flash; IRQ "
            "forwarding is volatile."
        ),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
