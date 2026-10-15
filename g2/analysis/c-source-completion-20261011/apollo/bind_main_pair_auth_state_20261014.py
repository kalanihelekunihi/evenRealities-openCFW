#!/usr/bin/env python3
"""Bind the source-owned byte used by native pair-auth flag accessors."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/pair_auth_state.c"
ACCESSORS = G2 / "components/audio/uart_thread_source_candidate/display_ble_pair_auth_flag.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-trace-level-state/apollo-main-trace-level-state.o"
OUT = G2 / "build/c-firmware/20261014/main-pair-auth-state"
NAME, RAM = "audio_ble_pair_auth_flag_20074ffc", 0x20074ffc


def bytes_at(segments, address, length):
    for base, data in segments:
        if base <= address and address + length <= base + len(data):
            return data[address-base:address-base+length]
    raise RuntimeError(f"native address not mapped: {address:#x}")


def main():
    native_segments, _ = image(NATIVE)
    if struct.unpack("<I", bytes_at(native_segments, 0x4bc188, 4))[0] != RAM or \
       f"extern uint8_t {NAME};" not in ACCESSORS.read_text():
        raise RuntimeError("pair-auth native RAM or source accessor contract changed")
    before = names(BASE, "-u")
    base_defined = names(BASE, "-g", "--defined-only")
    if NAME not in before or not {"pairMgrSecAuthFlagSet", "pairMgrSecAuthFlagGet"} <= base_defined:
        raise RuntimeError("Apollo Main pair-auth accessors changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pair_auth_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u"):
        raise RuntimeError("pair-auth state source symbol contract changed")
    nm = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(len(parts := line.split()) == 4 and parts[-1] == NAME and
               int(parts[1], 16) == 1 for line in nm.splitlines()):
        raise RuntimeError("pair-auth state must be one byte")
    linked = OUT / "apollo-main-pair-auth-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAIR_AUTH_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_setter": "0x4bb9b4", "native_getter": "0x4bb9bc",
               "native_cell": hex(RAM),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "accessor_source": str(ACCESSORS.relative_to(ROOT)),
               "accessor_source_sha256": sha(ACCESSORS),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Final RAM placement and startup initialization remain open.",
                          "Whole-image and hardware behavior remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
