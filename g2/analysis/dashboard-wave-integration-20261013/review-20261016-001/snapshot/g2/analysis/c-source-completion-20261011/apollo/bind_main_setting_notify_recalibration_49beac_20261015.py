#!/usr/bin/env python3
"""Bind native-checked recalibration notification into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/setting_notify_recalibration_49beac.c"
ORACLE = G2 / "build/c-firmware/20261015/main-setting-notify-recalibration-49beac/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-setting-ui-event-467e68/apollo-main-setting-ui-event-467e68.o"
OUT = G2 / "build/c-firmware/20261015/main-setting-notify-recalibration-49beac"
OWNED = {"audio_settings_notify_recalibration_status_49beac"}
IMPORTS = {"audio_log_extended", "audio_log_flags", "audio_settings_notify_common",
           "audio_uart_buffer_zero", "compressed_log_output"}
BODY_SHA = "54ec38cf0e8f951d1c68286c4d3a250b72b88775711c44e37aa6639a0d1b62ae"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_SETTING_NOTIFY_RECALIBRATION_49BEAC" or \
       oracle["cases"] != 25 or oracle["source_sha256"] != sha(SOURCE) or \
       oracle["native_body_sha256"] != BODY_SHA:
        raise RuntimeError("Native recalibration notification evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "setting_notify_recalibration_49beac.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != IMPORTS:
        raise RuntimeError("Recalibration notification object contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 220 or not OWNED <= before or \
       not IMPORTS <= symbols(BASE, "--defined-only"):
        raise RuntimeError("Recalibration notification base contract changed")
    linked = OUT / "apollo-main-setting-notify-recalibration-49beac.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before-after != OWNED or after-before or len(after) != 219:
        raise RuntimeError("Recalibration notification link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SETTING_NOTIFY_RECALIBRATION_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"], "native_body_sha256": BODY_SHA,
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(OWNED), "imports_added": [],
               "unresolved_before": 220, "unresolved_after": 219,
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Notification packet is C-bound; final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"], 220, 219, sha(path))

if __name__ == "__main__": main()
