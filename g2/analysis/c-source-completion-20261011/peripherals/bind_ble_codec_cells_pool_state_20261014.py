#!/usr/bin/env python3
"""Compile the recorded BLE and codec byte cells into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-ble-handler-current-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/ble_codec_byte_cells.c"
OBJECT = OUT / "ble-codec-byte-cells-pool.o"
OUTPUT = OUT / "apollo-main-pool-state-ble-codec-cells-bound.o"
RECEIPT = OUT / "pool-state-ble-codec-cells-current-receipt.json"
CELLS = {
    "audio_ble_flash_mode": "0x20074f62",
    "audio_ble_profile_handler_id": "0x20074f8a",
    "audio_ble_fast_mode_throttle_enabled": "0x20074f90",
    "audio_ble_connect_request_pending": "0x20074f91",
    "audio_ble_device_manager_queue_errors": "0x20074fb2",
    "audio_uart_font_flash_mode": "0x20074fb8",
    "audio_uart_font_flash_sleep": "0x20074fb9",
    "g2_pdm_alternate_initialized": "0x20074fba",
    "g2_pdm_production_initialized": "0x20074fbb",
    "audio_ble_ota_sync_enabled": "0x20074ff3",
}
ALIASES = {"audio_ble_discovery_handler_id_20074f8a"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 457
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    resolved = set(CELLS) | ALIASES
    assert resolved <= before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-fshort-enums", "-std=c11", "-ffreestanding",
                    "-Wall", "-Wextra", "-Werror", "-O2", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == resolved
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == resolved and after - before == set()
    assert len(before) == 457 and len(after) == 446
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_BLE_CODEC_BYTE_CELLS_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "native_ram_addresses": CELLS, "source_cell_bytes_each": 1,
        "shared_handler_alias": "audio_ble_discovery_handler_id_20074f8a",
        "imports_resolved": sorted(resolved), "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Native caller declarations fix these byte addresses; whole-image RAM integration, initialization values and hardware behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
