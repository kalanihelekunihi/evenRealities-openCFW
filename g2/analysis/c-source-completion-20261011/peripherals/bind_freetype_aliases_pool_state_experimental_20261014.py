#!/usr/bin/env python3
"""Apply recorded FreeType provider joins to pooled Main C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-freetype-base-current-receipt.json"
MANIFEST = G2 / "firmware_c/experimental-link-aliases.json"
EVIDENCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-base-round413/base-source-receipt.json"
BOUND = OUT / "apollo-main-pool-state-freetype-aliases-bound.o"
RECEIPT = OUT / "pool-state-freetype-aliases-current-receipt.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    manifest = json.loads(MANIFEST.read_text())["apollo_main"]
    evidence = json.loads(EVIDENCE.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_FREETYPE_BASE_C"
    assert evidence["all_alias_address_matches"] == 22
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = symbols(["-u"], prior)
    defined = symbols(["--defined-only"], prior)
    joins = {a: t for a, t in manifest.items()
             if (a.startswith("FT_") or a.startswith("ft_")) and a in before and t in defined}
    assert len(joins) == 27
    assert all(a not in defined for a in joins)
    subprocess.run(["arm-none-eabi-ld", "-r",
                    *(f"--defsym={a}={t}" for a, t in joins.items()),
                    str(prior), "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    assert after == before - set(joins)
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_FREETYPE_ABI_JOINS",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "alias_manifest": str(MANIFEST.relative_to(ROOT)), "alias_manifest_sha256": sha(MANIFEST),
               "historical_alias_evidence": str(EVIDENCE.relative_to(ROOT)),
               "historical_alias_evidence_sha256": sha(EVIDENCE),
               "bindings": joins, "imports_resolved": sorted(joins), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Recorded aliases join C providers by source signature/address evidence; full native body and call-domain equivalence remain unproved.",
                         "Remaining libc/FreeType dependencies, jump-buffer ABI and final placement remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
