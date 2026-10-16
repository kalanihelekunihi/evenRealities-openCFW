#!/usr/bin/env python3
"""Bind native-compared page notification with explicit update dependencies."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_notify_44d5f8.c"
OUT = G2 / "build/c-firmware/20261015/main-page-notify-44d5f8"
BASE = G2 / "build/c-firmware/20261015/main-page-attach-context-44d342/apollo-main-page-attach-context-44d342.o"
ORACLE = HERE / "verify_main_page_notify_44d5f8_oracle_20261015.py"
LOWER = {"audio_uart_page_update_unbound_44d45c", "audio_uart_page_update_bound_44d4b6"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_notify_44d5f8.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)],
                   check=True)
    linked = OUT / "apollo-main-page-notify-44d5f8.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    if before - after != {"audio_uart_page_notify_44d5f8"} or after - before != LOWER:
        raise RuntimeError("page notification import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_NOTIFY_44D5F8_ORACLE" or \
            oracle["cases"] != 33 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("page notification oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_NOTIFY_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Only 66-byte page notification dispatcher is native-compared.",
                          "Bound and unbound page update bodies remain lower C dependencies.",
                          "Full image layout and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
