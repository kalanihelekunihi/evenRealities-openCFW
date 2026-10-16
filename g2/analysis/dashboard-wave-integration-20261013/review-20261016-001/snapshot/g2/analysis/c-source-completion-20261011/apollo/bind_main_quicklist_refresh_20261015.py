#!/usr/bin/env python3
"""Rebuild the bounded Apollo QuickList refresh C chain and its evidence."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate"
ANALYSIS = G2 / "analysis/c-source-completion-20261011/apollo"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-refresh"
BASE = G2 / "build/c-firmware/20261014/main-quicklist-tx-encoders/apollo-main-quicklist-tx-encoders.o"
FILES = ["quicklist_refresh_4f5e84.c", "quicklist_refresh_mutex_4ffac8.c",
         "quicklist_refresh_enabled_4434d0.c", "quicklist_refresh_pending_4f5596.c",
         "quicklist_refresh_ready_4f5e18.c"]
ORACLES = [
    ("verify_main_quicklist_refresh_oracle_20261015.py", "oracle.json", 32),
    ("verify_main_quicklist_refresh_mutex_oracle_20261015.py", "mutex-oracle.json", 24),
    ("verify_main_quicklist_refresh_enabled_oracle_20261015.py", "enabled-oracle.json", 64),
    ("verify_main_quicklist_refresh_pending_oracle_20261015.py", "pending-oracle.json", 180),
    ("verify_main_quicklist_refresh_ready_oracle_20261015.py", "ready-oracle.json", 90),
]
CHILDREN = {"audio_quicklist_mode_one_4f5718", "audio_quicklist_mode_two_4f5a1c",
            "audio_quicklist_mode_two_detail_4f5838", "audio_quicklist_mode_three_4f5c4c"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in
            subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    for name in FILES:
        src, obj = SOURCE / name, OUT / name.replace(".c", ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(src), "-o", str(obj)],
                       check=True)
        objects.append(obj)
    old = imports(BASE)
    if "audio_quicklist_refresh_4f5e84" not in old:
        raise RuntimeError("Main QuickList refresh import changed")
    linked = OUT / "apollo-main-quicklist-refresh-v4.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *(str(o) for o in objects),
                    "-o", str(linked)], check=True)
    new = imports(linked)
    if old - new != {"audio_quicklist_refresh_4f5e84"} or new - old != CHILDREN:
        raise RuntimeError(("unexpected Main import delta", sorted(old-new), sorted(new-old)))
    oracle_data = []
    for script, name, expected_cases in ORACLES:
        subprocess.run([sys.executable, str(ANALYSIS / script)], check=True,
                       capture_output=True, text=True)
        path = OUT / name
        receipt = json.loads(path.read_text())
        if not receipt["status"].startswith("PASS_EXPERIMENTAL_MAIN_QUICKLIST_REFRESH") or \
                receipt["cases"] != expected_cases:
            raise RuntimeError(("oracle changed", name))
        oracle_data.append({"script": str((ANALYSIS / script).relative_to(ROOT)),
                            "script_sha256": sha(ANALYSIS / script),
                            "receipt": str(path.relative_to(ROOT)), "receipt_sha256": sha(path),
                            "cases": expected_cases})
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_REFRESH_CHAIN_C",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "sources": [{"path": str((SOURCE / name).relative_to(ROOT)),
                     "sha256": sha(SOURCE / name),
                     "object_sha256": sha(OUT / name.replace(".c", ".o"))} for name in FILES],
        "oracles": oracle_data, "native_cases_total": sum(x[2] for x in ORACLES),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": len(old), "unresolved_after": len(new),
        "imports_resolved": sorted(old-new), "imports_added": sorted(new-old),
        "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
        "limits": ["Four QuickList mode handlers are unresolved.",
                   "Refresh oracle controls lower calls and disables logging; logging-enabled refresh paths remain unqualified.",
                   "Final RAM/ROM placement and hardware behavior remain open."],
        "supersedes_experimental_receipts": ["receipt.json", "mutex-receipt.json"]}
    path = OUT / "integrated-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(old), len(new), receipt["native_cases_total"], sha(path))


if __name__ == "__main__":
    main()
