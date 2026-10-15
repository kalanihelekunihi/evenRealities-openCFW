#!/usr/bin/env python3
"""Reproduce CASE reset placement and aligned-section size diagnostics."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
OUT = G2 / "build/c-firmware/20261015/case-gc-size-frontier"
SOURCE_RECEIPT = HERE / "case_current_20261014.elf.receipt.json"
GC_RECEIPT = OUT / "receipt.json"
LAYOUT = HERE / "case_reset_placement_probe.ld"
STOCK = G2 / "blobs/official/g2-2.2.6.10/firmware_box.bin"
LD = Path("/opt/homebrew/bin/arm-none-eabi-ld")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(path, stock):
    with path.open("rb") as f:
        elf = ELFFile(f)
        load = max(seg["p_vaddr"] + seg["p_filesz"] for seg in elf.iter_segments()
                   if seg["p_type"] == "PT_LOAD") - 0x08000000
        vector = elf.get_section_by_name(".isr_vector").data()
        reset = elf.get_section_by_name(".text.reset")
        matches = [i for i in range(46) if vector[4*i:4*i+4] == stock[4*i:4*i+4]]
        return {"load_bytes": load, "overflow_bytes": load - len(stock),
                "entry": hex(elf["e_entry"]), "reset_section_address": hex(reset["sh_addr"]),
                "reset_section_bytes": reset["sh_size"], "vector_bytes": len(vector),
                "matching_vector_words": matches,
                "vector_reset_word": hex(int.from_bytes(vector[4:8], "little"))}


def defined(path):
    result = subprocess.check_output(["arm-none-eabi-nm", "-g", "--defined-only", str(path)], text=True)
    return {row.split()[-1] for row in result.splitlines() if len(row.split()) >= 3}


def main():
    source = json.loads(SOURCE_RECEIPT.read_text())
    gc = json.loads(GC_RECEIPT.read_text())
    reloc = Path(source["relocatable_object"])
    if sha(reloc) != source["relocatable_sha256"] or not LAYOUT.is_file():
        raise RuntimeError("CASE object or layout changed")
    old = ROOT / gc["gc_elf"]
    if sha(old) != gc["gc_elf_sha256"] or gc["gc_load_bytes"] != 66432:
        raise RuntimeError("CASE GC baseline changed")
    stock_package = STOCK.read_bytes()
    stock = stock_package[32:]
    if len(stock) != 55752 or sha(STOCK) != "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374":
        raise RuntimeError("stock CASE payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, flags in (("fixed-reset", []), ("fixed-reset-sort", ["--sort-section=alignment"])):
        path = OUT / ("case-current-gc-" + name + ".elf")
        command = [str(LD), "--gc-sections", *flags, "-T", str(LAYOUT), str(reloc),
                   "-o", str(path)]
        subprocess.run(command, check=True)
        undefined = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True).strip()
        if undefined:
            raise RuntimeError("CASE placement introduced unresolved symbols")
        measurements = inspect(path, stock)
        if measurements["entry"] != "0x8000145" or measurements["reset_section_bytes"] != 8 or \
                measurements["vector_reset_word"] != "0x8000145":
            raise RuntimeError("CASE reset placement changed")
        if defined(path) != defined(old):
            raise RuntimeError("CASE retained global set changed")
        rows.append({"name": name, "command": command, "elf": str(path.relative_to(ROOT)),
                     "elf_sha256": sha(path), **measurements})
    if rows[0]["load_bytes"] != 66572 or rows[1]["load_bytes"] != 66471 or \
            len(rows[1]["matching_vector_words"]) != 13:
        raise RuntimeError("CASE reset/size frontier changed")
    receipt = {"status": "PASS_EXPERIMENTAL_CASE_RESET_SIZE_FRONTIER",
               "source_receipt": str(SOURCE_RECEIPT.relative_to(ROOT)),
               "source_receipt_sha256": sha(SOURCE_RECEIPT),
               "gc_receipt": str(GC_RECEIPT.relative_to(ROOT)), "gc_receipt_sha256": sha(GC_RECEIPT),
               "linker_script": str(LAYOUT.relative_to(ROOT)), "linker_script_sha256": sha(LAYOUT),
               "source_relocatable_sha256": sha(reloc), "stock_package_sha256": sha(STOCK),
               "stock_payload_bytes": len(stock), "stock_reset_entry": "0x08000145",
               "variants": rows, "sort_bytes_saved": rows[0]["load_bytes"]-rows[1]["load_bytes"],
               "source_complete": False, "flashable": False, "hardware_proof": False,
               "limits": ["Reset placement qualifies only the first two vector words; 33 of 46 vector words still differ.",
                          "The best fixed-reset link still exceeds stock CASE payload by 10,719 bytes.",
                          "Section sorting is a diagnostic layout choice; rooted reachability and final scatter placement remain unproved."]}
    path = OUT / "reset-size-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], rows[1]["overflow_bytes"], sha(path))


if __name__ == "__main__":
    main()
