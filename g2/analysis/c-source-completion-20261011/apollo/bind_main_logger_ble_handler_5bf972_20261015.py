#!/usr/bin/env python3
"""Bind native-checked BLE logger handler into the Main C object."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_logger_ble_handler_5bf972.c"
ORACLE = G2 / "build/c-firmware/20261015/main-logger-ble-handler-5bf972/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-theme-refresh-all-44bc48/apollo-main-lv-theme-refresh-all-44bc48.o"
OUT = G2 / "build/c-firmware/20261015/main-logger-ble-handler-5bf972"
OWNED = {"audio_uart_logger_ble_handler_5bf972", "audio_uart_ble_log_frame_20069b24",
         "audio_uart_ble_log_encoded_2037cba0"}
IMPORTS = {"audio_uart_buffer_zero", "audio_pb_ostream_from_buffer", "audio_pb_encode",
           "audio_ring_pb_tx_ble_475c1a", "audio_uart_ble_log_pb_descriptor_777da4"}
BODY_SHA = "a95f002c3a94ebc4f109babb8f4c0a31538e4972a7a644f50fa31e714bdbbc75"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LOGGER_BLE_HANDLER_5BF972" or \
       oracle["cases"] != 16 or oracle["source_sha256"] != sha(SOURCE) or \
       oracle["native_body_sha256"] != BODY_SHA:
        raise RuntimeError("Native BLE logger evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_logger_ble_handler_5bf972.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != IMPORTS:
        raise RuntimeError("BLE logger symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 217 or "audio_uart_logger_ble_handler_5bf972" not in before or \
       not (IMPORTS - {"audio_uart_ble_log_pb_descriptor_777da4"}) <= symbols(BASE, "--defined-only"):
        raise RuntimeError("BLE logger base contract changed")
    linked = OUT / "apollo-main-logger-ble-handler-5bf972.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before-after != {"audio_uart_logger_ble_handler_5bf972"} or \
       after-before != {"audio_uart_ble_log_pb_descriptor_777da4"} or len(after) != 217:
        raise RuntimeError("BLE logger link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOGGER_BLE_HANDLER_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"], "native_body_sha256": BODY_SHA,
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": ["audio_uart_logger_ble_handler_5bf972"],
               "imports_added": ["audio_uart_ble_log_pb_descriptor_777da4"],
               "unresolved_before": 217, "unresolved_after": 217,
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Logger protobuf descriptor remains an unresolved native data provider; final RAM placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"], 217, 217, sha(path))

if __name__ == "__main__": main()
