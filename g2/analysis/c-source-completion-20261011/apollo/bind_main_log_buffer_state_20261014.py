#!/usr/bin/env python3
"""Bind observed Apollo logger buffers to C without guessing their startup."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/log_buffer_state.c"
EMIT = G2 / "components/audio/audio_log_format_source_candidate/emit.c"
DUMP = G2 / "components/audio/audio_dump_hex_source_candidate/dump.c"
BASE = G2 / "build/c-firmware/20261014/main-log-runtime-cells/apollo-main-log-runtime-cells.o"
OUT = G2 / "build/c-firmware/20261014/main-log-buffer-state"
CONTRACTS = {
    "g2_audio_log_ring_state": (0x200004c8, 0x43d0e8, 16),
    "g2_audio_dump_log_state": (0x20070be8, 0x43dcb4, 0xf2),
    "g2_audio_dump_buffer": (0x2006bd30, 0x43dc8c, 1024),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def main():
    raw = NATIVE.read_bytes()
    if raw[:4] != b"\x7fELF" or raw[4] != 1 or raw[5] != 1:
        raise RuntimeError("native ELF layout changed")
    phoff = struct.unpack_from("<I", raw, 28)[0]
    if struct.unpack_from("<H", raw, 44)[0] != 1:
        raise RuntimeError("native ELF segment count changed")
    typ, offset, vaddr, _, filesz, _, _, _ = struct.unpack_from("<IIIIIIII", raw, phoff)
    if typ != 1:
        raise RuntimeError("native ELF load segment changed")
    source = SOURCE.read_text()
    users = EMIT.read_text() + DUMP.read_text()
    for name, (ram, literal, _) in CONTRACTS.items():
        if not vaddr <= literal <= vaddr + filesz - 4:
            raise RuntimeError(f"unmapped native literal: {name}")
        if struct.unpack_from("<I", raw, offset + literal - vaddr)[0] != ram:
            raise RuntimeError(f"native RAM literal changed: {name}")
        if name not in source or f"extern " not in users or name not in users:
            raise RuntimeError(f"C ownership changed: {name}")
        if f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"C section changed: {name}")
    if "g2_audio_dump_log_state[0xf1]" not in DUMP.read_text() or "g2_audio_dump_buffer, 1024" not in DUMP.read_text():
        raise RuntimeError("dump buffer bounds changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "log_buffer_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("compiled logger symbol contract changed")
    sizes = {}
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    for line in output.splitlines():
        cols = line.split()
        if len(cols) == 4 and cols[-1] in CONTRACTS:
            sizes[cols[-1]] = int(cols[1], 16)
    if sizes != {name: row[2] for name, row in CONTRACTS.items()}:
        raise RuntimeError(f"compiled logger sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main logger imports changed")
    linked = OUT / "apollo-main-log-buffer-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LOG_BUFFER_STATE_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_contracts": {name: {"ram": hex(ram), "literal": hex(lit), "observed_bytes": size}
                             for name, (ram, lit, size) in CONTRACTS.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in (EMIT, DUMP)},
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Dump state covers only the highest observed byte; full allocation and initialization remain open.",
                   "Final SRAM placement, whole-image link, and hardware behavior remain open."],
    }
    receipt_path = OUT / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(receipt_path))


if __name__ == "__main__":
    main()
