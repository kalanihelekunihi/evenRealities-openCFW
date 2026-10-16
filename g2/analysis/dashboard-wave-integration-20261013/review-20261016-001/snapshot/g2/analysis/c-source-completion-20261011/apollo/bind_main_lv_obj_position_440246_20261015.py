#!/usr/bin/env python3
"""Bind native-checked LV position setter into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_position_440246.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-obj-position-440246/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-refr-pos-43ffd0/apollo-main-lv-refr-pos-43ffd0.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-position-440246"
OWNED = {"audio_uart_lv_obj_position_440246"}
CHILDREN = {"audio_uart_lv_obj_has_flag_43e0e0", "audio_uart_lv_obj_x_44e486", "audio_uart_lv_obj_y_44e498", "audio_uart_lv_style_pad_left_43efc6", "audio_uart_lv_style_pad_top_43f022", "audio_uart_page_invalidate_440656", "audio_uart_lv_obj_coords_43fc2a", "audio_uart_lv_obj_content_coords_43feca", "audio_uart_lv_area_contains_450f28", "audio_uart_lv_scrollbar_invalidate_44f2ca", "audio_uart_lv_obj_move_children_44035e", "audio_uart_lv_obj_event_451670"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_OBJ_POSITION_440246" or \
       oracle["cases"] != 64 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != "27563d06a5a625f77f0663468422c6bb0a61ccb2b49db72e16707cc54470466f":
        raise RuntimeError("Native LV position setter evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_obj_position_440246.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV position setter object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 224 or not OWNED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV position setter base contract changed")
    linked = OUT / "apollo-main-lv-obj-position-440246.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != OWNED or after - before or len(after) != 223:
        raise RuntimeError("LV position setter link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_OBJ_POSITION_C",
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
               "limits": ["Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
