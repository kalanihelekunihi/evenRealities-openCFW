#!/usr/bin/env python3
"""Build owner-keyed R1 bootloader images and signed Nordic Secure DFU packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils

from manage_r1_owner_key import (
    KEYCHAIN_SERVICE,
    PRIVATE_NAME,
    RAW_PUBLIC_NAME,
    keychain_load,
)


SOURCE_SHA256 = "566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b"
IMAGE_SIZE = 0x6000
PUBLIC_KEY_OFFSET = 0x5868
PUBLIC_KEY_SIZE = 64
SIGNATURE_GATE_OFFSET = 0x3D98
SIGNATURE_GATE_ORIGINAL = bytes.fromhex("04d1")  # bne 0xfbda4
SIGNATURE_GATE_OPTIONAL = bytes.fromhex("00bf")  # nop
HW_VERSION = 52
SD_REQ = 0x0100
OWNER_BOOTLOADER_VERSION = 0x52510001
OPTIONAL_BOOTLOADER_VERSION = 0x52510002


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("protobuf varints must be non-negative")
    encoded = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        encoded.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(encoded)


def scalar(field: int, value: int) -> bytes:
    return varint((field << 3) | 0) + varint(value)


def blob(field: int, value: bytes) -> bytes:
    return varint((field << 3) | 2) + varint(len(value)) + value


def build_init_command(image: bytes, firmware_version: int) -> bytes:
    # This matches pc-nrfutil's proto2 field order and value policy for a
    # bootloader-only package. Firmware hash bytes are stored little-endian.
    firmware_hash = hashlib.sha256(image).digest()[::-1]
    hash_message = scalar(1, 3) + blob(2, firmware_hash)  # SHA256
    boot_validation = scalar(1, 1) + blob(2, b"")  # generated CRC
    return b"".join(
        (
            scalar(1, firmware_version),
            scalar(2, HW_VERSION),
            blob(3, varint(SD_REQ)),  # packed repeated sd_req
            scalar(4, 2),  # BOOTLOADER
            scalar(5, 0),
            scalar(6, len(image)),
            scalar(7, 0),
            blob(8, hash_message),
            scalar(9, 1),  # is_debug=true; signature is still mandatory
            blob(10, boot_validation),
        )
    )


def sign_init_command(
    init_command: bytes, private_key: ec.EllipticCurvePrivateKey
) -> tuple[bytes, bytes]:
    command = command_message(init_command)
    der_signature = private_key.sign(init_command, ec.ECDSA(hashes.SHA256()))
    r, s = utils.decode_dss_signature(der_signature)
    signature = r.to_bytes(32, "little") + s.to_bytes(32, "little")
    signed_command = blob(1, command) + scalar(2, 0) + blob(3, signature)
    packet = blob(2, signed_command)
    private_key.public_key().verify(
        utils.encode_dss_signature(
            int.from_bytes(signature[:32], "little"),
            int.from_bytes(signature[32:], "little"),
        ),
        init_command,
        ec.ECDSA(hashes.SHA256()),
    )
    return packet, init_command


def command_message(init_command: bytes) -> bytes:
    return scalar(1, 1) + blob(2, init_command)


def unsigned_init_packet(init_command: bytes) -> bytes:
    return blob(1, command_message(init_command))


def write_package(path: Path, image: bytes, init_packet: bytes) -> None:
    manifest = {
        "manifest": {
            "bootloader": {
                "bin_file": "bootloader.bin",
                "dat_file": "bootloader.dat",
            }
        }
    }
    fixed_time = (2026, 8, 10, 0, 0, 0)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in (
            ("bootloader.bin", image),
            ("bootloader.dat", init_packet),
            ("manifest.json", (json.dumps(manifest, indent=2) + "\n").encode()),
        ):
            info = zipfile.ZipInfo(name, fixed_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)


def assert_only_ranges_changed(
    source: bytes, image: bytes, allowed_ranges: tuple[range, ...]
) -> None:
    changed = {index for index, pair in enumerate(zip(source, image)) if pair[0] != pair[1]}
    allowed = {index for allowed_range in allowed_ranges for index in allowed_range}
    if not changed or not changed <= allowed:
        unexpected = sorted(changed - allowed)
        raise SystemExit(f"unexpected bootloader changes: {unexpected[:16]}")


def build(args: argparse.Namespace) -> dict[str, object]:
    source = args.source.read_bytes()
    if len(source) != IMAGE_SIZE or sha256(source) != SOURCE_SHA256:
        raise SystemExit("source is not the version-pinned live R1 bootloader")
    if source[SIGNATURE_GATE_OFFSET : SIGNATURE_GATE_OFFSET + 2] != SIGNATURE_GATE_ORIGINAL:
        raise SystemExit("live signature gate bytes changed")

    raw_public = args.key_directory.joinpath(RAW_PUBLIC_NAME).read_bytes()
    if len(raw_public) != PUBLIC_KEY_SIZE:
        raise SystemExit("owner raw public key must be exactly 64 bytes")
    passphrase = keychain_load().encode("ascii")
    loaded = serialization.load_pem_private_key(
        args.key_directory.joinpath(PRIVATE_NAME).read_bytes(),
        password=passphrase,
    )
    if not isinstance(loaded, ec.EllipticCurvePrivateKey) or not isinstance(
        loaded.curve, ec.SECP256R1
    ):
        raise SystemExit("owner private key is not P-256")
    numbers = loaded.public_key().public_numbers()
    derived_public = numbers.x.to_bytes(32, "little") + numbers.y.to_bytes(32, "little")
    if derived_public != raw_public:
        raise SystemExit("owner private and raw public keys do not match")

    owner_image = bytearray(source)
    owner_image[PUBLIC_KEY_OFFSET : PUBLIC_KEY_OFFSET + PUBLIC_KEY_SIZE] = raw_public
    optional_image = bytearray(owner_image)
    optional_image[
        SIGNATURE_GATE_OFFSET : SIGNATURE_GATE_OFFSET + 2
    ] = SIGNATURE_GATE_OPTIONAL
    owner_bytes = bytes(owner_image)
    optional_bytes = bytes(optional_image)
    assert_only_ranges_changed(
        source,
        owner_bytes,
        (range(PUBLIC_KEY_OFFSET, PUBLIC_KEY_OFFSET + PUBLIC_KEY_SIZE),),
    )
    assert_only_ranges_changed(
        source,
        optional_bytes,
        (
            range(PUBLIC_KEY_OFFSET, PUBLIC_KEY_OFFSET + PUBLIC_KEY_SIZE),
            range(SIGNATURE_GATE_OFFSET, SIGNATURE_GATE_OFFSET + 2),
        ),
    )
    if owner_bytes[:0x100] != source[:0x100] or optional_bytes[:0x100] != source[:0x100]:
        raise SystemExit("vector table changed")

    if args.output.exists() and any(args.output.iterdir()) and not args.force:
        raise SystemExit(f"refusing to overwrite non-empty output directory: {args.output}")
    if args.output.exists() and args.force:
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    variants = (
        (
            "owner-keyed",
            owner_bytes,
            OWNER_BOOTLOADER_VERSION,
            True,
        ),
        (
            "owner-keyed-signing-optional",
            optional_bytes,
            OPTIONAL_BOOTLOADER_VERSION,
            False,
        ),
    )
    manifest_variants: dict[str, object] = {}
    for name, image, version, signature_enforced in variants:
        init_command = build_init_command(image, version)
        init_packet, init_command = sign_init_command(init_command, loaded)
        bin_path = args.output / f"r1-bootloader-{name}.bin"
        dat_path = args.output / f"r1-bootloader-{name}.dat"
        zip_path = args.output / f"r1-bootloader-{name}.zip"
        bin_path.write_bytes(image)
        dat_path.write_bytes(init_packet)
        write_package(zip_path, image, init_packet)
        manifest_variants[name] = {
            "firmware_version": version,
            "signature_enforced": signature_enforced,
            "image": bin_path.name,
            "image_bytes": len(image),
            "image_sha256": sha256(image),
            "init_packet": dat_path.name,
            "init_packet_sha256": sha256(init_packet),
            "init_command_sha256": sha256(init_command),
            "package": zip_path.name,
            "package_sha256": sha256(zip_path.read_bytes()),
            "is_debug": True,
            "hardware_version": HW_VERSION,
            "softdevice_requirement": f"0x{SD_REQ:04x}",
        }
        if not signature_enforced:
            unsigned_packet = unsigned_init_packet(init_command)
            unsigned_path = args.output / "r1-bootloader-unsigned-command-test.dat"
            unsigned_path.write_bytes(unsigned_packet)
            manifest_variants[name]["unsigned_command_test"] = unsigned_path.name
            manifest_variants[name]["unsigned_command_test_sha256"] = sha256(
                unsigned_packet
            )

    manifest = {
        "schema": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_image": str(args.source),
        "source_sha256": SOURCE_SHA256,
        "owner_public_key_sha256": sha256(raw_public),
        "owner_public_key_hex": raw_public.hex(),
        "keychain_service": KEYCHAIN_SERVICE,
        "public_key_patch": {
            "image_offset": f"0x{PUBLIC_KEY_OFFSET:04x}",
            "bytes": PUBLIC_KEY_SIZE,
        },
        "signing_optional_patch": {
            "image_offset": f"0x{SIGNATURE_GATE_OFFSET:04x}",
            "address": f"0x{0xF8000 + SIGNATURE_GATE_OFFSET:08x}",
            "original": SIGNATURE_GATE_ORIGINAL.hex(),
            "replacement": SIGNATURE_GATE_OPTIONAL.hex(),
            "instruction": "bne -> nop",
        },
        "variants": manifest_variants,
    }
    args.output.joinpath("manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return manifest


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=repo_root / "firmware" / "analysis" / "r1-live-2026-08-10" / "r1-bootloader-live.bin",
    )
    parser.add_argument(
        "--key-directory",
        type=Path,
        default=repo_root / "config" / "r1-owner-signing",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=repo_root / "firmware" / "r1-owner-bootloader",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
