#!/usr/bin/env python3
"""Resolve QuickList notify transport to the existing native-compared C body."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_settings_notify_ble.c"
ALIAS = G2 / "components/audio/uart_thread_source_candidate/quicklist_notify_alias_475c1a.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-notify-alias"
BASE = G2 / "build/c-firmware/20261015/main-quicklist-send-completed/apollo-main-quicklist-send-completed.o"
ORACLE = HERE / "verify_main_quicklist_notify_alias_oracle_20261015.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_notify_alias_475c1a.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(ALIAS), "-o", str(obj)],
                   check=True)
    linked = OUT / "apollo-main-quicklist-notify-alias.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    if before - after != {"audio_ring_pb_tx_ble_475c1a"} or after - before:
        raise RuntimeError("QuickList notify transport import contract changed")
    if "audio_settings_notify_ble" not in subprocess.check_output(
            ["arm-none-eabi-nm", "--defined-only", str(BASE)], text=True):
        raise RuntimeError("source-owned BLE notification body missing")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True,
                   text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_NOTIFY_ALIAS_ORACLE" or \
            oracle["cases"] != 64 or oracle["source_sha256"] != sha(SOURCE) or \
            oracle["alias_sha256"] != sha(ALIAS):
        raise RuntimeError("QuickList notify transport oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_NOTIFY_ALIAS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "alias": str(ALIAS.relative_to(ROOT)), "alias_sha256": sha(ALIAS),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["BLE lower send and logging are controlled interfaces.",
                          "Final RAM placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
