#!/usr/bin/env python3
"""Bind native-compared page relayout to source-owned LVGL style queries."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_relayout_43ffa0.c"
OUT = G2 / "build/c-firmware/20261015/main-page-relayout-43ffa0"
BASE = G2 / "build/c-firmware/20261015/main-page-context-44d33a/apollo-main-page-context-44d33a.o"
ORACLE = HERE / "verify_main_page_relayout_43ffa0_oracle_20261015.py"
EXISTING = {"audio_uart_lv_style_width_43eea6", "audio_uart_lv_style_height_43eec4",
            "audio_uart_lv_mark_layout_43f648"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_relayout_43ffa0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)],
                   check=True)
    defined = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "--defined-only", str(BASE)], text=True).splitlines()}
    if not EXISTING <= defined:
        raise RuntimeError("source-owned LVGL style providers missing")
    linked = OUT / "apollo-main-page-relayout-43ffa0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    if before - after != {"audio_uart_page_relayout_43ffa0"} or after - before:
        raise RuntimeError("page relayout import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True,
                   text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_RELAYOUT_43FFA0_ORACLE" or \
            oracle["cases"] != 32 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("page relayout oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_RELAYOUT_43FFA0_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "existing_providers": sorted(EXISTING),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Full LVGL style semantics and hardware display remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
