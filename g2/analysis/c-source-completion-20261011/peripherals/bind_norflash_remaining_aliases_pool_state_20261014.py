#!/usr/bin/env python3
"""Bind two recorded NOR flash caller names to pooled C definitions."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-nema-clear-current-receipt.json"
PRIOR_ALIAS_RECEIPT = OUT / "freetype-aliases-current-receipt.json"
MANIFEST = G2 / "firmware_c/experimental-link-aliases.json"
BOUND = OUT / "apollo-main-pool-state-norflash-remaining-bound.o"
RECEIPT = OUT / "pool-state-norflash-remaining-current-receipt.json"
ALIASES = {
    "g2_norflash_diagnostic_4733ee": "g2_log_transport_queue_failure",
    "g2_norflash_scheduler_state_44906c": "audio_uart_ring_kernel_state",
}


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
    prior = json.loads(PRIOR_ALIAS_RECEIPT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_NEMA_CLEAR_ALIAS"
    assert prior["status"] == "PASS_CURRENT_MAIN_FREETYPE_ALIAS_LINK"
    assert all(prior["aliases"][alias] == target and
               manifest["apollo_main"][alias] == target
               for alias, target in ALIASES.items())
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = imports(original)
    defs = definitions(original)
    assert set(ALIASES) <= before and set(ALIASES).isdisjoint(defs)
    assert all(target in defs for target in ALIASES.values())
    subprocess.run(["arm-none-eabi-ld", "-r",
                    *(f"--defsym={alias}={target}" for alias, target in ALIASES.items()),
                    str(original), "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    bound_defs = definitions(BOUND)
    assert after == before - set(ALIASES)
    assert all(bound_defs[alias] == bound_defs[target] == defs[target]
               for alias, target in ALIASES.items())
    receipt = {
        "status": "PASS_POOLED_MAIN_NORFLASH_RECORDED_ALIASES",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "prior_alias_receipt": str(PRIOR_ALIAS_RECEIPT.relative_to(ROOT)),
        "prior_alias_receipt_sha256": sha(PRIOR_ALIAS_RECEIPT),
        "alias_manifest": str(MANIFEST.relative_to(ROOT)),
        "alias_manifest_sha256": sha(MANIFEST),
        "aliases": ALIASES,
        "imports_resolved": sorted(ALIASES),
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Aliases establish source linkage, not full body equivalence; other imports and final placement remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
