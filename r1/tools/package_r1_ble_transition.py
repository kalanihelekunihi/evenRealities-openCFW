#!/usr/bin/env python3
"""Build and owner-sign the audited BLE transition into source OpenR1.

The two Nordic Secure DFU archives emitted here are installation media only.
The temporary transition bootloader is erased after it installs the source
MCUboot/recovery partition and the recovery loader accepts the signed OpenR1
application.  It is not part of the final transparent firmware runtime.
"""

from __future__ import annotations

import argparse
import binascii
import getpass
import hashlib
import json
import os
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from package_zephyr_bundle import parse_ihex
from sign_r1_firmware import (
    DEFAULT_APPLICATION_VERSION,
    DEFAULT_HARDWARE_VERSION,
    DEFAULT_SD_REQ,
    EXPECTED_PUBLIC_SHA256,
    FIRMWARE_TYPE_APPLICATION,
    FIRMWARE_TYPE_BOOTLOADER,
    KEYCHAIN_SERVICE,
    build_firmware_init_command,
    keychain_passphrase,
    load_owner_keypair,
    sha256,
    sign_init_command,
    verify_init_packet,
    write_firmware_package,
)


PROJECT = Path(__file__).resolve().parents[1]
BOOT_LIMIT = 0x27000
RETAIL_BOOT_START = 0xF8000
RETAIL_BOOT_LIMIT = 0xFE000
TRANSITION_BYTES_MAX = RETAIL_BOOT_LIMIT - RETAIL_BOOT_START
RECOVERED_LF_CLOCK_CONFIG = bytes.fromhex("00100201")


def extract_source_boot(bundle: Path) -> tuple[bytes, dict[str, object]]:
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
        if "openr1-mcuboot.hex" not in names or "manifest.json" not in names:
            raise ValueError("source bundle lacks MCUboot or manifest")
        source_manifest = json.loads(archive.read("manifest.json"))
        memory = parse_ihex(archive.read("openr1-mcuboot.hex"))
    if not memory or min(memory) < 0 or max(memory) >= BOOT_LIMIT:
        raise ValueError("MCUboot HEX escapes the 0x00000..<0x27000 boot partition")
    return bytes(memory.get(address, 0xFF) for address in range(BOOT_LIMIT)), source_manifest


def validate_transition(image: bytes, expected_public: bytes) -> None:
    if not image or len(image) > TRANSITION_BYTES_MAX:
        raise ValueError(
            f"transition bootloader is {len(image)} bytes; limit is {TRANSITION_BYTES_MAX}"
        )
    if len(image) < 8:
        raise ValueError("transition bootloader has no vector table")
    stack = int.from_bytes(image[0:4], "little")
    reset = int.from_bytes(image[4:8], "little")
    if not 0x20000000 <= stack <= 0x20040000:
        raise ValueError(f"transition initial stack is invalid: 0x{stack:08x}")
    if reset & 1 == 0 or not RETAIL_BOOT_START <= (reset & ~1) < RETAIL_BOOT_LIMIT:
        raise ValueError(f"transition reset vector is invalid: 0x{reset:08x}")
    if image.count(expected_public) != 1:
        raise ValueError("transition image does not contain exactly one owner trust anchor")
    if image.count(RECOVERED_LF_CLOCK_CONFIG) != 1:
        raise ValueError("transition image does not contain the exact recovered LFRC config")


def signed_packet(
    image: bytes,
    private,
    public,
    firmware_type: int,
    application_version: int,
) -> tuple[bytes, bytes]:
    command = build_firmware_init_command(
        image,
        application_version,
        DEFAULT_HARDWARE_VERSION,
        [DEFAULT_SD_REQ],
        is_debug=True,
        firmware_type=firmware_type,
    )
    packet = sign_init_command(command, private)
    if verify_init_packet(packet, public) != command:
        raise ValueError("owner-signed Nordic init packet did not round-trip")
    return command, packet


def linked_load_size(size_tool: Path, elf: Path) -> int:
    lines = subprocess.check_output(
        [os.fspath(size_tool), os.fspath(elf)], text=True
    ).splitlines()
    if len(lines) < 2:
        raise ValueError("toolchain size output is incomplete")
    fields = lines[-1].split()
    if len(fields) < 3:
        raise ValueError("toolchain size output has no text/data columns")
    text_bytes, data_bytes = (int(fields[0]), int(fields[1]))
    load_bytes = text_bytes + data_bytes
    if not 0 < load_bytes <= TRANSITION_BYTES_MAX:
        raise ValueError(f"transition linked load is invalid: {load_bytes} bytes")
    return load_bytes


