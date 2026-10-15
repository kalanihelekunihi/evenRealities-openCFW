#!/usr/bin/env python3
"""Compile native-backed Apollo UART queue and ring-worn cells."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/uart_queue_runtime_cells.c"
USERS = [G2 / "components/audio" / path for path in (
    "uart_thread_source_candidate/ready.c",
    "uart_thread_source_candidate/display_ring_send_packet_children.c")]
BASE = G2 / "build/c-firmware/20261014/main-uart-session-runtime/apollo-main-uart-session-runtime.o"
OUT = G2 / "build/c-firmware/20261014/main-uart-queue-runtime"
RAM = {
    "g2_uart_tinyframe": (0x200749c4, 0x45dd64, 4),
    "g2_uart_send_queue": (0x200749cc, 0x45ebc8, 4),
    "g2_uart_send_queue_control": (0x20072df8, 0x77c174, 0x50),
    "g2_uart_send_queue_storage": (0x2006e860, 0x77c17c, 0x258),
    "audio_uart_ring_worn": (0x2007500c, 0x472c20, 1),
}
EXTRA_POINTERS = {0x45ebdc: 0x200749c4, 0x45d068: 0x200749cc,
                  0x4651c0: 0x200749cc, 0x465d54: 0x200749cc,
                  0x465fe8: 0x200749cc}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    rows = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in rows.splitlines() if row.strip()}


def section_sizes(path):
    raw = path.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("compiled object ELF format changed")
    shoff = struct.unpack_from("<I", raw, 32)[0]
    shentsize, shnum = struct.unpack_from("<HH", raw, 46)
    sections = [struct.unpack_from("<IIIIIIIIII", raw, shoff + i * shentsize)
                for i in range(shnum)]
    strings = sections[struct.unpack_from("<H", raw, 50)[0]]
    result = {}
    for section in sections:
        start = strings[4] + section[0]
        name = raw[start:raw.index(b"\0", start)].decode()
        if name.startswith(".g2_ram_"):
            result[name] = section[5]
    return result


def main():
    raw = NATIVE.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("native ELF format changed")
    phoff = struct.unpack_from("<I", raw, 28)[0]
    kind, offset, vaddr, _, filesz, _, _, _ = struct.unpack_from("<IIIIIIII", raw, phoff)
    if kind != 1:
        raise RuntimeError("native load segment changed")
    source = SOURCE.read_text()
    users = "\n".join(path.read_text() for path in USERS)
    for name, (address, literal, _) in RAM.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"unmapped native literal: {literal:#x}")
        found = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
        if found != address or name not in users or f".g2_ram_{address:08x}" not in source:
            raise RuntimeError(f"UART queue RAM contract changed: {name} {found:#x}")
    for literal, address in EXTRA_POINTERS.items():
        if struct.unpack_from("<I", raw, offset + literal - vaddr)[0] != address:
            raise RuntimeError(f"extra UART queue pointer changed: {literal:#x}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "uart_queue_runtime_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(RAM) or names(obj, "-u"):
        raise RuntimeError("C UART queue symbol set changed")
    expected = {f".g2_ram_{address:08x}": size for address, _, size in RAM.values()}
    if section_sizes(obj) != expected:
        raise RuntimeError("C UART queue section sizes changed")
    before = names(BASE, "-u")
    if not set(RAM) <= before:
        raise RuntimeError("Apollo Main UART queue imports changed")
    linked = OUT / "apollo-main-uart-queue-runtime.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(RAM) or after - before:
        raise RuntimeError(f"unexpected UART queue import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_UART_QUEUE_RUNTIME_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_ram": {name: {"ram": hex(address), "literal": hex(literal), "bytes": size}
                       for name, (address, literal, size) in RAM.items()},
        "extra_native_pointer_literals": {hex(literal): hex(address)
                                          for literal, address in EXTRA_POINTERS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(path.relative_to(ROOT)): sha(path) for path in USERS},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["UART queue startup values and final RAM placement remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
