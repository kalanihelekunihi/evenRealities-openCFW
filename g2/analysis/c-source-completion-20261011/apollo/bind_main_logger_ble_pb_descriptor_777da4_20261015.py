#!/usr/bin/env python3
"""Bind the native-checked logger nanopb descriptor graph into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_logger_ble_pb_descriptor_777da4.c"
ORACLE = G2 / "build/c-firmware/20261015/main-logger-ble-pb-descriptor-777da4/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-logger-ble-handler-5bf972/apollo-main-logger-ble-handler-5bf972.o"
OUT = G2 / "build/c-firmware/20261015/main-logger-ble-pb-descriptor-777da4"
OWNED = {"audio_uart_ble_log_pb_descriptor_777da4"}
ROOT_SHA = "0ee5929d88127986472c58314d213ce4212157eb7d67382c588370decc5cd4ed"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LOGGER_BLE_PB_DESCRIPTOR_777DA4" or \
       oracle["source_sha256"] != sha(SOURCE) or \
       oracle["native_root_sha256"] != ROOT_SHA or \
       oracle["compared_descriptors"] != 4 or oracle["compared_field_words"] != 23:
        raise RuntimeError("Native logger descriptor evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_logger_ble_pb_descriptor_777da4.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u"):
        raise RuntimeError("Logger descriptor object contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 217 or not OWNED <= before:
        raise RuntimeError("Logger descriptor base contract changed")
    linked = OUT / "apollo-main-logger-ble-pb-descriptor-777da4.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before-after != OWNED or after-before or len(after) != 216:
        raise RuntimeError("Logger descriptor link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOGGER_BLE_PB_DESCRIPTOR_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "native_root_sha256": ROOT_SHA,
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(OWNED), "imports_added": [],
               "unresolved_before": 217, "unresolved_after": 216,
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Descriptor graph is source-owned; final placement and hardware encode behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"], 217, 216, sha(path))

if __name__ == "__main__": main()
