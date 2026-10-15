#!/usr/bin/env python3
"""Add source-owned BLE callback cells and minimum appMaster state."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-radio-literals-current-receipt.json"
PRIOR = (G2 / "build/c-firmware/ble-subsystem-slots-round1041/receipt.json",
         G2 / "build/c-firmware/ble-subsystem-state-round1043/receipt.json")
BOUND = OUT / "apollo-main-pool-state-ble-cells-bound.o"
RECEIPT = OUT / "pool-state-ble-cells-current-receipt.json"
PROVIDERS = {"audio_ble_subsystem_primary_callback_slot",
             "audio_ble_subsystem_callback_slot",
             "audio_ble_subsystem_state_20071670"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_EXACT_RADIO_ROM_LITERALS_C"
    records = [json.loads(path.read_text()) for path in PRIOR]
    assert records[0]["status"] == "PASS_BLE_SUBSYSTEM_CALLBACK_SLOTS_PLACEMENT"
    assert records[1]["status"] == "PASS_BLE_SUBSYSTEM_STATE_MINIMUM_PLACEMENT"
    assert records[1]["minimum_span_bytes"] == 158
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = names(original, "-u")
    assert PROVIDERS <= before
    objects = []
    for label, record in zip(("slots", "state"), records):
        source = G2 / record["source"]
        linker = G2 / record["linker"]
        assert sha(source) == record["source_sha256"]
        assert sha(linker) == record["linker_sha256"]
        obj = OUT / f"ble-subsystem-{label}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    assert set().union(*(names(obj, "-g", "--defined-only") for obj in objects)) == PROVIDERS
    assert not set().union(*(names(obj, "-u") for obj in objects))
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), *map(str, objects),
                    "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    assert after == before - PROVIDERS
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_BLE_CELLS_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "placement_receipts": {str(path.relative_to(ROOT)): sha(path) for path in PRIOR},
        "pool_abi_objects": {str(path.relative_to(ROOT)): sha(path) for path in objects},
        "imports_resolved": sorted(PROVIDERS),
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["The appMaster 158-byte state allocation is a proven minimum, not original extent.",
                  "Relocatable link does not prove callback cell placement, full RAM nonoverlap or boot initialization.",
                  "Other Main imports and hardware execution remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
