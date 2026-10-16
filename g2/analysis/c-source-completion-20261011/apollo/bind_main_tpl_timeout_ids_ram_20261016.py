#!/usr/bin/env python3
"""Bind the three stock TPL delayed-callback argument bytes to C RAM."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "tpl_timeout_ids_ram.c"
LINKER = COMP / "tpl_timeout_ids_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-tpl-response-buffer-ram-bound/apollo-main-tpl-response-buffer-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-tpl-timeout-ids-ram-bound"
SYMBOL = "audio_tpl_timeout_ids"
ADDRESS = 0x20074b04
EXTENT = 3
LITERAL = 0x4b9618
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
        raise RuntimeError("TPL timeout argument pointer or payload changed")
    native = G2 / "research/corpus/apollo-main/ghidra/open-2026-09-29/decomp/004b8c44.c"
    decomp = native.read_text()
    if not all(s in decomp for s in ("DAT_004b9618[2] = param_1", "*puVar1 = param_2",
                                      "puVar1[1] = param_3", "fw_event_loop_push_delayed")):
        raise RuntimeError("TPL timeout native write or delayed argument contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "tpl_timeout_ids_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {SYMBOL} or names(obj, "-u"):
        raise RuntimeError("TPL timeout C symbols changed")
    if sections(obj)[".bss.opencfw.tpl.timeout.ids"][1:] != (EXTENT, "SHT_NOBITS"):
        raise RuntimeError("TPL timeout C extent changed")
    placed = OUT / "tpl-timeout-ids-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER), "-e", SYMBOL,
                    str(obj), "-o", str(placed)], check=True)
    if sections(placed)[".opencfw.tpl.timeout.ids"] != (ADDRESS, EXTENT, "SHT_NOBITS"):
        raise RuntimeError("TPL timeout NOLOAD placement changed")
    located = {line.split()[-1]: int(line.split()[0], 16)
               for line in subprocess.check_output(
                   ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                   text=True).splitlines()}
    if located.get(SYMBOL) != ADDRESS:
        raise RuntimeError("TPL timeout symbol address changed")
    before = names(BASE, "-u")
    if len(before) != 175 or SYMBOL not in before:
        raise RuntimeError("Apollo TPL timeout base frontier changed")
    linked = OUT / "apollo-main-tpl-timeout-ids-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != {SYMBOL} or after - before or len(after) != 174:
        raise RuntimeError("Apollo TPL timeout binding frontier changed")
    fixed = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for item in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", item.name)
            if match and item["sh_size"]:
                start = int(match.group(1), 16)
                fixed.append((start, start + item["sh_size"], item.name))
    if any(ADDRESS < end and start < ADDRESS + EXTENT for start, end, _ in fixed):
        raise RuntimeError("TPL timeout overlaps named fixed RAM")
    for prior in ("main-even-ai-ram-state-bound", "main-os-scheduler-state-ram-bound",
                  "main-battery-callback-manager-ram-bound"):
        prior_receipt = json.loads((G2 / "build/c-firmware/20261016" / prior / "receipt.json").read_text())
        if any(ADDRESS < int(span["address"], 16) + span["bytes"] and
               int(span["address"], 16) < ADDRESS + EXTENT for span in prior_receipt["spans"]):
            raise RuntimeError(f"TPL timeout overlaps {prior}")
    for prior in ("main-dashboard-layout-current-ram-bound", "main-efs-transfer-state-ram-bound",
                  "main-ble-flash-staging-ram-bound", "main-ble-flash-callbacks-ram-bound",
                  "main-tpl-response-buffer-ram-bound"):
        prior_receipt = json.loads((G2 / "build/c-firmware/20261016" / prior / "receipt.json").read_text())
        start = int(prior_receipt["address"], 16)
        if ADDRESS < start + prior_receipt["bytes"] and start < ADDRESS + EXTENT:
            raise RuntimeError(f"TPL timeout overlaps {prior}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_TPL_TIMEOUT_IDS_RAM_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "native_decomp": str(native.relative_to(ROOT)), "native_decomp_sha256": sha(native),
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
        "limits": ["The native function writes three bytes and passes their address to a delayed callback.",
                   "Producer history, full allocation extent, final layout, and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
