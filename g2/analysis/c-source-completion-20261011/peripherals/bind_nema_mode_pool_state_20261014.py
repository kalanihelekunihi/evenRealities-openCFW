#!/usr/bin/env python3
"""Add native-checked Nema mode and cache C to pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-gpu-blit-current-receipt.json"
MODE_RECEIPT = OUT / "nema-mode-current-receipt.json"
CACHE_RECEIPT = OUT / "nema-cache-current-receipt.json"
BOUND = OUT / "apollo-main-pool-state-nema-mode-bound.o"
RECEIPT = OUT / "pool-state-nema-mode-current-receipt.json"
PROVIDERS = {"display_driver_nema_mode_513924", "display_driver_nema_cache_4b1588"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def compile_provider(receipt, name):
    source = ROOT / receipt["source"]
    prior = ROOT / receipt["object"]
    assert sha(source) == receipt["source_sha256"]
    assert sha(prior) == receipt["object_sha256"]
    object_file = OUT / f"{name}-pool-state-abi.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(object_file)],
                   check=True)
    assert names(object_file, "-g", "--defined-only") == {name}
    return object_file


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    mode = json.loads(MODE_RECEIPT.read_text())
    cache = json.loads(CACHE_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_GPU_BLIT_C"
    assert mode["status"] == "PASS_CURRENT_MAIN_NEMA_MODE_C"
    assert cache["status"] == "PASS_CURRENT_MAIN_NEMA_CACHE_C"
    assert mode["bounded_oracle"]["cases"] == 2420
    assert cache["bounded_oracle"]["cases"] == 216
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = names(original, "-u")
    assert "display_driver_nema_mode_513924" in before
    mode_obj = compile_provider(mode, "display_driver_nema_mode_513924")
    cache_obj = compile_provider(cache, "display_driver_nema_cache_4b1588")
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(mode_obj),
                    str(cache_obj), "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    added = after - before
    assert after == before - PROVIDERS and not added
    receipt = {
        "status": "PASS_POOLED_MAIN_NEMA_MODE_CACHE_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "provider_receipts": {"mode": str(MODE_RECEIPT.relative_to(ROOT)),
                              "cache": str(CACHE_RECEIPT.relative_to(ROOT))},
        "provider_receipt_sha256": {"mode": sha(MODE_RECEIPT), "cache": sha(CACHE_RECEIPT)},
        "native_cases": {"mode": 2420, "cache": 216},
        "pool_abi_objects": {str(p.relative_to(ROOT)): sha(p) for p in (mode_obj, cache_obj)},
        "imports_resolved": sorted(before & PROVIDERS),
        "imports_added": sorted(added),
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Other Main imports and final image placement remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
