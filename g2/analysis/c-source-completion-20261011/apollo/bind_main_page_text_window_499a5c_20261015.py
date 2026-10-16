#!/usr/bin/env python3
"""Bind the upstream-matched LVGL label letter-position body."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_text_window_499a5c.c"
OUT = G2 / "build/c-firmware/20261015/main-page-text-window-499a5c"
BASE = G2 / "build/c-firmware/20261015/main-page-layout-update-49a602/apollo-main-page-layout-update-49a602.o"
ORACLE = HERE / "verify_main_page_text_window_499a5c_oracle_20261015.py"
OWNED = {"audio_uart_page_text_window_499a5c",
         "audio_uart_page_pad_left_499388", "audio_uart_page_pad_top_49937e"}
CHILD = "audio_uart_page_text_align_class_44c448"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_text_window_499a5c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_WINDOW_ORACLE" or \
            oracle["cases"] != 50 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("text-window oracle changed")
    before = symbols(BASE, "-u")
    defined = symbols(BASE, "--defined-only")
    obj_imports = symbols(obj, "-u")
    if "audio_uart_page_text_window_499a5c" not in before or CHILD in before or \
            symbols(obj, "--defined-only") != OWNED or \
            obj_imports - defined != {CHILD}:
        raise RuntimeError("text-window provider contract changed")
    linked = OUT / "apollo-main-page-text-window-499a5c.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    resolved = {"audio_uart_page_text_window_499a5c"}
    if len(before) != 214 or len(after) != 214 or \
            before - after != resolved or after - before != {CHILD} or \
            not OWNED <= symbols(linked, "--defined-only"):
        raise RuntimeError("text-window linked contract changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_WINDOW_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
        "upstream": "third-party/upstream/lvgl/src/widgets/label/lv_label.c",
        "upstream_revision": "344c7c318047b7348e1be8572a9fd4260c251cfa",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "source_owned_symbols": sorted(OWNED),
        "imports_resolved": sorted(resolved), "imports_added": [CHILD],
        "source_complete": False, "full_payload_linked": False,
        "hardware_proof": False,
        "limits": ["50 controlled native comparisons cover ASCII positions, selected layout flags, and both fatal arguments.",
                   "Text alignment class 0x44c448 is bound in the next stage.",
                   "No full-image or hardware equivalence is established."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
