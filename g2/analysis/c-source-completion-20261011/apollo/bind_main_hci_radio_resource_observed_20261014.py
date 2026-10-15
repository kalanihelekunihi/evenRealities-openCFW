#!/usr/bin/env python3
"""Bind observed radio acquisition resource row to compiled C storage."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/hci_radio_resource_observed.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_radio_acquire.c"
NATIVE_TEST = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ble_hci_radio_acquire.py"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-ble-controller-observed/apollo-main-ble-controller-observed.o"
OUT = G2 / "build/c-firmware/20261014/main-hci-radio-resource-observed"
NAME, RAM, LITERAL, SIZE = "audio_ble_hci_radio_resource_state_20073dc4", 0x20073dc4, 0x52e940, 24


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    if struct.unpack("<I", bytes_at(segments, LITERAL))[0] != RAM:
        raise RuntimeError("native HCI radio resource literal changed")
    source, user, fixture = SOURCE.read_text(), USER.read_text(), NATIVE_TEST.read_text()
    if f"{NAME}[24u]" not in source or f"extern uint8_t {NAME}[];" not in user or \
       "state[9u]=1u" not in user or f"{NAME}[24]" not in fixture or \
       ".g2_ram_20073dc4" not in source:
        raise RuntimeError("radio resource observed C/test contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "hci_radio_resource_observed.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u"):
        raise RuntimeError("radio resource C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(len(parts := line.split()) == 4 and parts[-1] == NAME and
               int(parts[1], 16) == SIZE for line in output.splitlines()):
        raise RuntimeError("radio resource observed C size changed")
    before = names(BASE, "-u")
    if NAME not in before:
        raise RuntimeError("Apollo Main resource row import changed")
    linked = OUT / "apollo-main-hci-radio-resource-observed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_HCI_RADIO_RESOURCE_OBSERVED_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_ram": hex(RAM), "native_literal": hex(LITERAL),
               "selected_fixture_bytes": SIZE,
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
               "native_test": str(NATIVE_TEST.relative_to(ROOT)), "native_test_sha256": sha(NATIVE_TEST),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The 24-byte extent is a selected comparison-fixture slice, not proof of the full native allocation.",
                          "Vendor child accesses, startup contents and final SRAM placement remain open.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
