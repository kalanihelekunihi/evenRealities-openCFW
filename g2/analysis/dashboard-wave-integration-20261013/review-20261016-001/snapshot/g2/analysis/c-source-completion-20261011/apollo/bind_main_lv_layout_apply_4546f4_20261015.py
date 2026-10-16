#!/usr/bin/env python3
"""Bind native-checked LV layout callback dispatch into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_layout_apply_4546f4.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-layout-apply-4546f4/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-update-layout-recursive-440d70/apollo-main-update-layout-recursive-440d70.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-layout-apply-4546f4"
OWNED = {"audio_uart_lv_layout_id_4546d0", "audio_uart_lv_obj_layout_apply_4546f4"}
RESOLVED = {"audio_uart_lv_obj_layout_apply_4546f4"}
CHILDREN = {"audio_uart_display_lv_root", "audio_uart_lv_style_property_44bdea"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_LAYOUT_APPLY_4546F4" or \
       oracle["cases"] != 49 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != {
           "audio_uart_lv_layout_id_4546d0": "e7db7bdbf8592de737b706de2eac46859b2626af4752fa4c086646562d6a4a8e",
           "audio_uart_lv_obj_layout_apply_4546f4": "25316c1070fb5792e8274ea6bb6c0d88b8d6d27ede6f7e391bc904fdbb9b3eae"}:
        raise RuntimeError("Native LV layout dispatch evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_layout_apply_4546f4.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV layout-dispatch object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 226 or not RESOLVED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV layout-dispatch base contract changed")
    linked = OUT / "apollo-main-lv-layout-apply-4546f4.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before or len(after) != 225:
        raise RuntimeError("LV layout-dispatch link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_LAYOUT_APPLY_C",
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
               "limits": ["Layout registry callbacks remain runtime configuration.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
