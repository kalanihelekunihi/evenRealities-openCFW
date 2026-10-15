#!/usr/bin/env python3
"""Bind three distinct native logger RAM cells to compiled C."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/log_runtime_cells.c"
USERS = (G2 / "components/audio/audio_log_format_source_candidate/emit.c",
         G2 / "components/audio/audio_log_format_source_candidate/format.c",
         G2 / "components/audio/audio_log_format_source_candidate/helpers.c")
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-hub-timer-runtime-state/apollo-main-hub-timer-runtime-state.o"
OUT = G2 / "build/c-firmware/20261014/main-log-runtime-cells"
CONTRACTS = {
    "audio_log_lock_state": (0x20074388, 0x43d0e0, 4),
    "audio_log_sequence": (0x20074f9f, 0x43d108, 1),
    "audio_log_policy_byte": (0x20004544, 0x43d140, 1),
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
    for name, (ram, literal, size) in CONTRACTS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native logger RAM literal changed: {name}")
        decl = f"void *{name}" if size == 4 else f"volatile uint8_t {name}"
        if decl not in source or f"extern {decl};" not in users or f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"logger C declaration changed: {name}")
    if struct.unpack("<I", bytes_at(segments, 0x43d13c))[0] != 0x20004543:
        raise RuntimeError("adjacent log-flags native cell changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "log_runtime_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("logger C symbol contract changed")
    sizes = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in CONTRACTS:
            sizes[parts[-1]] = int(parts[1], 16)
    if sizes != {name: row[2] for name, row in CONTRACTS.items()}:
        raise RuntimeError(f"logger C cell sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main logger imports changed")
    linked = OUT / "apollo-main-log-runtime-cells.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOG_RUNTIME_CELLS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"ram": hex(ram), "literal": hex(literal),
                                            "scalar_bytes": size}
                                    for name, (ram, literal, size) in CONTRACTS.items()},
               "adjacent_log_flags_cell": "0x20004543",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in USERS},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Logger cell widths and native addresses are covered; startup values and lock lifetime remain open.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
