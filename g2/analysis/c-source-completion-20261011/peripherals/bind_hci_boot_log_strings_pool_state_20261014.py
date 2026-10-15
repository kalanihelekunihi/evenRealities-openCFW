#!/usr/bin/env python3
"""Verify exact stock HCI boot log strings and link their C definitions."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-ble-rom-templates-current-receipt.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/hci_boot_log_strings.c"
OBJECT = OUT / "hci-boot-log-strings-pool.o"
SCRIPT = OUT / "hci-boot-log-strings-placement.ld"
ELF = OUT / "hci-boot-log-strings-placement.elf"
OUTPUT = OUT / "apollo-main-pool-state-hci-boot-logs-bound.o"
RECEIPT = OUT / "pool-state-hci-boot-logs-current-receipt.json"
SPANS = {"audio_ble_hci_boot_log_first": (0x71f5d0, 56),
         "audio_ble_hci_boot_log_retry": (0x754ad0, 36)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    blob = STOCK.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 424
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert set(SPANS) <= before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-Wall", "-Wextra",
                    "-Werror", "-O2", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == set(SPANS)
    lines = ["SECTIONS", "{"]
    for address, size in sorted(SPANS.values()):
        section = f".g2_rom_{address:08x}"
        lines.append(f"  {section} 0x{address:08x} : {{ KEEP(*({section})) }}")
        lines.append(f'  ASSERT(SIZEOF({section}) == {size}, "{section} size mismatch")')
    lines.append("}")
    SCRIPT.write_text("\n".join(lines) + "\n")
    subprocess.run(["arm-none-eabi-ld", "-T", str(SCRIPT), str(OBJECT),
                    "-o", str(ELF)], check=True)
    with ELF.open("rb") as stream:
        elf = ELFFile(stream)
        syms = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
        for name, (address, size) in SPANS.items():
            section = elf.get_section_by_name(f".g2_rom_{address:08x}")
            native = blob[32 + address - 0x438000:32 + address - 0x438000 + size]
            assert native[-1] == 0 and native[:-1].find(b"\0") == -1
            assert syms[name] == address and section["sh_addr"] == address
            assert section["sh_size"] == size and section.data() == native
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == set(SPANS) and after - before == set()
    assert len(before) == 424 and len(after) == 422
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_HCI_BOOT_LOG_STRINGS_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "stock_blob_sha256": sha(STOCK),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "stock_rom_spans": {name: {"address": hex(address), "bytes": size}
                            for name, (address, size) in SPANS.items()},
        "placement_elf": str(ELF.relative_to(ROOT)), "placement_elf_sha256": sha(ELF),
        "imports_resolved": sorted(SPANS), "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["The complete C string bytes and isolated addresses match authenticated stock ROM; whole-image ROM integration and HCI boot runtime remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
