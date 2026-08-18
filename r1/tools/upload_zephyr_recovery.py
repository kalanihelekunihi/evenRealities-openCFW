#!/usr/bin/env python3
"""Verify an OpenR1 bundle and upload its signed app through BLE recovery."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from verify_zephyr_bundle import verify_bundle


PROJECT = Path(__file__).resolve().parents[1]
SWIFT_SOURCE = PROJECT / "tools" / "upload_openr1_recovery.swift"


def validated_application(bundle: Path, allow_development_key: bool) -> tuple[bytes, dict]:
    members, _ = verify_bundle(bundle)
    manifest = json.loads(members["manifest.json"])
    trust = manifest.get("trust", {})
    if trust.get("development_key") is not False and not allow_development_key:
        raise ValueError(
            "refusing a development-key bundle; pass --allow-development-key only for a disposable test target")
    contract = manifest.get("deployment_contract", {})
    if contract.get("on_device_application_recovery_available") is not True or \
            contract.get("application_recovery_preserves_bootloader") is not True:
        raise ValueError("bundle does not declare the source-built BLE recovery contract")
    image = members.get("openr1-application.signed.bin")
    if not image:
        raise ValueError("bundle has no signed application BIN")
    return image, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--match", default="OPENR1-RECOVERY")
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--allow-development-key", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.timeout < 30:
        parser.error("--timeout must be at least 30 seconds")

    bundle = args.bundle.expanduser().resolve()
    image, manifest = validated_application(bundle, args.allow_development_key)
    public_digest = manifest["trust"]["public_key_sha256"]
    if args.dry_run:
        print(
            "openR1 recovery upload preflight verified: "
            f"{len(image)} signed bytes; owner public key SHA-256 {public_digest}; "
            "no Bluetooth write performed")
        return

    with tempfile.TemporaryDirectory(prefix="openr1-recovery-upload-") as directory:
        temporary = Path(directory)
        image_path = temporary / "openr1-application.signed.bin"
        uploader = temporary / "openr1-recovery-uploader"
        image_path.write_bytes(image)
        image_path.chmod(0o600)
        subprocess.run([
            "xcrun", "swiftc", "-warnings-as-errors",
            "-framework", "CoreBluetooth", "-framework", "Foundation",
            os.fspath(SWIFT_SOURCE), "-o", os.fspath(uploader),
        ], check=True)
        print(
            "openR1 recovery: verified bundle and owner trust anchor "
            f"{public_digest}")
        completed = subprocess.run([
            os.fspath(uploader), "--image", os.fspath(image_path),
            "--match", args.match, "--timeout", str(args.timeout),
        ])
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        print(f"openR1 recovery upload refused: {error}", file=sys.stderr)
        raise SystemExit(1)
