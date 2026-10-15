#!/usr/bin/env python3
"""Bind bounded normal page attachment with explicit lower gates."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_attach_context_44d342.c"
OUT = G2 / "build/c-firmware/20261015/main-page-attach-context-44d342"
BASE = G2 / "build/c-firmware/20261015/main-page-overlay-44dca2/apollo-main-page-overlay-44dca2.o"
ORACLE = HERE / "verify_main_page_attach_context_44d342_oracle_20261015.py"
LOWER = {"audio_uart_page_unlink_44d3b2", "audio_uart_page_notify_44d5f8"}
EXISTING = {"audio_uart_lv_obj_setup_layer_43e1fa", "audio_uart_font_path_node_append",
            "audio_uart_lv_list_first", "audio_uart_lvgl_log"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_attach_context_44d342.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)],
                   check=True)
    defined = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "--defined-only", str(BASE)], text=True).splitlines()}
    if not EXISTING <= defined:
        raise RuntimeError("source-owned LVGL lower providers missing")
    linked = OUT / "apollo-main-page-attach-context-44d342.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    if before - after != {"audio_uart_page_attach_context_44d342"} or after - before != LOWER:
        raise RuntimeError("page attach context import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True,
                   text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_ATTACH_CONTEXT_44D342_ORACLE" or \
            oracle["cases"] != 8 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("page attach context oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_ATTACH_CONTEXT_NORMAL_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "existing_providers": sorted(EXISTING),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Normal attachment branches only were native-compared.",
                          "Unlink and notify need C ownership; allocation-failure log uses source-owned logger.",
                          "Final page-object layout and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
