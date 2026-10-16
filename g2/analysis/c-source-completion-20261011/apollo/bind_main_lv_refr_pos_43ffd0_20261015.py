#!/usr/bin/env python3
"""Bind native-checked LV position refresh into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_refr_pos_43ffd0.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-refr-pos-43ffd0/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-scroll-reconcile-44f316/apollo-main-lv-scroll-reconcile-44f316.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-refr-pos-43ffd0"
OWNED = {"audio_uart_lv_obj_refr_pos_43ffd0", "audio_uart_lv_style_translate_x_43ef02", "audio_uart_lv_style_translate_y_43ef0c"}
RESOLVED = {"audio_uart_lv_obj_refr_pos_43ffd0"}
ADDED = {"audio_uart_lv_obj_position_440246"}
CHILDREN = {"audio_uart_lv_layout_positioned_43f612", "audio_uart_lv_obj_content_height_43fe70", "audio_uart_lv_obj_content_width_43fe16", "audio_uart_lv_obj_height_43fdda", "audio_uart_lv_obj_parent_44dca2", "audio_uart_lv_obj_width_43fd9e", "audio_uart_lv_style_align_43eef6", "audio_uart_lv_style_base_dir_43efba", "audio_uart_lv_style_height_43eec4", "audio_uart_lv_style_property_44bdea", "audio_uart_lv_style_width_43eea6", "audio_uart_lv_style_x_43eee2", "audio_uart_lv_style_y_43eeec"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_REFR_POS_43FFD0" or \
       oracle["cases"] != 480 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != "e997ece6550c902b8375508d791689873a29d848f779e465ca899d307d644e14":
        raise RuntimeError("Native LV position refresh evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_refr_pos_43ffd0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN | ADDED:
        raise RuntimeError("LV position refresh object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 224 or not RESOLVED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV position refresh base contract changed")
    linked = OUT / "apollo-main-lv-refr-pos-43ffd0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before != ADDED or len(after) != 224:
        raise RuntimeError("LV position refresh link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_REFR_POS_C",
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
               "limits": ["Position setter is a deeper source dependency.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
