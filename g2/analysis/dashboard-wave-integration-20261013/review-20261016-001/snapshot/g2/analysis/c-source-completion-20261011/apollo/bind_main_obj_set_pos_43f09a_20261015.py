#!/usr/bin/env python3
"""Bind the native-checked lv_obj_set_pos provider into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_set_pos_43f09a.c"
ORACLE = G2 / "build/c-firmware/20261015/main-obj-set-pos-43f09a/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-page-pair-43f6b8/apollo-main-page-pair-43f6b8.o"
OUT = G2 / "build/c-firmware/20261015/main-obj-set-pos-43f09a"
OWNED = {"audio_uart_page_43f09a"}
CHILDREN = {"audio_uart_page_43f0e0", "audio_uart_page_43f142"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_OBJ_SET_POS_43F09A" or \
       oracle["cases"] != 48 or oracle["null_assertion_cases"] != 16 or \
       oracle["native_body_sha256"] != "a9fe79b614907d95aea1cc90e59bb470ca08d8120d08110190a0d49f55c17096" or \
       oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Native lv_obj_set_pos evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_obj_set_pos_43f09a.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or \
       symbols(obj, "-u") != CHILDREN | {"audio_uart_lvgl_log"}:
        raise RuntimeError("lv_obj_set_pos object symbol contract changed")
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if len(before) != 231 or not OWNED | CHILDREN <= before or \
       "audio_uart_lvgl_log" not in defined:
        raise RuntimeError("lv_obj_set_pos base contract changed")
    linked = OUT / "apollo-main-obj-set-pos-43f09a.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != OWNED or after - before or len(after) != 230:
        raise RuntimeError("lv_obj_set_pos link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_OBJ_SET_POS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(OWNED), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The X and Y child setters at 0x43f0e0 and 0x43f142 remain unresolved.",
                          "Null assertion was compared only through the logger call."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