def build(args: argparse.Namespace) -> dict[str, object]:
    bundle = args.source_bundle.expanduser().resolve()
    output = args.output.expanduser().resolve()
    project = args.transition_project.expanduser().resolve()
    toolchain_bin = args.toolchain_bin.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty output directory: {output}")
    subprocess.run(
        [os.fspath(args.python), os.fspath(PROJECT / "tools/verify_zephyr_bundle.py"), os.fspath(bundle)],
        check=True,
    )
    source_boot, source_manifest = extract_source_boot(bundle)
    source_crc = binascii.crc32(source_boot) & 0xFFFFFFFF
    make_variables = [
        "PROFILE=transition",
        f"TRANSITION_IMAGE_BYTES=0x{len(source_boot):x}",
        f"TRANSITION_IMAGE_CRC32=0x{source_crc:08x}",
        f"GNU_INSTALL_ROOT={toolchain_bin}/",
    ]
    # The pinned Nordic Makefile intentionally rejects clean alongside another
    # goal, even without -j. Keep the destructive clean and build explicit.
    subprocess.run(["make", *make_variables, "clean"], cwd=project, check=True)
    subprocess.run(["make", *make_variables, "default"], cwd=project, check=True)
    transition = (project / "build/transition/r1_bootloader.bin").read_bytes()
    transition_load_bytes = linked_load_size(
        toolchain_bin / "arm-none-eabi-size",
        project / "build/transition/r1_bootloader.out",
    )

    passphrase = keychain_passphrase(args.keychain_service, args.keychain_account)
    private, public, raw_public = load_owner_keypair(
        args.key_directory.expanduser().resolve(), passphrase,
        args.expected_public_sha256,
    )
    passphrase = b""
    validate_transition(transition, raw_public)
    transition_command, transition_packet = signed_packet(
        transition, private, public, FIRMWARE_TYPE_BOOTLOADER,
        args.application_version,
    )
    source_command, source_packet = signed_packet(
        source_boot, private, public, FIRMWARE_TYPE_APPLICATION,
        args.application_version,
    )

    output.mkdir(parents=True, exist_ok=True)
    transition_zip = output / "01-openr1-transition-bootloader.zip"
    source_zip = output / "02-openr1-source-boot-staging.zip"
    write_firmware_package(transition_zip, transition, transition_packet, "bootloader")
    write_firmware_package(source_zip, source_boot, source_packet, "application")
    artifacts = {
        transition_zip.name: transition_zip.read_bytes(),
        source_zip.name: source_zip.read_bytes(),
    }
    result: dict[str, object] = {
        "schema": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "target_device": args.target_device,
        "purpose": "destructive one-use BLE migration from retail Nordic DFU to transparent source OpenR1",
        "final_runtime_contains_temporary_installer": False,
        "source_bundle": os.fspath(bundle),
        "source_bundle_sha256": sha256(bundle.read_bytes()),
        "source_bundle_format": source_manifest.get("format"),
        "source_boot": {
            "range": [0, BOOT_LIMIT],
            "bytes": len(source_boot),
            "crc32": f"0x{source_crc:08x}",
            "sha256": sha256(source_boot),
            "nordic_init_command_sha256": sha256(source_command),
        },
        "transition_bootloader": {
            "installed_range": [RETAIL_BOOT_START, RETAIL_BOOT_LIMIT],
            "dfu_payload_bytes": len(transition),
            "linked_load_bytes": transition_load_bytes,
            "linked_load_headroom_bytes": TRANSITION_BYTES_MAX - transition_load_bytes,
            "sha256": sha256(transition),
            "nordic_init_command_sha256": sha256(transition_command),
            "recovered_lf_clock_config": {
                "bytes_le": "00100201",
                "source": "internal_rc",
                "calibration_interval": 16,
                "temperature_interval": 2,
                "accuracy_ppm": 500,
            },
            "entry_order": [
                "populate MBR bootloader addresses",
                "read-only DFU settings reload",
                "inspect exact staged source payload",
                "run normal Nordic bootloader initialization",
            ],
            "behavior": "verify exact staged size+CRC; copy pages 1..38; verify; write page zero last; verify all; reset",
        },
        "trust": {
            "owner_public_key_sha256": hashlib.sha256(raw_public).hexdigest(),
            "nordic_packets_ecdsa_p256_sha256_verified": True,
            "private_key_embedded": False,
        },
        "installation_sequence": [
            transition_zip.name,
            source_zip.name,
            "wait for OPENR1-RECOVERY advertising",
            bundle.name,
            "verify source application and erase checks over BLE",
        ],
        "destructive_boundary": {
            "sacrificial_device_only": True,
            "page_zero_written_last": True,
            "power_loss_before_page_zero": "transition retries from validated staged payload",
            "power_loss_during_page_zero": "device may require SWD recovery",
            "retail_bootloader_erased_by_source_recovery": True,
            "retail_settings_erased_by_source_recovery": True,
        },
        "artifacts": {
            name: {"bytes": len(data), "sha256": sha256(data)}
            for name, data in artifacts.items()
        },
    }
    (output / "manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--transition-project", type=Path,
        default=PROJECT / "research/bootloader-reconstruction/firmware-project",
    )
    parser.add_argument(
        "--toolchain-bin", type=Path,
        default=Path("/Users/kalani/vendor-cache/gcc-arm-none-eabi-9-2020-q2-update/bin"),
    )
    parser.add_argument("--key-directory", type=Path, default=PROJECT / "config/r1-owner-signing")
    parser.add_argument("--keychain-service", default=KEYCHAIN_SERVICE)
    parser.add_argument("--keychain-account", default=getpass.getuser())
    parser.add_argument("--expected-public-sha256", default=EXPECTED_PUBLIC_SHA256)
    parser.add_argument("--application-version", type=lambda value: int(value, 0), default=DEFAULT_APPLICATION_VERSION)
    parser.add_argument("--target-device", default="B56EE2")
    parser.add_argument("--python", type=Path, default=Path(os.sys.executable))
    args = parser.parse_args()
    print(json.dumps(build(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
