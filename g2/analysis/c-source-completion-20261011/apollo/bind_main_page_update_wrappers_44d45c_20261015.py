#!/usr/bin/env python3
"""Bind native-compared page update wrappers with traversal gates."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_update_wrappers_44d45c.c"
OUT = G2 / "build/c-firmware/20261015/main-page-update-wrappers-44d45c"
BASE = G2 / "build/c-firmware/20261015/main-page-notify-44d5f8/apollo-main-page-notify-44d5f8.o"
ORACLE = HERE / "verify_main_page_update_wrappers_44d45c_oracle_20261015.py"
FATAL_ORACLE = HERE / "verify_main_page_fatal_calls_20261015.py"
LOWER = {"audio_uart_page_update_core_44d63a"}
EXISTING = {"audio_uart_lv_list_first", "audio_uart_lv_list_next",
            "audio_uart_lv_list_first_482ce4", "audio_uart_lv_list_next_482cfa",
            "audio_uart_lvgl_log"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_update_wrappers_44d45c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)],
                   check=True)
    defined = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "--defined-only", str(BASE)], text=True).splitlines()}
    if not EXISTING <= defined:
        raise RuntimeError("source-owned LVGL list accessors missing")
    linked = OUT / "apollo-main-page-update-wrappers-44d45c.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    removed = {"audio_uart_page_update_unbound_44d45c", "audio_uart_page_update_bound_44d4b6"}
    if before - after != removed or after - before != LOWER:
        raise RuntimeError("page update wrapper import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_UPDATE_WRAPPERS_ORACLE" or \
            oracle["cases"] != 12 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("page update wrapper oracle changed")
    subprocess.run([sys.executable, str(FATAL_ORACLE)], check=True, capture_output=True,
                   text=True)
    fatal = json.loads((G2 / "build/c-firmware/20261015/main-page-fatal-calls/oracle.json").read_text())
    attach_source = G2 / "components/audio/uart_thread_source_candidate/display_page_attach_context_44d342.c"
    expected_sources = {str(path.relative_to(ROOT)): sha(path) for path in (attach_source, SOURCE)}
    if fatal["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FATAL_CALLS_ORACLE" or \
            fatal["cases"] != 3 or \
            {entry["path"]:entry["sha256"] for entry in fatal["sources"]} != expected_sources:
        raise RuntimeError("page fatal logger oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_UPDATE_WRAPPERS_NORMAL_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "fatal_oracle_sha256": sha(G2 / "build/c-firmware/20261015/main-page-fatal-calls/oracle.json"),
               "existing_providers": sorted(EXISTING),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Only non-null update wrappers are native-compared.",
                          "Traversal core remains a lower C dependency; four iterator callbacks use existing source-owned LVGL accessors.",
                          "Fatal diagnostic arguments use source-owned logger; layout and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
