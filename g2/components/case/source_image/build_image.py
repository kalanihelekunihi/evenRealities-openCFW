#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the source-backed STM32G0 charging-case ELF/raw/EVEN image."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMPONENT = Path(__file__).resolve().parent
SHARED = ROOT / "components/shared/case"
LINKER = COMPONENT / "linker.ld"
DEFAULT_OUTPUT = ROOT / "build/case-source-image"


class BuildError(RuntimeError):
    pass


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
    if len(raw) > 0x3F000:
        raise BuildError("raw image overlaps preserved bank-1 identity window")
    stack, reset = struct.unpack_from("<II", raw)
    if stack != 0x20002C88 or reset & 1 == 0 or not (0x08000000 <= reset < 0x08000000 + len(raw)):
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
    } for path in [*sources, LINKER]]
    report = {
        "schema_version": 1,
        "component": "G2 charging-case source image",
        "architecture": "ARMv6-M Cortex-M0+",
        "part_family": "STM32G0B0/G0B1 evidence class",
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
        "hardware_validation": "deferred by project direction",
        "hardware_blocker": "deferred by project direction",
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
