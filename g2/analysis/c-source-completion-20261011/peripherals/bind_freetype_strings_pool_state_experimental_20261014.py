#!/usr/bin/env python3
"""Join current FreeType libc imports to selected, bounded C string providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-freetype-aliases-current-receipt.json"
MANIFEST = G2 / "firmware_c/experimental-link-aliases.json"
PROVIDERS = (
    G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-libc-joins-round420/libc-provider-receipt.json",
    G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-string-joins-round421/string-provider-receipt.json",
)
ALIASES = {"strcat": "g2_strcat", "strncpy": "audio_settings_copy_text", "strrchr": "g2_strrchr"}
BOUND = OUT / "apollo-main-pool-state-freetype-strings-bound.o"
RECEIPT = OUT / "pool-state-freetype-strings-current-receipt.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    manifest = json.loads(MANIFEST.read_text())["apollo_main"]
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_FREETYPE_ABI_JOINS"
    assert all(manifest[name] == target for name, target in ALIASES.items())
    assert all(json.loads(p.read_text())["status"].startswith("PASS_") for p in PROVIDERS)
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = symbols(["-u"], prior)
    definitions = symbols(["--defined-only"], prior)
    assert set(ALIASES) <= before and set(ALIASES.values()) <= definitions
    subprocess.run(["arm-none-eabi-ld", "-r",
                    *(f"--defsym={name}={target}" for name, target in ALIASES.items()),
                    str(prior), "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    assert after == before - set(ALIASES)
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_FREETYPE_STRING_JOINS",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "alias_manifest": str(MANIFEST.relative_to(ROOT)), "alias_manifest_sha256": sha(MANIFEST),
               "historical_provider_receipts": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in PROVIDERS],
               "bindings": ALIASES, "imports_resolved": sorted(ALIASES), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Selected string C bodies have bounded native probes; whole input domains and FreeType call behavior remain unqualified.",
                         "Remaining imports, final placement and physical hardware remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
