#!/usr/bin/env python3
"""Bind two native BLE runtime pointer cells to compiled C storage."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ble_runtime_pointer_cells.c"
USERS = (G2 / "components/audio/uart_thread_source_candidate/display_ble_connect_request_impl.c",
         G2 / "components/audio/uart_thread_source_candidate/display_ble_discovery_events.c",
         G2 / "components/audio/uart_thread_source_candidate/display_ble_service_discovery_step.c",
         G2 / "components/audio/uart_thread_source_candidate/display_ble_service_discovery_start.c",
         G2 / "components/audio/uart_thread_source_candidate/display_ble_discovery_process.c")
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-shared-fatal-hook/apollo-main-shared-fatal-hook.o"
OUT = G2 / "build/c-firmware/20261014/main-ble-runtime-pointer-cells"
CONTRACTS = {
    "audio_ble_cached_conn_params": (0x2007433c, (0x477ab0, 0x478700), "uint8_t *"),
    "audio_ble_service_dispatch_20074348": (0x20074348, (0x53290c, 0x533624), "uintptr_t "),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    source = SOURCE.read_text()
    users = "\n".join(p.read_text() for p in USERS)
    for name, (ram, literals, c_type) in CONTRACTS.items():
        if any(struct.unpack("<I", bytes_at(segments, literal))[0] != ram for literal in literals):
            raise RuntimeError(f"native BLE RAM literals changed: {name}")
        if f"{c_type}{name}" not in source or f"extern {c_type}{name};" not in users or \
           f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"BLE pointer C contract changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ble_runtime_pointer_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("BLE pointer C symbol contract changed")
    sizes = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in CONTRACTS:
            sizes[parts[-1]] = int(parts[1], 16)
    if sizes != {name: 4 for name in CONTRACTS}:
        raise RuntimeError(f"BLE pointer C sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main BLE pointer imports changed")
    linked = OUT / "apollo-main-ble-runtime-pointer-cells.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_BLE_RUNTIME_POINTER_CELLS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"ram": hex(ram), "literals": [hex(x) for x in literals],
                                            "cell_bytes": 4}
                                    for name, (ram, literals, _) in CONTRACTS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in USERS},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The cells compile and link but their callback/parameter producers and startup values remain open.",
                          "The named sections express intended RAM addresses but final placement is unverified.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
