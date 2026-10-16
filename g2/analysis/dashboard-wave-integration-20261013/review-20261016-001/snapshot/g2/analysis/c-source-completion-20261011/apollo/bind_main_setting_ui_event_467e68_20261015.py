#!/usr/bin/env python3
"""Bind native-checked Setting UI callback into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/setting_ui_event_handler_467e68.c"
ORACLE = G2 / "build/c-firmware/20261015/main-setting-ui-event-467e68/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-logger-ble-pb-descriptor-777da4/apollo-main-logger-ble-pb-descriptor-777da4.o"
OUT = G2 / "build/c-firmware/20261015/main-setting-ui-event-467e68"
OWNED = {"audio_uart_registry_callback_467e68"}
ADDED = {"audio_settings_notify_recalibration_status_49beac",
         "audio_uart_calibration_snapshot_200749a8",
         "audio_uart_calibration_status_2007501c",
         "audio_uart_hub_calibration_display_update_4a7472",
         "audio_uart_hub_calibration_success_display_4a76e4"}
IMPORTS = ADDED | {"audio_log_extended", "audio_log_flags",
                   "audio_settings_get_config_46b44c", "audio_settings_notify_device_status",
                   "audio_uart_registry_context_20003a40", "compressed_log_output"}
BODY_SHA = "5c010c15b5e1c5a0b765a270cd037909278d4828af3559d87556784bf8ba72b3"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_SETTING_UI_EVENT_467E68" or \
       oracle["cases"] != 80 or oracle["source_sha256"] != sha(SOURCE) or \
       oracle["native_body_sha256"] != BODY_SHA:
        raise RuntimeError("Native Setting UI evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "setting_ui_event_handler_467e68.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != IMPORTS:
        raise RuntimeError("Setting UI object contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 216 or not OWNED <= before or \
       not (IMPORTS-ADDED-{"audio_uart_registry_context_20003a40"}) <= symbols(BASE, "--defined-only"):
        raise RuntimeError("Setting UI base contract changed")
    linked = OUT / "apollo-main-setting-ui-event-467e68.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before-after != OWNED or after-before != ADDED or len(after) != 220:
        raise RuntimeError("Setting UI link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SETTING_UI_EVENT_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"], "native_body_sha256": BODY_SHA,
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(OWNED), "imports_added": sorted(ADDED),
               "unresolved_before": 216, "unresolved_after": 220,
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Calibration UI providers and two RAM locations remain explicit imports; final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"], 216, 220, sha(path))

if __name__ == "__main__": main()
