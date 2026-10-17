#!/usr/bin/env python3
"""Bind stock codec shared enable mask cell to C-owned RAM."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/codec_gpio_selector_candidate/shared_enable_mask_ram_2007436c.c"
LINKER = SOURCE.with_suffix(".ld")
GPIO_SOURCE = G2 / "components/audio/codec_gpio_selector_candidate/gpio.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_codec_gpio.py"
PYTHON = Path("/tmp/opencfw-oracle-venv/bin/python")
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BASE_RECEIPT = G2 / "build/c-firmware/20261016/main-codec-check-timer-20074a98/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-codec-shared-mask-2007436c"
NAME = "g2_codec_shared_enable_mask"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def cell(path):
    rows = [line.split() for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-S", str(path)], text=True).splitlines()
        if line.endswith(" " + NAME)]
    if len(rows) != 1:
        raise RuntimeError("codec shared mask cell missing or duplicated")
    return int(rows[0][0], 16), int(rows[0][1], 16), rows[0][2]


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA or \
            int.from_bytes(payload[0x50946c - 0x438000:0x509470 - 0x438000],
                           "little") != 0x2007436c:
        raise RuntimeError("stock codec shared mask pointer literal changed")
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_CODEC_CHECK_TIMER_RAM_C" or \
            base["unresolved_after"] != 162:
        raise RuntimeError("Apollo Main input changed")
    original = ROOT / base["linked_object"]
    if sha(original) != base["linked_sha256"] or NAME not in imports(original):
        raise RuntimeError("Apollo Main codec shared mask import changed")
    OUT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([str(PYTHON), str(ORACLE)], capture_output=True,
                            text=True, check=True)
    if result.stdout.strip() != "PASS_AUDIO_CODEC_GPIO 240\nPASS_AUDIO_GPIO_CRITICAL 2\nPASS_AUDIO_CODEC_PIN 45\nPASS_AUDIO_GPIO_HAL 112":
        raise RuntimeError("stock/C codec GPIO oracle changed")
    oracle_receipt = {"status": "PASS_AUDIO_CODEC_GPIO", "cases": 240,
                      "script": str(ORACLE.relative_to(ROOT)),
                      "script_sha256": sha(ORACLE),
                      "gpio_source": str(GPIO_SOURCE.relative_to(ROOT)),
                      "gpio_source_sha256": sha(GPIO_SOURCE),
                      "stdout": result.stdout.strip()}
    oracle_path = OUT / "oracle-receipt.json"
    oracle_path.write_text(json.dumps(oracle_receipt, indent=2, sort_keys=True) + "\n")
    obj = OUT / "codec-shared-mask-ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if cell(obj) != (0, 4, "B"):
        raise RuntimeError("C-owned codec shared mask cell changed")
    placed = OUT / "codec-shared-mask-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(obj), "-o", str(placed)], check=True)
    if cell(placed) != (0x2007436c, 4, "B"):
        raise RuntimeError("isolated codec shared mask placement changed")
    linked = OUT / "apollo-main-codec-shared-mask-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    before, after = imports(original), imports(linked)
    if before - after != {NAME} or after - before or len(after) != 161:
        raise RuntimeError("unexpected Main codec shared mask import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_CODEC_SHARED_MASK_RAM_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(oracle_path.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(oracle_path),
               "payload_sha256": PAYLOAD_SHA, "stock_literal_address": "0x50946c",
               "stock_ram_address": "0x2007436c", "cell_bytes": 4,
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [NAME], "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The GPIO oracle controls pin writes and critical sections; startup mask value remains open.",
                          "Final RAM-map placement, whole-image link and G2 hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
