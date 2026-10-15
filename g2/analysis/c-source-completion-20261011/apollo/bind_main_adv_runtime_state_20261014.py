#!/usr/bin/env python3
"""Bind two observed Apollo advertising RAM state prefixes to C storage."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/adv_runtime_state.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-pair-mode-state/apollo-main-master-pair-mode-state.o"
OUT = G2 / "build/c-firmware/20261014/main-adv-runtime-state"
STATES = {
    "audio_ble_adv_resume_state_20074f38": (0x20074f38, 0x4b5ad8, 2),
    "audio_ble_adv_timer_20073df4": (0x20073df4, 0x4b2dd4, 16),
}


def bytes_at(segments, address, length):
    for base, data in segments:
        if base <= address and address + length <= base + len(data):
            return data[address-base:address-base+length]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    for name, (ram, literal, _) in STATES.items():
        if struct.unpack("<I", bytes_at(segments, literal, 4))[0] != ram:
            raise RuntimeError(f"native RAM literal changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "adv_runtime_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(STATES) or names(obj, "-u"):
        raise RuntimeError("advertising state C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    sizes = {parts[-1]: int(parts[1], 16) for line in output.splitlines()
             if len(parts := line.split()) == 4 and parts[-1] in STATES}
    if sizes != {name: size for name, (_, _, size) in STATES.items()}:
        raise RuntimeError(f"advertising state observed-prefix sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(STATES) <= before:
        raise RuntimeError("Apollo Main advertising state imports changed")
    linked = OUT / "apollo-main-adv-runtime-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(STATES) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_ADV_RUNTIME_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_states": {name: {"ram": hex(ram), "literal": hex(literal),
                                        "observed_prefix_bytes": size}
                                 for name, (ram, literal, size) in STATES.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The resume state is an observed two-byte prefix; its complete native allocation span remains open.",
                          "The timer follows the pinned 16-byte WSF layout; native initialization remains open.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
