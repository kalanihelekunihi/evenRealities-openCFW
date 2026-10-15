#!/usr/bin/env python3
"""Add the source-owned native-address service-mode byte to Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-itcm-delay-current-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/service_mode_state.c"
OBJECT = OUT / "service-mode-state-pool.o"
OUTPUT = OUT / "apollo-main-pool-state-service-mode-bound.o"
RECEIPT = OUT / "pool-state-service-mode-current-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def main():
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 472
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    aliases = {"g2_audio_service_mode", "audio_ble_ota_sync_status"}
    assert aliases <= before
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                    "-mthumb", "-fshort-enums", "-std=c11", "-ffreestanding",
                    "-Wall", "-Wextra", "-Werror", "-O2", "-c", str(SOURCE),
                    "-o", str(OBJECT)], check=True)
    definitions = names(OBJECT, "--defined-only")
    assert definitions == aliases
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT),
                    "-o", str(OUTPUT)], check=True)
    after = names(OUTPUT, "-u")
    assert before - after == aliases
    assert after - before == set()
    assert len(before) == 472 and len(after) == 470
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_SERVICE_MODE_STATE_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "source_object": str(OBJECT.relative_to(ROOT)), "source_object_sha256": sha(OBJECT),
        "native_ram_address": "0x20075024", "source_cell_bytes": 1,
        "source_aliases": sorted(aliases),
        "imports_resolved": sorted(aliases), "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["The source defines the byte cell used by native-checked accessors; final linker placement at the native RAM address and runtime initialization remain unproved."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
