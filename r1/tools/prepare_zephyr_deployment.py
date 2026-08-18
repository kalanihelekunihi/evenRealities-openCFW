#!/usr/bin/env python3
"""Prepare an auditable, non-flashing OpenR1 deployment/recovery package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from package_zephyr_bundle import (
    DATA_LIMIT,
    DATA_START,
    FLASH_LIMIT,
    SETTINGS_START,
    parse_ihex,
    write_ihex,
)
from verify_zephyr_bundle import verify_bundle


PRODUCT_PARTITIONS = (
    ("kv.bin", 0x00000, 0x02000),
    ("health.db", 0x02000, 0x06000),
    ("sleep.db", 0x08000, 0x02000),
    ("pKey.bin", 0x0A000, 0x01000),
    ("reserve", 0x0B000, 0x0B000),
    ("ep.bin", 0x16000, 0x02000),
    ("log.bin", 0x18000, 0x0C000),
)
FLASH_PAGE_SIZE = 0x1000
FDS_PAGE_MAGIC = 0xDEADC0DE
FDS_DATA_TAG = 0xF11E01FE
FDS_SWAP_TAG = 0xF11E01FF
EXPECTED_FLASH_ARTIFACT = "openr1-expected-internal-flash.bin"
UICR_START = 0x10001000
# Nordic's nRF52840 device header defines NRF_UICR_Type through REGOUT0 as
# exactly 776 (0x308) bytes. The remainder of the containing nonvolatile page
# is not an architected CPU-readable UICR range and faults under the live
# application memory map; do not fabricate a 4 KiB register backup.
UICR_SIZE = 0x0308
UICR_LIMIT = UICR_START + UICR_SIZE
UICR_BACKUP_ARTIFACT = "openr1-uicr-backup.bin"
UICR_RECOVERY_ARTIFACT = "openr1-uicr-recovery.hex"
BACKUP_PROVENANCE_ARTIFACT = "openr1-internal-flash-backup-provenance.json"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def addressed_digest(memory: dict[int, int], source: bytes | None = None) -> str:
    hasher = hashlib.sha256()
    for address in sorted(memory):
        hasher.update(address.to_bytes(4, "little"))
        hasher.update(bytes((memory[address] if source is None else source[address],)))
    return hasher.hexdigest()


def contiguous_ranges(memory: dict[int, int]) -> list[list[int]]:
    addresses = sorted(memory)
    if not addresses:
        return []
    ranges: list[list[int]] = []
    start = addresses[0]
    previous = start
    for address in addresses[1:]:
        if address != previous + 1:
            ranges.append([start, previous + 1])
            start = address
        previous = address
    ranges.append([start, previous + 1])
    return ranges


def classify_first_install_settings(backup: bytes) -> dict[str, object]:
    """Recognize only a clean store or the exact three-page retail FDS layout.

    The source-built target uses Zephyr NVS in this address range.  Nordic FDS
    records are deliberately not decoded or imported as owner credentials.
    Unknown and interrupted layouts fail closed so the offline recovery image
    can be restored before another installation attempt.
    """
    if len(backup) != FLASH_LIMIT:
        raise ValueError(
            f"internal-flash backup must be exactly {FLASH_LIMIT} bytes")
    pages = []
    counts = {"erased": 0, "fds-data": 0, "fds-swap": 0}
    for address in range(SETTINGS_START, DATA_START, FLASH_PAGE_SIZE):
        body = backup[address:address + FLASH_PAGE_SIZE]
        if all(value == 0xFF for value in body):
            kind = "erased"
        else:
            magic = int.from_bytes(body[0:4], "little")
            tag = int.from_bytes(body[4:8], "little")
            if magic != FDS_PAGE_MAGIC or tag not in (
                    FDS_DATA_TAG, FDS_SWAP_TAG):
                raise ValueError(
                    "settings preflight found an unknown or torn page at "
                    f"0x{address:08x}; restore/retain the recovery backup")
            kind = "fds-data" if tag == FDS_DATA_TAG else "fds-swap"
        counts[kind] += 1
        pages.append({
            "range": [address, address + FLASH_PAGE_SIZE],
            "kind": kind,
            "sha256": digest(body),
            "non_erased_bytes": sum(value != 0xFF for value in body),
        })

    layout = ""
    if counts == {"erased": 3, "fds-data": 0, "fds-swap": 0}:
        layout = "erased"
    elif counts == {"erased": 0, "fds-data": 2, "fds-swap": 1}:
        layout = "retail-nordic-fds"
    else:
        raise ValueError(
            "settings preflight found an interrupted retail FDS layout "
            f"({counts['erased']} erased, {counts['fds-data']} data, "
            f"{counts['fds-swap']} swap); restore the recovery backup")
    return {
        "layout": layout,
        "recognized": True,
        "pages": pages,
        "action": "erase-for-fresh-zephyr-nvs",
        "owner_repairing_required": layout == "retail-nordic-fds",
    }


def installation_erase_ranges(
    install_memory: dict[int, int],
) -> list[list[int]]:
    if not install_memory:
        return []
    # Erase the complete source-built boot/application partition, including
    # sparse HEX gaps and unused application tail. Leaving those pages intact
    # could retain opaque retail executable bytes even though no new symbol
    # references them.
    # The retail Nordic FDS store is not Zephyr NVS compatible.  First-install
    # preflight classifies it exactly, then these three pages are reset along
    # with the source-built executable partition. Product data alone survives.
    return [[0, DATA_START], [DATA_LIMIT, FLASH_LIMIT]]


def build_expected_internal_flash(
    install_memory: dict[int, int], backup: bytes,
) -> bytes:
    validate_deployment_inputs(install_memory, backup)
    classify_first_install_settings(backup)
    expected = bytearray(backup)
    for start, limit in installation_erase_ranges(install_memory):
        expected[start:limit] = b"\xff" * (limit - start)
    for address, value in install_memory.items():
        expected[address] = value
    return bytes(expected)


def validate_deployment_inputs(
    install_memory: dict[int, int], backup: bytes,
) -> None:
    if len(backup) != FLASH_LIMIT:
        raise ValueError(
            f"internal-flash backup must be exactly {FLASH_LIMIT} bytes")
    if not install_memory:
        raise ValueError("install image is empty")
    if min(install_memory) < 0 or max(install_memory) >= SETTINGS_START:
        raise ValueError(
            "install image overlaps settings or preserved product-data flash")


def validate_backup_provenance(
    provenance: dict[str, object], backup: bytes, uicr_backup: bytes,
) -> None:
    """Validate a mixed ACE/pinned recovery basis without calling it all-live."""
    if provenance.get("schema") != 1 or \
            provenance.get("format") != "r1-ace-recovery-basis":
        raise ValueError("flash-backup provenance schema differs")
    output = provenance.get("output")
    if not isinstance(output, dict) or \
            output.get("bytes") != FLASH_LIMIT or \
            output.get("sha256") != digest(backup):
        raise ValueError("flash-backup provenance output differs")
    uicr = provenance.get("uicr")
    if not isinstance(uicr, dict) or \
            uicr.get("range") != [UICR_START, UICR_LIMIT] or \
            uicr.get("bytes") != UICR_SIZE or \
            uicr.get("sha256") != digest(uicr_backup):
        raise ValueError("flash-backup provenance UICR differs")
    extents = provenance.get("provenance")
    expected_extents = (
        ([0, 0xFF8], "pinned-official-reconstruction"),
        ([0xFF8, 0x1000], "source-proven-mbr-config"),
        ([0x1000, 0x27000], "pinned-official-reconstruction"),
        ([0x27000, 0xFF000], "live-ace-page-readback"),
        ([0xFF000, FLASH_LIMIT], "source-proven-settings-mirror"),
    )
    if not isinstance(extents, list) or len(extents) != len(expected_extents):
        raise ValueError("flash-backup provenance extents differ")
    for extent, (expected_range, expected_kind) in zip(
            extents, expected_extents):
        if not isinstance(extent, dict) or \
                extent.get("range") != expected_range or \
                extent.get("kind") != expected_kind:
            raise ValueError("flash-backup provenance extents differ")
    if provenance.get("protected_extent_sha256") != digest(backup[:0x27000]):
        raise ValueError("reconstructed protected-extent digest differs")
    if extents[1].get("sha256") != digest(backup[0xFF8:0x1000]):
        raise ValueError("source-proven MBR configuration digest differs")

    page_records = provenance.get("live_pages")
    expected_page_count = (0xFF000 - 0x27000) // FLASH_PAGE_SIZE
    if not isinstance(page_records, list) or \
            len(page_records) != expected_page_count or \
            extents[3].get("pages") != expected_page_count or \
            extents[3].get("page_bytes") != FLASH_PAGE_SIZE:
        raise ValueError("live ACE page provenance differs")
    for index, record in enumerate(page_records):
        address = 0x27000 + index * FLASH_PAGE_SIZE
        if not isinstance(record, dict) or \
                record.get("range") != [address, address + FLASH_PAGE_SIZE] or \
                record.get("sha256") != digest(
                    backup[address:address + FLASH_PAGE_SIZE]):
            raise ValueError(
                f"live ACE page provenance differs at 0x{address:08x}")
    mirror = extents[4]
    if mirror.get("live_backup_range") != [0xFE000, 0xFF000] or \
            mirror.get("live_backup_sha256") != digest(backup[0xFE000:0xFF000]) or \
            backup[0xFF000:FLASH_LIMIT] != backup[0xFE000:0xFF000]:
        raise ValueError("source-proven primary settings mirror differs")

    matches = provenance.get("official_matches")
    if not isinstance(matches, dict):
        raise ValueError("official-image comparison provenance is absent")
    for name in ("application", "bootloader"):
        match = matches.get(name)
        if not isinstance(match, dict) or match.get("byte_exact") is not True:
            raise ValueError(f"official {name} comparison is not byte-exact")


def build_deployment_plan(
    bundle_sha256: str, install_memory: dict[int, int], backup: bytes,
    uicr_backup: bytes, recovery_hex: bytes, uicr_recovery_hex: bytes,
    expected_flash: bytes,
    backup_provenance: dict[str, object] | None = None,
) -> dict[str, object]:
    validate_deployment_inputs(install_memory, backup)
    settings_transition = classify_first_install_settings(backup)
    if len(uicr_backup) != UICR_SIZE:
        raise ValueError(f"UICR backup must be exactly {UICR_SIZE} bytes")
    if len(expected_flash) != FLASH_LIMIT:
        raise ValueError(
            f"expected internal flash must be exactly {FLASH_LIMIT} bytes")
    erase_ranges = installation_erase_ranges(install_memory)
    regions = []
    for name, start, limit in (
        ("openr1-product-data", DATA_START, DATA_LIMIT),
    ):
        body = backup[start:limit]
        regions.append({
            "name": name,
            "range": [start, limit],
            "bytes": len(body),
            "sha256": digest(body),
        })
    partitions = []
    for name, relative, length in PRODUCT_PARTITIONS:
        start = DATA_START + relative
        body = backup[start:start + length]
        partitions.append({
            "name": name,
            "range": [start, start + length],
            "bytes": length,
            "sha256": digest(body),
            "erased": all(value == 0xFF for value in body),
        })
    plan = {
        "schema": 3,
        "format": "openr1-offline-deployment-preflight",
        "bundle_sha256": bundle_sha256,
        "installation": {
            "artifact": "openr1-full.hex",
            "write_ranges": contiguous_ranges(install_memory),
            "flash_page_bytes": FLASH_PAGE_SIZE,
            "erase_ranges": erase_ranges,
            "addressed_bytes": len(install_memory),
            "before_addressed_sha256": addressed_digest(
                install_memory, backup),
            "expected_addressed_sha256": addressed_digest(install_memory),
            "erase_policy": "sector-erase-install-and-classified-retail-settings",
            "mass_erase_forbidden": True,
            "readback_required": True,
            "reset_held_until_readback_verified": True,
            "unaddressed_install_bytes_must_be_erased": True,
            "readback_range": [0, FLASH_LIMIT],
            "expected_readback_artifact": EXPECTED_FLASH_ARTIFACT,
        },
        "backup": {
            "artifact": "openr1-internal-flash-backup.bin",
            "range": [0, FLASH_LIMIT],
            "bytes": len(backup),
            "sha256": digest(backup),
        },
        "uicr_backup": {
            "artifact": UICR_BACKUP_ARTIFACT,
            "range": [UICR_START, UICR_LIMIT],
            "bytes": len(uicr_backup),
            "sha256": digest(uicr_backup),
            "must_remain_unchanged_by_install": True,
            "post_install_readback_required": True,
        },
        "preserved_regions": regions,
        "settings_transition": {
            **settings_transition,
            "range": [SETTINGS_START, DATA_START],
            "before_sha256": digest(backup[SETTINGS_START:DATA_START]),
            "expected_after_sha256": digest(
                b"\xff" * (DATA_START - SETTINGS_START)),
            "retail_credentials_imported": False,
            "recovery_source": "openr1-internal-flash-backup.bin",
        },
        "product_partitions": partitions,
        "recovery": {
            "artifact": "openr1-internal-flash-recovery.hex",
            "bytes": len(recovery_hex),
            "sha256": digest(recovery_hex),
            "covers_internal_flash": [0, FLASH_LIMIT],
            "includes_uicr": False,
            "requires_authorized_debug_access": True,
            "on_device_rollback_available": False,
            "readback_range": [0, FLASH_LIMIT],
            "expected_readback_sha256": digest(backup),
            "uicr_artifact": UICR_RECOVERY_ARTIFACT,
            "uicr_bytes": len(uicr_recovery_hex),
            "uicr_sha256": digest(uicr_recovery_hex),
            "covers_uicr": [UICR_START, UICR_LIMIT],
            "uicr_erase_before_restore_required": True,
            "uicr_readback_required": True,
            "expected_uicr_readback_sha256": digest(uicr_backup),
        },
        "expected_readback": {
            "artifact": EXPECTED_FLASH_ARTIFACT,
            "range": [0, FLASH_LIMIT],
            "bytes": len(expected_flash),
            "sha256": digest(expected_flash),
        },
    }
    if backup_provenance is not None:
        plan["backup"]["provenance_artifact"] = BACKUP_PROVENANCE_ARTIFACT
        plan["backup"]["provenance_sha256"] = digest(
            (json.dumps(
                backup_provenance, indent=2, sort_keys=True) + "\n").encode())
        plan["backup"]["protected_extent_source"] = \
            "pinned-official-reconstruction"
        plan["backup"]["live_readback_range"] = [0x27000, FLASH_LIMIT]
    return plan


def prepare(
    bundle: Path, flash_backup: Path, uicr_backup_path: Path, output: Path,
    backup_provenance_path: Path | None = None,
) -> Path:
    members, _ = verify_bundle(bundle)
    backup = flash_backup.read_bytes()
    uicr_backup = uicr_backup_path.read_bytes()
    backup_provenance = None
    if backup_provenance_path is not None:
        backup_provenance = json.loads(backup_provenance_path.read_text())
        validate_backup_provenance(backup_provenance, backup, uicr_backup)
    install_memory = parse_ihex(members["openr1-full.hex"])
    validate_deployment_inputs(install_memory, backup)
    recovery_hex = write_ihex({
        address: value for address, value in enumerate(backup)
    })
    if len(uicr_backup) != UICR_SIZE:
        raise ValueError(f"UICR backup must be exactly {UICR_SIZE} bytes")
    uicr_recovery_hex = write_ihex({
        UICR_START + offset: value
        for offset, value in enumerate(uicr_backup)
    })
    expected_flash = build_expected_internal_flash(install_memory, backup)
    plan = build_deployment_plan(
        digest(bundle.read_bytes()), install_memory, backup, uicr_backup,
        recovery_hex, uicr_recovery_hex, expected_flash, backup_provenance)

    if output.exists():
        if not output.is_dir():
            raise ValueError(f"deployment output is not a directory: {output}")
        if any(output.iterdir()):
            raise ValueError(
                f"refusing to overwrite nonempty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    backup_output = output / "openr1-internal-flash-backup.bin"
    recovery_output = output / "openr1-internal-flash-recovery.hex"
    expected_output = output / EXPECTED_FLASH_ARTIFACT
    uicr_backup_output = output / UICR_BACKUP_ARTIFACT
    uicr_recovery_output = output / UICR_RECOVERY_ARTIFACT
    plan_output = output / "deployment-plan.json"
    backup_output.write_bytes(backup)
    recovery_output.write_bytes(recovery_hex)
    expected_output.write_bytes(expected_flash)
    uicr_backup_output.write_bytes(uicr_backup)
    uicr_recovery_output.write_bytes(uicr_recovery_hex)
    if backup_provenance is not None:
        (output / BACKUP_PROVENANCE_ARTIFACT).write_text(
            json.dumps(backup_provenance, indent=2, sort_keys=True) + "\n")
    plan_output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")

    if digest(backup_output.read_bytes()) != plan["backup"]["sha256"]:
        raise RuntimeError("written backup digest differs")
    if digest(recovery_output.read_bytes()) != plan["recovery"]["sha256"]:
        raise RuntimeError("written recovery HEX digest differs")
    if digest(expected_output.read_bytes()) != \
            plan["expected_readback"]["sha256"]:
        raise RuntimeError("written expected readback digest differs")
    if digest(uicr_backup_output.read_bytes()) != \
            plan["uicr_backup"]["sha256"]:
        raise RuntimeError("written UICR backup digest differs")
    if digest(uicr_recovery_output.read_bytes()) != \
            plan["recovery"]["uicr_sha256"]:
        raise RuntimeError("written UICR recovery HEX digest differs")
    return plan_output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--flash-backup", type=Path, required=True)
    parser.add_argument("--uicr-backup", type=Path, required=True)
    parser.add_argument("--flash-backup-provenance", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = prepare(
        args.bundle.expanduser().resolve(),
        args.flash_backup.expanduser().resolve(),
        args.uicr_backup.expanduser().resolve(),
        args.output.expanduser().resolve(),
        (args.flash_backup_provenance.expanduser().resolve()
         if args.flash_backup_provenance is not None else None),
    )
    print(f"openR1 offline deployment preflight: {plan}")


if __name__ == "__main__":
    main()
