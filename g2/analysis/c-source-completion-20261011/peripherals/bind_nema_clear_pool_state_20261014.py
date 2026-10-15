#!/usr/bin/env python3
"""Bind the Nema clear caller name to the checked same-entry C provider."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-norflash-alias-current-receipt.json"
PROVIDER_RECEIPT = OUT / "nema-rectangle-alias-receipt.json"
BOUND = OUT / "apollo-main-pool-state-nema-clear-bound.o"
RECEIPT = OUT / "pool-state-nema-clear-current-receipt.json"
ALIAS = "display_driver_nema_clear_522ae0"
PROVIDER = "audio_uart_nema_mask_rectangle_522ae0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def definitions(path):
    return {parts[2]: (parts[0], parts[1]) for line in subprocess.check_output(
        ["arm-none-eabi-nm", "--defined-only", str(path)], text=True).splitlines()
            if len(parts := line.split()) == 3 and parts[1].isupper()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    provider = json.loads(PROVIDER_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_NORFLASH_ALIAS_C"
    assert provider["status"] == "PASS_CURRENT_MAIN_NEMA_RECTANGLE_ALIAS"
    assert provider["native_entry"] == "0x522ae0"
    assert (provider["alias"], provider["provider"]) == (ALIAS, PROVIDER)
    source = ROOT / provider["provider_source"]
    oracle = ROOT / provider["bounded_oracle"]["path"]
    assert sha(source) == provider["provider_source_sha256"]
    assert sha(oracle) == provider["bounded_oracle"]["sha256"]
    observed = subprocess.check_output([sys.executable, str(oracle)],
                                       cwd=ROOT, text=True).strip().splitlines()[-1]
    assert observed == "PASS_NEMA_MASK_RECTANGLE_NATIVE_RETURN 144"
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = imports(original)
    defs = definitions(original)
    assert ALIAS in before and ALIAS not in defs and defs[PROVIDER][1] == "T"
    subprocess.run(["arm-none-eabi-ld", "-r", "--defsym", f"{ALIAS}={PROVIDER}",
                    str(original), "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    bound_defs = definitions(BOUND)
    assert after == before - {ALIAS}
    assert bound_defs[ALIAS] == bound_defs[PROVIDER] == defs[PROVIDER]
    receipt = {
        "status": "PASS_POOLED_MAIN_NEMA_CLEAR_ALIAS",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "provider_receipt": str(PROVIDER_RECEIPT.relative_to(ROOT)),
        "provider_receipt_sha256": sha(PROVIDER_RECEIPT),
        "source": str(source.relative_to(ROOT)),
        "source_sha256": sha(source),
        "native_return_cases": 144,
        "imports_resolved": [ALIAS],
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Other Main imports, final placement and hardware behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
