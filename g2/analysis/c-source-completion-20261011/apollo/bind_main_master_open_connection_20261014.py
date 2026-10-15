#!/usr/bin/env python3
"""Bind the observed master-open connection byte to C storage."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/master_open_connection_state.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_ring_unpair_cleanup.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-charge-sync-records/apollo-main-charge-sync-records.o"
OUT = G2 / "build/c-firmware/20261014/main-master-open-connection"
NAME, RAM, LITERALS = "audio_ble_master_open_connection", 0x20074f86, (0x4a1168, 0x4a34cc)


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    if any(struct.unpack("<I", bytes_at(segments, address))[0] != RAM for address in LITERALS):
        raise RuntimeError("native master-open byte literals changed")
    user, source = USER.read_text(), SOURCE.read_text()
    if "extern volatile uint8_t audio_ble_master_open_connection;" not in user or \
       "audio_ble_master_open_connection!=0u" not in user or \
       "audio_ble_master_disconnect_delayed(connection);" not in user or \
       ".g2_ram_20074f86" not in source:
        raise RuntimeError("selected master-open source contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "master_open_connection_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u"):
        raise RuntimeError("master-open C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(len(parts := line.split()) == 4 and parts[-1] == NAME and
               int(parts[1], 16) == 1 for line in output.splitlines()):
        raise RuntimeError("master-open C cell size changed")
    before = names(BASE, "-u")
    if NAME not in before:
        raise RuntimeError("Apollo Main master-open import changed")
    linked = OUT / "apollo-main-master-open-connection.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_MASTER_OPEN_CONNECTION_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_ram": hex(RAM), "native_literals": [hex(x) for x in LITERALS],
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["This binds a single observed native byte; its producers and startup value remain open.",
                          "The named section expresses intended RAM address but final placement is unverified.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
