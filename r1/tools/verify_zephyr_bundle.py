#!/usr/bin/env python3
"""Verify an OpenR1 transparent full-flash bundle without a hardware target."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from cryptography.hazmat.primitives import serialization

from package_zephyr_bundle import (
    APPLICATION_LIMIT,
    BOOT_LIMIT,
    DATA_LIMIT,
    DATA_START,
    FLASH_LIMIT,
    merge_memory,
    memory_contains,
    HEALTH_STORAGE_PROVIDER_OBJECTS,
    GOODIX_PROVIDER_OBJECTS,
    MOTION_PROVIDER_OBJECTS,
    NFC_PROVIDER_OBJECTS,
    parse_ihex,
    require_range,
    RECONSTRUCTED_OBJECTS,
    SOURCE_LOCK,
    SETTINGS_START,
    verify_mcuboot_signature,
    write_ihex,
)


EXPECTED = {
    "manifest.json",
    "mcuboot-public.pem",
    "openr1-application.signed.bin",
    "openr1-application.signed.hex",
    "openr1-full.hex",
    "openr1-mcuboot.hex",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.bundle) as archive:
        names = set(archive.namelist())
        if names != EXPECTED:
            raise ValueError(f"bundle members differ: {sorted(names ^ EXPECTED)}")
        members = {name: archive.read(name) for name in names}
    manifest = json.loads(members["manifest.json"])
    if manifest["format"] != "openr1-transparent-full-flash":
        raise ValueError("unexpected bundle format")
    if manifest.get("source_lock") != SOURCE_LOCK:
        raise ValueError("bundle source lock differs")
    expected_layout = {
        "mcuboot": [0, BOOT_LIMIT],
        "application": [BOOT_LIMIT, APPLICATION_LIMIT],
        "bluetooth_settings_nvs": [SETTINGS_START, DATA_START],
        "openr1_data_preserved": [DATA_START, DATA_LIMIT],
        "migration_reserve": [DATA_LIMIT, FLASH_LIMIT],
    }
    if manifest.get("flash_layout") != expected_layout:
        raise ValueError("bundle manifest flash layout differs")
    for name, record in manifest["artifacts"].items():
        data = members[name]
        if record != {"bytes": len(data), "sha256": digest(data)}:
            raise ValueError(f"artifact digest mismatch: {name}")
    boot = parse_ihex(members["openr1-mcuboot.hex"])
    app = parse_ihex(members["openr1-application.signed.hex"])
    full = parse_ihex(members["openr1-full.hex"])
    require_range(boot, 0, BOOT_LIMIT, "MCUboot")
    require_range(app, BOOT_LIMIT, APPLICATION_LIMIT, "application")
    merged = merge_memory(boot, app)
    if full != merged or members["openr1-full.hex"] != write_ihex(merged):
        raise ValueError("full-flash image is not the canonical member union")
    app_start, app_limit = min(app), max(app) + 1
    if len(app) != app_limit - app_start:
        raise ValueError("signed application HEX is not contiguous")
    canonical_app_bin = bytes(app[address] for address in range(app_start, app_limit))
    if members["openr1-application.signed.bin"] != canonical_app_bin:
        raise ValueError("signed application BIN does not match its canonical HEX member")
    if manifest["trust"]["public_key_sha256"] != digest(members["mcuboot-public.pem"]):
        raise ValueError("public-key fingerprint mismatch")
    public_key = serialization.load_pem_public_key(members["mcuboot-public.pem"])
    public_der = public_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    if not memory_contains(boot, public_der):
        raise ValueError("MCUboot image does not contain the bundled trust anchor")
    verify_mcuboot_signature(
        members["openr1-application.signed.bin"], members["mcuboot-public.pem"]
    )
    source = manifest["openr1_source"]
    files = source["files"]
    if source["file_count"] != len(files) or not files:
        raise ValueError("openR1 source inventory count is invalid")
    if any(not isinstance(name, str) or not isinstance(value, str) or len(value) != 64
           for name, value in files.items()):
        raise ValueError("openR1 source inventory is malformed")
    serialized = b"".join(
        name.encode("utf-8") + b"\0" + bytes.fromhex(value)
        for name, value in sorted(files.items())
    )
    if source["aggregate_sha256"] != digest(serialized):
        raise ValueError("openR1 source inventory aggregate is invalid")
    retention = manifest["reconstructed_retention"]
    if set(retention) != set(RECONSTRUCTED_OBJECTS):
        raise ValueError("reconstructed retention inventory differs")
    if any(record.get("loadable_span_count", 0) < 1 or
           record.get("loadable_bytes", 0) < 1 for record in retention.values()):
        raise ValueError("reconstructed retention inventory has an empty object")
    motion_retention = manifest.get("motion_provider_retention", {})
    if set(motion_retention) != set(MOTION_PROVIDER_OBJECTS):
        raise ValueError("motion-provider retention inventory differs")
    if any(record.get("loadable_span_count", 0) < 1 or
           record.get("loadable_bytes", 0) < 1
           for record in motion_retention.values()):
        raise ValueError("motion-provider retention inventory has an empty object")
    nfc_retention = manifest.get("nfc_provider_retention", {})
    if set(nfc_retention) != set(NFC_PROVIDER_OBJECTS):
        raise ValueError("NFC-provider retention inventory differs")
    if any(record.get("loadable_span_count", 0) < 1 or
           record.get("loadable_bytes", 0) < 1
           for record in nfc_retention.values()):
        raise ValueError("NFC-provider retention inventory has an empty object")
    health_storage_retention = manifest.get(
        "health_storage_provider_retention", {})
    if set(health_storage_retention) != set(HEALTH_STORAGE_PROVIDER_OBJECTS):
        raise ValueError("health-storage-provider retention inventory differs")
    if any(record.get("loadable_span_count", 0) < 1 or
           record.get("loadable_bytes", 0) < 1
           for record in health_storage_retention.values()):
        raise ValueError(
            "health-storage-provider retention inventory has an empty object")
    goodix_retention = manifest.get("goodix_provider_retention", {})
    if set(goodix_retention) != set(GOODIX_PROVIDER_OBJECTS):
        raise ValueError("Goodix-provider retention inventory differs")
    if any(record.get("loadable_span_count", 0) < 1 or
           record.get("loadable_bytes", 0) < 1
           for record in goodix_retention.values()):
        raise ValueError("Goodix-provider retention inventory has an empty object")
    print(
        "openR1 Zephyr bundle verified: source-built MCUboot + signed application; "
        "no S140/retail-bootloader member"
    )


if __name__ == "__main__":
    main()
