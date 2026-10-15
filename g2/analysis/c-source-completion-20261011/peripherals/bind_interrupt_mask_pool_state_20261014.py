#!/usr/bin/env python3
"""Bind pinned Ambiq interrupt-mask C leaf into the pooled Main object."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-dma-descriptors-current-receipt.json"
SOURCE = G2 / "components/foundation/ambiq_mspi/ambiq_interrupt_mask.c"
PROVENANCE = G2 / "components/foundation/ambiq_mspi/INTERRUPT_MASK_PROVENANCE.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECT = OUT / "interrupt-mask-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-interrupt-mask-bound.o"
RECEIPT = OUT / "pool-state-interrupt-mask-current-receipt.json"
NAME = "am_hal_interrupt_master_disable"
ALIAS = "opencfw_cmdq_critical_enter"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def imports(p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_DMA_DESCRIPTOR_C"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    provenance = json.loads(PROVENANCE.read_text())
    assert provenance["function"] == NAME
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-DOPENCFW_REAL_CRITICAL",
                    "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        sym, = [s for s in elf.get_section_by_name(".symtab").iter_symbols()
                if s.name == NAME]
        assert sym["st_size"] == 8
        section = elf.get_section(sym["st_shndx"])
        # ARM ELF function values retain the Thumb bit in the symbol table.
        start = sym["st_value"] & ~1
        compiled = section.data()[start:start + 8]
    stock = STOCK.read_bytes()[32:]
    assert hashlib.sha256(stock).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    offset = int(provenance["original_address"], 16) - 0x438000
    assert compiled == stock[offset:offset + 8] == bytes.fromhex(provenance["original_bytes"])
    before = imports(prior)
    assert {NAME, ALIAS} <= before and not imports(OBJECT)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT), "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    assert after == before - {NAME, ALIAS}
    receipt = {"status": "PASS_POOLED_MAIN_EXACT_AMBIQ_INTERRUPT_MASK_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "provenance": str(PROVENANCE.relative_to(ROOT)), "provenance_sha256": sha(PROVENANCE),
               "stock_payload_sha256": hashlib.sha256(stock).hexdigest(),
               "stock_address": provenance["original_address"], "matched_bytes": compiled.hex(),
               "pool_abi_object": str(OBJECT.relative_to(ROOT)), "pool_abi_object_sha256": sha(OBJECT),
               "imports_resolved": [NAME, ALIAS], "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Privileged execution is a caller precondition; stock leaf bytes do not prove IRQ behavior in the composed image.",
                         "Other Main imports and final placement remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
