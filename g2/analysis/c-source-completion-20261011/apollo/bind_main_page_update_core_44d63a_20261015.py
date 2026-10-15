#!/usr/bin/env python3
"""Bind native-compared page traversal and expose context lookup."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_update_core_44d63a.c"
OUT = G2 / "build/c-firmware/20261015/main-page-update-core-44d63a"
BASE = G2 / "build/c-firmware/20261015/main-page-update-wrappers-44d45c/apollo-main-page-update-wrappers-44d45c.o"
ORACLE = HERE / "verify_main_page_update_core_44d63a_oracle_20261015.py"
LOWER = {"audio_uart_page_context_find_44d77a"}
EXISTING = {"audio_uart_lv_obj_has_flag_43e0e0", "audio_uart_page_overlay_44dca2",
            "audio_uart_lv_obj_event_451670", "audio_uart_display_size_changed"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_update_core_44d63a.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)],
                   check=True)
    defined = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "--defined-only", str(BASE)], text=True).splitlines()}
    if not EXISTING <= defined:
        raise RuntimeError("source-owned LVGL page traversal providers missing")
    linked = OUT / "apollo-main-page-update-core-44d63a.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    if before - after != {"audio_uart_page_update_core_44d63a"} or after - before != LOWER:
        raise RuntimeError("page traversal import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_UPDATE_CORE_ORACLE" or \
            oracle["cases"] != 48 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("page traversal oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_UPDATE_CORE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "existing_providers": sorted(EXISTING),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["48 controlled traversal cases native-compared; full object/event semantics remain open.",
                          "Active-page context lookup at 0x44d77a needs C ownership.",
                          "Null-object diagnostic, full layout, and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
