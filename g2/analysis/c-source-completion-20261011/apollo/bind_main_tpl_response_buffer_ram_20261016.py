#!/usr/bin/env python3
"""Bind the bounded _tplReponse live buffer to C-owned RAM."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "tpl_response_buffer_ram.c"
LINKER = COMP / "tpl_response_buffer_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-ble-flash-callbacks-ram-bound/apollo-main-ble-flash-callbacks-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-tpl-response-buffer-ram-bound"
SYMBOL = "audio_tpl_response_buffer"
ADDRESS = 0x20004204
EXTENT = 8
LITERAL = 0x4b99ec
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
        raise RuntimeError("TPL response buffer pointer or payload changed")
    caller = COMP / "display_tpl_response.c"
    if "buffer[7]" not in caller.read_text() or "buffer, 8u" not in caller.read_text():
        raise RuntimeError("TPL response buffer access contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "tpl_response_buffer_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {SYMBOL} or names(obj, "-u"):
        raise RuntimeError("TPL response C symbols changed")
    if sections(obj)[".bss.opencfw.tpl.response.buffer"][1:] != (EXTENT, "SHT_NOBITS"):
        raise RuntimeError("TPL response C extent changed")
    placed = OUT / "tpl-response-buffer-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER), "-e", SYMBOL,
                    str(obj), "-o", str(placed)], check=True)
    if sections(placed)[".opencfw.tpl.response.buffer"] != (ADDRESS, EXTENT, "SHT_NOBITS"):
        raise RuntimeError("TPL response NOLOAD placement changed")
    located = {line.split()[-1]: int(line.split()[0], 16)
               for line in subprocess.check_output(
                   ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                   text=True).splitlines()}
    if located.get(SYMBOL) != ADDRESS:
        raise RuntimeError("TPL response symbol address changed")
    before = names(BASE, "-u")
    if len(before) != 176 or SYMBOL not in before:
        raise RuntimeError("Apollo TPL response base frontier changed")
    linked = OUT / "apollo-main-tpl-response-buffer-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != {SYMBOL} or after - before or len(after) != 175:
        raise RuntimeError("Apollo TPL response binding frontier changed")
    fixed = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for item in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", item.name)
            if match and item["sh_size"]:
                start = int(match.group(1), 16)
                fixed.append((start, start + item["sh_size"], item.name))
    if any(ADDRESS < end and start < ADDRESS + EXTENT for start, end, _ in fixed):
        raise RuntimeError("TPL response overlaps named fixed RAM")
    for prior in ("main-even-ai-ram-state-bound", "main-os-scheduler-state-ram-bound",
                  "main-battery-callback-manager-ram-bound"):
        prior_receipt = json.loads((G2 / "build/c-firmware/20261016" / prior / "receipt.json").read_text())
        if any(ADDRESS < int(span["address"], 16) + span["bytes"] and
               int(span["address"], 16) < ADDRESS + EXTENT for span in prior_receipt["spans"]):
            raise RuntimeError(f"TPL response overlaps {prior}")
    for prior in ("main-dashboard-layout-current-ram-bound",
                  "main-efs-transfer-state-ram-bound",
                  "main-ble-flash-staging-ram-bound",
                  "main-ble-flash-callbacks-ram-bound"):
        path = G2 / "build/c-firmware/20261016" / prior / "receipt.json"
        if not path.exists():
            continue
        prior_receipt = json.loads(path.read_text())
        start = int(prior_receipt["address"], 16)
        if ADDRESS < start + prior_receipt["bytes"] and start < ADDRESS + EXTENT:
            raise RuntimeError(f"TPL response overlaps {prior}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_TPL_RESPONSE_BUFFER_RAM_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "caller": str(caller.relative_to(ROOT)), "caller_sha256": sha(caller),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PINNED, "pointer_literal": hex(LITERAL),
        "address": hex(ADDRESS), "bytes": EXTENT, "section_type": "NOBITS",
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "placement_elf": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": [SYMBOL], "imports_added": [],
        "fixed_ram_sections_checked": len(fixed), "source_complete": False,
        "full_payload_linked": False, "hardware_proof": False,
        "limits": ["The stock pointer and C caller establish only an eight-byte used span.",
                   "Stock initialization, full allocation extent, final layout, and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
