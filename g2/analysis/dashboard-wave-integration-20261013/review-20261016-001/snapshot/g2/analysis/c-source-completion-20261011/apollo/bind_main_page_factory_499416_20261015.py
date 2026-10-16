#!/usr/bin/env python3
"""Bind native-compared page factory callback into Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_factory_499416.c"
CLASS = G2 / "components/audio/uart_thread_source_candidate/display_page_class_7561bc.c"
OUT = G2 / "build/c-firmware/20261015/main-page-factory-499416"
BASE = G2 / "build/c-firmware/20261015/main-lv-font-bitmap-4b239c/apollo-main-lv-font-bitmap-4b239c.o"
ORACLE = HERE / "verify_main_page_factory_499416_oracle_20261015.py"
RESOLVED = {"audio_uart_page_499416"}
ADDED = {"audio_uart_page_class_ctor_49a0c0", "audio_uart_page_class_dtor_49a150",
         "audio_uart_page_class_event_49a16e"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_page_factory_499416.o"
    class_obj = OUT / "display_page_class_7561bc.o"
    for src, dest in ((SOURCE, obj), (CLASS, class_obj)):
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(src), "-o", str(dest)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_499416_ORACLE" or \
            oracle["cases"] != 9 or oracle["source_sha256"] != sha(SOURCE) or \
            oracle["class_source_sha256"] != sha(CLASS) or oracle["descriptor_bytes"] != 36:
        raise RuntimeError("page factory oracle changed")
    linked = OUT / "apollo-main-page-factory-499416.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), str(class_obj),
                    "-o", str(linked)], check=True)
    before, after = symbols(BASE), symbols(linked)
    if before - after != RESOLVED or after - before != ADDED or \
            len(before) != 234 or len(after) != 236:
        raise RuntimeError("page factory import contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_499416_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "class_source": str(CLASS.relative_to(ROOT)), "class_source_sha256": sha(CLASS),
               "object_sha256": sha(obj), "class_object_sha256": sha(class_obj),
               "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": oracle["limits"]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
