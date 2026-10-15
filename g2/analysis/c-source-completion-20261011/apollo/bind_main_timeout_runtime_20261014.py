#!/usr/bin/env python3
"""Bind exact timeout diagnostic aliases and native-backed RAM cells."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/timeout_runtime_cells.c"
USER_RAM = G2 / "components/audio/uart_thread_source_candidate/timeout_submit.c"
USER_STRINGS = G2 / "components/audio/uart_thread_source_candidate/send_timeout_end.c"
BASE = G2 / "build/c-firmware/20261014/main-display-context-runtime/apollo-main-display-context-runtime.o"
OUT = G2 / "build/c-firmware/20261014/main-timeout-runtime"
RAM = {
    "audio_uart_timeout_queue": (0x20074aa0, 0x491618, 4),
    "audio_uart_timeout_mutex": (0x20074aa4, 0x491650, 4),
    "audio_uart_timeout_running_state": (0x20075031, 0x491630, 1),
}
# Each target is already compiled in BASE; these native names refer to its entry.
ALIASES = {
    "audio_uart_timeout_module": "audio_uart_begin0_module",
    "audio_uart_timeout_source": "audio_uart_begin0_source",
    "audio_uart_timeout_module_peer": "audio_uart_begin0_module",
    "audio_uart_timeout_source_peer": "audio_uart_begin0_source",
    "audio_uart_timeout_module_display": "audio_uart_begin0_module",
    "audio_uart_timeout_source_display": "audio_uart_begin0_source",
    "audio_uart_timeout_compact_peer": "audio_uart_timeout_compact",
    "audio_uart_timeout_compact_display": "audio_uart_timeout_compact",
    "audio_uart_timeout_submit_compact_peer": "audio_uart_timeout_submit_compact",
}
NATIVE_STRINGS = {
    "audio_uart_begin0_module": (0x77c07c, b"sync.module.framework"),
    "audio_uart_begin0_source": (
        0x705fb8, b"D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c"),
    "audio_uart_timeout_compact": (
        0x74414c, b"[sync.module.framework]%s :timeout running"),
    "audio_uart_timeout_submit_compact": (
        0x744120, b"[sync.module.framework]submit work failed,"),
}
NATIVE_POINTERS = {
    0x45d7cc: 0x705fb8, 0x45e010: 0x705fb8, 0x45e8bc: 0x705fb8,
    0x45d7d0: 0x77c07c, 0x45e014: 0x77c07c, 0x45e8c0: 0x77c07c,
    0x45e008: 0x74414c, 0x45ebb8: 0x74414c,
    0x45dffc: 0x744120, 0x45e654: 0x744120,
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def elf_sections_symbols(path):
    raw = path.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("compiled object ELF format changed")
    shoff = struct.unpack_from("<I", raw, 32)[0]
    shentsize, shnum = struct.unpack_from("<HH", raw, 46)
    sections = [struct.unpack_from("<IIIIIIIIII", raw, shoff + i * shentsize)
                for i in range(shnum)]
    names_section = sections[struct.unpack_from("<H", raw, 50)[0]]
    sizes = {}
    for section in sections:
        start = names_section[4] + section[0]
        end = raw.index(b"\0", start)
        name = raw[start:end].decode()
        if name.startswith(".g2_ram_"):
            sizes[name] = section[5]
    symbols = {}
    for section in sections:
        if section[1] != 2:
            continue
        strings = sections[section[6]]
        for pos in range(section[4], section[4] + section[5], section[9]):
            name_off, value, size, _, _, shndx = struct.unpack_from("<IIIBBH", raw, pos)
            end = raw.index(b"\0", strings[4] + name_off)
            name = raw[strings[4] + name_off:end].decode()
            if name not in NATIVE_STRINGS:
                continue
            target = sections[shndx]
            symbols[name] = raw[target[4] + value:target[4] + value + size]
    return sizes, symbols


def main():
    raw = NATIVE.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("native ELF format changed")
    phoff = struct.unpack_from("<I", raw, 28)[0]
    kind, offset, vaddr, _, filesz, _, _, _ = struct.unpack_from("<IIIIIIII", raw, phoff)
    if kind != 1:
        raise RuntimeError("native load segment changed")

    def word(address):
        if not vaddr <= address <= vaddr + filesz - 4:
            raise RuntimeError(f"native pointer unmapped: {address:#x}")
        return struct.unpack_from("<I", raw, offset + address - vaddr)[0]

    for literal, expected in NATIVE_POINTERS.items():
        if word(literal) != expected:
            raise RuntimeError(f"timeout string literal changed: {literal:#x}")
    for name, (address, value) in NATIVE_STRINGS.items():
        pos = offset + address - vaddr
        if raw[pos:pos + len(value) + 1] != value + b"\0":
            raise RuntimeError(f"native timeout string changed: {name}")
    base_sizes, base_strings = elf_sections_symbols(BASE)
    if any(base_strings.get(name) != value + b"\0"
           for name, (_, value) in NATIVE_STRINGS.items()):
        raise RuntimeError("existing C timeout string bytes differ from native")
    users_ram = USER_RAM.read_text()
    users_strings = USER_STRINGS.read_text()
    source = SOURCE.read_text()
    for name, (ram, literal, _) in RAM.items():
        if word(literal) != ram or name not in users_ram or f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"timeout RAM contract changed: {name}")
    for name in ALIASES:
        if name not in users_strings:
            raise RuntimeError(f"timeout alias user changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "timeout_runtime_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(RAM) or names(obj, "-u"):
        raise RuntimeError("C timeout RAM symbol set changed")
    sizes, _ = elf_sections_symbols(obj)
    expected_sizes = {f".g2_ram_{ram:08x}": size for ram, _, size in RAM.values()}
    if sizes != expected_sizes:
        raise RuntimeError(f"C timeout RAM sizes changed: {sizes}")
    before = names(BASE, "-u")
    resolved = set(RAM) | set(ALIASES)
    if not resolved <= before or not set(ALIASES.values()) <= names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main timeout import/provider set changed")
    linked = OUT / "apollo-main-timeout-runtime.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    *(f"--defsym={name}={target}" for name, target in ALIASES.items()),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != resolved or after - before:
        raise RuntimeError(f"unexpected timeout import delta: {before-after}, {after-before}")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", str(linked)], text=True)
    addresses = {p[-1]: int(p[0], 16) for line in output.splitlines()
                 if len(p := line.split()) == 3 and p[-1] in set(ALIASES) | set(ALIASES.values())}
    if any(addresses[name] != addresses[target] for name, target in ALIASES.items()):
        raise RuntimeError("timeout aliases no longer share target addresses")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_TIMEOUT_RUNTIME_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_pointer_literals": {hex(k): hex(v) for k, v in NATIVE_POINTERS.items()},
        "native_ram": {name: {"ram": hex(ram), "literal": hex(literal), "bytes": size}
                       for name, (ram, literal, size) in RAM.items()},
        "same_entry_aliases": ALIASES,
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in (USER_RAM, USER_STRINGS)},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Timeout RAM startup values and final placement remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
