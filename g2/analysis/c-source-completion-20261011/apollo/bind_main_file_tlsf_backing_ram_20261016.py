#!/usr/bin/env python3
"""Reserve the bounded stock TLSF backing range at its observed SSRAM address."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "file_tlsf_backing_ram.c"
LINKER = COMP / "file_tlsf_backing_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-file-tlsf-pool-init/apollo-main-file-tlsf-pool-init-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-file-tlsf-backing-ram"
NAME = "g2_file_tlsf_backing_20208e70"
ADDRESS = 0x20208e70
SIZE = 0x70800

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "file_tlsf_backing_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {NAME}:
        raise RuntimeError("TLSF backing RAM symbols changed")
    placement = OUT / "file-tlsf-backing-placement.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-nostdlib", "-Wl,-Ttext=0x100000", "-Wl,-T," + str(LINKER),
                    "-Wl,-e,0x100000", str(obj), "-o", str(placement)], check=True)
    with placement.open("rb") as f:
        elf = ELFFile(f)
        section = elf.get_section_by_name(".opencfw.fileheap.tlsf.backing")
        symbols = {s.name: s for s in elf.get_section_by_name(".symtab").iter_symbols()}
        if section["sh_addr"] != ADDRESS or section["sh_size"] != SIZE or \
                section["sh_type"] != "SHT_NOBITS" or \
                symbols[NAME]["st_value"] != ADDRESS or symbols[NAME]["st_size"] != SIZE:
            raise RuntimeError("TLSF backing placement/extent changed")
    before = names(BASE, "-u")
    if len(before) != 176 or NAME in names(BASE, "--defined-only"):
        raise RuntimeError("Apollo backing RAM base changed")
    linked = OUT / "apollo-main-file-tlsf-backing-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if after != before or NAME not in names(linked, "--defined-only"):
        raise RuntimeError("Apollo backing RAM frontier changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FILE_TLSF_BACKING_RAM",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "placement_elf": str(placement.relative_to(ROOT)), "placement_sha256": sha(placement),
               "stock_address": hex(ADDRESS), "size": hex(SIZE), "end_exclusive": hex(ADDRESS + SIZE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 176, "unresolved_after": 176,
               "imports_resolved": [], "imports_added": [],
               "startup_wired": False, "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Stock zeroing call is exact, but independent writers and global collision remain unverified.",
                          "Boot order, whole-image link, and hardware execution remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 176, 176, sha(path))

if __name__ == "__main__":
    main()
