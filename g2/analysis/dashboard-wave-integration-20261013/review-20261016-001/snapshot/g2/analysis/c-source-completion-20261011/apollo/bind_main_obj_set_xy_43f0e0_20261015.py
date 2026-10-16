#!/usr/bin/env python3
"""Bind native-checked LV X/Y setters and their style wrappers into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_set_xy_43f0e0.c"
ORACLE = G2 / "build/c-firmware/20261015/main-obj-set-xy-43f0e0/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-obj-set-pos-43f09a/apollo-main-obj-set-pos-43f09a.o"
OUT = G2 / "build/c-firmware/20261015/main-obj-set-xy-43f0e0"
OWNED = {"audio_uart_page_43f0e0", "audio_uart_page_43f142",
         "audio_uart_page_4411b8", "audio_uart_page_4411c6"}
RESOLVED = {"audio_uart_page_43f0e0", "audio_uart_page_43f142"}
ADDED = {"audio_uart_page_style_get_44beaa"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_OBJ_SET_XY_43F0E0" or \
       oracle["cases"] != 32 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != {
           "audio_uart_page_43f0e0": "e78574240a23ff1098778c0817666a001be2f1b6c67604a3f23c08d3d7fa6daa",
           "audio_uart_page_43f142": "53139a957ef162991b0e6cd295f234162245f9f4eada878767ef512752876478",
           "audio_uart_page_4411b8": "9a08a8a413a4a6adb45d257eb37a69ddf6a1bf657e8ba81e4b0935f2a27bc944",
           "audio_uart_page_4411c6": "a8af682c4407fdf998f8b3c5ae5acf19df01d0bafb5e5c569bdf7e4982671ea6"}:
        raise RuntimeError("Native X/Y setter evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_obj_set_xy_43f0e0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or \
       symbols(obj, "-u") != ADDED | {"audio_uart_lvgl_log",
                                      "audio_uart_page_style_apply_44be4c"}:
        raise RuntimeError("X/Y object symbol contract changed")
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if len(before) != 230 or not RESOLVED <= before or \
       not {"audio_uart_lvgl_log", "audio_uart_page_style_apply_44be4c"} <= defined:
        raise RuntimeError("X/Y base contract changed")
    linked = OUT / "apollo-main-obj-set-xy-43f0e0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before != ADDED or len(after) != 229:
        raise RuntimeError("X/Y link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_OBJ_SET_XY_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["The style-get helper at 0x44beaa remains unresolved.",
                          "Null assertions were compared only through logger calls."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
