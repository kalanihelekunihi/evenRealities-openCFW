#!/usr/bin/env python3
"""Bind one C compressed-SRAM DM config object under both source names."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/dm_config_state.c"
DM_INIT = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_init.c"
MASTER_MODE = G2 / "components/audio/uart_thread_source_candidate/display_ble_master_mode.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-ring-policy-state/apollo-main-ring-policy-state.o"
OUT = G2 / "build/c-firmware/20261014/main-dm-config-state"
A, B = "audio_ble_dm_config", "audio_ble_mode_runtime_20000694"
RAM = 0x20000694
LITERALS = (0x4d253c, 0x4bacc0, 0x536a24)


def bytes_at(segments, address, length):
    for base, data in segments:
        if base <= address and address + length <= base + len(data):
            return data[address-base:address-base+length]
    raise RuntimeError(f"native address not mapped: {address:#x}")


def main():
    native_segments, _ = image(NATIVE)
    if any(struct.unpack("<I", bytes_at(native_segments, literal, 4))[0] != RAM
           for literal in LITERALS):
        raise RuntimeError("native compressed-SRAM DM origin changed")
    init_text = DM_INIT.read_text()
    mode_text = MASTER_MODE.read_text()
    if "put(0x3cu,audio_ble_dm_priv_table_b)" not in init_text or \
       f"{A}+offset" not in init_text or f"{B}+8u" not in mode_text:
        raise RuntimeError("DM config C access span changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "dm_config_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {A, B} or names(obj, "-u"):
        raise RuntimeError("DM config source symbols changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    rows = {parts[-1]: parts for line in output.splitlines()
            if len(parts := line.split()) == 4 and parts[-1] in {A, B}}
    if any(int(rows[name][1], 16) != 0x40 for name in (A, B)) or \
       rows[A][0] != rows[B][0]:
        raise RuntimeError("DM config aliases do not share the observed 0x40-byte span")
    before = names(BASE, "-u")
    if not {A, B} <= before:
        raise RuntimeError("Apollo Main DM config imports changed")
    linked = OUT / "apollo-main-dm-config-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {A, B} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_CONFIG_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_origin": hex(RAM), "native_literal_addresses": [hex(x) for x in LITERALS],
               "observed_accessed_bytes": 0x40,
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "dm_init_source": str(DM_INIT.relative_to(ROOT)),
               "dm_init_source_sha256": sha(DM_INIT),
               "master_mode_source": str(MASTER_MODE.relative_to(ROOT)),
               "master_mode_source_sha256": sha(MASTER_MODE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The object covers observed accesses through +0x3f; full native allocation span remains unproven.",
                          "Final SRAM placement/startup, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
