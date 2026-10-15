#!/usr/bin/env python3
"""Bind native HCI/DM state objects and record the stale-root rebuild gate."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/hci_dm_stack_state.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_stack_lowers.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-adv-runtime-state/apollo-main-adv-runtime-state.o"
OUT = G2 / "build/c-firmware/20261014/main-hci-dm-stack-state"
STATES = {
    "audio_ble_hci_stack_state_20073870": (0x20073870, 0x536810, 0x24),
    "audio_ble_dm_stack_rows_200738dc": (0x200738dc, 0x536a14, 0x19),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    for name, (ram, literal, _) in STATES.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native RAM literal changed: {name}")
    if "uint8_t *rows=audio_ble_dm_stack_rows_200738dc;" not in USER.read_text():
        raise RuntimeError("separate DM row source user changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "hci_dm_stack_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(STATES) or names(obj, "-u"):
        raise RuntimeError("HCI/DM C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    sizes = {parts[-1]: int(parts[1], 16) for line in output.splitlines()
             if len(parts := line.split()) == 4 and parts[-1] in STATES}
    if sizes != {name: size for name, (_, _, size) in STATES.items()}:
        raise RuntimeError(f"HCI/DM source sizes changed: {sizes}")
    before = names(BASE, "-u")
    hci = "audio_ble_hci_stack_state_20073870"
    if hci not in before:
        raise RuntimeError("Apollo Main HCI state import changed")
    linked = OUT / "apollo-main-hci-dm-stack-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {hci} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_HCI_DM_STACK_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_states": {name: {"ram": hex(ram), "literal": hex(literal),
                                        "source_bytes": size}
                                 for name, (ram, literal, size) in STATES.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The current root object predates the corrected DM-row source user; its prior function body must be rebuilt before the new row symbol is integrated.",
                          "The DM row object covers observed writes through +0x18; its complete native allocation span remains open.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
