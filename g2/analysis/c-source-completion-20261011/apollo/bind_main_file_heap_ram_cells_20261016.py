#!/usr/bin/env python3
"""Bind stock-addressed heap mutex/pool pointer cells to Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "file_heap_ram_cells.c"
LINKER = COMP / "file_heap_ram_cells.ld"
BASE = G2 / "build/c-firmware/20261016/main-file-heap-realloc/apollo-main-file-heap-realloc-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-file-heap-ram-cells"
PROVIDERS = {"g2_codec_heap_mutex": 0x200748f8,
             "g2_codec_heap_pool": 0x20074abc}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "file_heap_ram_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != set(PROVIDERS):
        raise RuntimeError("heap RAM symbols changed")
    placement = OUT / "file-heap-ram-placement.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-nostdlib", "-Wl,-Ttext=0x100000", "-Wl,-T," + str(LINKER),
                    "-Wl,-e,0x100000", str(obj), "-o", str(placement)], check=True)
    symbols = {line.split()[-1]: int(line.split()[0], 16) for line in
               subprocess.check_output(["arm-none-eabi-nm", "-g", "--defined-only",
                                        str(placement)], text=True).splitlines()}
    if any(symbols.get(name) != addr for name, addr in PROVIDERS.items()):
        raise RuntimeError("heap RAM placement changed")
    before = names(BASE, "-u")
    if len(before) != 178 or not set(PROVIDERS) <= before:
        raise RuntimeError("Apollo heap RAM base frontier changed")
    linked = OUT / "apollo-main-file-heap-ram-cells-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(PROVIDERS) or after - before or len(after) != 176:
        raise RuntimeError(f"Apollo heap RAM frontier changed: {sorted(before-after)}, {sorted(after-before)}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FILE_HEAP_RAM_CELLS",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "placement_elf": str(placement.relative_to(ROOT)), "placement_sha256": sha(placement),
               "placements": {k: hex(v) for k, v in PROVIDERS.items()},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 178, "unresolved_after": 176,
               "imports_resolved": sorted(PROVIDERS), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Four-byte pointer cells are bounded by current stock accesses.",
                          "Startup values, global section collisions, whole-image link and hardware remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 178, 176, sha(path))

if __name__ == "__main__":
    main()
