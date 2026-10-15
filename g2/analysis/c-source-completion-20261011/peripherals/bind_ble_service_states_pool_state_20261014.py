#!/usr/bin/env python3
"""Bind five adjacent BLE service handler records into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-ble-codec-cells-current-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/ble_service_handler_states.c"
OBJECT = OUT / "ble-service-handler-states-pool.o"
OUTPUT = OUT / "apollo-main-pool-state-ble-service-states-bound.o"
RECEIPT = OUT / "pool-state-ble-service-states-current-receipt.json"
CELLS = {
    "audio_ble_efs_handler_state": "0x200748a4",
    "audio_ble_ess_handler_state": "0x200748a8",
    "audio_ble_eus_handler_state": "0x200748ac",
    "audio_ble_nus_handler_state": "0x200748b0",
    "audio_ble_ota_handler_state": "0x200748b4",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 446
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert set(CELLS) <= before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-fshort-enums", "-std=c11", "-ffreestanding",
                    "-Wall", "-Wextra", "-Werror", "-O2", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == set(CELLS)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == set(CELLS) and after - before == set()
    assert len(before) == 446 and len(after) == 441
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_BLE_SERVICE_STATES_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "native_ram_addresses": CELLS, "record_bytes_each": 4,
        "imports_resolved": sorted(CELLS), "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Selected service initialization writes all four bytes of each record; whole-image placement, startup and hardware behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
