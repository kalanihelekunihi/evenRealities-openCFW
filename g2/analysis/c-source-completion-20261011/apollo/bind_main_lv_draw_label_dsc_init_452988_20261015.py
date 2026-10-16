#!/usr/bin/env python3
"""Bind native-compared LVGL label descriptor style initialization."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_label_dsc_init_452988.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-label-dsc-init-452988"
BASE = G2 / "build/c-firmware/20261015/main-lv-draw-label-489fe0/apollo-main-lv-draw-label-489fe0.o"
ORACLE = HERE / "verify_main_lv_draw_label_dsc_init_452988_oracle_20261015.py"
OWNED = "audio_uart_lv_draw_label_dsc_init_452988"
CHILDREN = set()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_draw_label_dsc_init_452988.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_LABEL_DSC_INIT_ORACLE" or \
            oracle["cases"] != 120 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("descriptor initializer oracle changed")
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    if OWNED not in before or symbols(obj, "--defined-only") != {OWNED} or \
            symbols(obj, "-u") - defined != CHILDREN:
        raise RuntimeError("descriptor initializer provider contract changed")
    linked = OUT / "apollo-main-lv-draw-label-dsc-init-452988.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if len(before) != 213 or len(after) != 212 or \
            before - after != {OWNED} or after - before != CHILDREN or \
            OWNED not in symbols(linked, "--defined-only"):
        raise RuntimeError("descriptor initializer linked contract changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_LABEL_DSC_INIT_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
        "upstream": "third-party/upstream/lvgl/src/core/lv_obj_draw.c",
        "upstream_revision": "344c7c318047b7348e1be8572a9fd4260c251cfa",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "source_owned_symbols": [OWNED], "imports_resolved": [OWNED],
        "imports_added": sorted(CHILDREN), "source_complete": False,
        "full_payload_linked": False, "hardware_proof": False,
        "limits": ["120 native opacity, style and descriptor comparisons.",
                   "Layer opacity and color mixing use previously bound C providers.",
                   "No full-image or hardware equivalence is established."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
