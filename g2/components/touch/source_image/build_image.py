#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the source-backed ARMv6-M Touch ELF, raw image, and FWPK package."""

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
SHARED = ROOT / "components/shared/touch"
LINKER = COMPONENT / "linker.ld"
DEFAULT_OUTPUT = ROOT / "build/touch-source-image"


class BuildError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def crc32c(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x82F63B78 if crc & 1 else 0)
    return crc ^ 0xFFFFFFFF


def tool(explicit: str | None, candidates: list[str]) -> str:
    if explicit:
        return explicit
    for candidate in candidates:
        if os.path.isabs(candidate) and Path(candidate).is_file():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise BuildError(f"required build tool unavailable: {', '.join(candidates)}")


def run(command: list[str]) -> None:
    completed = subprocess.run(command, text=True, capture_output=True)
    if completed.returncode != 0:
        raise BuildError(
            "command failed:\n  " + " ".join(command) + "\n" +
            completed.stdout + completed.stderr)


def build(output: Path, clang: str | None = None,
          linker: str | None = None, objcopy: str | None = None,
          nm: str | None = None) -> dict:
    clang_tool = tool(clang, [
        "/opt/homebrew/opt/llvm/bin/clang", "clang",
    ])
    linker_tool = tool(linker, [
        "/opt/homebrew/opt/lld/bin/ld.lld", "ld.lld",
    ])
    objcopy_tool = tool(objcopy, [
        "/opt/homebrew/opt/llvm/bin/llvm-objcopy", "llvm-objcopy",
    ])
    nm_tool = tool(nm, [
        "/opt/homebrew/opt/llvm/bin/llvm-nm", "llvm-nm",
    ])
    output.mkdir(parents=True, exist_ok=True)
    objects = output / "objects"
    objects.mkdir(exist_ok=True)

    sources = sorted(SHARED.glob("*.c")) + sorted(COMPONENT.glob("*.c"))
    assembly = sorted(SHARED.glob("*.S"))
    common = [
        clang_tool, "--target=armv6m-none-eabi", "-mcpu=cortex-m0plus",
        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
        "-fno-common", "-fdata-sections", "-ffunction-sections",
        "-Os", "-g0", "-Wall", "-Wextra", "-Werror",
        "-I", str(SHARED), "-I", str(COMPONENT),
    ]
    object_paths: list[Path] = []
    for source in sources:
        destination = objects / (source.stem + ".o")
        run(common + ["-c", str(source), "-o", str(destination)])
        object_paths.append(destination)
    for source in assembly:
        destination = objects / (source.stem + ".o")
        run([
            clang_tool, "--target=armv6m-none-eabi", "-mcpu=cortex-m0plus",
            "-mthumb", "-ffreestanding", "-x", "assembler-with-cpp",
            "-I", str(SHARED), "-c", str(source), "-o", str(destination),
        ])
        object_paths.append(destination)

    elf = output / "touch-source.elf"
    map_file = output / "touch-source.map"
    run([
        linker_tool, "-flavor", "gnu", "-m", "armelf", "-T", str(LINKER),
        "--Map=" + str(map_file), "--no-undefined", "--fatal-warnings",
        "-o", str(elf), *map(str, object_paths),
    ])
    undefined = subprocess.run(
        [nm_tool, "-u", str(elf)], check=True, text=True,
        capture_output=True).stdout.strip()
    if undefined:
        raise BuildError("linked Touch ELF retains undefined symbols:\n" + undefined)

    raw_unchecked = output / "touch-source-unchecked.bin"
    run([objcopy_tool, "-O", "binary", str(elf), str(raw_unchecked)])
    body = raw_unchecked.read_bytes()
    body += b"\xFF" * ((-len(body)) & 3)
    if len(body) + 4 > 65536:
        raise BuildError("Touch raw image plus checksum exceeds 64 KiB flash")
    trailing_crc = crc32c(body)
    raw = body + struct.pack("<I", trailing_crc)
    raw_path = output / "touch-source.bin"
    raw_path.write_bytes(raw)

    if len(raw) < 8:
        raise BuildError("Touch raw image has no vector table")
    stack, reset = struct.unpack_from("<II", raw)
    if stack != 0x20002000 or reset & 1 == 0 or reset >= len(raw):
        raise BuildError(
            f"invalid Touch vectors: SP={stack:#x}, reset={reset:#x}, size={len(raw):#x}")
    wrapper = (
        b"FWPK" + bytes.fromhex("01000202") + struct.pack("<II", 1, 0) +
        struct.pack("<IIII", 3, len(raw), 0x20, crc32c(raw))
    )
    package = wrapper + raw
    package_path = output / "firmware_touch.bin"
    package_path.write_bytes(package)

    source_inventory = [{
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256(path.read_bytes()),
    } for path in [*sources, *assembly, LINKER]]
    report = {
        "schema_version": 1,
        "component": "G2 Touch source image",
        "architecture": "ARMv6-M Cortex-M0+",
        "part_family": "CY8C4046FNI / PSoC 4000T",
        "source_translation_units": len(sources) + len(assembly),
        "undefined_symbols": 0,
        "elf": {"path": elf.name, "size": elf.stat().st_size,
                "sha256": sha256(elf.read_bytes())},
        "raw": {"path": raw_path.name, "size": len(raw),
                "sha256": sha256(raw), "trailing_crc32c": trailing_crc},
        "fwpk": {"path": package_path.name, "size": len(package),
                 "sha256": sha256(package), "record_crc32c": crc32c(raw)},
        "source_inventory": source_inventory,
        "software_link_complete": True,
        "production_routed": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_blocker": "blocked by unavailable physical evidence",
    }
    (output / "touch-source-image-summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true",
                        help="build in a temporary directory and retain no artifacts")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="g2-touch-source-image-") as directory:
            report = build(Path(directory))
    else:
        report = build(args.output)
    print(json.dumps({key: report[key] for key in (
        "source_translation_units", "undefined_symbols",
        "software_link_complete", "production_routed",
        "hardware_validation")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BuildError as error:
        raise SystemExit(f"Touch source image build failed: {error}") from error
