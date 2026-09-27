#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the source-backed STM32G0 charging-case ELF/raw/EVEN image."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMPONENT = Path(__file__).resolve().parent
SHARED = ROOT / "components/shared/case"
LINKER = COMPONENT / "linker.ld"
BOARD_CONFIG = COMPONENT / "board_config.h"
DEFAULT_OUTPUT = ROOT / "build/case-source-image"


class BuildError(RuntimeError):
    pass


def board_config_u32(name: str) -> int:
    """Read one ``UINT32_C(0x...)`` macro from board_config.h.

    board_config.h is the single documented source of truth for the
    board-routing assumptions (vectors, bank addresses, identity windows)
    this builder validates against; parsing it here instead of repeating
    the literal keeps the two from silently drifting apart.
    """
    text = BOARD_CONFIG.read_text(encoding="utf-8")
    match = re.search(
        rf"#define {re.escape(name)}\s+UINT32_C\((0x[0-9A-Fa-f]+)\)", text)
    if not match:
        raise BuildError(f"board_config.h is missing macro {name}")
    return int(match.group(1), 16)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tool(candidates: list[str]) -> str:
    for candidate in candidates:
        if os.path.isabs(candidate) and Path(candidate).is_file():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise BuildError("required build tool unavailable: " + ", ".join(candidates))


def run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode != 0:
        raise BuildError("command failed:\n  " + " ".join(command) + "\n" +
                         completed.stdout + completed.stderr)


def build(output: Path) -> dict:
    clang = tool(["/opt/homebrew/opt/llvm/bin/clang", "clang"])
    linker = tool(["/opt/homebrew/opt/lld/bin/ld.lld", "ld.lld"])
    objcopy = tool(["/opt/homebrew/opt/llvm/bin/llvm-objcopy", "llvm-objcopy"])
    nm = tool(["/opt/homebrew/opt/llvm/bin/llvm-nm", "llvm-nm"])
    output.mkdir(parents=True, exist_ok=True)
    objects = output / "objects"
    objects.mkdir(exist_ok=True)
    sources = sorted(SHARED.glob("*.c")) + sorted(COMPONENT.glob("*.c"))
    common = [
        clang, "--target=armv6m-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
        "-std=c11", "-ffreestanding", "-fno-builtin", "-fno-common",
        "-fdata-sections", "-ffunction-sections", "-Os", "-g0",
        "-Wall", "-Wextra", "-Werror", "-I", str(SHARED), "-I", str(COMPONENT),
    ]
    object_paths = []
    for source in sources:
        destination = objects / (source.stem + ".o")
        run(common + ["-c", str(source), "-o", str(destination)])
        object_paths.append(destination)
    elf = output / "case-source.elf"
    map_file = output / "case-source.map"
    run([linker, "-flavor", "gnu", "-m", "armelf", "-T", str(LINKER),
         "--Map=" + str(map_file), "--no-undefined", "--fatal-warnings",
         "-o", str(elf), *map(str, object_paths)])
    undefined = subprocess.run([nm, "-u", str(elf)], check=True, text=True,
                               capture_output=True).stdout.strip()
    if undefined:
        raise BuildError("linked Case ELF retains undefined symbols:\n" + undefined)
    unchecked = output / "case-source-unchecked.bin"
    run([objcopy, "-O", "binary", str(elf), str(unchecked)])
    raw = unchecked.read_bytes()
    raw += b"\xFF" * ((-len(raw)) & 3)
    # board_config.h is the documented source of truth for these board-
    # routing constants (stack top, flash bank base, preserved identity
    # window); read from there instead of repeating the literals.
    flash_base = board_config_u32("OPEN_CFW_CASE_FLASH_BASE")
    flash_bank_bytes = board_config_u32("OPEN_CFW_CASE_FLASH_BANK_BYTES")
    sram_base = board_config_u32("OPEN_CFW_CASE_SRAM_BASE")
    sram_bytes = board_config_u32("OPEN_CFW_CASE_SRAM_BYTES")
    stack_top = board_config_u32("OPEN_CFW_CASE_STACK_TOP")
    identity_limit = board_config_u32("OPEN_CFW_CASE_BANK1_IDENTITY_LIMIT")
    if flash_base + len(raw) > identity_limit:
        raise BuildError("raw image overlaps preserved bank-1 identity window")
    stack, reset = struct.unpack_from("<II", raw)
    if stack != stack_top or reset & 1 == 0 or not (flash_base <= reset < flash_base + len(raw)):
        raise BuildError(f"invalid Case vectors: SP={stack:#x}, reset={reset:#x}")
    checksum = sum(struct.unpack(f">{len(raw) // 4}I", raw)) & 0xFFFFFFFF
    wrapper = b"EVEN" + bytes((1, 2, 57, 0)) + struct.pack(">II", len(raw), checksum) + bytes(16)
    package = wrapper + raw
    raw_path = output / "case-source.bin"
    package_path = output / "firmware_box.bin"
    raw_path.write_bytes(raw)
    package_path.write_bytes(package)
    source_inventory = [{
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path.read_bytes()),
    } for path in [*sources, LINKER, BOARD_CONFIG]]
    report = {
        "schema_version": 1,
        "component": "G2 charging-case source image",
        "architecture": "ARMv6-M Cortex-M0+",
        "part_family": "STM32G0B0/G0B1 evidence class",
        "board_contract": {
            "flash_base": flash_base,
            "flash_bank_bytes": flash_bank_bytes,
            "bank1_base": flash_base,
            "bank2_base": flash_base + flash_bank_bytes,
            "sram_base": sram_base,
            "sram_bytes": sram_bytes,
            "stack_top": stack_top,
            "bank1_identity_limit": identity_limit,
            "confirmed_irq_slots": {
                "PVD": 1,
                "TIM2": 15,
                "USART1": 27,
                "CEC": 30,
            },
            "confirmed_usart_bases": {
                "USART3": board_config_u32("OPEN_CFW_CASE_USART3_BASE"),
                "USART4": board_config_u32("OPEN_CFW_CASE_USART4_BASE"),
            },
            "unconfirmed_defaults": {
                "link_uart": "USART1",
                "led_gpio_port": "GPIOB",
                "pmic_gpio_ports": "GPIOB,GPIOC,GPIOD",
            },
            "blocked_contracts": [
                "exact board interrupt ownership",
                "GPIO/timer routing",
                "dual-bank updater handoff",
                "preserved identity copy-forward",
            ],
        },
        "source_translation_units": len(sources),
        "undefined_symbols": 0,
        "elf": {"path": elf.name, "size": elf.stat().st_size,
                "sha256": sha256(elf.read_bytes())},
        "raw": {"path": raw_path.name, "size": len(raw), "sha256": sha256(raw)},
        "even": {"path": package_path.name, "size": len(package),
                 "sha256": sha256(package), "checksum_be_u32": checksum},
        "source_inventory": source_inventory,
        "software_link_complete": True,
        "software_package_complete": True,
        "production_routed": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_blocker": "blocked by unavailable physical evidence",
        "evidence_locked_contracts": [
            "exact board interrupt ownership", "GPIO/timer routing",
            "dual-bank updater handoff", "preserved identity copy-forward",
        ],
    }
    (output / "case-source-image-summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="g2-case-source-image-") as directory:
            report = build(Path(directory))
    else:
        report = build(args.output)
    print(json.dumps({key: report[key] for key in (
        "source_translation_units", "undefined_symbols",
        "software_link_complete", "software_package_complete",
        "production_routed", "hardware_validation")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as error:
        raise SystemExit(f"Case source image build failed: {error}") from error
