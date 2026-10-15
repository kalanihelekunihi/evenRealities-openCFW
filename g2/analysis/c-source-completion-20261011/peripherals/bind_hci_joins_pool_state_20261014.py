#!/usr/bin/env python3
"""Apply source-backed Cordio HCI ABI joins to pooled Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-cordio-bda-copy-current-receipt.json"
PROVIDER = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-joins-round435/hci-joins-receipt.json"
MANIFEST = G2 / "firmware_c/experimental-link-aliases.json"
BOUND = OUT / "apollo-main-pool-state-hci-joins-bound.o"
RECEIPT = OUT / "pool-state-hci-joins-current-receipt.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    provider = json.loads(PROVIDER.read_text())
    manifest = json.loads(MANIFEST.read_text())["apollo_main"]
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_PINNED_CORDIO_BDA_COPY_C"
    assert provider["status"] == "completed"
    joins = provider["bindings"]
    assert len(joins) == 7 and all(manifest.get(a) == t for a, t in joins.items())
    assert all(sha(ROOT / path) == digest for path, digest in provider["source_hashes"].items())
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = symbols(["-u"], prior)
    definitions = symbols(["--defined-only"], prior)
    assert set(joins) <= before and set(joins.values()) <= definitions
    assert not (set(joins) & definitions)
    subprocess.run(["arm-none-eabi-ld", "-r",
                    *(f"--defsym={alias}={target}" for alias, target in joins.items()),
                    str(prior), "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    assert after == before - set(joins)
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_HCI_ABI_JOINS",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "provider_receipt": str(PROVIDER.relative_to(ROOT)), "provider_receipt_sha256": sha(PROVIDER),
               "alias_manifest": str(MANIFEST.relative_to(ROOT)), "alias_manifest_sha256": sha(MANIFEST),
               "bindings": joins, "imports_resolved": sorted(joins), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Pinned source signatures support these aliases; whole native behavior and call-domain equivalence remain unproved.",
                         "hciCb RAM placement and vendor command completion remain unresolved.",
                         "Other Main imports and final placement remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
