#!/usr/bin/env python3
"""Bind the LVGL text-align style resolver and its small source helpers."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_text_align_class_44c448.c"
OUT = G2 / "build/c-firmware/20261015/main-page-text-align-class-44c448"
BASE = G2 / "build/c-firmware/20261015/main-page-text-window-499a5c/apollo-main-page-text-window-499a5c.o"
ORACLE = HERE / "verify_main_page_text_align_class_44c448_oracle_20261015.py"
OWNED = {"audio_uart_lv_text_align_style_44b8ac",
         "audio_uart_lv_base_dir_style_44b8f6",
         "audio_uart_lv_bidi_calculate_align_44b7b4",
         "audio_uart_page_text_align_class_44c448"}
RESOLVED = "audio_uart_page_text_align_class_44c448"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_text_align_class_44c448.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_ALIGN_CLASS_ORACLE" or \
            oracle["cases"] != 25 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("text-align oracle changed")
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if RESOLVED not in before or symbols(obj, "--defined-only") != OWNED or \
            not symbols(obj, "-u") <= defined:
        raise RuntimeError("text-align provider contract changed")
    linked = OUT / "apollo-main-page-text-align-class-44c448.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if len(before) != 214 or len(after) != 213 or \
            before - after != {RESOLVED} or after - before or \
            not OWNED <= symbols(linked, "--defined-only"):
        raise RuntimeError("text-align linked contract changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_ALIGN_CLASS_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "source_owned_symbols": sorted(OWNED),
        "imports_resolved": [RESOLVED], "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "hardware_proof": False,
        "limits": ["25 controlled native style alignment comparisons.",
                   "Full-image placement and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
