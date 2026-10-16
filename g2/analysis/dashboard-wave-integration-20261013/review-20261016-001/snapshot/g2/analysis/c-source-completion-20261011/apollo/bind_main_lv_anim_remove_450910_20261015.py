#!/usr/bin/env python3
"""Bind native-checked LV animation removal into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_anim_remove_450910.c"
ORACLE = G2 / "build/c-firmware/20261015/main-lv-anim-remove-450910/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-transition-timer-450758/apollo-main-lv-transition-timer-450758.o"
OUT = G2 / "build/c-firmware/20261015/main-lv-anim-remove-450910"
OWNED = {"audio_uart_lv_anim_remove_450910"}
CHILDREN = {"audio_uart_display_lv_state", "audio_uart_lv_heap_free", "audio_uart_lv_list_remove_482c0e", "audio_uart_lv_transition_schedule_4509da"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_LV_ANIM_REMOVE_450910" or \
       oracle["cases"] != 384 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != "0f68d2cce4e87eb638b49a31e62108a1c07cd7af5fc1c2189801483082abb360":
        raise RuntimeError("Native LV animation removal evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_anim_remove_450910.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV animation removal object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 223 or not OWNED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV animation removal base contract changed")
    linked = OUT / "apollo-main-lv-anim-remove-450910.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != OWNED or after - before or len(after) != 222:
        raise RuntimeError("LV animation removal link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_ANIM_REMOVE_C",
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
