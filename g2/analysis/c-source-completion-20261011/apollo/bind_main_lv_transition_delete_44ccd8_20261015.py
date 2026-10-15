#!/usr/bin/env python3
"""Bind the native-compared transition deletion callback."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_transition_delete_44ccd8.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-transition-delete-44ccd8"
BASE = G2 / "build/c-firmware/20261015/main-lv-transition-ready-44cc8c/apollo-main-lv-transition-ready-44cc8c.o"
ORACLE = HERE / "verify_main_lv_transition_delete_44ccd8_oracle_20261015.py"
OWNED = {"audio_uart_lv_transition_delete_44ccd8"}
LOWER = {"audio_uart_display_lv_root", "audio_uart_lv_list_first",
         "audio_uart_lv_list_next", "audio_uart_lv_list_remove_482c0e",
         "audio_uart_lv_heap_free", "audio_uart_lv_style_notify_4827b0",
         "audio_uart_lv_style_remove_44ba9a"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_transition_delete_44ccd8.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_DELETE_ORACLE" or \
       oracle["cases"] != 4 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("transition delete oracle changed")
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != LOWER:
        raise RuntimeError("transition delete object contract changed")
    if not LOWER <= symbols(BASE, "--defined-only"):
        raise RuntimeError("transition delete lower provider absent")
    linked = OUT / "apollo-main-lv-transition-delete-44ccd8.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if before - after != OWNED or after - before or len(before) != 235 or len(after) != 234:
        raise RuntimeError("transition delete linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_DELETE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 235, "unresolved_after": 234,
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Four controlled deletion branches native-compared.",
                          "Transition execution callback and live list effects remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
