#!/usr/bin/env python3
"""Bind selected timer and codec routing RAM state into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-ble-service-states-current-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/timing_state_cells.c"
OBJECT = OUT / "timing-state-cells-pool.o"
OUTPUT = OUT / "apollo-main-pool-state-timing-state-bound.o"
RECEIPT = OUT / "pool-state-timing-state-current-receipt.json"
CELLS = {
    "g2_codec_clock_mux_requests": ["0x200740ec", 6],
    "audio_ble_profile_runtime_rows": ["0x20074310", 24],
    "audio_ble_fast_mode_last_reject_tick": ["0x20074340", 4],
    "audio_event_loop_base_tick": ["0x200745fc", 4],
    "audio_uart_logger_ble_timeout": ["0x200746b0", 4],
    "audio_uart_ring_touch_tick": ["0x20074900", 4],
    "audio_uart_ring_wear_tick": ["0x20074904", 4],
    "g2_audio_notify_assert_enabled": ["0x20074a34", 4],
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 441
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
    assert len(before) == 441 and len(after) == 433
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_TIMING_STATE_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "native_ram_spans": CELLS, "imports_resolved": sorted(CELLS), "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Selected C callers fix these addresses and accessed extents; startup values, whole-image RAM integration, timing behavior and hardware remain unproved."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
