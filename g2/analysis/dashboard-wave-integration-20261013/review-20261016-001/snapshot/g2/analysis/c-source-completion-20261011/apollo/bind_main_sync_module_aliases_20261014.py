#!/usr/bin/env python3
"""Bind four native sync log families to their shared C string entries."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-timeout-runtime/apollo-main-timeout-runtime.o"
OUT = G2 / "build/c-firmware/20261014/main-sync-module-aliases"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/send_begin_log_strings.c"
USERS = {
    "role": G2 / "components/audio/uart_thread_source_candidate/role_get.c",
    "timer": G2 / "components/audio/uart_thread_source_candidate/sync_timer_start.c",
    "user": G2 / "components/audio/uart_thread_source_candidate/user_response.c",
    "master": G2 / "components/audio/uart_thread_source_candidate/master_prepare.c",
}
ALIASES = {f"audio_uart_{family}_{kind}": f"audio_uart_begin0_{kind}"
           for family in USERS for kind in ("module", "source")}
POINTERS = {
    0x45b0fc: 0x705fb8, 0x45b100: 0x77c07c,
    0x45d7cc: 0x705fb8, 0x45d7d0: 0x77c07c,
}
BYTES = {
    "audio_uart_begin0_module": (0x77c07c, b"sync.module.framework"),
    "audio_uart_begin0_source": (
        0x705fb8, b"D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def symbol_bytes(path):
    raw = path.read_bytes()
    if raw[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("Main object ELF format changed")
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
            if name in BYTES:
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

    def word(address):
        if not vaddr <= address <= vaddr + filesz - 4:
            raise RuntimeError(f"native pointer unmapped: {address:#x}")
        return struct.unpack_from("<I", raw, offset + address - vaddr)[0]

    for literal, expected in POINTERS.items():
        if word(literal) != expected:
            raise RuntimeError(f"sync module literal changed: {literal:#x}")
    compiled = symbol_bytes(BASE)
    for name, (address, value) in BYTES.items():
        pos = offset + address - vaddr
        if raw[pos:pos + len(value) + 1] != value + b"\0" or compiled.get(name) != value + b"\0":
            raise RuntimeError(f"native/C sync log bytes changed: {name}")
    for family, source in USERS.items():
        body = source.read_text()
        if any(f"audio_uart_{family}_{kind}" not in body for kind in ("module", "source")):
            raise RuntimeError(f"sync log user changed: {family}")
    before = names(BASE, "-u")
    defined = names(BASE, "-g", "--defined-only")
    if not set(ALIASES) <= before or not set(ALIASES.values()) <= defined:
        raise RuntimeError("Apollo Main sync alias imports/providers changed")
    OUT.mkdir(parents=True, exist_ok=True)
    linked = OUT / "apollo-main-sync-module-aliases.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(f"--defsym={name}={target}" for name, target in ALIASES.items()),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(ALIASES) or after - before:
        raise RuntimeError(f"unexpected sync alias import delta: {before-after}, {after-before}")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", str(linked)], text=True)
    addresses = {p[-1]: int(p[0], 16) for line in output.splitlines()
                 if len(p := line.split()) == 3 and p[-1] in set(ALIASES) | set(ALIASES.values())}
    if any(addresses[name] != addresses[target] for name, target in ALIASES.items()):
        raise RuntimeError("sync module aliases no longer share C addresses")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_SYNC_MODULE_ALIASES_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_pointer_literals": {hex(k): hex(v) for k, v in POINTERS.items()},
        "same_entry_aliases": ALIASES,
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in USERS.values()},
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Same-entry names are tied to observed native pointers and existing C bytes; downstream log behavior is separate.",
                   "Final placement, full image, and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
