#!/usr/bin/env python3
"""Bind the observed dashboard layout destination into Apollo main."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "dashboard_layout_current_ram.c"
LINKER = COMP / "dashboard_layout_current_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-os-scheduler-state-ram-bound/apollo-main-os-scheduler-state-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-dashboard-layout-current-ram-bound"
NAME = "audio_dashboard_layout_current"
ADDRESS = 0x200e7934
EXTENT = 128
LITERAL = 0x5588a8
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def section(path, name):
    with path.open("rb") as f:
        elf = ELFFile(f)
        item = elf.get_section_by_name(name)
        if item is None:
            raise RuntimeError(f"Missing section: {name}")
        return item["sh_addr"], item["sh_size"], item["sh_type"]

def main():
    image = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PINNED or \
            int.from_bytes(image[LITERAL-0x438000:LITERAL-0x438000+4], "little") != ADDRESS:
        raise RuntimeError("Dashboard layout pointer or payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "dashboard_layout_current_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {NAME} or names(obj, "-u") or \
            section(obj, ".bss.opencfw.dashboard.layout.current")[1:] != (EXTENT, "SHT_NOBITS"):
        raise RuntimeError("Dashboard layout storage source changed")
    placed = OUT / "dashboard-layout-current-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER), "-e", NAME,
                    str(obj), "-o", str(placed)], check=True)
    if section(placed, ".opencfw.dashboard.layout.current") != (ADDRESS, EXTENT, "SHT_NOBITS"):
        raise RuntimeError("Dashboard layout NOLOAD placement changed")
    placed_symbols = {line.split()[-1]: int(line.split()[0], 16)
                      for line in subprocess.check_output(
                          ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                          text=True).splitlines()}
    if placed_symbols.get(NAME) != ADDRESS:
        raise RuntimeError("Dashboard layout symbol address changed")
    before = names(BASE, "-u")
    if len(before) != 182 or NAME not in before:
        raise RuntimeError("Apollo base frontier changed")
    linked = OUT / "apollo-main-dashboard-layout-current-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before or len(after) != 181:
        raise RuntimeError("Apollo dashboard layout frontier changed")
    fixed = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for item in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", item.name)
            if match and item["sh_size"]:
                start = int(match.group(1), 16)
                fixed.append((start, start + item["sh_size"], item.name))
    if any(ADDRESS < end and start < ADDRESS + EXTENT for start, end, _ in fixed):
        raise RuntimeError("Dashboard layout overlaps named fixed RAM")
    for previous in ("main-even-ai-ram-state-bound", "main-os-scheduler-state-ram-bound"):
        data = json.loads((G2 / "build/c-firmware/20261016" / previous / "receipt.json").read_text())
        if any(ADDRESS < int(row["address"], 16) + row["bytes"] and
               int(row["address"], 16) < ADDRESS + EXTENT for row in data["spans"]):
            raise RuntimeError(f"Dashboard layout overlaps {previous}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_DASHBOARD_LAYOUT_CURRENT_RAM_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PINNED, "pointer_literal": hex(LITERAL),
        "address": hex(ADDRESS), "bytes": EXTENT, "section_type": "NOBITS",
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "placement_elf": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": [NAME], "imports_added": [],
        "fixed_ram_sections_checked": len(fixed),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Only the observed 128-byte copy extent is reserved.",
                   "Final global layout, startup state, and device behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
