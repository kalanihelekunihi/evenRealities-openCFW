#!/usr/bin/env python3
"""Bind individually observed UART sync RAM cells into Apollo Main C composition."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/sync_runtime_cells.c"
USERS = tuple(G2 / f"components/audio/uart_thread_source_candidate/{name}.c" for name in
              ("sync_reset", "sync_write", "sync_hal", "process_receive", "process_event4"))
BASE = G2 / "build/c-firmware/20261014/main-sync-receive-strings/apollo-main-sync-receive-strings.o"
OUT = G2 / "build/c-firmware/20261014/main-sync-runtime-cells"
CONTRACTS = {
    "g2_uart_sync_driver": (0x20074610, 0x584e48, 4),
    "g2_uart_sync_callback_cell": (0x20074618, 0x584e6c, 4),
    "g2_uart_sync_semaphore_handle": (0x2007461c, 0x584e54, 4),
    "g2_uart_sync_mutex": (0x20074620, 0x584e74, 4),
    "g2_uart_sync_module": (0x200749c4, 0x45dd64, 4),
    "g2_uart_sync_semaphore": (0x200749d4, 0x45dd38, 4),
    "g2_uart_sync_started": (0x20074fc9, 0x584e4c, 1),
    "g2_uart_sync_write_error": (0x20074fca, 0x584e58, 1),
    "g2_uart_sync_tx_buffer": (0x20379da0, 0x584e84, 0x400),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def section_sizes(path):
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
        raise RuntimeError("native ELF load segment changed")
    users = "\n".join(p.read_text() for p in USERS)
    source = SOURCE.read_text()
    for name, (ram, literal, _) in CONTRACTS.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"unmapped native literal: {name}")
        actual = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
        if actual != ram or name not in users or f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"native/user/source RAM contract changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "sync_runtime_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("C runtime cell symbol contract changed")
    sections = section_sizes(obj)
    expected = {f".g2_ram_{ram:08x}": size for ram, _, size in CONTRACTS.values()}
    if sections != expected:
        raise RuntimeError(f"C runtime cell sizes changed: {sections}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main sync runtime imports changed")
    linked = OUT / "apollo-main-sync-runtime-cells.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected sync runtime import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_SYNC_RUNTIME_CELLS_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_cells": {name: {"ram": hex(ram), "literal": hex(literal), "size": size}
                         for name, (ram, literal, size) in CONTRACTS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in USERS},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["RAM addresses are literal backed but final section placement is unverified.",
                   "Cell startup values and device behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
