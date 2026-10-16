#!/usr/bin/env python3
"""Compile and bind native-byte-checked sync receive log operands."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/sync_receive_log_strings.c"
USER = G2 / "components/audio/uart_thread_source_candidate/process_receive.c"
BASE = G2 / "build/c-firmware/20261014/main-lvgl-runtime-state/apollo-main-lvgl-runtime-state.o"
OUT = G2 / "build/c-firmware/20261014/main-sync-receive-strings"
CONTRACTS = {
    "g2_uart_sync_module_name": (0x77c07c, b"sync.module.framework"),
    "g2_uart_sync_source_file": (
        0x705fb8, b"D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c"),
    "g2_uart_sync_receive_function": (0x765890, b"SyncModuleReceivedDataHandler"),
    "g2_uart_sync_uninit_message": (0x783c30, b"sync module uninit!"),
    "g2_uart_sync_uninit_short": (
        0x7440c8, b"[sync.module.framework]sync module uninit!"),
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
        if section[1] != 2:  # SHT_SYMTAB
            continue
        strings = sections[section[6]]
        for pos in range(section[4], section[4] + section[5], section[9]):
            name_off, value, size, _, _, shndx = struct.unpack_from("<IIIBBH", raw, pos)
            end = raw.index(b"\0", strings[4] + name_off)
            name = raw[strings[4] + name_off:end].decode()
            if name not in CONTRACTS:
                continue
            expected = CONTRACTS[name][1] + b"\0"
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
    for name, (va, value) in CONTRACTS.items():
        if not vaddr <= va < vaddr + filesz - len(value):
            raise RuntimeError(f"unmapped native string: {name}")
        pos = offset + va - vaddr
        if raw[pos:pos + len(value) + 1] != value + b"\0" or name not in user:
            raise RuntimeError(f"native string/user contract changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "sync_receive_log_strings.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("C string object symbol contract changed")
    check_object_bytes(obj)
    sections = subprocess.check_output(["arm-none-eabi-objdump", "-h", str(obj)], text=True)
    if ".rodata" not in sections:
        raise RuntimeError("C strings are not in read-only data")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main sync receive imports changed")
    linked = OUT / "apollo-main-sync-receive-strings.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected string import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_SYNC_RECEIVE_STRINGS_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_strings": {name: {"address": hex(va), "bytes_hex": value.hex()}
                           for name, (va, value) in CONTRACTS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["String byte identity does not establish whole-image placement or runtime behavior."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
