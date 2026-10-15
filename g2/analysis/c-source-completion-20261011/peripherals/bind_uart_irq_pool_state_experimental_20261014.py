#!/usr/bin/env python3
"""Compose the source-owned UART IRQ graph with pooled Main, experimentally."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-ble-subsystem-current-receipt.json"
HERE = G2 / "components/audio/uart_irq_source_candidate"
BUILD = OUT / "uart-irq-pool-state-abi"
BOUND = OUT / "apollo-main-pool-state-uart-irq-experimental.o"
RECEIPT = OUT / "pool-state-uart-irq-experimental-receipt.json"
SOURCES = ("irq_service", "lower_dma", "rx_abort", "read_abort", "read_sm",
           "fifo_bridge", "tx_bridge", "delay_bridge")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_BLE_SUBSYSTEM_CALLBACKS_C"
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    BUILD.mkdir(parents=True, exist_ok=True)
    objects = []
    for stem in SOURCES:
        source = HERE / f"{stem}.c"
        obj = BUILD / f"{stem}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-fshort-enums", "-std=c11", "-ffreestanding",
                        "-fno-builtin", "-O2", "-Wall", "-Wextra",
                        "-Wno-unused-function", "-c", str(source), "-o", str(obj)],
                       check=True)
        objects.append(obj)
    composed = BUILD / "uart-irq-composed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", *map(str, objects),
                    "-o", str(composed)], check=True)
    before = names(original, "-u")
    assert "codec_irq_service" in before
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(composed),
                    "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    assert after == before - {"codec_irq_service"}
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_UART_IRQ_C_GRAPH",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "source_sha256": {str((HERE / f"{stem}.c").relative_to(ROOT)):
                          sha(HERE / f"{stem}.c") for stem in SOURCES},
        "pool_abi_objects": {str(obj.relative_to(ROOT)): sha(obj) for obj in objects},
        "composed_object": str(composed.relative_to(ROOT)),
        "composed_object_sha256": sha(composed),
        "composed_imports": sorted(names(composed, "-u")),
        "imports_resolved": ["codec_irq_service"],
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "selected_stock_equivalent": False,
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Prior 360-case top-level stock/C fixtures cut at six child calls.",
                  "Composed callback, DMA, MMIO and interrupt effects lack native whole-path validation.",
                  "Other Main imports and final image placement remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
