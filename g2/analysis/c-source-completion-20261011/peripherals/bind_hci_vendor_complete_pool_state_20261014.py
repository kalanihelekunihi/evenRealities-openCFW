#!/usr/bin/env python3
"""Bind the source-owned, native-branch-qualified Cordio vendor event child."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-hci-joins-current-receipt.json"
PROVIDER = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-vendor-complete-round436/vendor-complete-receipt.json"
SOURCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-vendor-complete-round436/vendor_complete.c"
OBJECT = OUT / "hci-vendor-complete-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-hci-vendor-complete-bound.o"
RECEIPT = OUT / "pool-state-hci-vendor-complete-current-receipt.json"
NAME = "hciCoreVsCmdCmplRcvd"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def imports(p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    provider = json.loads(PROVIDER.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_HCI_ABI_JOINS"
    assert provider["status"] == "completed"
    assert provider["import_delta"]["removed"] == [NAME]
    assert sha(SOURCE) == provider["source_unit"]["source_sha256"]
    native = ROOT / provider["native_branch_evidence"]["path"]
    assert sha(native) == provider["native_branch_evidence"]["sha256"]
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symbol, = [s for s in elf.get_section_by_name(".symtab").iter_symbols() if s.name == NAME]
        assert symbol["st_size"] > 0
    assert not imports(OBJECT)
    before = imports(prior)
    assert NAME in before
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT), "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    assert after == before - {NAME}
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_HCI_VENDOR_EVENT_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "provider_receipt": str(PROVIDER.relative_to(ROOT)), "provider_receipt_sha256": sha(PROVIDER),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "native_branch_evidence": str(native.relative_to(ROOT)), "native_branch_evidence_sha256": sha(native),
               "pool_abi_object": str(OBJECT.relative_to(ROOT)), "pool_abi_object_sha256": sha(OBJECT),
               "imports_resolved": [NAME], "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["The stock vendor command-complete case is inlined; this source models the observed event value, not a separate stock body.",
                         "hciCb product RAM placement, other Main imports, and final layout remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
