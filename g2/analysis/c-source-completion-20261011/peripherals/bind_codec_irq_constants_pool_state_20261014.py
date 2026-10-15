#!/usr/bin/env python3
"""Verify stock codec IRQ literals, then bind their C definitions into Main."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-wsf-timer-expired-current-receipt.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/codec_pdm_init_source_candidate/irq_constants.c"
OBJECT = OUT / "codec-irq-constants-pool.o"
SCRIPT = OUT / "codec-irq-constants-placement.ld"
ELF = OUT / "codec-irq-constants-placement.elf"
OUTPUT = OUT / "apollo-main-pool-state-codec-irq-bound.o"
RECEIPT = OUT / "pool-state-codec-irq-current-receipt.json"
VALUES = {"g2_codec_i2s_irq_number": (0x78f558, 44),
          "g2_pdm_alternate_irq": (0x78f55a, 48),
          "g2_pdm_production_irq": (0x78f55c, 48)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    blob = STOCK.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 429
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert set(VALUES) <= before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-Wall", "-Wextra",
                    "-Werror", "-O2", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == set(VALUES)
    lines = ["SECTIONS", "{"]
    for address, _ in sorted(VALUES.values()):
        section = f".g2_rom_{address:08x}"
        lines.append(f"  {section} 0x{address:08x} : {{ KEEP(*({section})) }}")
        lines.append(f'  ASSERT(SIZEOF({section}) == 2, "{section} must be two bytes")')
    lines.append("}")
    SCRIPT.write_text("\n".join(lines) + "\n")
    subprocess.run(["arm-none-eabi-ld", "-T", str(SCRIPT), str(OBJECT),
                    "-o", str(ELF)], check=True)
    with ELF.open("rb") as stream:
        elf = ELFFile(stream)
        syms = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
        for name, (address, value) in VALUES.items():
            section = elf.get_section_by_name(f".g2_rom_{address:08x}")
            native = blob[32 + address - 0x438000:32 + address - 0x438000 + 2]
            expected = value.to_bytes(2, "little", signed=True)
            assert syms[name] == address and section["sh_addr"] == address
            assert section["sh_size"] == 2 and section.data() == native == expected
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == set(VALUES) and after - before == set()
    assert len(before) == 429 and len(after) == 426
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_CODEC_IRQ_CONSTANTS_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "stock_blob_sha256": sha(STOCK),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "stock_rom_constants": {name: {"address": hex(address), "value": value}
                                for name, (address, value) in VALUES.items()},
        "placement_elf": str(ELF.relative_to(ROOT)), "placement_elf_sha256": sha(ELF),
        "imports_resolved": sorted(VALUES), "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["The isolated C literal sections match authenticated stock ROM bytes and addresses; whole-image ROM integration and hardware behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
