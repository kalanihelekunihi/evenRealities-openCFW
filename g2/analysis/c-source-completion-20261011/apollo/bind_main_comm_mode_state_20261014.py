#!/usr/bin/env python3
"""Bind the observed BLE communication mode range and corrected array ABI."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/comm_mode_state.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_comm_handler_init.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-ancc-cache-cells/apollo-main-ancc-cache-cells.o"
OUT = G2 / "build/c-firmware/20261014/main-comm-mode-state"
NAME, RAM, LITERAL, SIZE = "audio_ble_comm_mode", 0x200737b0, 0x4b8730, 0x24


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    if struct.unpack("<I", bytes_at(segments, LITERAL))[0] != RAM:
        raise RuntimeError("native communication mode literal changed")
    user = USER.read_text()
    if "extern uint8_t audio_ble_comm_mode[];" not in user or \
       "audio_ble_comm_mode[0]=4u;" not in user:
        raise RuntimeError("communication mode array user changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "comm_mode_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u"):
        raise RuntimeError("communication mode C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(len(parts := line.split()) == 4 and parts[-1] == NAME and
               int(parts[1], 16) == SIZE for line in output.splitlines()):
        raise RuntimeError("communication mode observed size changed")
    before = names(BASE, "-u")
    if NAME not in before:
        raise RuntimeError("Apollo Main communication mode import changed")
    linked = OUT / "apollo-main-comm-mode-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_COMM_MODE_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_ram": hex(RAM), "native_literal": hex(LITERAL),
               "observed_source_bytes": SIZE,
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The source object covers observed fields through +0x23; its complete native allocation and startup contents remain open.",
                          "The current aggregate predates the corrected array declaration and requires a root source rebuild for freshness.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
