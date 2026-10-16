#!/usr/bin/env python3
"""Bind the observed service-zero TPL row, without claiming full table extent."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "tpl_service_row0_ram.c"
LINKER = COMP / "tpl_service_row0_ram.ld"
BASE = G2 / "build/c-firmware/20261016/main-tpl-timeout-ids-ram-bound/apollo-main-tpl-timeout-ids-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-tpl-service-row0-ram-bound"
SYMBOL = "audio_tpl_service_table"
ADDRESS = 0x20071414
EXTENT = 20
LITERALS = (0x4b90e8, 0x4b9a30)
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
    if hashlib.sha256(image).hexdigest() != PINNED or any(
            int.from_bytes(image[x-0x438000:x-0x438000+4], "little") != ADDRESS
            for x in LITERALS):
        raise RuntimeError("TPL service table pointers or payload changed")
    native_caller = G2 / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-06.c"
    if "FUN_004b892c(0,PTR_FUN_00464d1c_1_004c9c68" not in native_caller.read_text():
        raise RuntimeError("TPL service-zero registration caller changed")
    init = COMP / "display_tpl_initialize.c"
    response = COMP / "display_tpl_response.c"
    if "* 20u" not in init.read_text() or \
            "row + 16u" not in init.read_text() or \
            "audio_tpl_service_table + 16u" not in response.read_text():
        raise RuntimeError("TPL row access contract changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "tpl_service_row0_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {SYMBOL} or names(obj, "-u"):
        raise RuntimeError("TPL service row C symbols changed")
    if sections(obj)[".bss.opencfw.tpl.service.row0"][1:] != (EXTENT, "SHT_NOBITS"):
        raise RuntimeError("TPL service row C extent changed")
    placed = OUT / "tpl-service-row0-placement.elf"
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINKER), "-e", SYMBOL,
                    str(obj), "-o", str(placed)], check=True)
    if sections(placed)[".opencfw.tpl.service.row0"] != (ADDRESS, EXTENT, "SHT_NOBITS"):
        raise RuntimeError("TPL service row NOLOAD placement changed")
    located = {line.split()[-1]: int(line.split()[0], 16)
               for line in subprocess.check_output(
                   ["arm-none-eabi-nm", "-g", "--defined-only", str(placed)],
                   text=True).splitlines()}
    if located.get(SYMBOL) != ADDRESS:
        raise RuntimeError("TPL service row symbol address changed")
    before = names(BASE, "-u")
    if len(before) != 174 or SYMBOL not in before:
        raise RuntimeError("Apollo TPL service row base frontier changed")
    linked = OUT / "apollo-main-tpl-service-row0-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    after = names(linked, "-u")
    if before - after != {SYMBOL} or after - before or len(after) != 173:
        raise RuntimeError("Apollo TPL service row binding frontier changed")
    fixed = []
    with linked.open("rb") as f:
        elf = ELFFile(f)
        for item in elf.iter_sections():
            match = re.fullmatch(r"\.g2_ram_([0-9a-fA-F]{8})", item.name)
            if match and item["sh_size"]:
                start = int(match.group(1), 16)
                fixed.append((start, start + item["sh_size"], item.name))
    if any(ADDRESS < end and start < ADDRESS + EXTENT for start, end, _ in fixed):
        raise RuntimeError("TPL service row overlaps named fixed RAM")
    for prior in ("main-even-ai-ram-state-bound", "main-os-scheduler-state-ram-bound",
                  "main-battery-callback-manager-ram-bound"):
        prior_receipt = json.loads((G2 / "build/c-firmware/20261016" / prior / "receipt.json").read_text())
        if any(ADDRESS < int(span["address"], 16) + span["bytes"] and
               int(span["address"], 16) < ADDRESS + EXTENT for span in prior_receipt["spans"]):
            raise RuntimeError(f"TPL service row overlaps {prior}")
    for prior in ("main-dashboard-layout-current-ram-bound", "main-efs-transfer-state-ram-bound",
                  "main-ble-flash-staging-ram-bound", "main-ble-flash-callbacks-ram-bound",
                  "main-tpl-response-buffer-ram-bound", "main-tpl-timeout-ids-ram-bound"):
        prior_receipt = json.loads((G2 / "build/c-firmware/20261016" / prior / "receipt.json").read_text())
        start = int(prior_receipt["address"], 16)
        if ADDRESS < start + prior_receipt["bytes"] and start < ADDRESS + EXTENT:
            raise RuntimeError(f"TPL service row overlaps {prior}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_TPL_SERVICE_ROW0_RAM_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "native_caller": str(native_caller.relative_to(ROOT)),
        "native_caller_sha256": sha(native_caller),
        "init_source": str(init.relative_to(ROOT)), "init_source_sha256": sha(init),
        "response_source": str(response.relative_to(ROOT)), "response_source_sha256": sha(response),
        "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
        "payload_sha256": PINNED, "pointer_literals": [hex(x) for x in LITERALS],
        "address": hex(ADDRESS), "bytes": EXTENT, "section_type": "NOBITS",
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "placement_elf": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": [SYMBOL], "imports_added": [],
        "fixed_ram_sections_checked": len(fixed), "source_complete": False,
        "full_payload_linked": False, "hardware_proof": False,
        "limits": ["The observed registration caller uses service zero and the response path reads row zero.",
                   "Dynamic service indices, full table extent, final layout, and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
