#!/usr/bin/env python3
"""Bind native-literal-backed display context RAM cells into Apollo Main."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_context_runtime_cells.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_context_locale.c"
BASE = G2 / "build/c-firmware/20261014/main-page-locale-lookup/apollo-main-page-locale-lookup.o"
OUT = G2 / "build/c-firmware/20261014/main-display-context-runtime"
CONTRACTS = {
    "audio_uart_display_locale_index": (0x20000030, 0x471ac4),
    "audio_uart_display_context_list_cell": (0x200746c8, 0x460120),
    "audio_uart_display_context_active_cell": (0x200746cc, 0x46011c),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def sections_by_name(path):
    raw = path.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("compiled object ELF format changed")
    shoff = struct.unpack_from("<I", raw, 32)[0]
    shentsize, shnum = struct.unpack_from("<HH", raw, 46)
    sections = [struct.unpack_from("<IIIIIIIIII", raw, shoff + i * shentsize)
                for i in range(shnum)]
    names_section = sections[struct.unpack_from("<H", raw, 50)[0]]
    found = {}
    for section in sections:
        start = names_section[4] + section[0]
        end = raw.index(b"\0", start)
        name = raw[start:end].decode()
        if name.startswith(".g2_ram_"):
            found[name] = section[5]
    return found


def main():
    raw = NATIVE.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("native ELF format changed")
    phoff = struct.unpack_from("<I", raw, 28)[0]
    if struct.unpack_from("<H", raw, 44)[0] != 1:
        raise RuntimeError("native ELF segment count changed")
    kind, offset, vaddr, _, filesz, _, _, _ = struct.unpack_from("<IIIIIIII", raw, phoff)
    if kind != 1:
        raise RuntimeError("native load segment changed")
    user = USER.read_text()
    source = SOURCE.read_text()
    for name, (ram, literal) in CONTRACTS.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"unmapped native literal: {name}")
        actual = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
        if actual != ram or name not in user or f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"native/user/source RAM contract changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_context_runtime_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("C display context cell symbols changed")
    expected = {f".g2_ram_{ram:08x}": 4 for ram, _ in CONTRACTS.values()}
    if sections_by_name(obj) != expected:
        raise RuntimeError("C display context cell sizes changed")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main display context imports changed")
    linked = OUT / "apollo-main-display-context-runtime.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected display context import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_CONTEXT_RUNTIME_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_cells": {name: {"ram": hex(ram), "literal": hex(literal), "bytes": 4}
                         for name, (ram, literal) in CONTRACTS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["The 157-entry locale lookup table at RAM 0x20002928 has no recovered source-owned contents.",
                   "Cell startup values, final RAM placement, and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
