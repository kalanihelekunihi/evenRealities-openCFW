#!/usr/bin/env python3
"""Compile UART thread log operands with native pool and C byte checks."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/thread_log_strings.c"
USER = G2 / "components/audio/uart_thread_source_candidate/thread.c"
BASE = G2 / "build/c-firmware/20261014/main-sync-runtime-cells/apollo-main-sync-runtime-cells.o"
OUT = G2 / "build/c-firmware/20261014/main-thread-log-strings"
# symbol: native literal-pool word, native string address, exact ASCII bytes
CONTRACTS = {
    "g2_uart_log_module": (0x541aa4, 0x7846d0, b"sync.module.uart"),
    "g2_uart_log_file": (0x541aa0, 0x710b64,
                         b"D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\uart_sync.c"),
    "g2_uart_log_function": (0x541a9c, 0x7846bc, b"uart_thread_handler"),
    "g2_uart_mutex_error": (0x541a98, 0x75c180, b"Failed to create uart sender mutex"),
    "g2_uart_mutex_error_short": (
        0x541aa8, 0x725098, b"[sync.module.uart]Failed to create uart sender mutex"),
    "g2_uart_event_error": (0x541aac, 0x75c1a4, b"Failed to create uart EventFlags"),
    "g2_uart_event_error_short": (
        0x541ab0, 0x72fa4c, b"[sync.module.uart]Failed to create uart EventFlags"),
    "g2_uart_transport_error": (
        0x541abc, 0x745c74, b"Failed to create uart receive stream buffer"),
    "g2_uart_transport_error_short": (
        0x541ac0, 0x710ba4, b"[sync.module.uart]Failed to create uart receive stream buffer"),
    "g2_uart_ready_error": (0x541ac4, 0x77d0fc, b"sync module init failed"),
    "g2_uart_ready_error_short": (
        0x541ac8, 0x745ca0, b"[sync.module.uart]sync module init failed"),
    "g2_uart_command_log": (0x541ad0, 0x7672d0, b"xStreamBufferReceive val :%s"),
    "g2_uart_command_log_short": (
        0x541ad4, 0x73a5d4, b"[sync.module.uart]xStreamBufferReceive val :%s"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def check_object_bytes(path):
    raw = path.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("compiled object ELF format changed")
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
            end = raw.index(b"\0", strings[4] + name_off)
            name = raw[strings[4] + name_off:end].decode()
            if name not in CONTRACTS:
                continue
            expected = CONTRACTS[name][2] + b"\0"
            target = sections[shndx]
            actual = raw[target[4] + value:target[4] + value + size]
            if actual != expected or size != len(expected):
                raise RuntimeError(f"compiled C string bytes changed: {name}")
            found[name] = actual
    if set(found) != set(CONTRACTS):
        raise RuntimeError("compiled C string set changed")


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
    for name, (literal, va, value) in CONTRACTS.items():
        if not vaddr <= literal <= vaddr + filesz - 4 or not vaddr <= va < vaddr + filesz - len(value):
            raise RuntimeError(f"unmapped native log contract: {name}")
        pool = struct.unpack_from("<I", raw, offset + literal - vaddr)[0]
        pos = offset + va - vaddr
        if pool != va or raw[pos:pos + len(value) + 1] != value + b"\0" or name not in user:
            raise RuntimeError(f"native log/user contract changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "thread_log_strings.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("C log object symbol contract changed")
    check_object_bytes(obj)
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main UART thread log imports changed")
    linked = OUT / "apollo-main-thread-log-strings.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected log import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_THREAD_LOG_STRINGS_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_strings": {name: {"pool_literal": hex(literal), "address": hex(va),
                                  "bytes_hex": value.hex()}
                           for name, (literal, va, value) in CONTRACTS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["String identity does not prove final placement, full image, or device behavior."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
