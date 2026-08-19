#!/usr/bin/env python3
"""Fail-closed, sector-bounded SWD installer for the OpenR1 full image.

Dry-run is the default.  Execution requires an exact bundle digest, an explicit
probe ID, and a new evidence directory.  The target remains halted on every
failure and, by default, after success.  UICR is never written by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Callable, Iterable

from package_zephyr_bundle import (
    DATA_LIMIT,
    DATA_START,
    FLASH_LIMIT,
    parse_ihex,
)
from prepare_zephyr_deployment import UICR_SIZE, UICR_START
from verify_zephyr_bundle import verify_bundle
from verify_zephyr_deployment import (
    BACKUP_ARTIFACT,
    UICR_BACKUP_ARTIFACT,
    verify_deployment,
    verify_deployment_package,
    verify_recovery_readback,
)


FICR_PART_ADDRESS = 0x10000100
NRF52840_PART = 0x00052840
FLASH_PAGE_SIZE = 0x1000
NVMC_READY = 0x4001E400
NVMC_CONFIG = 0x4001E504
NVMC_ERASEPAGE = 0x4001E508
NVMC_ERASEUICR = 0x4001E514
NVMC_CONFIG_READ = 0
NVMC_CONFIG_WRITE = 1
NVMC_CONFIG_ERASE = 2
PRE_FLASH_ARTIFACT = "pre-install-internal-flash.bin"
PRE_UICR_ARTIFACT = "pre-install-uicr.bin"
POST_FLASH_ARTIFACT = "post-install-internal-flash.bin"
POST_UICR_ARTIFACT = "post-install-uicr.bin"
RESULT_ARTIFACT = "deployment-result.json"
PRE_RECOVERY_FLASH_ARTIFACT = "pre-recovery-internal-flash.bin"
PRE_RECOVERY_UICR_ARTIFACT = "pre-recovery-uicr.bin"
POST_RECOVERY_FLASH_ARTIFACT = "post-recovery-internal-flash.bin"
POST_RECOVERY_UICR_ARTIFACT = "post-recovery-uicr.bin"

EraseCallback = Callable[[object, list[tuple[int, int]]], None]
ProgramCallback = Callable[[object, list[tuple[int, bytes]]], None]
ReadbackVerifier = Callable[[Path, Path], None]
UicrRestoreCallback = Callable[[object, bytes], None]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contiguous_chunks(memory: dict[int, int]) -> list[tuple[int, bytes]]:
    addresses = sorted(memory)
    if not addresses:
        return []
    chunks: list[tuple[int, bytes]] = []
    start = addresses[0]
    previous = start
    body = bytearray((memory[start],))
    for address in addresses[1:]:
        if address != previous + 1:
            chunks.append((start, bytes(body)))
            start = address
            body = bytearray()
        body.append(memory[address])
        previous = address
    chunks.append((start, bytes(body)))
    return chunks


def chunk_ranges(chunks: Iterable[tuple[int, bytes]]) -> list[list[int]]:
    return [[address, address + len(body)] for address, body in chunks]


def non_erased_chunks(data: bytes, base: int = 0) -> list[tuple[int, bytes]]:
    chunks: list[tuple[int, bytes]] = []
    start: int | None = None
    body = bytearray()
    for offset, value in enumerate(data):
        if value == 0xFF:
            if start is not None:
                chunks.append((base + start, bytes(body)))
                start = None
                body.clear()
            continue
        if start is None:
            start = offset
        body.append(value)
    if start is not None:
        chunks.append((base + start, bytes(body)))
    return chunks


def validate_execution_contract(
    plan: dict[str, object], install_memory: dict[int, int],
) -> list[tuple[int, int]]:
    installation = plan.get("installation")
    if not isinstance(installation, dict):
        raise ValueError("deployment installation contract is absent")
    erase_ranges = installation.get("erase_ranges")
    expected_erase_ranges = [[0, DATA_START], [DATA_LIMIT, FLASH_LIMIT]]
    if erase_ranges != expected_erase_ranges:
        raise ValueError("deployment erase ranges are not the exact bounded plan")
    if installation.get("mass_erase_forbidden") is not True:
        raise ValueError("deployment does not explicitly forbid mass erase")
    if installation.get("readback_required") is not True or \
            installation.get("reset_held_until_readback_verified") is not True:
        raise ValueError("deployment does not hold reset through exact readback")
    chunks = contiguous_chunks(install_memory)
    if not chunks or installation.get("write_ranges") != chunk_ranges(chunks):
        raise ValueError("deployment write ranges differ from the verified image")
    for address, body in chunks:
        if address < 0 or address + len(body) > DATA_START:
            raise ValueError("install write leaves the executable partition")
    return [(start, limit) for start, limit in expected_erase_ranges]


def validate_recovery_contract(
    plan: dict[str, object], backup: bytes, uicr_backup: bytes,
    installed_flash: bytes,
) -> list[tuple[int, int]]:
    recovery = plan.get("recovery")
    installation = plan.get("installation")
    if not isinstance(recovery, dict) or not isinstance(installation, dict):
        raise ValueError("deployment recovery contract is absent")
    if installation.get("mass_erase_forbidden") is not True:
        raise ValueError("deployment does not explicitly forbid mass erase")
    if recovery.get("requires_authorized_debug_access") is not True or \
            recovery.get("readback_range") != [0, FLASH_LIMIT] or \
            recovery.get("covers_internal_flash") != [0, FLASH_LIMIT] or \
            recovery.get("covers_uicr") != [UICR_START, UICR_START + UICR_SIZE] or \
            recovery.get("uicr_readback_required") is not True or \
            recovery.get("includes_uicr") is not False or \
            recovery.get("uicr_erase_before_restore_required") is not True:
        raise ValueError("deployment recovery ranges or authorization differ")
    if recovery.get("expected_readback_sha256") != digest(backup) or \
            recovery.get("expected_uicr_readback_sha256") != digest(uicr_backup):
        raise ValueError("deployment recovery hashes differ")
    expected = plan.get("expected_readback")
    if not isinstance(expected, dict) or \
            expected.get("sha256") != digest(installed_flash):
        raise ValueError("deployment installed-state hash differs")
    return [(0, FLASH_LIMIT)]


def first_difference(actual: bytes, expected: bytes) -> str:
    if len(actual) != len(expected):
        return f"length {len(actual)} instead of {len(expected)}"
    for offset, (observed, wanted) in enumerate(zip(actual, expected)):
        if observed != wanted:
            return (
                f"offset 0x{offset:08x}: observed 0x{observed:02x}, "
                f"expected 0x{wanted:02x}")
    return "no difference"


def require_equal(label: str, actual: bytes, expected: bytes) -> None:
    if actual != expected:
        raise ValueError(f"{label} differs: {first_difference(actual, expected)}")


def validate_uicr_confirmation(
    restore_uicr: bool, supplied_digest: str | None, uicr_backup: bytes,
) -> None:
    if restore_uicr and supplied_digest != digest(uicr_backup):
        raise ValueError(
            "UICR disaster recovery requires the exact backup SHA-256")


def execute_session(
    session: object,
    plan: dict[str, object],
    install_memory: dict[int, int],
    backup: bytes,
    uicr_backup: bytes,
    expected_flash: bytes,
    output: Path,
    erase_callback: EraseCallback,
    program_callback: ProgramCallback,
    release_after_verify: bool = False,
    verification_callback: ReadbackVerifier | None = None,
) -> dict[str, object]:
    """Execute one already-verified plan through an open, exclusive SWD session."""
    erase_ranges = validate_execution_contract(plan, install_memory)
    if len(backup) != FLASH_LIMIT or len(expected_flash) != FLASH_LIMIT:
        raise ValueError("deployment flash images must be exactly one MiB")
    if len(uicr_backup) != UICR_SIZE:
        raise ValueError("deployment UICR image has the wrong length")
    if output.exists():
        raise ValueError(f"deployment evidence path already exists: {output}")

    target = session.target
    target.halt()
    try:
        part = int(target.read_memory(FICR_PART_ADDRESS, 32))
        if part != NRF52840_PART:
            raise ValueError(
                f"SWD target is not nRF52840: FICR.PART=0x{part:08x}")

        pre_flash = bytes(target.read_memory_block8(0, FLASH_LIMIT))
        pre_uicr = bytes(target.read_memory_block8(UICR_START, UICR_SIZE))
        output.mkdir(parents=False, exist_ok=False)
        (output / PRE_FLASH_ARTIFACT).write_bytes(pre_flash)
        (output / PRE_UICR_ARTIFACT).write_bytes(pre_uicr)
        require_equal("pre-install internal flash", pre_flash, backup)
        require_equal("pre-install UICR", pre_uicr, uicr_backup)

        erase_callback(session, erase_ranges)
        program_callback(session, contiguous_chunks(install_memory))
        target.halt()

        post_flash = bytes(target.read_memory_block8(0, FLASH_LIMIT))
        post_uicr = bytes(target.read_memory_block8(UICR_START, UICR_SIZE))
        (output / POST_FLASH_ARTIFACT).write_bytes(post_flash)
        (output / POST_UICR_ARTIFACT).write_bytes(post_uicr)
        require_equal("post-install internal flash", post_flash, expected_flash)
        require_equal("post-install UICR", post_uicr, uicr_backup)
        if verification_callback is not None:
            verification_callback(
                output / POST_FLASH_ARTIFACT,
                output / POST_UICR_ARTIFACT)

        result: dict[str, object] = {
            "format": "openr1-swd-deployment-result",
            "schema": 1,
            "device_part": part,
            "erase_ranges": [list(item) for item in erase_ranges],
            "pre_install_flash_sha256": digest(pre_flash),
            "pre_install_uicr_sha256": digest(pre_uicr),
            "post_install_flash_sha256": digest(post_flash),
            "post_install_uicr_sha256": digest(post_uicr),
            "released_after_verification": release_after_verify,
            "mass_erase_used": False,
            "uicr_written": False,
        }
        (output / RESULT_ARTIFACT).write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        if release_after_verify:
            target.reset()
        return result
    except Exception:
        # resume_on_disconnect is forced false by main(), and an explicit halt
        # here makes the invariant testable with alternate pyOCD probes.
        target.halt()
        raise


def execute_recovery_session(
    session: object,
    plan: dict[str, object],
    installed_flash: bytes,
    backup: bytes,
    uicr_backup: bytes,
    output: Path,
    erase_callback: EraseCallback,
    program_callback: ProgramCallback,
    release_after_verify: bool = False,
    verification_callback: ReadbackVerifier | None = None,
    restore_uicr: bool = False,
    uicr_restore_callback: UicrRestoreCallback | None = None,
) -> dict[str, object]:
    """Restore the exact pre-install flash while requiring unchanged UICR."""
    erase_ranges = validate_recovery_contract(
        plan, backup, uicr_backup, installed_flash)
    if len(installed_flash) != FLASH_LIMIT or len(backup) != FLASH_LIMIT:
        raise ValueError("recovery flash images must be exactly one MiB")
    if len(uicr_backup) != UICR_SIZE:
        raise ValueError("recovery UICR image has the wrong length")
    if output.exists():
        raise ValueError(f"recovery evidence path already exists: {output}")

    target = session.target
    target.halt()
    try:
        part = int(target.read_memory(FICR_PART_ADDRESS, 32))
        if part != NRF52840_PART:
            raise ValueError(
                f"SWD target is not nRF52840: FICR.PART=0x{part:08x}")
        pre_flash = bytes(target.read_memory_block8(0, FLASH_LIMIT))
        pre_uicr = bytes(target.read_memory_block8(UICR_START, UICR_SIZE))
        output.mkdir(parents=False, exist_ok=False)
        (output / PRE_RECOVERY_FLASH_ARTIFACT).write_bytes(pre_flash)
        (output / PRE_RECOVERY_UICR_ARTIFACT).write_bytes(pre_uicr)
        require_equal("pre-recovery installed flash", pre_flash, installed_flash)
        if not restore_uicr:
            require_equal("pre-recovery UICR", pre_uicr, uicr_backup)

        erase_callback(session, erase_ranges)
        program_callback(session, non_erased_chunks(backup))
        if restore_uicr:
            if uicr_restore_callback is None:
                raise ValueError("UICR restore callback is absent")
            uicr_restore_callback(session, uicr_backup)
        target.halt()
        post_flash = bytes(target.read_memory_block8(0, FLASH_LIMIT))
        post_uicr = bytes(target.read_memory_block8(UICR_START, UICR_SIZE))
        (output / POST_RECOVERY_FLASH_ARTIFACT).write_bytes(post_flash)
        (output / POST_RECOVERY_UICR_ARTIFACT).write_bytes(post_uicr)
        require_equal("post-recovery internal flash", post_flash, backup)
        require_equal("post-recovery UICR", post_uicr, uicr_backup)
        if verification_callback is not None:
            verification_callback(
                output / POST_RECOVERY_FLASH_ARTIFACT,
                output / POST_RECOVERY_UICR_ARTIFACT)

        result: dict[str, object] = {
            "format": "openr1-swd-recovery-result",
            "schema": 1,
            "device_part": part,
            "erase_ranges": [[0, FLASH_LIMIT]],
            "pre_recovery_flash_sha256": digest(pre_flash),
            "pre_recovery_uicr_sha256": digest(pre_uicr),
            "post_recovery_flash_sha256": digest(post_flash),
            "post_recovery_uicr_sha256": digest(post_uicr),
            "released_after_verification": release_after_verify,
            "mass_erase_used": False,
            "uicr_written": restore_uicr,
        }
        (output / RESULT_ARTIFACT).write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
        if release_after_verify:
            target.reset()
        return result
    except Exception:
        target.halt()
        raise


def nvmc_wait_ready(target: object, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if int(target.read32(NVMC_READY)) == 1:
            return
    raise TimeoutError("nRF52840 NVMC did not become ready")


def nvmc_set_config(target: object, value: int) -> None:
    target.write32(NVMC_CONFIG, value)
    nvmc_wait_ready(target)


def nvmc_sector_erase(
    session: object, ranges: list[tuple[int, int]],
) -> None:
    target = session.target
    for start, limit in ranges:
        if start % FLASH_PAGE_SIZE != 0 or limit % FLASH_PAGE_SIZE != 0 or \
                start < 0 or limit > FLASH_LIMIT or start >= limit:
            raise ValueError("NVMC erase range is not page-aligned internal flash")
    nvmc_set_config(target, NVMC_CONFIG_ERASE)
    try:
        for start, limit in ranges:
            for address in range(start, limit, FLASH_PAGE_SIZE):
                target.write32(NVMC_ERASEPAGE, address)
                nvmc_wait_ready(target)
    finally:
        nvmc_set_config(target, NVMC_CONFIG_READ)


def nvmc_program_chunks(
    session: object, chunks: list[tuple[int, bytes]],
    allowed_start: int, allowed_limit: int,
) -> None:
    words: dict[int, bytearray] = {}
    for address, body in chunks:
        if not body or address < allowed_start or \
                address + len(body) > allowed_limit:
            raise ValueError("NVMC program chunk leaves its authorized range")
        for offset, value in enumerate(body):
            byte_address = address + offset
            word_address = byte_address & ~3
            word = words.setdefault(word_address, bytearray(b"\xff" * 4))
            index = byte_address - word_address
            if word[index] != 0xFF and word[index] != value:
                raise ValueError("overlapping install chunks disagree")
            word[index] = value

    target = session.target
    nvmc_set_config(target, NVMC_CONFIG_WRITE)
    try:
        for address in sorted(words):
            value = int.from_bytes(words[address], "little")
            if value == 0xFFFFFFFF:
                continue
            target.write32(address, value)
            nvmc_wait_ready(target)
    finally:
        nvmc_set_config(target, NVMC_CONFIG_READ)


def nvmc_program(
    session: object, chunks: list[tuple[int, bytes]],
) -> None:
    nvmc_program_chunks(session, chunks, 0, FLASH_LIMIT)


def nvmc_restore_uicr(session: object, uicr_backup: bytes) -> None:
    if len(uicr_backup) != UICR_SIZE:
        raise ValueError("UICR restore image has the wrong length")
    target = session.target
    nvmc_set_config(target, NVMC_CONFIG_ERASE)
    try:
        target.write32(NVMC_ERASEUICR, 1)
        nvmc_wait_ready(target)
    finally:
        nvmc_set_config(target, NVMC_CONFIG_READ)
    erased = bytes(target.read_memory_block8(UICR_START, UICR_SIZE))
    if erased != b"\xff" * UICR_SIZE:
        raise ValueError("UICR did not read back erased before restoration")
    nvmc_program_chunks(
        session, non_erased_chunks(uicr_backup, UICR_START),
        UICR_START, UICR_START + UICR_SIZE)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--deployment", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--recover", action="store_true")
    parser.add_argument("--restore-uicr", action="store_true")
    parser.add_argument("--confirm-uicr-sha256")
    parser.add_argument("--probe-id")
    parser.add_argument("--confirm-bundle-sha256")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--frequency", type=int, default=1_000_000)
    parser.add_argument("--release-after-verify", action="store_true")
    args = parser.parse_args()

    bundle = args.bundle.expanduser().resolve()
    deployment = args.deployment.expanduser().resolve()
    plan, expected_flash, uicr_backup = verify_deployment_package(
        bundle, deployment)
    members, _ = verify_bundle(bundle)
    install_memory = parse_ihex(members["openr1-full.hex"])
    erase_ranges = validate_execution_contract(plan, install_memory)
    bundle_digest = digest(bundle.read_bytes())
    backup = (deployment / BACKUP_ARTIFACT).read_bytes()
    if args.restore_uicr and not args.recover:
        parser.error("--restore-uicr is valid only with --recover")
    if args.recover:
        erase_ranges = validate_recovery_contract(
            plan, backup, uicr_backup, expected_flash)

    if not args.execute:
        uicr_policy = (
            "UICR disaster restore planned; required_sha256=" +
            digest(uicr_backup)
            if args.restore_uicr else "UICR write forbidden")
        print(
            f"openR1 SWD {'recovery' if args.recover else 'deployment'} "
            "dry-run verified: "
            f"bundle_sha256={bundle_digest}; erase_ranges={erase_ranges}; "
            f"mass erase forbidden; {uicr_policy}; target reset withheld")
        return

    if not args.probe_id or args.output is None or \
            args.confirm_bundle_sha256 != bundle_digest:
        parser.error(
            "--execute requires --probe-id, a new --output path, and the exact "
            "--confirm-bundle-sha256 value printed by dry-run")
    try:
        validate_uicr_confirmation(
            args.restore_uicr, args.confirm_uicr_sha256, uicr_backup)
    except ValueError as error:
        parser.error(str(error))
    if args.frequency <= 0 or args.frequency > 4_000_000:
        parser.error("--frequency must be between 1 and 4000000 Hz")

    try:
        from pyocd.core.helpers import ConnectHelper
    except ImportError as error:
        raise SystemExit(
            "pyOCD is required only for --execute; install the pinned deployment "
            "environment before attaching a probe") from error

    options = {
        "target_override": "nrf52840",
        "frequency": args.frequency,
        "dap_protocol": "swd",
        "connect_mode": "under-reset",
        "auto_unlock": False,
        "chip_erase": "sector",
        "smart_flash": True,
        "fast_program": False,
        "keep_unwritten": False,
        "resume_on_disconnect": False,
        "cache.enable_memory": False,
        "cache.read_code_from_elf": False,
        "load.post_reset": "off",
    }
    session = ConnectHelper.session_with_chosen_probe(
        unique_id=args.probe_id,
        blocking=False,
        return_first=False,
        options=options,
        no_config=True,
    )
    if session is None:
        raise SystemExit(f"no unique SWD probe matched {args.probe_id!r}")

    with session:
        if args.recover:
            result = execute_recovery_session(
                session, plan, expected_flash, backup, uicr_backup,
                args.output.expanduser().resolve(), nvmc_sector_erase,
                nvmc_program, args.release_after_verify,
                lambda flash, uicr: verify_recovery_readback(
                    deployment, flash, uicr),
                args.restore_uicr, nvmc_restore_uicr)
        else:
            result = execute_session(
                session, plan, install_memory, backup, uicr_backup,
                expected_flash, args.output.expanduser().resolve(),
                nvmc_sector_erase, nvmc_program, args.release_after_verify,
                lambda flash, uicr: verify_deployment(
                    bundle, deployment, flash, uicr))
    print(
        f"openR1 SWD {'recovery' if args.recover else 'deployment'} verified: "
        "exact full-flash and UICR readback; "
        f"released={result['released_after_verification']}; "
        f"evidence={args.output.expanduser().resolve()}")


if __name__ == "__main__":
    main()
