#!/usr/bin/env python3
"""Bind checked GPU mode and position sources into the pooled Main object."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-nema-mode-current-receipt.json"
MODE_RECEIPT = OUT / "gpu-mode-current-receipt.json"
POSITION_RECEIPT = OUT / "gpu-position-current-receipt.json"
BOUND = OUT / "apollo-main-pool-state-gpu-mode-position-bound.o"
RECEIPT = OUT / "pool-state-gpu-mode-position-current-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def build(source_name, source_sha, object_name, prior_sha, symbols, label):
    source = ROOT / source_name
    prior = ROOT / object_name
    assert sha(source) == source_sha and sha(prior) == prior_sha
    obj = OUT / f"{label}-pool-state-abi.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)],
                   check=True)
    assert names(obj, "-g", "--defined-only") == set(symbols)
    return obj


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    mode = json.loads(MODE_RECEIPT.read_text())
    position = json.loads(POSITION_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_NEMA_MODE_CACHE_C"
    assert mode["status"] == "PASS_CURRENT_MAIN_GPU_MODE_C"
    assert position["status"] == "PASS_CURRENT_MAIN_GPU_POSITION_C"
    assert mode["bounded_oracle"]["cases"] == 408
    assert position["bounded_oracle"]["cases"] == 198
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = names(original, "-u")
    providers = set(mode["providers"]) | set(position["imports_resolved"])
    assert providers <= before
    objects = [build(mode["source"], mode["source_sha256"], mode["object"],
                     mode["object_sha256"], mode["providers"], "gpu-mode")]
    for row in position["source_units"]:
        objects.append(build(row["source"], row["source_sha256"], row["object"],
                             row["object_sha256"], row["defined"], Path(row["source"]).stem))
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), *map(str, objects),
                    "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    assert after == before - providers
    receipt = {
        "status": "PASS_POOLED_MAIN_GPU_MODE_POSITION_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "provider_receipts": {"mode": str(MODE_RECEIPT.relative_to(ROOT)),
                              "position": str(POSITION_RECEIPT.relative_to(ROOT))},
        "provider_receipt_sha256": {"mode": sha(MODE_RECEIPT),
                                     "position": sha(POSITION_RECEIPT)},
        "native_cases": {"mode": 408, "position": 198},
        "pool_abi_objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "imports_resolved": sorted(providers),
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
