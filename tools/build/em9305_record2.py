#!/usr/bin/env python3
"""Finalize the source-linked EM9305 user-app header and split its records.

The 40-byte FHDR is emitted by C at 0x302000. GNU ARC emits the ten-byte
source-owned NVM entry at 0x302028, followed by six erased bytes. The stock
SDK fills firmware size and both CRC-32 fields after linking. This module does
the same for record 2 and leaves record 3 as the linked application image.
It does not supply the separate NVM bootloader records 0 and 1.
"""

from __future__ import annotations

import struct
import zlib


HEADER_BASE = 0x00302000
ENTRY = 0x00302028
APP_BASE = 0x00302400
HEADER_SIZE = 40
RECORD2_SIZE = 56
APP_OFFSET = APP_BASE - HEADER_BASE
NVM_BASE = 0x00300000
BOOT_HEADER_OFFSET = HEADER_BASE - NVM_BASE
BOOT_APP_OFFSET = APP_BASE - NVM_BASE


class Record2Error(ValueError):
    pass


def finalize_record2(record2: bytes, application: bytes) -> bytes:
    """Return a CRC-complete 56-byte record from C-built fields and code."""
    if len(record2) != RECORD2_SIZE or not application:
        raise Record2Error("record 2 must be 56 bytes and application nonempty")
    if record2[:8] != b"FHDR\x00\x28\x03\x00":
        raise Record2Error("unexpected EM9305 header version, size or section")
    if struct.unpack_from("<I", record2, 8)[0] != ENTRY:
        raise Record2Error("firmware start is not the NVM entry")
    if struct.unpack_from("<I", record2, 30)[0] != ENTRY:
        raise Record2Error("execution address is not the NVM entry")
    if (struct.unpack_from("<I", record2, 20)[0] != 0xFFFFFFFF or
            struct.unpack_from("<I", record2, 24)[0] != 0 or
            struct.unpack_from("<H", record2, 28)[0] != 0 or
            record2[38:40] != b"\0\0"):
        raise Record2Error("unsupported EM9305 header options or padding")
    if record2[50:] != b"\xff" * 6:
        raise Record2Error("NVM entry is not ten bytes followed by erased padding")
    if record2[40:46] != bytes.fromhex("db44800078f9"):
        raise Record2Error("NVM entry does not set the stock stack top")

    result = bytearray(record2)
    firmware_size = APP_BASE + len(application) - ENTRY
    if APP_BASE + len(application) > 0x00380000:
        raise Record2Error("application exceeds EM9305 main NVM")
    struct.pack_into("<I", result, 12, firmware_size)
    firmware = (bytes(result[HEADER_SIZE:]) +
                b"\xff" * (APP_BASE - (HEADER_BASE + RECORD2_SIZE)) +
                application)
    if len(firmware) != firmware_size:
        raise Record2Error("firmware span is not contiguous")
    struct.pack_into("<I", result, 16, zlib.crc32(firmware))
    struct.pack_into("<I", result, 34, zlib.crc32(result[:34]))
    return bytes(result)


def split_flat_image(flat: bytes) -> tuple[bytes, bytes]:
    """Split GNU objcopy output at the known app VMA and finalize record 2."""
    if len(flat) <= APP_OFFSET:
        raise Record2Error("source ELF has no application at 0x302400")
    if any(byte not in (0, 0xFF) for byte in flat[RECORD2_SIZE:APP_OFFSET]):
        raise Record2Error("unexpected linked content in the sparse NVM gap")
    app = flat[APP_OFFSET:]
    return finalize_record2(flat[:RECORD2_SIZE], app), app


def split_bootloader_image(flat: bytes, bootloader: bytes) -> tuple[bytes, bytes, bytes]:
    """Split a source-linked 0x300000 image into boot, header, and app records."""
    if not bootloader or len(bootloader) > BOOT_HEADER_OFFSET:
        raise Record2Error("NVM bootloader is empty or overlaps the app header")
    if len(flat) <= BOOT_APP_OFFSET or flat[:len(bootloader)] != bootloader:
        raise Record2Error("linked bootloader does not match the flat image")
    if any(byte not in (0, 0xFF) for byte in flat[len(bootloader):BOOT_HEADER_OFFSET]):
        raise Record2Error("unexpected content between bootloader and app header")
    record2, application = split_flat_image(flat[BOOT_HEADER_OFFSET:])
    return bootloader, record2, application
