#!/usr/bin/env python3
"""Bind native-compared page factory with explicit lower provider imports."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_factory_498668.c"
OUT = G2 / "build/c-firmware/20261015/main-page-factory-498668"
BASE = G2 / "build/c-firmware/20261015/main-quicklist-notify-alias/apollo-main-quicklist-notify-alias.o"
ORACLE = HERE / "verify_main_page_factory_498668_oracle_20261015.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_factory_498668.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)],
                   check=True)
    linked = OUT / "apollo-main-page-factory-498668.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    if before - after != {"audio_uart_page_498668"} or after - before != {
            "audio_uart_page_create_44cf98", "audio_uart_page_initialize_44d0f0"}:
        raise RuntimeError("page factory import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True,
                   text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_498668_ORACLE" or \
            oracle["cases"] != 9 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("page factory oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_498668_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Page allocator 0x44cf98 and initializer 0x44d0f0 need C ownership.",
                          "Descriptor 0x756108 is a stock ROM address, pending source-owned layout."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
