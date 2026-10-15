#!/usr/bin/env python3
"""Compile native-backed Apollo dashboard buffers and file mutex."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/dashboard_file_runtime_cells.c"
USERS = [G2 / "components/audio/uart_thread_source_candidate" / name
         for name in ("display_file_api.c", "service_prepare8.c",
                      "dashboard_apply_layout.c")]
BASE = G2 / "build/c-firmware/20261014/main-audio-clock-pin-config/apollo-main-audio-clock-pin-config.o"
OUT = G2 / "build/c-firmware/20261014/main-dashboard-file-runtime"
RAM = {
    "audio_file_api_mutex": (0x200748f4, 0x474e48, 4),
    "audio_uart_dashboard_ready": (0x20074fa5, 0x50215c, 1),
    "audio_uart_dashboard_file_buffer": (0x2036ae40, 0x502654, 4096),
    "audio_uart_dashboard_decoded": (0x2037cc68, 0x502660, 188),
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
    for name, (address, literal, _) in RAM.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"unmapped native literal: {literal:#x}")
        found = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
        if found != address or name not in users or f".g2_ram_{address:08x}" not in source:
            raise RuntimeError(f"dashboard/file RAM contract changed: {name} {found:#x}")
    if struct.unpack_from("<I", raw, offset + 0x502678 - vaddr)[0] != 0x20074fa5:
        raise RuntimeError("second dashboard ready literal changed")
    if 0x2036ae40 + 4096 != 0x2036be40:
        raise RuntimeError("dashboard buffer/ring stack boundary changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "dashboard_file_runtime_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(RAM) or names(obj, "-u"):
        raise RuntimeError("C dashboard/file symbol set changed")
    expected = {f".g2_ram_{address:08x}": size for address, _, size in RAM.values()}
    if section_sizes(obj) != expected:
        raise RuntimeError("C dashboard/file section sizes changed")
    before = names(BASE, "-u")
    if not set(RAM) <= before:
        raise RuntimeError("Apollo Main dashboard/file imports changed")
    linked = OUT / "apollo-main-dashboard-file-runtime.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(RAM) or after - before:
        raise RuntimeError(f"unexpected dashboard/file import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_DASHBOARD_FILE_RUNTIME_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_ram": {name: {"ram": hex(address), "literal": hex(literal), "bytes": size}
                       for name, (address, literal, size) in RAM.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(path.relative_to(ROOT)): sha(path) for path in USERS},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Dashboard/file startup values and final RAM placement remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
