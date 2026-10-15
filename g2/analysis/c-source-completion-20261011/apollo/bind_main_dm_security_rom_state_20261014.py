#!/usr/bin/env python3
"""Bind exact 16-byte DmSec ROM state while preserving placement gates."""
import json
import subprocess
import tempfile
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/dm_security_rom_state.c"
INIT_SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_init.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-profile-and-csf-state/apollo-main-profile-and-csf-state.o"
OUT = G2 / "build/c-firmware/20261014/main-dm-security-rom-state"
NAME = "audio_ble_dm_security_state_table"
ROM = 0x7856b0


def bytes_at(segments, address, length):
    for base, data in segments:
        if base <= address and address + length <= base + len(data):
            return data[address-base:address-base+length]
    raise RuntimeError(f"unmapped ROM address {address:#x}")


def main():
    native_segments, _ = image(NATIVE)
    if bytes_at(native_segments, ROM, 16) != bytes(16) or \
       bytes_at(native_segments, ROM + 16, 12) != b"callback.mgr":
        raise RuntimeError("native security ROM span or boundary changed")
    if f"{NAME}[]; /* ROM 0x7856b0 */" not in INIT_SOURCE.read_text():
        raise RuntimeError("DmSecInit ROM source annotation changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "dm_security_rom_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u"):
        raise RuntimeError("security ROM source symbol contract changed")
    nm = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(len(parts := line.split()) == 4 and parts[-1] == NAME and
               int(parts[1], 16) == 16 for line in nm.splitlines()):
        raise RuntimeError("security ROM source dimension changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "rom.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", NAME,
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        segments, symbols = image(trial)
        if bytes_at(segments, symbols[NAME], 16) != bytes(16):
            raise RuntimeError("compiled security ROM differs from native")
    before = names(BASE, "-u")
    if NAME not in before:
        raise RuntimeError("Apollo Main security ROM import changed")
    linked = OUT / "apollo-main-dm-security-rom-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_SECURITY_ROM_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_origin": hex(ROM), "table_bytes": 16,
               "native_boundary": "0x7856c0 callback.mgr",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "init_source": str(INIT_SOURCE.relative_to(ROOT)),
               "init_source_sha256": sha(INIT_SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Exact bytes do not establish final ROM placement.",
                          "DmSecInit sequencing, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
