#!/usr/bin/env python3
"""Bind native HCI scheduler six-word ring control structure to C."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/hci_scheduler_ring_state.c"
BOOT_USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_radio_boot.c"
WRITE_USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_driver_write.c"
SCHEDULER = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_radio_scheduler.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-hci-driver-timer-state/apollo-main-hci-driver-timer-state.o"
OUT = G2 / "build/c-firmware/20261014/main-hci-scheduler-ring-state"
NAME, RAM, LITERAL, SIZE = "audio_ble_hci_radio_scheduler_state", 0x20073ba8, 0x4b4d90, 24


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    if struct.unpack("<I", bytes_at(segments, LITERAL))[0] != RAM:
        raise RuntimeError("native HCI scheduler ring RAM literal changed")
    source, boot, writer, scheduler = (p.read_text() for p in (SOURCE, BOOT_USER, WRITE_USER, SCHEDULER))
    if f"{NAME}[24u]" not in source or ".g2_ram_20073ba8" not in source or \
       f"extern uint8_t {NAME}[];" not in boot or f"extern uint8_t {NAME}[];" not in writer or \
       "put32(p+20u,(uint32_t)(uintptr_t)storage);" not in scheduler or \
       "word(ring+20u)" not in writer:
        raise RuntimeError("HCI six-word ring source contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "hci_scheduler_ring_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u"):
        raise RuntimeError("HCI scheduler ring C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(len(parts := line.split()) == 4 and parts[-1] == NAME and
               int(parts[1], 16) == SIZE for line in output.splitlines()):
        raise RuntimeError("HCI scheduler ring C size changed")
    before = names(BASE, "-u")
    if NAME not in before:
        raise RuntimeError("Apollo Main HCI scheduler ring import changed")
    linked = OUT / "apollo-main-hci-scheduler-ring-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_HCI_SCHEDULER_RING_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_ram": hex(RAM), "native_literal": hex(LITERAL),
               "selected_source_bytes": SIZE,
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p)
                                for p in (BOOT_USER, WRITE_USER, SCHEDULER)},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The six-word ring control structure is covered; backing storage extent and contents remain open.",
                          "Startup contents, final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
