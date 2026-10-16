#!/usr/bin/env python3
"""Compile native-backed Apollo font flash cells and GPIO base table."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/font_gpio_runtime_cells.c"
USERS = [G2 / "components/audio/uart_thread_source_candidate" / name
         for name in ("role_get.c", "display_font_flash_lock.c", "display_brightness_prepare.c")]
BASE = G2 / "build/c-firmware/20261014/main-role-display-runtime/apollo-main-role-display-runtime.o"
OUT = G2 / "build/c-firmware/20261014/main-font-gpio-runtime"
RAM = {
    "audio_uart_font_flash_device": (0x20074544, (0x470014, 0x4708a4, 0x4710ac), 4),
    "audio_uart_font_flash_mutex": (0x20074548, (0x47001c,), 4),
}
GPIO = {
    "audio_uart_gpio_input_base": (0x40010404, 0x48174c),
    "audio_uart_gpio_output_base": (0x40010420, 0x481750),
    "audio_uart_gpio_enable_base": (0x40010474, 0x481754),
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
    for name, (address, literals, _) in RAM.items():
        for literal in literals:
            if not vaddr <= literal <= vaddr + filesz - 4:
                raise RuntimeError(f"unmapped native literal: {literal:#x}")
            found = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
            if found != address:
                raise RuntimeError(f"font flash RAM contract changed: {name} {found:#x}")
        if name not in users or f".g2_ram_{address:08x}" not in source:
            raise RuntimeError(f"font flash C contract changed: {name}")
    for name, (address, literal) in GPIO.items():
        if struct.unpack_from("<I", raw, offset + literal - vaddr)[0] != address:
            raise RuntimeError(f"GPIO native table changed: {name}")
        if name not in users or f"0x{address:08x}u" not in source:
            raise RuntimeError(f"GPIO C provider changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "font_gpio_runtime_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(RAM) | set(GPIO) or names(obj, "-u"):
        raise RuntimeError("C font/GPIO symbol set changed")
    expected = {f".g2_ram_{address:08x}": size for address, _, size in RAM.values()}
    if section_sizes(obj) != expected:
        raise RuntimeError("C font flash section sizes changed")
    raw_obj = obj.read_bytes()
    for address, _ in GPIO.values():
        if raw_obj.count(struct.pack("<I", address)) != 1:
            raise RuntimeError(f"compiled GPIO base value changed: {address:#x}")
    before = names(BASE, "-u")
    if not set(RAM) | set(GPIO) <= before:
        raise RuntimeError("Apollo Main font/GPIO imports changed")
    linked = OUT / "apollo-main-font-gpio-runtime.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(RAM) | set(GPIO) or after - before:
        raise RuntimeError(f"unexpected font/GPIO import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_FONT_GPIO_RUNTIME_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_ram": {name: {"ram": hex(address), "literals": [hex(x) for x in literals], "bytes": size}
                       for name, (address, literals, size) in RAM.items()},
        "native_gpio": {name: {"value": hex(address), "literal": hex(literal)}
                        for name, (address, literal) in GPIO.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(path.relative_to(ROOT)): sha(path) for path in USERS},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Font flash pointer startup values and final RAM placement remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
