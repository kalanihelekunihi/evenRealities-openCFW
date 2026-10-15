#!/usr/bin/env python3
"""Compile and link fixed-address Main state cells and a display-state alias."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-service-mode-current-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/byte_state_cells.c"
OBJECT = OUT / "byte-state-cells-pool.o"
OUTPUT = OUT / "apollo-main-pool-state-byte-cells-bound.o"
RECEIPT = OUT / "pool-state-byte-cells-current-receipt.json"
CELLS = {
    "audio_ble_ring_link_state": "0x20074f85",
    "audio_ble_slave_unpair_flag_20074f8b": "0x20074f8b",
    "audio_ble_slave_link_flags_20074f8c": "0x20074f8c",
    "audio_ble_slave_adv_stop_flag_20074f8d": "0x20074f8d",
    "g2_audio_log_wake_enabled": "0x20074f2c",
    "g2_audio_log_transport_bits": "0x20075043",
    "g2_codec_i2s_initialized": "0x20074fb7",
}
ALIASES = {"audio_uart_display_state"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 470
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert set(CELLS) | ALIASES <= before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-fshort-enums", "-std=c11", "-ffreestanding",
                    "-Wall", "-Wextra", "-Werror", "-O2", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == set(CELLS) | ALIASES
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == set(CELLS) | ALIASES and after - before == set()
    assert len(before) == 470 and len(after) == 462
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_BYTE_STATE_CELLS_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "native_ram_addresses": CELLS,
        "shared_display_state": {"address": "0x20074f2c", "bytes": 2,
                                 "alias": "g2_audio_log_wake_enabled"},
        "imports_resolved": sorted(set(CELLS) | ALIASES), "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Source declarations and native addresses identify the cells and two-byte display state; whole-image linker placement, neighboring RAM allocation, startup initialization and hardware behavior remain unproved."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
