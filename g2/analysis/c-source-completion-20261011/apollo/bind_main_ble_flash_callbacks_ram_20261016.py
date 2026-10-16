#!/usr/bin/env python3
"""Bind the native 0x3c-byte HAL callback table to bounded C storage."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "ble_flash_callbacks_ram.c"
LINKER = COMP / "ble_flash_callbacks_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-battery-callback-manager-ram-bound/apollo-main-battery-callback-manager-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-ble-flash-callbacks-ram-bound"
HEAD = "audio_ble_flash_callbacks"
TAIL = "audio_ble_flash_callbacks_tail"
ADDRESS = 0x20073270
EXTENT = 0x3c
LITERAL = 0x4806fc
PINNED = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def sections(path):
    with path.open("rb") as f:
        elf = ELFFile(f)
        return {s.name: (s["sh_addr"], s["sh_size"], s["sh_type"])
                for s in elf.iter_sections()}

def main():
    image = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PINNED or \
            int.from_bytes(image[LITERAL-0x438000:LITERAL-0x438000+4], "little") != ADDRESS:
        raise RuntimeError("BLE callback table pointer or payload changed")
    native_decomp = G2 / "research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/00480434.c"
    if "FUN_0043c0e4(DAT_004806fc,0x3c,0)" not in native_decomp.read_text():
        raise RuntimeError("BLE callback table native clear extent changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ble_flash_callbacks_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {HEAD, TAIL} or names(obj, "-u"):
        raise RuntimeError("BLE callback table C symbols changed")
    raw = sections(obj)
    if raw[".bss.opencfw.ble.flash.callbacks.head"][1:] != (8, "SHT_NOBITS") or \
            raw[".bss.opencfw.ble.flash.callbacks.tail"][1:] != (0x34, "SHT_NOBITS"):
        raise RuntimeError("BLE callback table C extent changed")
    placed = OUT / "ble-flash-callbacks-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER), "-e", HEAD,
                    str(obj), "-o", str(placed)], check=True)
    layout = sections(placed)
    if layout[".opencfw.ble.flash.callbacks.head"] != (ADDRESS, 8, "SHT_NOBITS") or \
            layout[".opencfw.ble.flash.callbacks.tail"] != (ADDRESS + 8, 0x34, "SHT_NOBITS"):
        raise RuntimeError("BLE callback table NOLOAD placement changed")
    located = {line.split()[-1]: int(line.split()[0], 16)
               for line in subprocess.check_output(
                   ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                   text=True).splitlines()}
    if located.get(HEAD) != ADDRESS or located.get(TAIL) != ADDRESS + 8:
        raise RuntimeError("BLE callback table symbol addresses changed")
    before = names(BASE, "-u")
    if len(before) != 177 or HEAD not in before:
        raise RuntimeError("Apollo callback table base frontier changed")
    linked = OUT / "apollo-main-ble-flash-callbacks-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != {HEAD} or after - before or len(after) != 176:
        raise RuntimeError("Apollo callback table binding frontier changed")
    fixed = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for item in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", item.name)
            if match and item["sh_size"]:
                start = int(match.group(1), 16)
                fixed.append((start, start + item["sh_size"], item.name))
    if any(ADDRESS < end and start < ADDRESS + EXTENT for start, end, _ in fixed):
        raise RuntimeError("BLE callback table overlaps named fixed RAM")
    for prior in ("main-even-ai-ram-state-bound", "main-os-scheduler-state-ram-bound",
                  "main-battery-callback-manager-ram-bound"):
        receipt = json.loads((G2 / "build/c-firmware/20261016" / prior / "receipt.json").read_text())
        if any(ADDRESS < int(span["address"], 16) + span["bytes"] and
               int(span["address"], 16) < ADDRESS + EXTENT for span in receipt["spans"]):
            raise RuntimeError(f"BLE callback table overlaps {prior}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_BLE_FLASH_CALLBACKS_RAM_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PINNED, "native_decomp": str(native_decomp.relative_to(ROOT)),
        "native_decomp_sha256": sha(native_decomp),
        "pointer_literal": hex(LITERAL), "address": hex(ADDRESS),
        "bytes": EXTENT, "section_type": "NOBITS",
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "placement_elf": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": [HEAD], "imports_added": [],
        "fixed_ram_sections_checked": len(fixed),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["The stock initializer clears 0x3c bytes and the C provider accesses the first two words.",
                   "Final global layout, startup initialization, and device behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
