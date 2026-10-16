#!/usr/bin/env python3
"""Own the stock Main display-manager queue RAM cell in C."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_manager_queue_cell_20000664.c"
OUT = G2 / "build/c-firmware/20261015/main-display-manager-queue-cell-20000664"
BASE = G2 / "build/c-firmware/20261015/main-display-flush-view-474066/apollo-main-display-flush-view-474066.o"
RESOLVED = {"audio_uart_display_manager_queue_cell"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    literal = int.from_bytes(blob[0x4742f8-0x438000:0x4742fc-0x438000], "little")
    if literal != 0x20000658 or literal + 0xc != 0x20000664:
        raise RuntimeError("display-manager queue address changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_manager_queue_cell_20000664.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defined = subprocess.check_output(["arm-none-eabi-nm", "-S", "-g", "--defined-only",
                                       str(obj)], text=True).splitlines()
    if len(defined) != 1 or not re.search(
            r"\b00000004 D audio_uart_display_manager_queue_cell$", defined[0]):
        raise RuntimeError("display queue symbol size changed")
    sections = subprocess.check_output(["arm-none-eabi-readelf", "-SW", str(obj)], text=True)
    if not re.search(r"\.g2_ram_20000664\s+PROGBITS\s+[0-9a-fA-F]+\s+[0-9a-fA-F]+\s+000004\b",
                     sections):
        raise RuntimeError("display queue section changed")
    linked = OUT / "apollo-main-display-manager-queue-cell-20000664.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE), symbols(linked)
    if before - after != RESOLVED or after - before or len(before) != 237 or len(after) != 236:
        raise RuntimeError("display queue cell import contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_MANAGER_QUEUE_CELL_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_sha256": sha(linked), "official_payload_sha256": digest,
               "native_literal": "0x4742f8", "ram_cell": "0x20000664",
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(RESOLVED), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Section is source-owned but final linker placement and startup initialization remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
