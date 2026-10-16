#!/usr/bin/env python3
"""Bind native-checked LV event callback insertion into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_event_add_451740.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-event-add-451740/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-obj-set-size-43f4c0/apollo-main-obj-set-size-43f4c0.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-event-add-451740"
OWNED = {"audio_uart_page_451740", "audio_uart_lv_event_add_4500e4",
         "audio_uart_lv_array_init_4883fc"}
RESOLVED = {"audio_uart_page_451740"}
CHILDREN = {"audio_uart_lvgl_log", "audio_uart_lv_malloc",
            "audio_uart_lv_obj_setup_layer_43e1fa", "audio_uart_lv_event_count_450388",
            "audio_uart_lv_array_push_488506"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_EVENT_ADD_451740" or \
       oracle["cases"] != 44 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != {
           "audio_uart_page_451740": "2b01a268acfe0bf6b126a8a5720cdf1f80bfa3ef7ae2afc92d78f70b7619d3ba",
           "audio_uart_lv_event_add_4500e4": "54dd79b705b3dac36b31cb50ca25e43a613a336c3037eed8ab7048c06a207a7f",
           "audio_uart_lv_array_init_4883fc": "985d46cc3f391c6c3aaac9808c0e4a334727d1fbda99f41c847e5ae11a26db1d"}:
        raise RuntimeError("Native LV event-add evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_event_add_451740.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV event-add object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 225 or not RESOLVED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV event-add base contract changed")
    linked = OUT / "apollo-main-lv-event-add-451740.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before or len(after) != 224:
        raise RuntimeError("LV event-add link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_EVENT_ADD_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(RESOLVED), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Allocator, event-count, setup and array-push effects were controlled hooks.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
