#!/usr/bin/env python3
"""Bind the exact eight-byte stock BLE ring event template."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-ble-msgtx-table-current-receipt.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/ble_master_ring_event_template.c"
OBJECT = OUT / "ble-master-ring-event-template-pool.o"
SCRIPT = OUT / "ble-master-ring-event-template-placement.ld"
ELF = OUT / "ble-master-ring-event-template-placement.elf"
OUTPUT = OUT / "apollo-main-pool-state-ring-event-template-bound.o"
RECEIPT = OUT / "pool-state-ring-event-template-current-receipt.json"
NAME = "audio_ble_master_ring_event_template"
ADDRESS = 0x78e4fc
SIZE = 8


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    blob = STOCK.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 419
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert NAME in before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-Wall", "-Wextra",
                    "-Werror", "-O2", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == {NAME}
    SCRIPT.write_text(f"SECTIONS {{ .g2_rom_{ADDRESS:08x} 0x{ADDRESS:08x} : "
                      f"{{ KEEP(*(.g2_rom_{ADDRESS:08x})) }} "
                      f'ASSERT(SIZEOF(.g2_rom_{ADDRESS:08x}) == {SIZE}, "ring event size") }}\n')
    subprocess.run(["arm-none-eabi-ld", "-T", str(SCRIPT), str(OBJECT),
                    "-o", str(ELF)], check=True)
    with ELF.open("rb") as stream:
        elf = ELFFile(stream)
        symbol = next(s for s in elf.get_section_by_name(".symtab").iter_symbols()
                      if s.name == NAME)
        section = elf.get_section_by_name(f".g2_rom_{ADDRESS:08x}")
        native = blob[32 + ADDRESS - 0x438000:32 + ADDRESS - 0x438000 + SIZE]
        assert symbol["st_value"] == ADDRESS and symbol["st_size"] == SIZE
        assert section["sh_addr"] == ADDRESS and section["sh_size"] == SIZE
        assert section.data() == native == bytes(SIZE)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == {NAME} and after - before == set()
    assert len(before) == 419 and len(after) == 418
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_RING_EVENT_TEMPLATE_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "stock_blob_sha256": sha(STOCK),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "stock_rom_address": hex(ADDRESS), "bytes": SIZE,
        "placement_elf": str(ELF.relative_to(ROOT)), "placement_elf_sha256": sha(ELF),
        "imports_resolved": [NAME], "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["The isolated C template matches all eight authenticated stock ROM bytes; whole-image placement and ring-message runtime behavior remain open.",
                  "Nearby Cordio DM tables contain Thumb function pointers and require source provider mapping before relocation."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
