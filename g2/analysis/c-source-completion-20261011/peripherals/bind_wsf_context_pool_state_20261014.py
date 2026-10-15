#!/usr/bin/env python3
"""Bind the native-checked IPSR context predicate into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-wsf-message-current-receipt.json"
EVIDENCE = OUT / "wsf-context-is-isr-native-comparison.json"
SOURCE = ROOT / "g2/components/foundation/wsf_radio/context_is_isr.c"
OBJECT = OUT / "wsf-context-is-isr-pool.o"
OUTPUT = OUT / "apollo-main-pool-state-wsf-context-bound.o"
RECEIPT = OUT / "pool-state-wsf-context-current-receipt.json"
NAME = "opencfw_wsf_context_is_isr"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    evidence = json.loads(EVIDENCE.read_text())
    assert base["unresolved_after"] == 431
    assert evidence["status"] == "PASS_BOUNDED_NATIVE_WSF_CONTEXT_IS_ISR_C"
    assert evidence["stock_entry_bytes"] == "eff30580002801d1002000e001207047"
    assert sha(SOURCE) == evidence["source_sha256"]
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert NAME in before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-Wall", "-Wextra",
                    "-Werror", "-O2", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == {NAME}
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == {NAME} and after - before == set()
    assert len(before) == 431 and len(after) == 430
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_WSF_CONTEXT_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "native_comparison": str(EVIDENCE.relative_to(ROOT)),
        "native_comparison_sha256": sha(EVIDENCE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "imports_resolved": [NAME], "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Compiled C and stock entry return values match 11 IPSR contexts; exception transitions, whole-image placement and hardware behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
