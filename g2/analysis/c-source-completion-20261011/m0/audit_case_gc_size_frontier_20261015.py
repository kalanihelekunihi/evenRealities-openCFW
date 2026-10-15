#!/usr/bin/env python3
"""Measure the current CASE C graph after section GC against stock capacity."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
BASE_RECEIPT = HERE / "case_current_20261014.elf.receipt.json"
LAYOUT_RECEIPT = HERE / "case-current-layout-20261014.json"
OUT = G2 / "build/c-firmware/20261015/case-gc-size-frontier"
LD = Path("/opt/homebrew/bin/arm-none-eabi-ld")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def image_extent(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        sections = {sec.name: sec["sh_size"] for sec in elf.iter_sections()}
        load_end = max(seg["p_vaddr"] + seg["p_filesz"] for seg in elf.iter_segments()
                       if seg["p_type"] == "PT_LOAD")
        return {"entry": elf["e_entry"], "load_bytes": load_end - 0x08000000,
                "text_bytes": sections.get(".text", 0),
                "vector_bytes": sections.get(".isr_vector", 0)}


def globals_defined(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "--defined-only", str(path)], text=True)
    return {parts[-1] for row in output.splitlines() if len(parts := row.split()) >= 3}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    prior = json.loads(LAYOUT_RECEIPT.read_text())
    reloc = Path(base["relocatable_object"])
    layout = Path(base["layout"])
    selected = Path(base["output"])
    if sha(reloc) != base["relocatable_sha256"] or sha(layout) != base["layout_sha256"]:
        raise RuntimeError("CASE current object or layout changed")
    if sha(selected) != base["output_sha256"] or sha(selected) != prior["source_elf_sha256"]:
        raise RuntimeError("CASE selected experimental ELF changed")
    OUT.mkdir(parents=True, exist_ok=True)
    linked = OUT / "case-current-gc-experimental.elf"
    command = [str(LD), "--gc-sections", "-T", str(layout), str(reloc), "-o", str(linked)]
    subprocess.run(command, check=True)
    undefined = subprocess.check_output(["arm-none-eabi-nm", "-u", str(linked)], text=True).strip()
    if undefined:
        raise RuntimeError(f"GC link introduced imports: {undefined}")
    original, gc = image_extent(selected), image_extent(linked)
    capacity = prior["stock_payload_bytes"]
    if original["load_bytes"] != prior["experimental_load_bytes"] or capacity != 55752:
        raise RuntimeError("CASE stock/candidate size baseline changed")
    if gc["load_bytes"] >= original["load_bytes"] or gc["vector_bytes"] != original["vector_bytes"]:
        raise RuntimeError("CASE GC probe did not preserve expected vector/size boundary")
    original_symbols, gc_symbols = globals_defined(selected), globals_defined(linked)
    receipt = {
        "status": "PASS_EXPERIMENTAL_CASE_GC_SIZE_FRONTIER",
        "source_receipt": str(BASE_RECEIPT.relative_to(ROOT)), "source_receipt_sha256": sha(BASE_RECEIPT),
        "layout_receipt": str(LAYOUT_RECEIPT.relative_to(ROOT)), "layout_receipt_sha256": sha(LAYOUT_RECEIPT),
        "source_relocatable": str(reloc.relative_to(ROOT)), "source_relocatable_sha256": sha(reloc),
        "linker_script": str(layout.relative_to(ROOT)), "linker_script_sha256": sha(layout),
        "linker_sha256": sha(LD), "command": command,
        "gc_elf": str(linked.relative_to(ROOT)), "gc_elf_sha256": sha(linked),
        "stock_payload_bytes": capacity, "stock_reset_entry": prior["stock_reset_entry"],
        "original_load_bytes": original["load_bytes"], "original_text_bytes": original["text_bytes"],
        "original_entry": hex(original["entry"]),
        "gc_load_bytes": gc["load_bytes"], "gc_text_bytes": gc["text_bytes"],
        "gc_entry": hex(gc["entry"]), "vector_bytes": gc["vector_bytes"],
        "gc_bytes_removed": original["load_bytes"] - gc["load_bytes"],
        "gc_overflow_bytes": gc["load_bytes"] - capacity,
        "defined_globals_before": len(original_symbols), "defined_globals_after": len(gc_symbols),
        "removed_globals": sorted(original_symbols - gc_symbols),
        "undefined_symbols": [], "source_complete": False, "full_payload_linked": False,
        "limits": ["Section GC is a size diagnostic, not a native-equivalent inclusion policy.",
                   "The GC C graph still exceeds the official CASE payload and reset entry remains misplaced.",
                   "Function reachability, source coverage, final layout, checksums and hardware behavior remain unproved."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], receipt["gc_bytes_removed"], receipt["gc_overflow_bytes"], sha(path))


if __name__ == "__main__":
    main()
