#!/usr/bin/env python3
"""Bind the shared BLE handler ID byte into pooled Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-ota-export-current-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/ble_handler_id_state.c"
OBJECT = OUT / "ble-handler-id-state-pool.o"
OUTPUT = OUT / "apollo-main-pool-state-ble-handler-bound.o"
RECEIPT = OUT / "pool-state-ble-handler-current-receipt.json"
ALIASES = {"audio_ble_msgtx_handler_id", "audio_ble_connect_event_handler"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 459
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert ALIASES <= before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-fshort-enums", "-std=c11", "-ffreestanding",
                    "-Wall", "-Wextra", "-Werror", "-O2", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    assert names(OBJECT, "--defined-only") == ALIASES
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == ALIASES and after - before == set()
    assert len(before) == 459 and len(after) == 457
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_BLE_HANDLER_ID_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "native_ram_address": "0x20074f8e", "source_cell_bytes": 1,
        "source_aliases": sorted(ALIASES), "imports_resolved": sorted(ALIASES),
        "imports_added": [], "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Service-init write and connect-request read identify one native handler-ID byte; whole-image placement, startup and runtime behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
