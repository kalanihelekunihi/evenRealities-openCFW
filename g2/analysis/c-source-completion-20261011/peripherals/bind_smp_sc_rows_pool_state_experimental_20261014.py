#!/usr/bin/env python3
"""Bind the observed three-row SMP SC RAM minimum to pooled Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-cordio-ecc-current-receipt.json"
SOURCE = G2 / "components/main/smp_sc_rows_candidate_20261014/smp_sc_rows.c"
VERIFY = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ble_conn_hci_sc.py"
OBJECT = OUT / "smp-sc-rows-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-smp-sc-rows-bound.o"
RECEIPT = OUT / "pool-state-smp-sc-rows-current-receipt.json"
NAME = "audio_ble_smp_sc_rows"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def imports(p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_CORDIO_ECC_C"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    run = subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    lines = run.stdout.strip().splitlines()
    assert any(line == "PASS SmpScInit ()" for line in lines), lines
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symbol, = [s for s in elf.get_section_by_name(".symtab").iter_symbols() if s.name == NAME]
        assert symbol["st_size"] == 84 and elf.get_section(symbol["st_shndx"]).name == ".bss"
    before = imports(prior)
    assert NAME in before and not imports(OBJECT)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT), "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    assert after == before - {NAME}
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_SMP_SC_ROW_STORAGE_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "native_initializer_verifier": str(VERIFY.relative_to(ROOT)),
               "native_initializer_verifier_sha256": sha(VERIFY), "native_initializer_output": lines,
               "observed_native_address": "0x200728f4", "row_count": 3, "row_bytes": 28,
               "compiled_storage_bytes": 84, "compiled_storage_alignment": 4,
               "pool_abi_object": str(OBJECT.relative_to(ROOT)), "pool_abi_object_sha256": sha(OBJECT),
               "imports_resolved": [NAME], "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["The three indexed rows support an 84-byte minimum; original allocation extent and overlap with adjacent product RAM are unproved.",
                         "Final SRAM placement, full SMP pairing behavior, and hardware operation remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
