#!/usr/bin/env python3
"""Apply remaining documented runtime joins after FreeType source closure."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-freetype-strings-current-receipt.json"
MANIFEST = G2 / "firmware_c/experimental-link-aliases.json"
ALIASES = {"__aeabi_memcpy4": "__aeabi_memcpy", "qsort": "audio_uart_ft_qsort_567c4c",
           "strlen": "g2_log_module_length", "strncmp": "audio_l2c_strncmp"}
BOUND = OUT / "apollo-main-pool-state-runtime-aliases-bound.o"
RECEIPT = OUT / "pool-state-runtime-aliases-current-receipt.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    manifest = json.loads(MANIFEST.read_text())["apollo_main"]
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_FREETYPE_STRING_JOINS"
    assert all(manifest[name] == target for name, target in ALIASES.items())
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
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_RUNTIME_ABI_JOINS",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "alias_manifest": str(MANIFEST.relative_to(ROOT)), "alias_manifest_sha256": sha(MANIFEST),
               "bindings": ALIASES, "imports_resolved": sorted(ALIASES), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["qsort comparator and string input domains are only bounded; aliases do not establish whole-function stock equivalence.",
                         "Remaining libc/runtime imports, layout and hardware behavior remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
