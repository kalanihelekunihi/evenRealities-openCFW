#!/usr/bin/env python3
"""Bind native-compared LVGL draw-label task submission and text copy."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_label_489fe0.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-label-489fe0"
BASE = G2 / "build/c-firmware/20261015/main-page-draw-main-49a31c/apollo-main-page-draw-main-49a31c.o"
ORACLE = HERE / "verify_main_lv_draw_label_489fe0_oracle_20261015.py"
OWNED = {"audio_uart_lv_draw_label_489fe0", "audio_uart_lv_draw_task_strdup_4547f2"}
RESOLVED = "audio_uart_lv_draw_label_489fe0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_draw_label_489fe0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_LABEL_ORACLE" or \
            oracle["cases"] != 48 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("draw-label oracle changed")
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if RESOLVED not in before or symbols(obj, "--defined-only") != OWNED or \
            symbols(obj, "-u") - defined:
        raise RuntimeError("draw-label provider contract changed")
    linked = OUT / "apollo-main-lv-draw-label-489fe0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if len(before) != 214 or len(after) != 213 or \
            before - after != {RESOLVED} or after - before or \
            not OWNED <= symbols(linked, "--defined-only"):
        raise RuntimeError("draw-label linked contract changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_LABEL_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
        "upstream": "third-party/upstream/lvgl/src/draw/lv_draw_label.c",
        "upstream_revision": "344c7c318047b7348e1be8572a9fd4260c251cfa",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "source_owned_symbols": sorted(OWNED),
        "imports_resolved": [RESOLVED], "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "hardware_proof": False,
        "limits": ["48 controlled native draw-task and local text-copy comparisons.",
                   "Allocation failure and hardware rendering remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
