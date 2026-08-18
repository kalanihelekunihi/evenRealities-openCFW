#!/usr/bin/env python3
"""Assemble an auditable R1 recovery basis from ACE reads and pinned images.

The retail SoftDevice memory isolation prevents general application-context
reads below 0x27000. That extent is reconstructed from the exact, hash-pinned
Nordic S140 7.2.0 HEX identified by DFU firmware ID 0x0100 and the live 0x27000
application boundary. The live-programmed MBR words at 0xFF8...0xFFF are
source-proven from the byte-exact owner bootloader and corroborated by live
UICR NRFFW values. Every general byte at or above 0x27000 must come from a
bounded live page read. The complete live application and owner bootloader are
then byte-compared with their independently pinned archives before an output is
created. The evidence JSON keeps this mixed provenance explicit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zipfile
import zlib
from pathlib import Path

from package_zephyr_bundle import parse_ihex


FLASH_SIZE = 0x100000
PAGE_SIZE = 0x1000
SOFTDEVICE_LIMIT = 0x27000
APPLICATION_START = 0x27000
BOOTLOADER_START = 0xF8000
BOOTLOADER_LIMIT = 0xFE000
UICR_START = 0x10001000
UICR_SIZE = 0x308
MBR_CONFIG_START = 0xFF8
MBR_CONFIG_SIZE = 8
SETTINGS_BACKUP_START = 0xFE000
SETTINGS_PRIMARY_START = 0xFF000
SETTINGS_SOURCE_SHA256 = (
    "d3605f167072a19f2e98ac900e54cb7f703cc2f792eb2e2ad919f984d84b0486"
)

S140_HEX_SHA256 = (
    "c52b61a6ceeb58438dbef075abfc5f6812718dda78630b39e82a20829f09c125"
)
APPLICATION_ARCHIVE_SHA256 = (
    "662ca213e628f6bd82b8cd930bd63d6c1efe00b6f470fd6ed21e6367712bfdb7"
)
APPLICATION_IMAGE_SHA256 = (
    "41ea4fdcf1b2d1d3702c41669983b4ef0817ee4eb789f8eebc7dd6102609e274"
)
BOOTLOADER_ARCHIVE_SHA256 = (
    "4e64f55d18394627a89db3174fa1c1f824858857c4c344189073ee3e696ab49b"
)
BOOTLOADER_IMAGE_SHA256 = (
    "18851ceede792f316df328d935075464a0facfbfec4e64fb32f13812bba85dba"
)
OWNER_KEY_SHA256 = (
    "03a3d417e1b0071ae436798fa821f03d2d3458eb24959494516e2a1a7e040d0c"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned_member(
    archive_path: Path,
    archive_sha256: str,
    expected_members: set[str],
    member: str,
    member_sha256: str,
) -> bytes:
    archive_bytes = archive_path.read_bytes()
    if digest(archive_bytes) != archive_sha256:
        raise ValueError(f"archive failed its trust pin: {archive_path}")
    with zipfile.ZipFile(archive_path) as archive:
        if set(archive.namelist()) != expected_members:
            raise ValueError(f"archive members differ: {archive_path}")
        value = archive.read(member)
    if digest(value) != member_sha256:
        raise ValueError(f"archive member failed its trust pin: {member}")
    return value


def assemble(
    softdevice_hex: Path,
    application_archive: Path,
    bootloader_archive: Path,
    pages: Path,
    uicr_path: Path,
    settings_source_path: Path,
    prior_primary_prefix_path: Path,
    prior_settings_backup_path: Path,
    output: Path,
    evidence_path: Path,
) -> dict[str, object]:
    softdevice_bytes = softdevice_hex.read_bytes()
    if digest(softdevice_bytes) != S140_HEX_SHA256:
        raise ValueError("S140 7.2.0 HEX failed its trust pin")
    softdevice = parse_ihex(softdevice_bytes)
    if not softdevice or min(softdevice) != 0 or max(softdevice) >= SOFTDEVICE_LIMIT:
        raise ValueError("S140 HEX is outside the protected 0x00000..<0x27000 extent")

    application = pinned_member(
        application_archive,
        APPLICATION_ARCHIVE_SHA256,
        {"application.bin", "application.dat", "manifest.json"},
        "application.bin",
        APPLICATION_IMAGE_SHA256,
    )
    bootloader = pinned_member(
        bootloader_archive,
        BOOTLOADER_ARCHIVE_SHA256,
        {"bootloader.bin", "bootloader.dat", "manifest.json"},
        "bootloader.bin",
        BOOTLOADER_IMAGE_SHA256,
    )
    if len(bootloader) != BOOTLOADER_LIMIT - BOOTLOADER_START:
        raise ValueError("owner bootloader length differs")
    if APPLICATION_START + len(application) > BOOTLOADER_START:
        raise ValueError("official application overlaps the bootloader")

    flash = bytearray(b"\xff" * FLASH_SIZE)
    for address, value in softdevice.items():
        flash[address] = value

    page_records = []
    for address in range(APPLICATION_START, SETTINGS_PRIMARY_START, PAGE_SIZE):
        page_path = pages / f"{address:05x}.bin"
        if not page_path.is_file():
            raise ValueError(f"missing live page 0x{address:05x}")
        page = page_path.read_bytes()
        if len(page) != PAGE_SIZE:
            raise ValueError(f"live page 0x{address:05x} is not 4096 bytes")
        flash[address:address + PAGE_SIZE] = page
        page_records.append({
            "range": [address, address + PAGE_SIZE],
            "sha256": digest(page),
        })

    settings_source = settings_source_path.read_bytes()
    if digest(settings_source) != SETTINGS_SOURCE_SHA256:
        raise ValueError("Nordic DFU settings redundancy source failed its trust pin")
    prior_primary_prefix = prior_primary_prefix_path.read_bytes()
    prior_settings_backup = prior_settings_backup_path.read_bytes()
    if len(prior_settings_backup) != PAGE_SIZE or \
            not prior_primary_prefix or \
            len(prior_primary_prefix) >= PAGE_SIZE or \
            prior_primary_prefix != prior_settings_backup[:len(prior_primary_prefix)] or \
            any(value != 0xFF for value in
                prior_settings_backup[len(prior_primary_prefix):]):
        raise ValueError("prior primary/backup settings mirror proof differs")
    live_settings_backup = bytes(
        flash[SETTINGS_BACKUP_START:SETTINGS_PRIMARY_START])
    stored_crc = struct.unpack_from("<I", live_settings_backup, 0)[0]
    computed_crc = zlib.crc32(live_settings_backup[4:0x5C]) & 0xFFFFFFFF
    if stored_crc == 0xFFFFFFFF or stored_crc != computed_crc:
        raise ValueError("live backup DFU settings CRC differs")
    flash[SETTINGS_PRIMARY_START:FLASH_SIZE] = live_settings_backup

    live_application = bytes(
        flash[APPLICATION_START:APPLICATION_START + len(application)])
    if live_application != application:
        differing = next(
            index for index, pair in enumerate(zip(live_application, application))
            if pair[0] != pair[1])
        raise ValueError(
            f"live 2.2.8.0002 application differs at "
            f"0x{APPLICATION_START + differing:08x}")
    live_bootloader = bytes(flash[BOOTLOADER_START:BOOTLOADER_LIMIT])
    if live_bootloader != bootloader:
        differing = next(
            index for index, pair in enumerate(zip(live_bootloader, bootloader))
            if pair[0] != pair[1])
        raise ValueError(
            f"live owner bootloader differs at "
            f"0x{BOOTLOADER_START + differing:08x}")

    key = live_bootloader[0x5868:0x5868 + 64]
    gate = live_bootloader[0x3D98:0x3D9A]
    if digest(key) != OWNER_KEY_SHA256 or gate != b"\x00\xbf":
        raise ValueError("live bootloader is not the reviewed owner-optional image")

    uicr = uicr_path.read_bytes()
    if len(uicr) != UICR_SIZE:
        raise ValueError("UICR readback must be the complete 0x308-byte register extent")
    nrffw0, nrffw1 = struct.unpack_from("<II", uicr, 0x14)
    approtect = struct.unpack_from("<I", uicr, 0x208)[0]
    debugctrl = struct.unpack_from("<I", uicr, 0x210)[0]
    if (nrffw0, nrffw1) != (0xF8000, 0xFE000):
        raise ValueError("live UICR bootloader/settings addresses differ")
    mbr_config = struct.pack("<II", nrffw0, nrffw1)
    flash[MBR_CONFIG_START:MBR_CONFIG_START + MBR_CONFIG_SIZE] = mbr_config

    protected = bytes(flash[:SOFTDEVICE_LIMIT])
    assembled = bytes(flash)
    evidence = {
        "schema": 1,
        "format": "r1-ace-recovery-basis",
        "target": "EVEN R1_B56EE2",
        "application_version": "2.2.8.0002",
        "limitations": [
            "General bytes in 0x00000000..<0x00027000 are reconstructed from the exact pinned S140 7.2.0 HEX because retail SoftDevice memory isolation blocks application-context reads; programmed MBR words 0xFF8...0xFFF are source-proven from the byte-exact owner bootloader and the matching live UICR NRFFW values.",
            "The ACL-protected primary DFU settings page at 0xFF000 is reconstructed from the CRC-valid live 0xFE000 backup page under the pinned Nordic write-and-backup implementation and a prior same-device primary-prefix/backup identity observation.",
            "The reconstructed protected extent is recovery material with explicit provenance; it is not misreported as a direct device readback.",
        ],
        "provenance": [
            {
                "range": [0, MBR_CONFIG_START],
                "kind": "pinned-official-reconstruction",
                "artifact": str(softdevice_hex),
                "artifact_sha256": S140_HEX_SHA256,
                "identity_evidence": "DFU firmware ID 0x0100 and live application base 0x27000",
            },
            {
                "range": [MBR_CONFIG_START,
                          MBR_CONFIG_START + MBR_CONFIG_SIZE],
                "kind": "source-proven-mbr-config",
                "sha256": digest(mbr_config),
                "values": [nrffw0, nrffw1],
                "identity_evidence": "byte-exact owner bootloader nrf_bootloader_mbr_addrs_populate plus live UICR NRFFW[0:1]",
            },
            {
                "range": [MBR_CONFIG_START + MBR_CONFIG_SIZE,
                          SOFTDEVICE_LIMIT],
                "kind": "pinned-official-reconstruction",
                "artifact": str(softdevice_hex),
                "artifact_sha256": S140_HEX_SHA256,
                "identity_evidence": "DFU firmware ID 0x0100 and live application base 0x27000",
            },
            {
                "range": [APPLICATION_START, SETTINGS_PRIMARY_START],
                "kind": "live-ace-page-readback",
                "pages": len(page_records),
                "page_bytes": PAGE_SIZE,
            },
            {
                "range": [SETTINGS_PRIMARY_START, FLASH_SIZE],
                "kind": "source-proven-settings-mirror",
                "source": str(settings_source_path),
                "source_sha256": SETTINGS_SOURCE_SHA256,
                "live_backup_range": [SETTINGS_BACKUP_START,
                                      SETTINGS_PRIMARY_START],
                "live_backup_sha256": digest(live_settings_backup),
                "prior_primary_prefix_bytes": len(prior_primary_prefix),
                "prior_primary_prefix_sha256": digest(prior_primary_prefix),
                "prior_backup_sha256": digest(prior_settings_backup),
                "settings_crc32": stored_crc,
            },
        ],
        "protected_extent_sha256": digest(protected),
        "official_matches": {
            "application": {
                "range": [APPLICATION_START, APPLICATION_START + len(application)],
                "archive_sha256": APPLICATION_ARCHIVE_SHA256,
                "image_sha256": APPLICATION_IMAGE_SHA256,
                "byte_exact": True,
            },
            "bootloader": {
                "range": [BOOTLOADER_START, BOOTLOADER_LIMIT],
                "archive_sha256": BOOTLOADER_ARCHIVE_SHA256,
                "image_sha256": BOOTLOADER_IMAGE_SHA256,
                "byte_exact": True,
                "owner_key_sha256": digest(key),
                "signature_gate_hex": gate.hex(),
            },
        },
        "uicr": {
            "range": [UICR_START, UICR_START + UICR_SIZE],
            "bytes": len(uicr),
            "sha256": digest(uicr),
            "nrffw0": nrffw0,
            "nrffw1": nrffw1,
            "approtect": approtect,
            "debugctrl": debugctrl,
        },
        "live_pages": page_records,
        "output": {
            "artifact": str(output),
            "bytes": len(assembled),
            "sha256": digest(assembled),
        },
    }
    if output.exists() or evidence_path.exists():
        raise ValueError("refusing to overwrite an existing recovery artifact")
    output.write_bytes(assembled)
    evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--softdevice-hex", required=True, type=Path)
    parser.add_argument("--application-archive", required=True, type=Path)
    parser.add_argument("--bootloader-archive", required=True, type=Path)
    parser.add_argument("--pages", required=True, type=Path)
    parser.add_argument("--uicr", required=True, type=Path)
    parser.add_argument("--settings-source", required=True, type=Path)
    parser.add_argument("--prior-primary-prefix", required=True, type=Path)
    parser.add_argument("--prior-settings-backup", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    evidence = assemble(
        args.softdevice_hex.resolve(),
        args.application_archive.resolve(),
        args.bootloader_archive.resolve(),
        args.pages.resolve(),
        args.uicr.resolve(),
        args.settings_source.resolve(),
        args.prior_primary_prefix.resolve(),
        args.prior_settings_backup.resolve(),
        args.output.resolve(),
        args.evidence.resolve(),
    )
    print(json.dumps(evidence["output"], sort_keys=True))


if __name__ == "__main__":
    main()
