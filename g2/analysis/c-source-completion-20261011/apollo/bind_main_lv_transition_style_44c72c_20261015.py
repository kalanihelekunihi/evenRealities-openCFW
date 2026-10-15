#!/usr/bin/env python3
"""Link the transition overlay style provider after its native lookup oracle."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_transition_style_44c72c.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-transition-style-44c72c"
BASE = G2 / "build/c-firmware/20261015/main-lv-state-transition-kind-44c178/apollo-main-lv-state-transition-kind-44c178.o"
ORACLE = HERE / "verify_main_lv_transition_style_44c72c_oracle_20261015.py"
OWNED = {"audio_uart_lv_transition_style_44c72c"}
LOWER = {"audio_uart_buffer_zero", "audio_uart_lv_malloc",
         "audio_uart_lv_realloc_44f76a", "audio_uart_lvgl_log"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_transition_style_44c72c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_STYLE_LOOKUP_ORACLE" or \
       oracle["cases"] != 8 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("transition style lookup oracle changed")
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != LOWER:
        raise RuntimeError("transition style object contract changed")
    if not LOWER <= symbols(BASE, "--defined-only"):
        raise RuntimeError("transition style lower provider absent")
    linked = OUT / "apollo-main-lv-transition-style-44c72c.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if before != after or len(after) != 234:
        raise RuntimeError("transition style linked contract changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_STYLE_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 234,
        "source_owned_symbols": sorted(OWNED), "imports_resolved": [], "imports_added": [],
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Five existing-record lookups and three allocator-controlled insertion cases native-compared.",
                   "Provider is now available to per-property state refresh, which remains open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
