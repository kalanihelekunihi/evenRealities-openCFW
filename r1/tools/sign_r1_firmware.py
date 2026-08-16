#!/usr/bin/env python3
"""Create an owner-signed Nordic Secure DFU package for OpenR1."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils


KEYCHAIN_SERVICE = "com.sybilsight.r1-owner-signing"
PRIVATE_NAME = "r1-owner-private.key"
PUBLIC_NAME = "r1-owner-public.pem"
RAW_PUBLIC_NAME = "r1-owner-public-x-y-le.bin"
EXPECTED_PUBLIC_SHA256 = (
    "03a3d417e1b0071ae436798fa821f03d2d3458eb24959494516e2a1a7e040d0c"
)
DEFAULT_APPLICATION_VERSION = 3
DEFAULT_HARDWARE_VERSION = 52
DEFAULT_SD_REQ = 0x0100


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


def build_application_init_command(
    image: bytes,
    application_version: int,
    hardware_version: int,
    sd_requirements: Iterable[int],
    *,
    is_debug: bool,
) -> bytes:
    requirements = b"".join(varint(requirement) for requirement in sd_requirements)
    if not requirements:
        raise ValueError("at least one SoftDevice requirement is required")
    firmware_hash = hashlib.sha256(image).digest()[::-1]
    hash_message = scalar(1, 3) + blob(2, firmware_hash)  # SHA-256
    boot_validation = scalar(1, 1) + blob(2, b"")  # generated CRC
    return b"".join(
        (
            scalar(1, application_version),
            scalar(2, hardware_version),
            blob(3, requirements),
            scalar(4, 0),  # APPLICATION
            scalar(5, 0),
            scalar(6, 0),
            scalar(7, len(image)),
            blob(8, hash_message),
            scalar(9, int(is_debug)),
            blob(10, boot_validation),
        )
    )


def sign_init_command(
    init_command: bytes, private_key: ec.EllipticCurvePrivateKey
) -> bytes:
    command = scalar(1, 1) + blob(2, init_command)  # INIT command
    der_signature = private_key.sign(init_command, ec.ECDSA(hashes.SHA256()))
    r, s = utils.decode_dss_signature(der_signature)
    signature = r.to_bytes(32, "little") + s.to_bytes(32, "little")
    signed_command = blob(1, command) + scalar(2, 0) + blob(3, signature)
    return blob(2, signed_command)


def _read_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while offset < len(data) and shift <= 63:
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
    raise ValueError("invalid protobuf varint")


def _fields(data: bytes) -> list[tuple[int, int, int | bytes]]:
    parsed: list[tuple[int, int, int | bytes]] = []
    offset = 0
    while offset < len(data):
        tag, offset = _read_varint(data, offset)
        field, wire_type = tag >> 3, tag & 7
        if wire_type == 0:
            value, offset = _read_varint(data, offset)
        elif wire_type == 2:
            length, offset = _read_varint(data, offset)
            end = offset + length
            if end > len(data):
                raise ValueError("truncated protobuf field")
            value = data[offset:end]
            offset = end
        else:
            raise ValueError(f"unsupported protobuf wire type {wire_type}")
        parsed.append((field, wire_type, value))
    return parsed


def _one_blob(data: bytes, field: int) -> bytes:
    matches = [value for number, wire, value in _fields(data) if number == field and wire == 2]
    if len(matches) != 1 or not isinstance(matches[0], bytes):
        raise ValueError(f"expected one protobuf blob field {field}")
    return matches[0]


def _one_scalar(data: bytes, field: int) -> int:
    matches = [value for number, wire, value in _fields(data) if number == field and wire == 0]
    if len(matches) != 1 or not isinstance(matches[0], int):
        raise ValueError(f"expected one protobuf scalar field {field}")
    return matches[0]


def verify_init_packet(
    packet: bytes, public_key: ec.EllipticCurvePublicKey
) -> bytes:
    signed_command = _one_blob(packet, 2)
    command = _one_blob(signed_command, 1)
    if _one_scalar(signed_command, 2) != 0:
        raise ValueError("init packet is not ECDSA P-256 SHA-256")
    signature = _one_blob(signed_command, 3)
    if len(signature) != 64:
        raise ValueError("init packet signature is not 64 bytes")
    if _one_scalar(command, 1) != 1:
        raise ValueError("packet does not contain an INIT command")
    init_command = _one_blob(command, 2)
    der_signature = utils.encode_dss_signature(
        int.from_bytes(signature[:32], "little"),
        int.from_bytes(signature[32:], "little"),
    )
    try:
        public_key.verify(der_signature, init_command, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as error:
        raise ValueError("owner signature verification failed") from error
    return init_command


def raw_public_little_endian(public_key: ec.EllipticCurvePublicKey) -> bytes:
    numbers = public_key.public_numbers()
    return numbers.x.to_bytes(32, "little") + numbers.y.to_bytes(32, "little")


def load_owner_keypair(
    key_directory: Path,
    passphrase: bytes,
    expected_public_sha256: str,
) -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey, bytes]:
    private_path = key_directory / PRIVATE_NAME
    public_path = key_directory / PUBLIC_NAME
    if private_path.stat().st_mode & 0o777 != 0o600:
        raise ValueError(f"private key must be mode 0600: {private_path}")
    private = serialization.load_pem_private_key(private_path.read_bytes(), password=passphrase)
    public = serialization.load_pem_public_key(public_path.read_bytes())
    if not isinstance(private, ec.EllipticCurvePrivateKey) or not isinstance(
        private.curve, ec.SECP256R1
    ):
        raise ValueError("owner private key is not P-256")
    if not isinstance(public, ec.EllipticCurvePublicKey) or not isinstance(
        public.curve, ec.SECP256R1
    ):
        raise ValueError("owner public key is not P-256")
    if private.public_key().public_numbers() != public.public_numbers():
        raise ValueError("owner private/public key mismatch")
    raw_public = raw_public_little_endian(public)
    raw_path = key_directory / RAW_PUBLIC_NAME
    if raw_path.exists() and raw_path.read_bytes() != raw_public:
        raise ValueError("raw owner public key does not match the PEM key")
    fingerprint = sha256(raw_public)
    if fingerprint != expected_public_sha256.lower():
        raise ValueError(
            f"owner public-key SHA-256 is {fingerprint}, expected {expected_public_sha256}"
        )
    return private, public, raw_public


def keychain_passphrase(service: str, account: str) -> bytes:
    completed = subprocess.run(
        [
            "security",
            "find-generic-password",
            "-a",
            account,
            "-s",
            service,
            "-w",
        ],
        check=True,
        capture_output=True,
    )
    return completed.stdout.rstrip(b"\n")


def write_package(path: Path, image: bytes, packet: bytes) -> None:
    package_manifest = {
        "manifest": {
            "application": {
                "bin_file": "application.bin",
                "dat_file": "application.dat",
            }
        }
    }
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    if epoch:
        # ZIP timestamps cannot represent dates before 1980-01-01.
        stamp = datetime.fromtimestamp(max(epoch, 315_532_800), timezone.utc)
        fixed_time = (stamp.year, stamp.month, stamp.day, stamp.hour, stamp.minute, stamp.second)
    else:
        fixed_time = (2026, 8, 16, 0, 0, 0)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in (
            ("application.bin", image),
            ("application.dat", packet),
            ("manifest.json", (json.dumps(package_manifest, indent=2) + "\n").encode()),
        ):
            info = zipfile.ZipInfo(name, fixed_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)


def parse_int(value: str) -> int:
    return int(value, 0)


def build(args: argparse.Namespace) -> dict[str, object]:
    source = args.source.resolve()
    key_directory = args.key_directory.resolve()
    output = args.output.resolve()
    image = source.read_bytes()
    if not image:
        raise SystemExit(f"firmware image is empty: {source}")
    passphrase = keychain_passphrase(args.keychain_service, args.keychain_account)
    private, public, raw_public = load_owner_keypair(
        key_directory, passphrase, args.expected_public_sha256
    )

    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)

    init_command = build_application_init_command(
        image,
        args.application_version,
        args.hardware_version,
        args.sd_req,
        is_debug=not args.enforce_version,
    )
    packet = sign_init_command(init_command, private)
    if verify_init_packet(packet, public) != init_command:
        raise SystemExit("generated init packet did not round-trip")

    image_path = output / "openr1-application.bin"
    packet_path = output / "openr1-application.dat"
    package_path = output / "openr1-owner-signed.zip"
    image_path.write_bytes(image)
    packet_path.write_bytes(packet)
    write_package(package_path, image, packet)

    result = {
        "schema": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_image": str(source),
        "firmware_type": "application",
        "firmware_version": args.application_version,
        "hardware_version": args.hardware_version,
        "softdevice_requirements": [f"0x{value:04x}" for value in args.sd_req],
        "is_debug": not args.enforce_version,
        "boot_validation": "generated_crc",
        "owner_public_key_sha256": sha256(raw_public),
        "image": image_path.name,
        "image_bytes": len(image),
        "image_sha256": sha256(image),
        "init_packet": packet_path.name,
        "init_packet_sha256": sha256(packet),
        "init_command_sha256": sha256(init_command),
        "package": package_path.name,
        "package_sha256": sha256(package_path.read_bytes()),
        "ecdsa_p256_sha256_verified": True,
        "private_key_embedded": False,
    }
    (output / "manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    return result


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=repo_root / "platform/nrf52840/sdk/_build/openr1_nrf52840_s140.bin",
    )
    parser.add_argument(
        "--key-directory",
        type=Path,
        default=repo_root / "config/r1-owner-signing",
    )
    parser.add_argument("--output", type=Path, default=repo_root / "build/owner-dfu")
    parser.add_argument("--application-version", type=parse_int, default=DEFAULT_APPLICATION_VERSION)
    parser.add_argument("--hardware-version", type=parse_int, default=DEFAULT_HARDWARE_VERSION)
    parser.add_argument("--sd-req", type=parse_int, action="append", default=None)
    parser.add_argument("--enforce-version", action="store_true")
    parser.add_argument("--keychain-service", default=KEYCHAIN_SERVICE)
    parser.add_argument("--keychain-account", default=getpass.getuser())
    parser.add_argument("--expected-public-sha256", default=EXPECTED_PUBLIC_SHA256)
    args = parser.parse_args()
    if args.sd_req is None:
        args.sd_req = [DEFAULT_SD_REQ]
    print(json.dumps(build(args), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
