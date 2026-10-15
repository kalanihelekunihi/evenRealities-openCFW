#!/usr/bin/env python3
"""Bind native ring policy RAM cells with explicit state-span limit."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ring_policy_state.c"
CHILDREN = G2 / "components/audio/uart_thread_source_candidate/display_ble_ring_policy_children.c"
RESET = G2 / "components/audio/uart_thread_source_candidate/display_ble_pair_auth_flag.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-pair-auth-state/apollo-main-pair-auth-state.o"
OUT = G2 / "build/c-firmware/20261014/main-ring-policy-state"
SYMBOLS = {"audio_ble_ring_policy_state_2007408c": (0x2007408c, 12, 0x49f744),
           "audio_ble_ring_policy_deadline_200748fc": (0x200748fc, 4, 0x49f7a8),
           "audio_ble_ring_policy_pending_2007500b": (0x2007500b, 1, 0x49f7d0)}


def bytes_at(segments, address, length):
    for base, data in segments:
        if base <= address and address + length <= base + len(data):
            return data[address-base:address-base+length]
    raise RuntimeError(f"native address not mapped: {address:#x}")


def main():
    native_segments, _ = image(NATIVE)
    for name, (ram, size, literal) in SYMBOLS.items():
        if struct.unpack("<I", bytes_at(native_segments, literal, 4))[0] != ram:
            raise RuntimeError(f"native ring policy literal changed: {name}")
    if "audio_ble_ring_policy_state_2007408c[8u]" not in CHILDREN.read_text() or \
       "audio_ble_ring_policy_deadline_200748fc=0u" not in RESET.read_text() or \
       "audio_ble_ring_policy_pending_2007500b=0u" not in RESET.read_text():
        raise RuntimeError("C ring policy access pattern changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ring_policy_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(SYMBOLS) or names(obj, "-u"):
        raise RuntimeError("ring policy source symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    rows = {parts[-1]: parts for line in output.splitlines()
            if len(parts := line.split()) == 4 and parts[-1] in SYMBOLS}
    if any(int(rows[name][1], 16) != size for name, (_, size, _) in SYMBOLS.items()):
        raise RuntimeError("ring policy source state dimensions changed")
    before = names(BASE, "-u")
    if not set(SYMBOLS) <= before:
        raise RuntimeError("Apollo Main ring policy imports changed")
    linked = OUT / "apollo-main-ring-policy-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(SYMBOLS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_RING_POLICY_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_literals": {name: {"ram": hex(ram), "literal": hex(literal)}
                                   for name, (ram, _, literal) in SYMBOLS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "children_source": str(CHILDREN.relative_to(ROOT)),
               "children_source_sha256": sha(CHILDREN),
               "reset_source": str(RESET.relative_to(ROOT)), "reset_source_sha256": sha(RESET),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The 12-byte state object covers the observed accessed prefix; full native span remains unproven.",
                          "Final RAM placement/startup, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
