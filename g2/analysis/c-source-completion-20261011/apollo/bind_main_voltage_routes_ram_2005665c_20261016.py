#!/usr/bin/env python3
"""Bind the 27-word Apollo calibration route table to C-owned RAM."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/callback_voltage_source_candidate/voltage_routes_ram_2005665c.c"
LINKER = SOURCE.with_suffix(".ld")
CALLER = G2 / "components/audio/callback_voltage_source_candidate/voltage.c"
PRODUCER = G2 / "components/audio/platform_callbacks_offline/read_init.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_callback_voltage.py"
PRODUCER_DIR = G2 / "analysis/audio-platform-callbacks-closure-2026-10-08"
PYTHON = Path("/tmp/opencfw-oracle-venv/bin/python")
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BASE_RECEIPT = G2 / "build/c-firmware/20261016/main-codec-i2s-pool-20071114/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-voltage-routes-2005665c"
NAME = "g2_audio_voltage_routes"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def symbol(path):
    rows = [line.split() for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-S", str(path)], text=True).splitlines()
        if line.endswith(" " + NAME)]
    if len(rows) != 1:
        raise RuntimeError("voltage route table missing or duplicated")
    return int(rows[0][0], 16), int(rows[0][1], 16), rows[0][2]


def main():
    payload = PACKAGE.read_bytes()[32:]
    literal = 0x5a4d3c - 0x438000
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA or \
            int.from_bytes(payload[literal:literal + 4], "little") != 0x2005665c:
        raise RuntimeError("stock voltage route address literal changed")
    if NAME not in CALLER.read_text() or \
            "uint32_t *data=(uint32_t *)(uintptr_t)0x2005665c" not in PRODUCER.read_text() or \
            "data[26]=temporary[0];data[0]=0x1f01600d" not in PRODUCER.read_text():
        raise RuntimeError("route table caller or 27-word producer changed")
    reproduction_path = PRODUCER_DIR / "reproduction-receipt.json"
    read_init_path = PRODUCER_DIR / "read-init-results.json"
    itcm_path = PRODUCER_DIR / "itcm-results.json"
    reproduction = json.loads(reproduction_path.read_text())
    read_init = json.loads(read_init_path.read_text())
    itcm = json.loads(itcm_path.read_text())
    if reproduction["sources"][str(PRODUCER.relative_to(ROOT))] != sha(PRODUCER) or \
            read_init["status"] != "PASS" or read_init["cases"] != 2376 or \
            itcm["status"] != "PASS" or itcm["cases"] != 74 or \
            read_init["elf_sha256"] != reproduction["elf_sha256"] or \
            itcm["elf_sha256"] != reproduction["elf_sha256"]:
        raise RuntimeError("archived producer evidence changed")
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_CODEC_I2S_POOL_RAM_C" or \
            base["unresolved_after"] != 158:
        raise RuntimeError("Apollo Main input changed")
    original = ROOT / base["linked_object"]
    if sha(original) != base["linked_sha256"] or NAME not in imports(original):
        raise RuntimeError("Apollo Main route table import changed")
    OUT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([str(PYTHON), str(ORACLE)], capture_output=True,
                            text=True, check=True)
    if result.stdout.strip() != "PASS_AUDIO_CALLBACK_VOLTAGE 120":
        raise RuntimeError("stock/C voltage callback oracle changed")
    oracle_receipt = {"status": "PASS_AUDIO_CALLBACK_VOLTAGE", "cases": 120,
                      "script": str(ORACLE.relative_to(ROOT)),
                      "script_sha256": sha(ORACLE),
                      "caller": str(CALLER.relative_to(ROOT)),
                      "caller_sha256": sha(CALLER),
                      "producer": str(PRODUCER.relative_to(ROOT)),
                      "producer_sha256": sha(PRODUCER),
                      "archived_reproduction": str(reproduction_path.relative_to(ROOT)),
                      "archived_reproduction_sha256": sha(reproduction_path),
                      "archived_read_init": str(read_init_path.relative_to(ROOT)),
                      "archived_read_init_sha256": sha(read_init_path),
                      "archived_itcm": str(itcm_path.relative_to(ROOT)),
                      "archived_itcm_sha256": sha(itcm_path),
                      "stdout": result.stdout.strip()}
    oracle_path = OUT / "oracle-receipt.json"
    oracle_path.write_text(json.dumps(oracle_receipt, indent=2, sort_keys=True) + "\n")
    obj = OUT / "voltage-routes-ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbol(obj) != (0, 108, "B"):
        raise RuntimeError("C-owned voltage route table extent changed")
    placed = OUT / "voltage-routes-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(obj), "-o", str(placed)], check=True)
    if symbol(placed) != (0x2005665c, 108, "B"):
        raise RuntimeError("isolated voltage table placement changed")
    linked = OUT / "apollo-main-voltage-routes-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    before, after = imports(original), imports(linked)
    if before - after != {NAME} or after - before or len(after) != 157:
        raise RuntimeError("unexpected Main voltage table import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_VOLTAGE_ROUTES_RAM_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(oracle_path.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(oracle_path),
               "payload_sha256": PAYLOAD_SHA, "stock_literal_address": "0x5a4d3c",
               "stock_ram_address": "0x2005665c", "table_bytes": 108,
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [NAME], "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The current 120-case voltage callback oracle and archived producer/ITCM receipts establish the bounded 27-word table extent; the historical GCC toolchain is unavailable for an exact producer rebuild in this run.",
                          "Real INFO1 calibration values, startup order, final RAM-map placement and G2 hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
