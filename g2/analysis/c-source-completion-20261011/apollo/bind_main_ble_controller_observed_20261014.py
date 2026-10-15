#!/usr/bin/env python3
"""Bind the observed direct BLE controller slice to C RAM storage."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ble_controller_observed.c"
USERS = (G2 / "components/audio/uart_thread_source_candidate/display_tpl_timeout_callback.c",
         G2 / "components/audio/uart_thread_source_candidate/display_ble_master_connect_callbacks.c",
         G2 / "components/audio/uart_thread_source_candidate/display_ble_connect_request.c",
         G2 / "components/audio/uart_thread_source_candidate/display_ble_comm_recovery_delayed.c")
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-ble-runtime-pointer-cells/apollo-main-ble-runtime-pointer-cells.o"
OUT = G2 / "build/c-firmware/20261014/main-ble-controller-observed"
NAME, RAM, SIZE, LITERALS = "audio_ble_controller", 0x200727f0, 0x57, (0x4b81fc, 0x4b8488)


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    if any(struct.unpack("<I", bytes_at(segments, literal))[0] != RAM for literal in LITERALS):
        raise RuntimeError("native direct BLE controller literals changed")
    source = SOURCE.read_text()
    users = [p.read_text() for p in USERS]
    if f"uint8_t {NAME}[0x57u]" not in source or ".g2_ram_200727f0" not in source or \
       not all(f"extern uint8_t {NAME}[];" in user for user in users) or \
       not all("[0x56u]" in user for user in users):
        raise RuntimeError("selected BLE controller array contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ble_controller_observed.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u"):
        raise RuntimeError("BLE controller C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(len(parts := line.split()) == 4 and parts[-1] == NAME and
               int(parts[1], 16) == SIZE for line in output.splitlines()):
        raise RuntimeError("BLE controller observed C size changed")
    before = names(BASE, "-u")
    if NAME not in before:
        raise RuntimeError("Apollo Main controller import changed")
    linked = OUT / "apollo-main-ble-controller-observed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_BLE_CONTROLLER_OBSERVED_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_ram": hex(RAM), "native_literals": [hex(x) for x in LITERALS],
               "observed_source_bytes": SIZE,
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in USERS},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The 0x57-byte array covers selected C reads through +0x56 only; complete native allocation and other users remain open.",
                          "The named section expresses intended RAM base but final placement and initialization are unverified.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
