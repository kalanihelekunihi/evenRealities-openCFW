#!/usr/bin/env python3
"""Bind native-literal-backed UART thread RAM cells and observed buffer slices."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/thread_runtime_cells.c"
USER = G2 / "components/audio/uart_thread_source_candidate/thread.c"
BASE = G2 / "build/c-firmware/20261014/main-thread-log-strings/apollo-main-thread-log-strings.o"
OUT = G2 / "build/c-firmware/20261014/main-thread-runtime-cells"
# symbol: native thread literal-pool word, RAM address, observed C slice bytes
CONTRACTS = {
    "g2_uart_thread_event": (0x541a8c, 0x20074b10, 4),
    "g2_uart_thread_transport": (0x541a88, 0x20074b14, 4),
    "g2_uart_thread_mutex": (0x541a94, 0x20074b18, 4),
    "g2_uart_thread_initialize_callback": (0x541acc, 0x20000658, 4),
    "g2_uart_command": (0x541ad8, 0x20074080, 11),
    "g2_uart_rx_buffer": (0x541adc, 0x2006c930, 1024),
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
    user = USER.read_text()
    source = SOURCE.read_text()
    if "g2_uart_command+1u,10u" not in user or "g2_uart_rx_buffer,1024u" not in user:
        raise RuntimeError("UART thread buffer-use size contract changed")
    for name, (literal, ram, size) in CONTRACTS.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"unmapped native literal: {name}")
        actual = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
        if actual != ram or name not in user or f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"native/user/source RAM contract changed: {name}")
        if size not in (4, 11, 1024):
            raise RuntimeError(f"unexpected RAM slice size: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "thread_runtime_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("C runtime cell symbol contract changed")
    sections = section_sizes(obj)
    expected = {f".g2_ram_{ram:08x}": size for _, ram, size in CONTRACTS.values()}
    if sections != expected:
        raise RuntimeError(f"C runtime cell sizes changed: {sections}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main UART thread imports changed")
    linked = OUT / "apollo-main-thread-runtime-cells.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected UART thread import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_THREAD_RUNTIME_CELLS_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_cells": {name: {"pool_literal": hex(literal), "ram": hex(ram),
                                "observed_slice_bytes": size}
                         for name, (literal, ram, size) in CONTRACTS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["11 command bytes are the observed minimum, not the proven full allocation.",
                   "Final RAM placement, callback initialization, and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
