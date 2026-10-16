#!/usr/bin/env python3
"""Bind the native-checked outer LV layout loop into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_update_layout_43f66c.c"
ORACLE = G2 / "build/c-firmware/20261015/main-update-layout-43f66c/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-event-add-451740/apollo-main-lv-event-add-451740.o"
OUT = G2 / "build/c-firmware/20261015/main-update-layout-43f66c"
OWNED = {"audio_uart_page_43f66c"}
ADDED = {"audio_uart_lv_obj_update_layout_440d70"}
CHILDREN = {"audio_uart_display_lv_root", "audio_uart_lv_object_screen"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_UPDATE_LAYOUT_43F66C" or \
       oracle["cases"] != 36 or oracle["source_sha256"] != sha(SOURCE) or \
       oracle["native_body_sha256"] != "b83933a76976dd96b902ce608d450efcc6a633e1187acb1144bbd34ed743f06f":
        raise RuntimeError("Native outer layout evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_update_layout_43f66c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or \
       symbols(obj, "-u") != CHILDREN | ADDED:
        raise RuntimeError("Outer layout object symbol contract changed")
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if len(before) != 224 or not OWNED <= before or \
       not CHILDREN <= defined or ADDED & (before | defined):
        raise RuntimeError("Outer layout base contract changed")
    linked = OUT / "apollo-main-update-layout-43f66c.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != OWNED or after - before != ADDED or len(after) != 224:
        raise RuntimeError("Outer layout link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_UPDATE_LAYOUT_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(OWNED), "imports_added": sorted(ADDED),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Recursive layout child at 0x440d70 remains unresolved.",
                          "Screen and recursive effects were controlled hooks."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
