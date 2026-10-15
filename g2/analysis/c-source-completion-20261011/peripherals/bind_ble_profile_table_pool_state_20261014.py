#!/usr/bin/env python3
"""Verify and bind the source-owned 20-halfword BLE profile ROM table."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-hci-register-callback-current-receipt.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/ble_profile_table.c"
CALLER = G2 / "components/audio/uart_thread_source_candidate/display_ble_profile_handler_init.c"
OBJECT = OUT / "ble-profile-table-pool.o"
SCRIPT = OUT / "ble-profile-table-placement.ld"
ELF = OUT / "ble-profile-table-placement.elf"
OUTPUT = OUT / "apollo-main-pool-state-ble-profile-table-bound.o"
RECEIPT = OUT / "pool-state-ble-profile-table-current-receipt.json"
NAME = "audio_ble_profile_table_78f530"
ADDRESS = 0x78f530
SIZE = 40


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    blob = STOCK.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 421
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
                      f'ASSERT(SIZEOF(.g2_rom_{ADDRESS:08x}) == {SIZE}, "profile size") }}\n')
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
        assert section.data() == native
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == {NAME} and after - before == set()
    assert len(before) == 421 and len(after) == 420
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_BLE_PROFILE_TABLE_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "stock_blob_sha256": sha(STOCK),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "caller": str(CALLER.relative_to(ROOT)), "caller_sha256": sha(CALLER),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "stock_rom_address": hex(ADDRESS), "halfwords": 20, "bytes": SIZE,
        "placement_elf": str(ELF.relative_to(ROOT)), "placement_elf_sha256": sha(ELF),
        "imports_resolved": [NAME], "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["All 40 C table bytes match authenticated stock ROM in an isolated fixed-address link; semantic interpretation of every halfword and whole-image ROM integration remain open.",
                  "The unrelated even 0x5fa056 dispatch pointer remains unresolved."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
