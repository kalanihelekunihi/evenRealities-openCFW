#!/usr/bin/env python3
"""Bind exact Apollo Main ITCM delay-loop instructions as a C-compilable provider."""
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_vendor_itcm_delay_00000040.c"
LINKER = SOURCE.with_suffix(".ld")
CALLER = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_vendor_yield.c"
DECODER = G2 / "analysis/audio-platform-callbacks-closure-2026-10-08/itcm_record.py"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ble_hci_vendor_yield.py"
PYTHON = Path("/tmp/opencfw-oracle-venv/bin/python")
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BASE_RECEIPT = G2 / "build/c-firmware/20261016/main-voltage-routes-2005665c/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-ble-vendor-itcm-delay-00000040"
NAME = "audio_ble_vendor_cycle_delay_rom_00000040"
SECTION = ".text.opencfw.itcm.delay_00000040"


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
        raise RuntimeError("ITCM delay function missing or duplicated")
    return int(rows[0][0], 16), int(rows[0][1], 16), rows[0][2]


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("official Apollo payload changed")
    spec = importlib.util.spec_from_file_location("opencfw_itcm_record", DECODER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    decoded = module.decode_itcm(payload)
    if len(decoded) != 24 or decoded[:6] != bytes.fromhex("0138fdd17047") or \
            NAME not in CALLER.read_text():
        raise RuntimeError("authenticated ITCM delay or caller changed")
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_MAIN_VOLTAGE_ROUTES_RAM_C" or \
            base["unresolved_after"] != 157:
        raise RuntimeError("Apollo Main input changed")
    original = ROOT / base["linked_object"]
    if sha(original) != base["linked_sha256"] or NAME not in imports(original):
        raise RuntimeError("Apollo Main ITCM delay import changed")
    OUT.mkdir(parents=True, exist_ok=True)
    result = subprocess.run([str(PYTHON), str(ORACLE)], capture_output=True,
                            text=True, check=True)
    lines = result.stdout.strip().splitlines()
    if len(lines) != 16 or not all(line.startswith("PASS ") for line in lines):
        raise RuntimeError("stock/C vendor-yield oracle changed")
    oracle_receipt = {"status": "PASS_BLE_HCI_VENDOR_YIELD", "cases": 16,
                      "script": str(ORACLE.relative_to(ROOT)), "script_sha256": sha(ORACLE),
                      "caller": str(CALLER.relative_to(ROOT)), "caller_sha256": sha(CALLER),
                      "itcm_decoder": str(DECODER.relative_to(ROOT)),
                      "itcm_decoder_sha256": sha(DECODER),
                      "decoded_itcm_sha256": hashlib.sha256(decoded).hexdigest(),
                      "stdout": lines}
    oracle_path = OUT / "oracle-receipt.json"
    oracle_path.write_text(json.dumps(oracle_receipt, indent=2, sort_keys=True) + "\n")
    obj = OUT / "ble-vendor-itcm-delay.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbol(obj) != (0, 6, "T"):
        raise RuntimeError("C-compilable ITCM delay size changed")
    emitted = OUT / "ble-vendor-itcm-delay.bin"
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary",
                    "--only-section=" + SECTION, str(obj), str(emitted)], check=True)
    if emitted.read_bytes() != decoded[:6]:
        raise RuntimeError("C-compilable ITCM delay bytes differ from stock")
    placed = OUT / "ble-vendor-itcm-delay-placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER),
                    str(obj), "-o", str(placed)], check=True)
    if symbol(placed) != (0x40, 6, "T"):
        raise RuntimeError("isolated ITCM placement changed")
    linked = OUT / "apollo-main-ble-vendor-itcm-delay-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(obj),
                    "-o", str(linked)], check=True)
    before, after = imports(original), imports(linked)
    if before - after != {NAME} or after - before or len(after) != 156:
        raise RuntimeError("unexpected Main ITCM delay import change")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_BLE_VENDOR_ITCM_DELAY_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
               "oracle_receipt": str(oracle_path.relative_to(ROOT)),
               "oracle_receipt_sha256": sha(oracle_path),
               "payload_sha256": PAYLOAD_SHA, "stock_itcm_address": "0x40",
               "decoded_itcm_sha256": hashlib.sha256(decoded).hexdigest(),
               "function_bytes": 6,
               "emitted_binary": str(emitted.relative_to(ROOT)),
               "emitted_sha256": sha(emitted),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
               "base_object": base["linked_object"], "base_sha256": sha(original),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": [NAME], "imports_added": [],
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The six emitted Thumb bytes match the OTA-decoded ITCM loop, and 16 vendor-yield call-boundary cases pass; boot copy to 0x40 and executable ITCM mapping remain open.",
                          "Flash-resident alias linking, whole-image placement and physical cycle timing remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
