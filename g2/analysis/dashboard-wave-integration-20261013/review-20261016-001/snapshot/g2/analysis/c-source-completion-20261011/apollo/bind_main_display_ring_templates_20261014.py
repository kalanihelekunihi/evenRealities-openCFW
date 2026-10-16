#!/usr/bin/env python3
"""Compile native-backed Apollo display and ring request templates."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_template_data.c"
USERS = [G2 / "components/audio" / path for path in (
    "uart_thread_source_candidate/display_driver.c",
    "uart_thread_source_candidate/ring_sync.c")]
BASE = G2 / "build/c-firmware/20261014/main-display-control-lock-data/apollo-main-display-control-lock-data.o"
OUT = G2 / "build/c-firmware/20261014/main-display-ring-templates"
DATA = {
    "audio_uart_display_create_error": (0x473904, 0x77f950, b"lv_disp_drv_setup\0"),
    "audio_uart_ring_status_template": (0x47d904, 0x78ede4, bytes((6, 0, 1, 0, 0, 0, 0, 0))),
    "audio_uart_ring_query_template": (0x47d908, 0x78edec, bytes((5, 0, 1, 0, 0, 0, 0, 0))),
}


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


def symbol_bytes(path):
    raw = path.read_bytes()
    shoff = struct.unpack_from("<I", raw, 32)[0]
    shentsize, shnum = struct.unpack_from("<HH", raw, 46)
    sections = [struct.unpack_from("<IIIIIIIIII", raw, shoff + i * shentsize)
                for i in range(shnum)]
    found = {}
    for section in sections:
        if section[1] != 2:
            continue
        strings = sections[section[6]]
        for pos in range(section[4], section[4] + section[5], section[9]):
            name_off, value, size, _, _, shndx = struct.unpack_from("<IIIBBH", raw, pos)
            start = strings[4] + name_off
            name = raw[start:raw.index(b"\0", start)].decode()
            if name in DATA:
                target = sections[shndx]
                found[name] = raw[target[4] + value:target[4] + value + size]
    return found


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
    for name, (literal, address, value) in DATA.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"unmapped native literal: {literal:#x}")
        found = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
        if found != address or name not in users or name not in source:
            raise RuntimeError(f"display/ring native pointer contract changed: {name} {found:#x}")
        if raw[offset + address - vaddr:offset + address - vaddr + len(value)] != value:
            raise RuntimeError(f"display/ring native bytes changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_ring_template_data.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    resolved = set(DATA)
    if names(obj, "-g", "--defined-only") != resolved or names(obj, "-u"):
        raise RuntimeError("C display/ring template symbol set changed")
    if section_sizes(obj):
        raise RuntimeError("unexpected display/ring RAM section")
    compiled = symbol_bytes(obj)
    for name, (_, _, value) in DATA.items():
        if compiled.get(name) != value:
            raise RuntimeError(f"compiled display/ring bytes changed: {name}")
    before = names(BASE, "-u")
    if not resolved <= before:
        raise RuntimeError("Apollo Main display/ring template imports changed")
    linked = OUT / "apollo-main-display-ring-templates.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != resolved or after - before:
        raise RuntimeError(f"unexpected display/ring template import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_RING_TEMPLATES_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_data": {name: {"literal": hex(literal), "address": hex(address),
                               "bytes_sha256": hashlib.sha256(value).hexdigest()}
                        for name, (literal, address, value) in DATA.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(path.relative_to(ROOT)): sha(path) for path in USERS},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Final ROM placement and image composition remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
