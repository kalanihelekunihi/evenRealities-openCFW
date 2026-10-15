#!/usr/bin/env python3
"""Bind observed ring kernel and RTC words to source-owned C storage."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ring_kernel_rtc_state.c"
USERS = (G2 / "components/audio/uart_thread_source_candidate/display_ring_kernel_state.c",
         G2 / "components/audio/uart_thread_source_candidate/display_ring_rtc_snapshot.c")
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-charge-sync-scalars/apollo-main-charge-sync-scalars.o"
OUT = G2 / "build/c-firmware/20261014/main-ring-kernel-rtc-state"
CONTRACTS = {
    "audio_uart_ring_kernel_initialized_20074384": (0x20074384, 0x449698),
    "audio_uart_ring_rtc_shadow_200742ac": (0x200742ac, 0x4d3608),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    source = SOURCE.read_text()
    for name, (ram, literal) in CONTRACTS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native RAM literal changed: {name}")
        if f"volatile uint32_t {name};" not in source or not any(
                f"extern volatile uint32_t {name};" in user.read_text() for user in USERS):
            raise RuntimeError(f"source/user type contract changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ring_kernel_rtc_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("ring state C symbol contract changed")
    sizes = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in CONTRACTS:
            sizes[parts[-1]] = int(parts[1], 16)
    if sizes != {name: 4 for name in CONTRACTS}:
        raise RuntimeError(f"ring state C sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main expected imports changed")
    linked = OUT / "apollo-main-ring-kernel-rtc-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_RING_KERNEL_RTC_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"ram": hex(ram), "literal": hex(literal), "scalar_bytes": 4}
                                    for name, (ram, literal) in CONTRACTS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in USERS},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Typed word sizes and native literals are covered; startup values and full native allocation remain open.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
