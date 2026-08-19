#!/usr/bin/env python3
"""Verify an OpenR1 post-install internal-flash readback offline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from package_zephyr_bundle import FLASH_LIMIT, parse_ihex, write_ihex
from prepare_zephyr_deployment import (
    BACKUP_PROVENANCE_ARTIFACT,
    EXPECTED_FLASH_ARTIFACT,
    UICR_BACKUP_ARTIFACT,
    UICR_LIMIT,
    UICR_RECOVERY_ARTIFACT,
    UICR_SIZE,
    UICR_START,
    build_deployment_plan,
    build_expected_internal_flash,
    validate_backup_provenance,
)
from verify_zephyr_bundle import verify_bundle


BACKUP_ARTIFACT = "openr1-internal-flash-backup.bin"
RECOVERY_ARTIFACT = "openr1-internal-flash-recovery.hex"
PLAN_ARTIFACT = "deployment-plan.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_deployment_package(
    bundle: Path, deployment: Path,
) -> tuple[dict[str, object], bytes, bytes]:
    """Verify the immutable install package before any target is touched."""
    if not deployment.is_dir():
        raise ValueError(f"deployment package is not a directory: {deployment}")
    members, _ = verify_bundle(bundle)
    plan_path = deployment / PLAN_ARTIFACT
    backup_path = deployment / BACKUP_ARTIFACT
    recovery_path = deployment / RECOVERY_ARTIFACT
    expected_path = deployment / EXPECTED_FLASH_ARTIFACT
    uicr_backup_path = deployment / UICR_BACKUP_ARTIFACT
    uicr_recovery_path = deployment / UICR_RECOVERY_ARTIFACT
    for artifact in (
            plan_path, backup_path, recovery_path, expected_path,
            uicr_backup_path, uicr_recovery_path):
        if not artifact.is_file():
            raise ValueError(f"deployment artifact is absent: {artifact.name}")

    plan = json.loads(plan_path.read_text())
    backup = backup_path.read_bytes()
    recovery_hex = recovery_path.read_bytes()
    expected_flash = expected_path.read_bytes()
    uicr_backup = uicr_backup_path.read_bytes()
    uicr_recovery_hex = uicr_recovery_path.read_bytes()
    install_memory = parse_ihex(members["openr1-full.hex"])
    backup_provenance = None
    if "provenance_artifact" in plan.get("backup", {}):
        provenance_path = deployment / BACKUP_PROVENANCE_ARTIFACT
        if not provenance_path.is_file():
            raise ValueError("flash-backup provenance artifact is absent")
        backup_provenance = json.loads(provenance_path.read_text())
        validate_backup_provenance(backup_provenance, backup, uicr_backup)
    independently_expected = build_expected_internal_flash(
        install_memory, backup)
    if expected_flash != independently_expected:
        raise ValueError("expected internal-flash artifact differs from page-erase model")
    canonical_recovery = write_ihex({
        address: value for address, value in enumerate(backup)
    })
    if recovery_hex != canonical_recovery:
        raise ValueError("recovery HEX is not the canonical backup encoding")
    if len(uicr_backup) != UICR_SIZE:
        raise ValueError(f"UICR backup must be exactly {UICR_SIZE} bytes")
    canonical_uicr_recovery = write_ihex({
        UICR_START + offset: value
        for offset, value in enumerate(uicr_backup)
    })
    if uicr_recovery_hex != canonical_uicr_recovery:
        raise ValueError("UICR recovery HEX is not the canonical backup encoding")
    independently_planned = build_deployment_plan(
        digest(bundle.read_bytes()), install_memory, backup, uicr_backup,
        canonical_recovery, canonical_uicr_recovery,
        independently_expected, backup_provenance)
    if plan != independently_planned:
        raise ValueError("deployment plan differs from verified bundle and backup")

    return plan, independently_expected, uicr_backup


def verify_deployment(
    bundle: Path, deployment: Path, readback: Path, uicr_readback: Path,
) -> dict[str, object]:
    plan, independently_expected, uicr_backup = verify_deployment_package(
        bundle, deployment)

    observed = readback.read_bytes()
    if len(observed) != FLASH_LIMIT:
        raise ValueError(
            f"post-install readback must be exactly {FLASH_LIMIT} bytes")
    if observed != independently_expected:
        differing = next(
            index for index, (actual, expected) in enumerate(
                zip(observed, independently_expected))
            if actual != expected
        )
        raise ValueError(
            "post-install readback differs at "
            f"0x{differing:08x}: observed 0x{observed[differing]:02x}, "
            f"expected 0x{independently_expected[differing]:02x}")
    observed_uicr = uicr_readback.read_bytes()
    if len(observed_uicr) != UICR_SIZE:
        raise ValueError(f"post-install UICR readback must be exactly {UICR_SIZE} bytes")
    if observed_uicr != uicr_backup:
        differing = next(
            index for index, (actual, expected) in enumerate(
                zip(observed_uicr, uicr_backup))
            if actual != expected
        )
        raise ValueError(
            "post-install UICR readback differs at "
            f"0x{UICR_START + differing:08x}: "
            f"observed 0x{observed_uicr[differing]:02x}, "
            f"expected 0x{uicr_backup[differing]:02x}")
    return plan


def verify_recovery_readback(
    deployment: Path, readback: Path, uicr_readback: Path,
) -> None:
    plan_path = deployment / PLAN_ARTIFACT
    backup_path = deployment / BACKUP_ARTIFACT
    uicr_backup_path = deployment / UICR_BACKUP_ARTIFACT
    if not plan_path.is_file() or not backup_path.is_file() or \
            not uicr_backup_path.is_file():
        raise ValueError("deployment plan or original backup is absent")
    plan = json.loads(plan_path.read_text())
    backup = backup_path.read_bytes()
    uicr_backup = uicr_backup_path.read_bytes()
    if len(backup) != FLASH_LIMIT:
        raise ValueError(
            f"original backup must be exactly {FLASH_LIMIT} bytes")
    recovery = plan.get("recovery", {})
    if recovery.get("readback_range") != [0, FLASH_LIMIT] or \
            recovery.get("expected_readback_sha256") != digest(backup):
        raise ValueError("recovery readback contract differs from original backup")
    if len(uicr_backup) != UICR_SIZE or \
            recovery.get("covers_uicr") != [UICR_START, UICR_LIMIT] or \
            recovery.get("expected_uicr_readback_sha256") != digest(uicr_backup):
        raise ValueError("UICR recovery readback contract differs from original backup")
    observed = readback.read_bytes()
    if len(observed) != FLASH_LIMIT:
        raise ValueError(
            f"post-recovery readback must be exactly {FLASH_LIMIT} bytes")
    if observed != backup:
        differing = next(
            index for index, (actual, expected) in enumerate(
                zip(observed, backup))
            if actual != expected
        )
        raise ValueError(
            "post-recovery readback differs at "
            f"0x{differing:08x}: observed 0x{observed[differing]:02x}, "
            f"expected 0x{backup[differing]:02x}")
    observed_uicr = uicr_readback.read_bytes()
    if len(observed_uicr) != UICR_SIZE:
        raise ValueError(f"post-recovery UICR readback must be exactly {UICR_SIZE} bytes")
    if observed_uicr != uicr_backup:
        differing = next(
            index for index, (actual, expected) in enumerate(
                zip(observed_uicr, uicr_backup))
            if actual != expected
        )
        raise ValueError(
            "post-recovery UICR readback differs at "
            f"0x{UICR_START + differing:08x}: "
            f"observed 0x{observed_uicr[differing]:02x}, "
            f"expected 0x{uicr_backup[differing]:02x}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--deployment", type=Path, required=True)
    parser.add_argument("--readback", type=Path, required=True)
    parser.add_argument("--uicr-readback", type=Path, required=True)
    parser.add_argument("--recovery-readback", type=Path)
    parser.add_argument("--recovery-uicr-readback", type=Path)
    args = parser.parse_args()
    plan = verify_deployment(
        args.bundle.expanduser().resolve(),
        args.deployment.expanduser().resolve(),
        args.readback.expanduser().resolve(),
        args.uicr_readback.expanduser().resolve(),
    )
    if (args.recovery_readback is None) != \
            (args.recovery_uicr_readback is None):
        parser.error(
            "--recovery-readback and --recovery-uicr-readback are required together")
    if args.recovery_readback is not None:
        verify_recovery_readback(
            args.deployment.expanduser().resolve(),
            args.recovery_readback.expanduser().resolve(),
            args.recovery_uicr_readback.expanduser().resolve())
    print(
        "openR1 deployment readback verified: exact 1-MiB page-erase model; "
        f"{len(plan['installation']['erase_ranges'])} erase range(s); "
        "classified retail settings are fresh-erased, product data matches, "
        "and legacy executable reserve is erased; "
        "architected 0x308-byte UICR extent is byte-identical" +
        ("; internal-flash and UICR recovery readbacks match original backups"
         if args.recovery_readback is not None else "")
    )


if __name__ == "__main__":
    main()
