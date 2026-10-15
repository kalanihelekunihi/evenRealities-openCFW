#!/usr/bin/env python3
"""Carry the native-checked GPU blit C provider into the pooled Main graph."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE_RECEIPT = G2 / "build/c-firmware/pool-state-round873/receipt.json"
PROVIDER_RECEIPT = G2 / "build/c-firmware/20261014/main-root-dependencies/gpu-blit-current-receipt.json"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
RECOMPILED = OUT / "gpu-blit-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-gpu-blit-bound.o"
RECEIPT = OUT / "pool-state-gpu-blit-current-receipt.json"
PROVIDER = "display_driver_gpu_blit_4b1608"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    provider = json.loads(PROVIDER_RECEIPT.read_text())
    assert base["status"] == "PASS_DISTINCT_TIMEOUT_TEXT_AND_LIVE_RAM_STATE"
    assert provider["status"] == "PASS_CURRENT_MAIN_GPU_BLIT_C"
    original = G2 / base["linked_object"]
    object_file = ROOT / provider["object"]
    source = ROOT / provider["source"]
    assert sha(original) == base["linked_sha256"]
    assert sha(object_file) == provider["object_sha256"]
    assert sha(source) == provider["source_sha256"]
    assert provider["imports_resolved"] == [PROVIDER]
    assert provider["bounded_oracle"]["cases"] == 3611
    before = imports(original)
    assert PROVIDER in before and len(before) == base["unresolved_after"]
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(RECOMPILED)],
                   check=True)
    definitions = subprocess.check_output(
        ["arm-none-eabi-nm", "-g", "--defined-only", str(RECOMPILED)], text=True)
    assert {line.split()[-1] for line in definitions.splitlines()} == {PROVIDER}
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(RECOMPILED),
                    "-o", str(BOUND)], check=True)
    after = imports(BOUND)
    assert after == before - {PROVIDER}
    receipt = {
        "status": "PASS_POOLED_MAIN_GPU_BLIT_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "provider_receipt": str(PROVIDER_RECEIPT.relative_to(ROOT)),
        "provider_receipt_sha256": sha(PROVIDER_RECEIPT),
        "native_cases": provider["bounded_oracle"]["cases"],
        "pool_abi_object": str(RECOMPILED.relative_to(ROOT)),
        "pool_abi_object_sha256": sha(RECOMPILED),
        "imports_resolved": [PROVIDER],
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Remaining Main imports and final image placement are open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
