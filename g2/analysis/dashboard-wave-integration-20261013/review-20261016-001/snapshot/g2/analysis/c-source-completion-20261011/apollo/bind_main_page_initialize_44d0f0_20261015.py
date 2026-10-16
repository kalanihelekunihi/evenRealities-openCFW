#!/usr/bin/env python3
"""Bind native-compared page initializer with explicit child imports."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_initialize_44d0f0.c"
OUT = G2 / "build/c-firmware/20261015/main-page-initialize-44d0f0"
BASE = G2 / "build/c-firmware/20261015/main-page-factory-498668/apollo-main-page-factory-498668.o"
ORACLE = HERE / "verify_main_page_initialize_44d0f0_oracle_20261015.py"
CHILDREN = {
    "audio_uart_page_lock_44bde0", "audio_uart_page_descriptor_init_44d1fc",
    "audio_uart_page_relayout_43ffa0",
    "audio_uart_page_context_44d33a", "audio_uart_page_needs_context_44d1cc",
    "audio_uart_page_attach_context_44d342", "audio_uart_page_overlay_44dca2",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_initialize_44d0f0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)],
                   check=True)
    linked = OUT / "apollo-main-page-initialize-44d0f0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    if before - after != {"audio_uart_page_initialize_44d0f0"} or after - before != CHILDREN:
        raise RuntimeError("page initializer import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True,
                   text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_INITIALIZE_44D0F0_ORACLE" or \
            oracle["cases"] != 16 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("page initializer oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_INITIALIZE_44D0F0_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Seven page-tree children now require C ownership or attribution; five use existing C bodies.",
                          "Final descriptor layout and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
