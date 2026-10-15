#!/usr/bin/env python3
"""Bind the two C names for one native BLE/L2C trace-enable byte."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/trace_level_state.c"
GETTER_SOURCE = G2 / "components/audio/uart_thread_source_candidate/l2c_log_helpers.c"
TRACE_USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_smp_db_records.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-dm-security-rom-state/apollo-main-dm-security-rom-state.o"
OUT = G2 / "build/c-firmware/20261014/main-trace-level-state"
A, B = "audio_l2c_log_enabled_cell", "audio_ble_trace_level_cell"
RAM = 0x2007502f


def bytes_at(segments, address, length):
    for base, data in segments:
        if base <= address and address + length <= base + len(data):
            return data[address-base:address-base+length]
    raise RuntimeError(f"native address not mapped: {address:#x}")


def main():
    native_segments, _ = image(NATIVE)
    if struct.unpack("<I", bytes_at(native_segments, 0x4c9cd4, 4))[0] != RAM or \
       "RAM 0x2007502f" not in GETTER_SOURCE.read_text() or \
       "0x2007502f" not in TRACE_USER.read_text():
        raise RuntimeError("native trace byte or C source ownership changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "trace_level_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {A, B} or names(obj, "-u"):
        raise RuntimeError("trace state source symbol contract changed")
    nm = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    rows = {parts[-1]: parts for line in nm.splitlines()
            if len(parts := line.split()) == 4 and parts[-1] in {A, B}}
    if any(int(rows[name][1], 16) != 1 for name in (A, B)) or \
       rows[A][0] != rows[B][0]:
        raise RuntimeError("trace aliases do not share one byte")
    before = names(BASE, "-u")
    if not {A, B} <= before:
        raise RuntimeError("Apollo Main trace state imports changed")
    linked = OUT / "apollo-main-trace-level-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {A, B} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TRACE_LEVEL_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_getter": "0x4c9c50", "native_cell": hex(RAM),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "getter_source": str(GETTER_SOURCE.relative_to(ROOT)),
               "getter_source_sha256": sha(GETTER_SOURCE),
               "trace_user_source": str(TRACE_USER.relative_to(ROOT)),
               "trace_user_source_sha256": sha(TRACE_USER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["One source byte backs both names; final absolute RAM placement remains open.",
                          "Whole-image and hardware behavior remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
