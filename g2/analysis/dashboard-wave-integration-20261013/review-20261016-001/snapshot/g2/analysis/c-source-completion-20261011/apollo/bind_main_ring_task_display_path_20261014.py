#!/usr/bin/env python3
"""Compile native-backed ring task buffers and display source path."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/ring_task_display_path_data.c"
USERS = [G2 / "components/audio" / path for path in (
    "uart_thread_source_candidate/display_ring_task_producer.c",
    "uart_thread_source_candidate/display_init.c",
    "uart_thread_source_candidate/display_driver.c")]
BASE = G2 / "build/c-firmware/20261014/main-uart-queue-runtime/apollo-main-uart-queue-runtime.o"
OUT = G2 / "build/c-firmware/20261014/main-ring-task-display-path"
RAM = {
    "audio_uart_ring_thread_cb": (0x20072290, 0x75b8ac, 112),
    "audio_uart_ring_thread_stack": (0x2036be40, 0x75b8b4, 4096),
}
DISPLAY_PATH = b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\lvgl_ambiq_porting\\lv_ambiq_display.c\0"


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
            raise RuntimeError(f"ring task RAM contract changed: {name} {found:#x}")
    if struct.unpack_from("<I", raw, offset + 0x4738f0 - vaddr)[0] != 0x6dd7d4:
        raise RuntimeError("native display source pointer changed")
    if raw[offset + 0x6dd7d4 - vaddr:offset + 0x6dd7d4 - vaddr + len(DISPLAY_PATH)] != DISPLAY_PATH:
        raise RuntimeError("native display source bytes changed")
    if "audio_uart_display_source_path" not in source + users:
        raise RuntimeError("display source C user/provider changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ring_task_display_path_data.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(RAM) | {"audio_uart_display_source_path"} or names(obj, "-u"):
        raise RuntimeError("C ring task/display symbol set changed")
    expected = {f".g2_ram_{address:08x}": size for address, _, size in RAM.values()}
    if section_sizes(obj) != expected:
        raise RuntimeError("C ring task section sizes changed")
    if DISPLAY_PATH not in obj.read_bytes():
        raise RuntimeError("compiled display source bytes changed")
    before = names(BASE, "-u")
    resolved = set(RAM) | {"audio_uart_display_source_path"}
    if not resolved <= before:
        raise RuntimeError("Apollo Main ring task/display imports changed")
    linked = OUT / "apollo-main-ring-task-display-path.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != resolved or after - before:
        raise RuntimeError(f"unexpected ring task/display import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_RING_TASK_DISPLAY_PATH_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_ram": {name: {"ram": hex(address), "literal": hex(literal), "bytes": size}
                       for name, (address, literal, size) in RAM.items()},
        "native_display_source": {"pointer_literal": "0x4738f0", "string_address": "0x6dd7d4",
                                  "bytes_sha256": hashlib.sha256(DISPLAY_PATH).hexdigest()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(path.relative_to(ROOT)): sha(path) for path in USERS},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Ring task buffer startup values and final RAM placement remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
