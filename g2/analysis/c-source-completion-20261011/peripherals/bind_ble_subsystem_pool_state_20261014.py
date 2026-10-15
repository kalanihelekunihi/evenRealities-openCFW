#!/usr/bin/env python3
"""Carry bounded native-checked BLE subsystem callbacks into pooled Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-hci-masks-current-receipt.json"
PRIMARY_RECEIPT = G2 / "build/c-firmware/ble-subsystem-primary-round1040/receipt.json"
SECONDARY_RECEIPT = G2 / "build/c-firmware/ble-subsystem-secondary-round1042/receipt.json"
BOUND = OUT / "apollo-main-pool-state-ble-subsystem-bound.o"
RECEIPT = OUT / "pool-state-ble-subsystem-current-receipt.json"
PROVIDERS = ("audio_ble_subsystem_primary_handler_4b3bec",
             "audio_ble_subsystem_handler_503936")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    prior = [json.loads(path.read_text()) for path in (PRIMARY_RECEIPT, SECONDARY_RECEIPT)]
    assert base["status"] == "PASS_POOLED_MAIN_EXACT_HCI_MASK_C"
    assert [r["status"] for r in prior] == ["PASS_NATIVE_BLE_SUBSYSTEM_PRIMARY_CALLBACK",
                                            "PASS_NATIVE_BLE_SUBSYSTEM_SECONDARY_CALLBACK"]
    assert [r["native_cases"] for r in prior] == [20, 12]
    objects = []
    for name, row in zip(PROVIDERS, prior):
        source = G2 / row["source"]
        assert sha(source) == row["source_sha256"]
        obj = OUT / f"{name}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        assert names(obj, "-g", "--defined-only") == {name} and not names(obj, "-u")
        objects.append(obj)
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = names(original, "-u")
    assert set(PROVIDERS) <= before
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), *map(str, objects),
                    "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    assert after == before - set(PROVIDERS)
    receipt = {
        "status": "PASS_POOLED_MAIN_BLE_SUBSYSTEM_CALLBACKS_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "native_receipts": {str(path.relative_to(ROOT)): sha(path) for path in
                            (PRIMARY_RECEIPT, SECONDARY_RECEIPT)},
        "native_cases": {PROVIDERS[0]: 20, PROVIDERS[1]: 12},
        "pool_abi_objects": {str(path.relative_to(ROOT)): sha(path) for path in objects},
        "imports_resolved": list(PROVIDERS),
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Native comparison covers valid event buffers only.",
                  "Other Main imports, final placement and BLE hardware behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
