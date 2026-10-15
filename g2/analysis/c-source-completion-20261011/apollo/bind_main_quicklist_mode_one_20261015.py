#!/usr/bin/env python3
"""Bind the native-compared QuickList full-update and record-copy C bodies."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate"
HERE = Path(__file__).resolve().parent
OUT = G2 / "build/c-firmware/20261015/main-quicklist-mode-one"
BASE = G2 / "build/c-firmware/20261015/main-quicklist-refresh/apollo-main-quicklist-refresh-v4.o"
SOURCES = ("quicklist_mode_one_4f5718.c", "quicklist_copy_record_4f55e0.c")
ORACLES = (("verify_main_quicklist_mode_one_oracle_20261015.py", "oracle.json", 128),
           ("verify_main_quicklist_copy_record_oracle_20261015.py", "copy-oracle.json", 48))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    return {row.split()[-1] for row in
            subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    for name in SOURCES:
        src, obj = SOURCE / name, OUT / name.replace(".c", ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(src), "-o", str(obj)],
                       check=True)
        objects.append(obj)
    before = names(BASE, "-u")
    if "audio_quicklist_mode_one_4f5718" not in before:
        raise RuntimeError("QuickList full-update Main import changed")
    linked = OUT / "apollo-main-quicklist-mode-one.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *(str(p) for p in objects),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before-after != {"audio_quicklist_mode_one_4f5718"} or \
            after-before != {"audio_quicklist_aux_update_4f6328"}:
        raise RuntimeError("QuickList mode-one import delta changed")
    oracle_data = []
    for script, name, cases in ORACLES:
        subprocess.run([sys.executable, str(HERE / script)], check=True,
                       capture_output=True, text=True)
        path = OUT / name
        row = json.loads(path.read_text())
        if row["cases"] != cases or not row["status"].startswith("PASS_EXPERIMENTAL_MAIN_QUICKLIST_"):
            raise RuntimeError("QuickList mode-one oracle changed")
        oracle_data.append({"script": str((HERE / script).relative_to(ROOT)),
                            "script_sha256": sha(HERE / script),
                            "receipt": str(path.relative_to(ROOT)), "receipt_sha256": sha(path),
                            "cases": cases})
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_ONE_C",
               "sources": [{"path": str((SOURCE / name).relative_to(ROOT)),
                            "sha256": sha(SOURCE / name),
                            "object_sha256": sha(OUT / name.replace(".c", ".o"))} for name in SOURCES],
               "oracles": oracle_data, "native_cases_total": 176,
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["QuickList auxiliary update 0x4f6328 and three other mode handlers remain open.",
                          "Mode-one oracle controls record copy, auxiliary update and logging at lower interfaces.",
                          "Final RAM placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
