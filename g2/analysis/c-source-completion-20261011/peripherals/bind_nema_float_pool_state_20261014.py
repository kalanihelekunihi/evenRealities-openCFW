#!/usr/bin/env python3
"""Bind checked Nema float translation C into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-gpu-mode-position-current-receipt.json"
PROVIDER_RECEIPT = OUT / "nema-float-translate-current-receipt.json"
OBJECT = OUT / "nema-float-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-nema-float-bound.o"
RECEIPT = OUT / "pool-state-nema-float-current-receipt.json"
PROVIDER = "display_driver_nema_float_translate_5228b0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    provider = json.loads(PROVIDER_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_GPU_MODE_POSITION_C"
    assert provider["status"] == "PASS_CURRENT_MAIN_NEMA_FLOAT_TRANSLATE_C"
    assert provider["bounded_oracle"]["cases"] == 512
    original = ROOT / base["linked_object"]
    source = ROOT / provider["source"]
    prior = ROOT / provider["object"]
    assert sha(original) == base["linked_sha256"]
    assert sha(source) == provider["source_sha256"]
    assert sha(prior) == provider["object_sha256"]
    before = names(original, "-u")
    assert PROVIDER in before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(OBJECT)],
                   check=True)
    assert names(OBJECT, "-g", "--defined-only") == {PROVIDER}
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(OBJECT),
                    "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    assert after == before - {PROVIDER}
    receipt = {
        "status": "PASS_POOLED_MAIN_NEMA_FLOAT_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "provider_receipt": str(PROVIDER_RECEIPT.relative_to(ROOT)),
        "provider_receipt_sha256": sha(PROVIDER_RECEIPT),
        "native_cases": 512,
        "pool_abi_object": str(OBJECT.relative_to(ROOT)),
        "pool_abi_object_sha256": sha(OBJECT),
        "imports_resolved": [PROVIDER],
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Other Main imports, final image placement and device execution remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
