#!/usr/bin/env python3
"""Bind native-checked LV scroll reconciliation into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_scroll_reconcile_44f316.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-scroll-reconcile-44f316/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-layout-apply-4546f4/apollo-main-lv-layout-apply-4546f4.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-scroll-reconcile-44f316"
OWNED = {"audio_uart_lv_scroll_x_spec_mode_44e45a", "audio_uart_lv_scroll_y_spec_mode_44e470", "audio_uart_lv_obj_scroll_reconcile_44f316"}
RESOLVED = {"audio_uart_lv_obj_scroll_reconcile_44f316"}
CHILDREN = {"audio_uart_lv_scroll_top_44e4aa", "audio_uart_lv_scroll_bottom_44e4bc", "audio_uart_lv_scroll_left_44e586", "audio_uart_lv_scroll_right_44e67a", "audio_uart_lv_scroll_mode_44e2a4", "audio_uart_lv_scroll_dispatch_44e884"}
BODIES = {
    "audio_uart_lv_scroll_x_spec_mode_44e45a": "08bb33cbc2a069e69c623e3da2ff2b1003fcd312db68e56662065bf15aca2c94",
    "audio_uart_lv_scroll_y_spec_mode_44e470": "f05d5542aac5bc00db80e1c970305705be67cf9956fbc70f9ca51d01b5b48139",
    "audio_uart_lv_obj_scroll_reconcile_44f316": "f5d644435517aee65c70805cf7787d175b1a99856115587a72afcb77c0632c31",
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_SCROLL_RECONCILE_44F316" or \
       oracle["cases"] != 327 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or oracle["native_body_sha256"] != BODIES:
        raise RuntimeError("Native LV scroll reconciliation evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_scroll_reconcile_44f316.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV scroll reconciliation object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 225 or not RESOLVED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV scroll reconciliation base contract changed")
    linked = OUT / "apollo-main-lv-scroll-reconcile-44f316.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before or len(after) != 224:
        raise RuntimeError("LV scroll reconciliation link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_RECONCILE_C",
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
               "limits": ["Six lower scroll providers were linked from earlier bounded stages.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
