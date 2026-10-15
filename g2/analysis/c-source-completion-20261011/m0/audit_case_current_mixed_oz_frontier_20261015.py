#!/usr/bin/env python3
"""Rebuild the current pinned CASE C graph with mixed -Oz and fixed reset."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
OUT = G2 / "build/c-firmware/20261015/case-gc-size-frontier"
SELECTED = G2 / "analysis/case-source-candidate-round2-20261010/receipt.json"
RESET_RECEIPT = OUT / "reset-size-receipt.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/firmware_box.bin"
LAYOUT = HERE / "case_reset_placement_probe.ld"
LD = Path("/opt/homebrew/bin/arm-none-eabi-ld")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    subprocess.run(command, check=True, capture_output=True, text=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reset = json.loads(RESET_RECEIPT.read_text())
    if reset["status"] != "PASS_EXPERIMENTAL_CASE_RESET_SIZE_FRONTIER" or \
            reset["variants"][-1]["load_bytes"] != 66471:
        raise RuntimeError("CASE fixed-reset baseline changed")
    command_obj = OUT / "case-command-oz.o"
    startup_obj = OUT / "case-startup-oz-mixed.o"
    reloc = OUT / "case-current-oz-mixed.reloc.o"
    linked = OUT / "case-current-oz-mixed-fixed-reset.elf"
    run([sys.executable, str(HERE / "build_case_command_size_variant.py"),
         "--output", str(command_obj), "--opt", "Oz",
         "--os-source", "application_policy_idle_candidate.c",
         "--os-source", "application_policy_no_reply_candidate.c"])
    run([sys.executable, str(HERE / "build_startup_candidate.py"),
         "--output", str(startup_obj), "--opt", "Oz-except-divmod",
         "--exclude-selected-receipt", str(SELECTED)])
    run([str(LD), "-r", str(command_obj), str(startup_obj), "-o", str(reloc)])
    run([str(LD), "--gc-sections", "--sort-section=alignment", "-T", str(LAYOUT),
         str(reloc), "-o", str(linked)])
    undefined = subprocess.check_output(["arm-none-eabi-nm", "-u", str(linked)], text=True).strip()
    if undefined:
        raise RuntimeError("mixed -Oz CASE link has unresolved symbols")
    stock = STOCK.read_bytes()[32:]
    with linked.open("rb") as f:
        elf = ELFFile(f)
        load = max(seg["p_vaddr"] + seg["p_filesz"] for seg in elf.iter_segments()
                   if seg["p_type"] == "PT_LOAD") - 0x08000000
        vector = elf.get_section_by_name(".isr_vector").data()
        entry = elf["e_entry"]
    matches = [i for i in range(46) if vector[4*i:4*i+4] == stock[4*i:4*i+4]]
    if load != 63603 or entry != 0x08000145 or len(matches) != 13:
        raise RuntimeError("mixed -Oz CASE size or reset frontier changed")
    run([sys.executable, str(HERE / "audit_case_indirect_link_roots.py"), str(linked)])
    roots_path = linked.with_suffix(".indirect-roots.json")
    roots = json.loads(roots_path.read_text())
    if roots["source_entry_present"] != 39 or roots["native_pointer_target_count"] != 39:
        raise RuntimeError("CASE native pointer source leads changed")
    command_receipt = Path(str(command_obj) + ".receipt.json")
    startup_receipt = Path(str(startup_obj) + ".receipt.json")
    receipt = {
        "status": "PASS_EXPERIMENTAL_CASE_MIXED_OZ_FIXED_RESET_FRONTIER",
        "selected_receipt": str(SELECTED.relative_to(ROOT)), "selected_receipt_sha256": sha(SELECTED),
        "reset_frontier_receipt": str(RESET_RECEIPT.relative_to(ROOT)),
        "reset_frontier_receipt_sha256": sha(RESET_RECEIPT),
        "command_object": str(command_obj.relative_to(ROOT)), "command_object_sha256": sha(command_obj),
        "command_receipt_sha256": sha(command_receipt),
        "startup_object": str(startup_obj.relative_to(ROOT)), "startup_object_sha256": sha(startup_obj),
        "startup_receipt_sha256": sha(startup_receipt),
        "relocatable": str(reloc.relative_to(ROOT)), "relocatable_sha256": sha(reloc),
        "linker_script": str(LAYOUT.relative_to(ROOT)), "linker_script_sha256": sha(LAYOUT),
        "elf": str(linked.relative_to(ROOT)), "elf_sha256": sha(linked),
        "indirect_roots": str(roots_path.relative_to(ROOT)), "indirect_roots_sha256": sha(roots_path),
        "stock_payload_bytes": len(stock), "load_bytes": load,
        "overflow_bytes": load-len(stock), "bytes_saved_vs_os_fixed_sort": 66471-load,
        "entry": hex(entry), "matching_vector_words": matches,
        "native_pointer_leads_present": roots["source_entry_present"],
        "undefined_symbols": [], "source_complete": False, "flashable": False,
        "hardware_proof": False,
        "limits": ["Mixed -Oz is a diagnostic compiler profile, not an admitted CASE build policy.",
                   "The fixed-reset load still exceeds stock payload by 7,851 bytes and 33 vector words differ.",
                   "The 39 pointer-lead check proves symbol presence only; runtime-formed callbacks remain open.",
                   "Final placement, source coverage and hardware behavior remain unproved."]}
    path = OUT / "mixed-oz-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], load, receipt["overflow_bytes"], sha(path))


if __name__ == "__main__":
    main()
