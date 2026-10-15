#!/usr/bin/env python3
"""Bind the bounded native-checked ITCM delay body into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-portable-libc-current-receipt.json"
EVIDENCE = OUT / "itcm-delay-native-comparison.json"
RECEIPT = OUT / "pool-state-itcm-delay-current-receipt.json"
OUTPUT = OUT / "apollo-main-pool-state-itcm-delay-bound.o"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, option):
    result = subprocess.run(["arm-none-eabi-nm", option, str(path)],
                            check=True, capture_output=True, text=True)
    return {line.split()[-1] for line in result.stdout.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    evidence = json.loads(EVIDENCE.read_text())
    assert base["unresolved_after"] == 473
    assert evidence["status"] == "PASS_BOUNDED_NATIVE_ITCM_DELAY_C"
    assert evidence["cases"] == 139 and evidence["delay_entry_bytes"] == "0138fdd17047"
    source = ROOT / evidence["source"]
    assert sha(source) == evidence["source_sha256"]
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = symbols(prior, "-u")
    defined = symbols(prior, "--defined-only")
    assert "actual_itcm_delay" in before
    assert "audio_itcm_delay_iterations" in defined
    subprocess.run(["arm-none-eabi-ld", "-r",
                    "--defsym=actual_itcm_delay=audio_itcm_delay_iterations",
                    str(prior), "-o", str(OUTPUT)], check=True)
    after = symbols(OUTPUT, "-u")
    assert before - after == {"actual_itcm_delay"}
    assert after - before == set()
    assert len(before) == 473 and len(after) == 472
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_ITCM_DELAY_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "native_comparison": str(EVIDENCE.relative_to(ROOT)),
        "native_comparison_sha256": sha(EVIDENCE),
        "source": evidence["source"], "source_sha256": evidence["source_sha256"],
        "alias": "actual_itcm_delay=audio_itcm_delay_iterations",
        "imports_resolved": ["actual_itcm_delay"], "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": [
            "139 positive inputs have matching final R0 in Unicorn; cycle timing and interrupt interactions are unproved.",
            "Zero input wraps through 2^32 iterations in the native loop and was not exercised.",
            "Final ITCM placement and startup sequencing remain unproved."
        ],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
